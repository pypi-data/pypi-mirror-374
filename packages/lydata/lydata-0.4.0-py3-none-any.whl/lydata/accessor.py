"""Module containing a custom accessor for interacting with lyDATA tables.

Because of the special three-level header of the lyDATA tables, it is sometimes
cumbersome and lengthy to access the columns. While this is certainly necessary to
access e.g. the contralateral involvement of LNL II as observed on CT images
(``df["CT", "contra", "II"]``), for simple patient information such as age and HPV
status, it is more convenient to use short names, which we implement in this module.

The main class in this module is the :py:class:`LyDataAccessor` class, which provides
the above mentioned functionality. That way, accessing the age of all patients is now
as easy as typing ``df.ly.age``.

Beyond that, we implement methods like :py:meth:`~LyDataAccessor.query` for filtering
the DataFrame using reusable query objects (see the :py:mod:`lydata.querier` module
for more information), :py:meth:`~LyDataAccessor.stats` for computing common statistics
that we use in our `LyProX`_ web app, and :py:meth:`~LyDataAccessor.combine` for
combining diagnoses from different modalities into a single column.

.. _LyProX: https://lyprox.org/
"""

from __future__ import annotations

import warnings
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

import pandas as pd
import pandas.api.extensions as pd_ext

from lydata.augmentor import combine_and_augment_levels
from lydata.types import CanExecute
from lydata.utils import (
    ModalityConfig,
    _get_all_true,
    _sort_all,
    get_default_column_map_new,
    get_default_column_map_old,
    get_default_modalities,
    replace,
)

warnings.simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


AggFuncType = dict[str | tuple[str, str, str], Callable[[pd.Series], pd.Series]]


@dataclass  # we use a dataclass over pydantic, because it allows positional arguments
class QueryPortion:
    """Dataclass for storing the portion of a query.

    An instance of this is returned by the :py:meth:`LyDataAccessor.portion` method.
    """

    match: int
    total: int

    def __post_init__(self) -> None:
        """Check that the portion is valid.

        >>> QueryPortion(5, 2)
        Traceback (most recent call last):
            ...
        ValueError: Match must be less than or equal to total.
        """
        if self.total < 0:
            raise ValueError("Total must be non-negative.")
        if self.match < 0:
            raise ValueError("Match must be non-negative.")
        if self.match > self.total:
            raise ValueError("Match must be less than or equal to total.")

    @property
    def fail(self) -> int:
        """Get the number of failures.

        >>> QueryPortion(2, 5).fail
        3
        """
        return self.total - self.match

    @property
    def ratio(self) -> float:
        """Get the ratio of matches over the total.

        >>> QueryPortion(2, 5).ratio
        0.4
        """
        return self.match / self.total

    @property
    def percent(self) -> float:
        """Get the percentage of matches over the total.

        >>> QueryPortion(2, 5).percent
        40.0
        """
        return self.ratio * 100.0

    def invert(self) -> QueryPortion:
        """Return the inverted portion.

        >>> QueryPortion(2, 5).invert()
        QueryPortion(match=3, total=5)
        """
        return QueryPortion(match=self.fail, total=self.total)


@pd_ext.register_dataframe_accessor("ly")
class LyDataAccessor:
    """Custom accessor for handling lymphatic involvement data.

    This aims to provide an easy and user-friendly interface to the most commonly needed
    operations on the lymphatic involvement data we publish in the lydata project.
    """

    def __init__(self, obj: pd.DataFrame) -> None:
        """Initialize the accessor with a DataFrame."""
        self._obj = obj
        self._column_map_old = get_default_column_map_old()
        self._column_map_new = get_default_column_map_new()

    def _get_safe_long_old(self, key: Any) -> tuple[str, str, str]:
        """Get the old long column name or return the input."""
        return getattr(self._column_map_old.from_short.get(key), "long", key)

    def _get_safe_long_new(self, key: Any) -> tuple[str, str, str]:
        """Get the new long column name or return the input."""
        return getattr(self._column_map_new.from_short.get(key), "long", key)

    def __contains__(self, key: str) -> bool:
        """Check if a column is contained in the DataFrame.

        >>> df = pd.DataFrame({("patient", "#", "age"): [61, 52, 73]})
        >>> "age" in df.ly
        True
        >>> "foo" in df.ly
        False
        >>> ("patient", "#", "age") in df.ly
        True
        >>> df = pd.DataFrame({("patient", "core", "age"): [61, 52, 73]})
        >>> "age" in df.ly
        True
        >>> "foo" in df.ly
        False
        >>> ("patient", "core", "age") in df.ly
        True
        """
        key_old = self._get_safe_long_old(key)
        key_new = self._get_safe_long_new(key)
        return key_new in self._obj or key_old in self._obj

    def __getitem__(self, key: str) -> pd.Series:
        """Allow column access by short name, too.

        >>> df = pd.DataFrame({("patient", "core", "nicotine_abuse"): [True, False]})
        >>> df.ly["smoke"]
        0     True
        1    False
        Name: (patient, core, nicotine_abuse), dtype: bool
        """
        key_old = self._get_safe_long_old(key)
        key_new = self._get_safe_long_new(key)

        for key in (key_new, key_old):
            if key in self:
                return self._obj[key]

        raise KeyError(f"Neither '{key_new}' nor '{key_old}' found in DataFrame.")

    def __getattr__(self, name: str) -> Any:
        """Access columns also by short name.

        >>> df = pd.DataFrame({("patient", "#", "age"): [61, 52, 73]})
        >>> df.ly.age
        0    61
        1    52
        2    73
        Name: (patient, #, age), dtype: int64
        >>> df = pd.DataFrame({("patient", "core", "age"): [61, 52, 73]})
        >>> df.ly.age
        0    61
        1    52
        2    73
        Name: (patient, core, age), dtype: int64
        >>> df.ly.foo
        Traceback (most recent call last):
            ...
        AttributeError: Attribute 'foo' not found.
        """
        try:
            return self[name]
        except KeyError as key_err:
            raise AttributeError(f"Attribute {name!r} not found.") from key_err

    def validate(self, modalities: list[str] | None = None) -> pd.DataFrame:
        """Validate the DataFrame against the lydata schema."""
        raise NotImplementedError("Validation is not yet implemented.")

    def get_modalities(self, ignore_cols: list[str] | None = None) -> list[str]:
        """Return the modalities present in this DataFrame.

        .. warning::

            This method assumes that all top-level columns are modalities, except for
            some predefined non-modality columns. For some custom dataset, this may not
            be correct. In that case, you should provide a list of columns to
            ``ignore_cols``, i.e., the columns that are *not* modalities.
        """
        top_level_cols = self._obj.columns.get_level_values(0)
        modalities = top_level_cols.unique().tolist()

        if ignore_cols is None:
            ignore_cols = [
                "patient",
                "tumor",
                "total_dissected",
                "positive_dissected",
                "enbloc_dissected",
                "enbloc_positive",
            ]

        for col in ignore_cols:
            if col in modalities:
                modalities.remove(col)

        return modalities

    def get_tnm(self) -> pd.DataFrame:
        """Return the T, N, and M stage with all pre- and suffixes.

        This info will be collected in three separate column `"T"`, `"N"`, and `"M"`.

        >>> df = pd.DataFrame({
        ...     ('tumor', 'core', 't_stage_prefix'):   ['c', 'p'],
        ...     ('tumor', 'core', 't_stage'):          [2  ,  3 ],
        ...     ('tumor', 'core', 't_stage_suffix'):   ['a', 'b'],
        ...     ('patient', 'core', 'n_stage'):        [1  ,  2 ],
        ...     ('patient', 'core', 'n_stage_suffix'): ['a', 'b'],
        ...     ('patient', 'core', 'm_stage'):        [0  ,  1 ],
        ... })
        >>> df.ly.get_tnm()   # doctest: +NORMALIZE_WHITESPACE
           T    N   M
        0  c2a  1a  0
        1  p3b  2b  1
        """
        empty = pd.Series([""] * len(self._obj), index=self._obj.index)
        result = pd.DataFrame(index=self._obj.index)

        for stage in ("t", "n", "m"):
            tmp = pd.DataFrame(index=self._obj.index)
            for part in ["prefix", "", "suffix"]:
                name = "_".join([stage, "stage", part]).strip("_")
                try:
                    col = self._obj.xs(name, axis="columns", level=2).iloc[:, 0]
                except KeyError:
                    col = empty.copy()

                tmp = pd.concat([tmp, col], axis="columns")

            result[stage.upper()] = tmp.astype(str).agg("".join, axis="columns")

        return result

    def _get_mask(self, query: CanExecute | None = None) -> pd.Series:
        """Safely get a boolean mask for the DataFrame based on the query."""
        if query is None:
            return _get_all_true(self._obj)

        if isinstance(query, CanExecute):
            return query.execute(self._obj)

        raise TypeError(f"Cannot query with {type(query).__name__}.")

    def query(self, query: CanExecute | None = None) -> pd.DataFrame:
        """Return a DataFrame with rows that satisfy the ``query``.

        A query is a :py:class:`Q` object that can be combined with logical operators.
        See this class' documentation for more information.

        As a shorthand for creating these :py:class:`Q` objects, you can use the
        :py:class:`C` object as in the example below, where we query all entries where
        ``x`` is greater than 1 and not less than 3:

        >>> from lydata import C
        >>> df = pd.DataFrame({'x': [1, 2, 3]})
        >>> df.ly.query((C('x') > 1) & ~(C('x') < 3))
           x
        2  3
        >>> df.ly.query(C('x').isin([1, 3]))
           x
        0  1
        2  3
        """
        mask = self._get_mask(query)
        return self._obj[mask]

    def portion(
        self,
        query: CanExecute | None = None,
        given: CanExecute | None = None,
    ) -> QueryPortion:
        """Compute how many rows satisfy a ``query``, ``given`` some other conditions.

        This returns a :py:class:`QueryPortion` object that contains the number of rows
        satisfying the ``query`` and ``given`` :py:class:`Q` object divided by the
        number of rows satisfying only the ``given`` condition.

        >>> from lydata import C
        >>> df = pd.DataFrame({'x': [1, 2, 3]})
        >>> df.ly.portion(query=C('x') ==  2, given=C('x') > 1)
        QueryPortion(match=np.int64(1), total=np.int64(2))
        >>> df.ly.portion(query=C('x') ==  2, given=C('x') > 3)
        QueryPortion(match=np.int64(0), total=np.int64(0))
        """
        given_mask = self._get_mask(given)
        query_mask = self._get_mask(query)

        return QueryPortion(
            match=query_mask[given_mask].sum(),
            total=given_mask.sum(),
        )

    def stats(
        self,
        agg_funcs: AggFuncType | None = None,
        use_shortnames: bool = True,
        out_format: str = "dict",
    ) -> Any:
        """Compute statistics.

        The ``agg_funcs`` argument is a mapping of column names to functions that
        receive a :py:class:`pd.Series` and return a :py:class:`pd.Series`. The default
        is a useful selection of statistics for the most common columns. E.g., for the
        column ``('patient', 'core', 'age')`` (or its short column name ``age``), the
        default function returns the value counts.

        The ``use_shortnames`` argument determines whether the output should use the
        short column names or the long ones. The default is to use the short names.

        With ``out_format`` one can specify the output format. Available options are
        those formats for which pandas has a ``to_<format>`` method.

        >>> df = pd.DataFrame({
        ...     ('patient', '#', 'age'): [61, 52, 73, 61],
        ...     ('patient', '#', 'hpv_status'): [True, False, None, True],
        ...     ('tumor', '1', 't_stage'): [2, 3, 1, 2],
        ... })
        >>> df.ly.stats()   # doctest: +NORMALIZE_WHITESPACE
        {'age': {61: 2, 52: 1, 73: 1},
         'hpv': {True: 2, False: 1, None: 1},
         't_stage': {2: 2, 3: 1, 1: 1}}
        >>> df = pd.DataFrame({
        ...     ('patient', 'core', 'age'): [61, 52, 73, 61],
        ...     ('patient', 'core', 'hpv_status'): [True, False, None, True],
        ...     ('tumor', 'core', 't_stage'): [2, 3, 1, 2],
        ... })
        >>> df.ly.stats()   # doctest: +NORMALIZE_WHITESPACE
        {'age': {61: 2, 52: 1, 73: 1},
         'hpv': {True: 2, False: 1, None: 1},
         't_stage': {2: 2, 3: 1, 1: 1}}
        """
        _agg_funcs = self._column_map_new.from_short.copy()
        _agg_funcs.update(agg_funcs or {})
        stats = {}

        for colname, func in _agg_funcs.items():
            if colname not in self:
                continue

            column = self[colname]
            if use_shortnames and colname in self._column_map_old.from_long:
                colname = self._column_map_old.from_long[colname].short

            stats[colname] = getattr(func(column), f"to_{out_format}")()

        return stats

    def _filter_modalities(
        self,
        modalities: dict[str, ModalityConfig] | None = None,
    ) -> dict[str, ModalityConfig]:
        """Keep only those ``modalities`` present in data."""
        if modalities is None:
            modalities = get_default_modalities()

        return {
            modality_name: modality_config
            for modality_name, modality_config in modalities.items()
            if modality_name in self.get_modalities()
        }

    def combine(
        self,
        modalities: dict[str, ModalityConfig] | None = None,
        method: Literal["max_llh", "rank"] = "max_llh",
        subdivisions: Mapping[str, Sequence[str]] | None = None,
    ) -> pd.DataFrame:
        """Combine diagnoses of ``modalities`` using ``method``.

        The order of the provided ``modalities`` does not matter, as it is aligned
        with the order in the DataFrame. With ``method="max_llh"``, the most likely
        true state of involvement is inferred based on all available diagnoses for
        each patient and level. With ``method="rank"``, only the most trustworthy
        diagnosis is chosen for each patient and level based on the sensitivity and
        specificity of the given list of ``modalities``.

        The result contains only the combined columns and no top-level header. This
        means that if you want to add that to the original DataFrame, you could do so
        like this:

        .. code-block:: python

            combined = data.ly.combine()
            combined_full_header = pd.concat({"foo": combined}, axis="columns")
            combined_full_header.index = data.index
            data = pd.concat([data, combined_full_header], axis="columns")

        The method :py:func:`.enhance` is a shorthand for combining, augmenting, and
        joining the results in a way similar to that example above.

        .. warning::

            Here, the default value for ``subdivisions`` is set to an empty dictionary.
            This is because on the one hand, we still want to retain the functionality
            of combining and augmenting in one step (necessary in the
            :py:meth:`.enhance` method), but if not explicitly chosen, we keep only
            the originally provided levels.

        >>> df = pd.DataFrame({
        ...     ('CT'       , 'ipsi', 'I'): [False, True , False,  True, None],
        ...     ('MRI'      , 'ipsi', 'I'): [False, True , True ,  None, None],
        ...     ('pathology', 'ipsi', 'I'): [True , None ,  None, False, None],
        ... })
        >>> df.ly.combine()   # doctest: +NORMALIZE_WHITESPACE
             ipsi
                I
        0    True
        1    True
        2   False
        3   False
        4    None
        """
        # We need the ability to pass the subdivisions for the `.enhance` method,
        # but normally, we don't want to augment when combining.
        if subdivisions is None:
            subdivisions = {}

        modalities = self._filter_modalities(modalities)
        obj_copy = self._obj.copy()

        return combine_and_augment_levels(
            diagnoses=[obj_copy[mod] for mod in modalities.keys()],
            specificities=[mod.spec for mod in modalities.values()],
            sensitivities=[mod.sens for mod in modalities.values()],
            method=method,
            subdivisions=subdivisions,
        )

    def augment(
        self,
        modality: str = "max_llh",
        subdivisions: dict[str, list[str]] | None = None,
    ) -> pd.DataFrame:
        """Complete the sub- and superlevel involvement columns.

        This is useful if the intention is not to combine multiple modalities, but
        rather to fill in the missing super- and sub-level involvement columns for a
        single modality.

        Like the :py:meth:`~LyDataAccessor.combine` method, the returned DataFrame
        only has a two-level header. So, for combining this with the original data,
        one has to perform additional steps. Or use the :py:meth:`.enhance` method.

        >>> df = pd.DataFrame({
        ...     ('MRI', 'ipsi'  , 'I' ): [True , False, False, None],
        ...     ('MRI', 'contra', 'I' ): [False, True , False, None],
        ...     ('MRI', 'ipsi'  , 'II'): [False, False, True , None],
        ...     ('MRI', 'ipsi'  , 'IV'): [False, False, True , None],
        ...     ('CT' , 'ipsi'  , 'I' ): [True , False, False, None],
        ... })
        >>> df.ly.augment(modality="MRI")   # doctest: +NORMALIZE_WHITESPACE
          contra                 ipsi
               I     Ia     Ib      I     Ia     Ib     II    IIa    IIb     IV
        0  False  False  False   True   None   None  False  False  False  False
        1   True   None   None  False  False  False  False  False  False  False
        2  False  False  False  False  False  False   True   None   None   True
        3   None   None   None   None   None   None   None   None   None   None
        """
        if modality not in self.get_modalities():
            raise ValueError(f"Modality {modality!r} not found in DataFrame.")

        obj_copy = self._obj.copy()

        return combine_and_augment_levels(
            diagnoses=[obj_copy[modality]],
            specificities=[0.9],  # Numbers here don't matter, as we only "combine"
            sensitivities=[0.9],  # a single modality's involvement info.
            subdivisions=subdivisions,
        )

    def enhance(
        self,
        modalities: dict[str, ModalityConfig] | None = None,
        method: Literal["max_llh", "rank"] = "max_llh",
        subdivisions: Mapping[str, Sequence[str]] | None = None,
    ) -> LyDataFrame:
        """Shorthand for first combining ``modalities`` and then augmenting them.

        This first runs the :py:meth:`~LyDataAccessor.combine` method and after that
        the :py:meth:`~LyDataAccessor.augment` for every modality in ``modalities``
        and the newly combined ``method`` column.
        """
        if subdivisions is None:
            subdivisions = {
                "I": ["a", "b"],
                "II": ["a", "b"],
                "V": ["a", "b"],
            }

        if modalities is None:
            modalities = get_default_modalities()

        # Originally, I thought we could just combine and not augment the super- and
        # sub-levels, but then we discard the involvement probability information from
        # the original modalities.
        combined = self.combine(
            modalities=modalities,
            method=method,
            subdivisions=subdivisions,
        )
        combined = pd.concat({method: combined}, axis="columns")
        combined.index = self._obj.index
        enhanced: LyDataFrame = pd.concat([self._obj, combined], axis="columns")

        for modality in list(modalities.keys()):
            if modality not in enhanced.columns:
                continue

            augmented = enhanced.ly.augment(
                modality=modality,
                subdivisions=subdivisions,
            )
            augmented = pd.concat({modality: augmented}, axis="columns")
            augmented.index = enhanced.index
            enhanced = replace(left=enhanced, right=augmented)

        return _sort_all(enhanced)

    def cast(
        self,
        casters: Mapping[type, str] | None = None,
    ) -> LyDataFrame:
        """Cast the dtypes of the DataFrame to the expected types.

        This uses the annotations of the Pydantic schema to cast the individual columns
        of the DataFrame to the expected types. It uses the ``casters`` mapping to
        determine the type to cast to. By default, it uses the mapping from the
        :py:func:`_get_default_casters` function.
        """
        from lydata.validator import cast_dtypes

        return cast_dtypes(self._obj, casters=casters)


# Using the class below instead of pd.DataFrame enables IDE type hints.
class LyDataFrame(pd.DataFrame):
    """Subclass of a pandas DataFrame with a custom lydata accessor."""

    ly: LyDataAccessor
    """The custom lydata accessor for these DataFrame subclass instances."""


if __name__ == "__main__":
    import doctest

    doctest.testmod()
