"""Utility functions and classes."""

import os
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cmp_to_key
from typing import Any, Literal

import pandas as pd
from github import Auth
from loguru import logger
from pydantic import BaseModel, Field
from roman import fromRoman as roman_to_int  # noqa: N813


def get_github_auth(
    token: str | None = None,
    user: str | None = None,
    password: str | None = None,
) -> Auth.Auth | None:
    """Get the GitHub authentication object from arguments or environment variables."""
    token = token or os.getenv("GITHUB_TOKEN")
    user = user or os.getenv("GITHUB_USER")
    password = password or os.getenv("GITHUB_PASSWORD")

    if token:
        logger.debug("Using GITHUB_TOKEN for authentication.")
        return Auth.Token(token)

    if user and password:
        logger.debug("Using GITHUB_USER and GITHUB_PASSWORD for authentication.")
        return Auth.Login(user, password)

    logger.info("No authentication provided. Using unauthenticated access.")
    return None


def update_and_expand(
    left: pd.DataFrame,
    right: pd.DataFrame,
    **update_kwargs: Any,
) -> pd.DataFrame:
    """Update ``left`` with values from ``right``, also adding columns from ``right``.

    The added feature of this function over pandas' :py:meth:`~pandas.DataFrame.update`
    is that it also adds columns that are present in ``right`` but not in ``left``.

    Any keyword arguments are also directly passed to the
    :py:meth:`~pandas.DataFrame.update`.

    >>> left = pd.DataFrame({"a": [1, 2, None], "b": [3, 4, 5]})
    >>> right = pd.DataFrame({"a": [None, 3, 4], "c": [6, 7, 8]})
    >>> update_and_expand(left, right)
         a  b  c
    0  1.0  3  6
    1  3.0  4  7
    2  4.0  5  8
    """
    result = left.copy()
    result.update(right, **update_kwargs)

    for column in right.columns:
        if column not in result.columns:
            result[column] = right[column]

    return result


def replace(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    """Replace all columns in ``left`` with those from ``right``."""
    result = left.copy()

    for column in right.columns:
        result[column] = right[column]

    return result


@dataclass
class _ColumnSpec:
    """Class for specifying column names and aggfuncs.

    This serves a dual purpose:

    1. It is a simple container that ties together a short name and a long name. For
       this we could have used a `namedtuple` as well.
    2. Every `_ColumnSpec` is also an aggregation function in itself. This is used in
       the :py:meth:`~lydata.accessor.LyDataAccessor.stats` method.
    """

    short: str
    long: tuple[str, str, str]
    agg_func: str | Callable[[pd.Series], pd.Series] = "value_counts"
    agg_kwargs: dict[str, Any] = field(default_factory=lambda: {"dropna": False})

    def __call__(self, series: pd.Series) -> pd.Series:
        """Call the aggregation function on the series."""
        return series.agg(self.agg_func, **self.agg_kwargs)


@dataclass
class _ColumnMap:
    """Class for mapping short and long column names."""

    from_short: dict[str, _ColumnSpec]
    from_long: dict[tuple[str, str, str], _ColumnSpec]

    def __post_init__(self) -> None:
        """Check ``from_short`` and ``from_long`` contain same ``_ColumnSpec``."""
        for left, right in zip(
            self.from_short.values(), self.from_long.values(), strict=True
        ):
            if left != right:
                raise ValueError(
                    "`from_short` and `from_long` contain different "
                    "`_ColumnSpec` instances"
                )

    @classmethod
    def from_list(cls, columns: list[_ColumnSpec]) -> "_ColumnMap":
        """Create a ColumnMap from a list of ColumnSpecs."""
        short = {col.short: col for col in columns}
        long = {col.long: col for col in columns}
        return cls(short, long)

    def __iter__(self):
        """Iterate over the short names."""
        return iter(self.from_short.values())


def get_default_column_map_old() -> _ColumnMap:
    """Get the old default column map.

    This map defines which short column names can be used to access columns in the
    DataFrames.

    >>> from lydata import accessor, loader
    >>> df = next(loader.load_datasets(
    ...     institution="usz",
    ...     repo_name="lycosystem/lydata.private",
    ...     ref="ab04379a36b6946306041d1d38ad7e97df8ee7ba",
    ... ))
    >>> df.ly.surgery   # doctest: +ELLIPSIS
    0      False
    ...
    286    False
    Name: (patient, #, neck_dissection), Length: 287, dtype: bool
    >>> df.ly.smoke   # doctest: +ELLIPSIS
    0       True
    ...
    286     True
    Name: (patient, #, nicotine_abuse), Length: 287, dtype: bool
    """
    return _ColumnMap.from_list(
        [
            _ColumnSpec("id", ("patient", "#", "id")),
            _ColumnSpec("institution", ("patient", "#", "institution")),
            _ColumnSpec("sex", ("patient", "#", "sex")),
            _ColumnSpec("age", ("patient", "#", "age")),
            _ColumnSpec("weight", ("patient", "#", "weight")),
            _ColumnSpec("date", ("patient", "#", "diagnose_date")),
            _ColumnSpec("surgery", ("patient", "#", "neck_dissection")),
            _ColumnSpec("hpv", ("patient", "#", "hpv_status")),
            _ColumnSpec("smoke", ("patient", "#", "nicotine_abuse")),
            _ColumnSpec("alcohol", ("patient", "#", "alcohol_abuse")),
            _ColumnSpec("t_stage", ("tumor", "1", "t_stage")),
            _ColumnSpec("n_stage", ("patient", "#", "n_stage")),
            _ColumnSpec("m_stage", ("patient", "#", "m_stage")),
            _ColumnSpec("midext", ("tumor", "1", "extension")),
            _ColumnSpec("subsite", ("tumor", "1", "subsite")),
            _ColumnSpec("location", ("tumor", "1", "location")),
            _ColumnSpec("volume", ("tumor", "1", "volume")),
            _ColumnSpec("central", ("tumor", "1", "central")),
            _ColumnSpec("side", ("tumor", "1", "side")),
        ]
    )


def _new_from_old(long_name: tuple[str, str, str]) -> tuple[str, str, str]:
    """Convert an old long key name to a new long key name.

    >>> _new_from_old(("patient", "#", "neck_dissection"))
    ('patient', 'core', 'neck_dissection')
    >>> _new_from_old(("tumor", "1", "t_stage"))
    ('tumor', 'core', 't_stage')
    >>> _new_from_old(("a", "b", "c"))
    ('a', 'b', 'c')
    """
    start, middle, end = long_name
    if (start == "patient" and middle == "#") or (start == "tumor" and middle == "1"):
        middle = "core"
    return (start, middle, end)


def is_old(dataset: pd.DataFrame) -> bool:
    """Check if the dataset uses the old column names."""
    second_lvl_headers = dataset.columns.get_level_values(1)
    return "#" in second_lvl_headers or "1" in second_lvl_headers


def get_default_column_map_new() -> _ColumnMap:
    """Get the old default column map.

    This map defines which short column names can be used to access columns in the
    DataFrames.

    >>> from lydata import accessor, loader
    >>> df = next(loader.load_datasets(
    ...     institution="usz",
    ...     repo_name="lycosystem/lydata.private",
    ...     ref="fb55afa26ff78afa78274a86b131fb3014d0ceea",
    ... ))
    >>> df.ly.surgery   # doctest: +ELLIPSIS
    0      False
    ...
    286    False
    Name: (patient, core, neck_dissection), Length: 287, dtype: bool
    >>> df.ly.smoke   # doctest: +ELLIPSIS
    0       True
    ...
    286     True
    Name: (patient, core, nicotine_abuse), Length: 287, dtype: bool
    """
    return _ColumnMap.from_list(
        [
            _ColumnSpec(cs.short, _new_from_old(cs.long))
            for cs in get_default_column_map_old()
        ]
    )


class ModalityConfig(BaseModel):
    """Define a diagnostic or pathological modality."""

    spec: float = Field(ge=0.5, le=1.0, description="Specificity of the modality.")
    sens: float = Field(ge=0.5, le=1.0, description="Sensitivity of the modality.")
    kind: Literal["clinical", "pathological"] = Field(
        default="clinical",
        description="Clinical modalities cannot detect microscopic disease.",
    )


def get_default_modalities() -> dict[str, ModalityConfig]:
    """Get defaults values for sensitivities and specificities of modalities.

    Taken from `de Bondt et al. (2007) <https://doi.org/10.1016/j.ejrad.2007.02.037>`_
    and `Kyzas et al. (2008) <https://doi.org/10.1093/jnci/djn125>`_.
    """
    return {
        "CT": ModalityConfig(spec=0.76, sens=0.81),
        "MRI": ModalityConfig(spec=0.63, sens=0.81),
        "PET": ModalityConfig(spec=0.86, sens=0.79),
        "FNA": ModalityConfig(spec=0.98, sens=0.80, kind="pathological"),
        "diagnostic_consensus": ModalityConfig(spec=0.86, sens=0.81),
        "pathology": ModalityConfig(spec=1.0, sens=1.0, kind="pathological"),
        "pCT": ModalityConfig(spec=0.86, sens=0.81),
    }


def _get_all_true(df: pd.DataFrame) -> pd.Series:
    """Return a mask with all entries set to ``True``."""
    return pd.Series([True] * len(df))


def _get_numeral_with_sub_value(key: str) -> float:
    """Get the value of a Roman numeral with an optional sublevel.

    >>> _get_numeral_with_sub_value("I")
    1.0
    >>> _get_numeral_with_sub_value("IIa")
    2.01
    >>> _get_numeral_with_sub_value("IXb")
    9.02
    """
    match = re.match(r"([IVXLCDM]+)([a-z]?)", key)
    if match is None:
        raise ValueError(f"Invalid Roman numeral with sublevel: {key}")
    numeral, sublvl = match.groups()

    base = roman_to_int(numeral)
    addition = 0.0

    if len(sublvl) == 1:
        addition = "abcdefghijklmnopqrstuvwxyz".index(sublvl) / 100.0 + 0.01

    return base + addition


def _top_lvl_cmp(left: str, right: str) -> int:
    """Compare two top-level column names."""
    if left == right:
        return 0

    if left == "patient":
        return -1

    if right == "patient":
        return 1

    if left == "tumor":
        return -1

    if right == "tumor":
        return 1

    if left == "max_llh":
        return -1

    if right == "max_llh":
        return 1

    return (left > right) - (left < right)


def _mid_lvl_cmp(left: str, right: str) -> int:
    """Compare two mid-level column names."""
    if left == right:
        return 0

    if left == "core":
        return -1

    if right == "core":
        return 1

    return (left > right) - (left < right)


def _lnl_cmp(left: str, right: str) -> int:
    """Compare two roman numeral LNLs."""
    try:
        left_value = _get_numeral_with_sub_value(left)
        right_value = _get_numeral_with_sub_value(right)
        return (left_value > right_value) - (left_value < right_value)
    except ValueError:
        if "id" in left:
            return -1
        if "id" in right:
            return 1

        return (left > right) - (left < right)


def _sort_by(
    dataset: pd.DataFrame,
    which: Literal["top", "mid", "lnl"],
    level: int | None = None,
) -> pd.DataFrame:
    """Sort the DataFrame columns by the specified level."""
    if level is None:
        level = ["top", "mid", "lnl"].index(which)

    cmps = {
        "top": _top_lvl_cmp,
        "mid": _mid_lvl_cmp,
        "lnl": _lnl_cmp,
    }

    if which not in cmps:
        raise ValueError(f"Invalid sorting level: {which} ('top', 'mid', or 'lnl').")

    if level < 0 or level > 2:
        raise ValueError(f"Invalid level: {level} (must be 0, 1, or 2).")

    columns = dataset.columns.get_level_values(level).unique()
    sorted_columns = sorted(columns, key=cmp_to_key(cmps[which]))
    return dataset.reindex(columns=sorted_columns, level=level)


def _sort_all(dataset: pd.DataFrame) -> pd.DataFrame:
    """Use the custom sorting to sort the DataFrame columns by all levels."""
    dataset = _sort_by(dataset, "lnl", level=2)
    dataset = _sort_by(dataset, "mid", level=1)
    return _sort_by(dataset, "top", level=0)
