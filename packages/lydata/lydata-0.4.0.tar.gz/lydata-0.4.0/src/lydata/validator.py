"""Module to cast dtypes and to and validate the lyDATA datasets.

The two main functions here are :py:func:`cast_dtypes` and :py:func:`is_valid`. The
first one can be used to cast the dtypes of the columns in a :py:class:`LyDataFrame`
to the expected types according to the schema constructed using
:py:func:`create_full_record_model`.

Subsequently, :py:func:`is_valid` can be used to validate every row in the table, again
using the constructed schema.
"""

import sys
from collections.abc import Mapping
from typing import Any, Literal

from loguru import logger
from pydantic import BaseModel, Field, PastDate, ValidationError  # noqa: F401

from lydata.accessor import LyDataAccessor, LyDataFrame  # noqa: F401
from lydata.schema import create_full_record_model


def flatten(
    nested: dict,
    prev_key: tuple = (),
    max_depth: int | None = None,
) -> dict:
    """Flatten ``nested`` dict by creating key tuples for each value at ``max_depth``.

    >>> nested = {"tumor": {"1": {"t_stage": 1, "size": 12.3}}}
    >>> flatten(nested)
    {('tumor', '1', 't_stage'): 1, ('tumor', '1', 'size'): 12.3}
    >>> mapping = {"patient": {"#": {"age": {"func": int, "columns": ["age"]}}}}
    >>> flatten(mapping, max_depth=3)
    {('patient', '#', 'age'): {'func': <class 'int'>, 'columns': ['age']}}

    Note that flattening an already flat dictionary will yield some weird results.
    """
    result = {}

    for key, value in nested.items():
        is_dict = isinstance(value, dict)
        has_reached_max_depth = max_depth is not None and len(prev_key) >= max_depth - 1

        if is_dict and not has_reached_max_depth:
            result.update(flatten(value, (*prev_key, key), max_depth))
        else:
            result[(*prev_key, key)] = value

    return result


def unflatten(flat: dict) -> dict:
    """Take a flat dictionary with tuples of keys and create nested dict from it.

    >>> flat = {('tumor', '1', 't_stage'): 1, ('tumor', '1', 'size'): 12.3}
    >>> unflatten(flat)
    {'tumor': {'1': {'t_stage': 1, 'size': 12.3}}}
    >>> mapping = {('patient', '#', 'age'): {'func': int, 'columns': ['age']}}
    >>> unflatten(mapping)
    {'patient': {'#': {'age': {'func': <class 'int'>, 'columns': ['age']}}}}
    """
    result = {}

    for keys, value in flat.items():
        current = result
        for key in keys[:-1]:
            current = current.setdefault(key, {})

        current[keys[-1]] = value

    return result


def is_valid(dataset: LyDataFrame, fail_on_error: bool = True) -> bool:
    """Validate the given dataset against the lyDATA schema.

    Returns ``True`` if all records are valid, otherwise it either raises an error
    (if ``fail_on_error`` is ``True``) or returns ``False``.
    """
    modalities = dataset.ly.get_modalities()
    FullRecord = create_full_record_model(modalities)  # noqa: N806
    result = True

    for _i, row in dataset.iterrows():
        patient_id = row.patient.core.id
        record = unflatten(row.to_dict())

        try:
            _validated_record = FullRecord(**record)
            logger.debug(f"Successful validation of {patient_id=}")
        except ValidationError as e:
            if fail_on_error:
                raise ValueError(f"Validation error for {patient_id=}") from e
            logger.error(f"{patient_id}: {e}")
            result = False

    return result


def _get_field_annotations(
    model: type[BaseModel],
) -> dict[str, Any]:
    """Get the field annotations of a three-level nested Pydantic model.

    >>> class Foo(BaseModel):
    ...     bar: int = 3
    >>> class Baz(BaseModel):
    ...     foo: Foo = Field(default_factory=Foo)
    >>> _get_field_annotations(Baz)
    {'foo': {'bar': <class 'int'>}}
    """
    annotations = {}
    for field_name, field_info in model.model_fields.items():
        if issubclass(field_info.annotation, BaseModel):
            annotations[field_name] = _get_field_annotations(field_info.annotation)
        else:
            annotations[field_name] = field_info.annotation

    return annotations


def _get_default_casters() -> Mapping[type, str]:
    """Get the default dtype casters for the lyDATA schema."""
    return {
        int: "Int64",
        int | None: "Int64",
        float: "Float64",
        float | None: "Float64",
        str: "string",
        str | None: "string",
        bool: "boolean",
        bool | None: "boolean",
        PastDate: "datetime64[ns]",
        PastDate | None: "datetime64[ns]",
        Literal["male", "female"]: "string",
        Literal["c", "p"]: "string",
        Literal["a", "b"] | None: "string",
        Literal["a", "b", "c"] | None: "string",
        Literal["left", "right"] | None: "string",
    }


def cast_dtypes(
    dataset: LyDataFrame,
    casters: Mapping[type, str] | None = None,
    fail_on_error: bool = True,
) -> LyDataFrame:
    """Cast the dtypes of the ``dataset`` to the expected types.

    This function uses the annotations of the Pydantic schema to cast the individual
    columns of the ``dataset`` to the expected types. It uses the ``casters`` mapping
    to determine the type to cast to. By default, it uses the mapping from the
    :py:func:`_get_default_casters` function.

    That way, pandas uses e.g. the nullable integer type ``Int64`` if we specify in
    pydantic that a field can be an integer or None. If you want to use a different
    mapping, you can pass it as the ``casters`` argument.
    """
    dataset = dataset.convert_dtypes()

    if casters is None:
        casters = _get_default_casters()

    modalities = dataset.ly.get_modalities()
    FullRecord = create_full_record_model(modalities)  # noqa: N806
    annotations = _get_field_annotations(FullRecord)
    annotations = flatten(annotations, max_depth=3)

    for col in dataset.columns:
        annotation = annotations.get(col, None)
        old_type = dataset[col].dtype
        new_type = casters.get(annotation, old_type)

        if annotation is None:
            logger.warning(f"No annotation found for {col=}. Using {old_type=}.")
            continue

        if new_type == old_type:
            logger.debug(f"Column {col=} already has expected {old_type=}. Skipping.")
            continue

        try:
            dataset = dataset.astype({col: new_type})
            logger.success(f"Cast {col=} from {old_type=} to {new_type=}.")
        except TypeError as e:
            msg = (
                f"Failed to cast column {col=} with ({annotation=}) to "
                f"caster = `{new_type}."
            )
            logger.error(msg)
            if fail_on_error:
                raise TypeError(msg) from e

    return dataset


if __name__ == "__main__":
    from lydata import loader

    logger.enable("lydata")
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    dataset = next(
        loader.load_datasets(
            repo_name="lycosystem/lydata.private",
            ref="e68141fd5440d4cfa6491df14ca2203ddb7946b0",
        )
    )
    dataset = cast_dtypes(dataset)
    print(f"{is_valid(dataset, fail_on_error=False)=}")  # noqa: T201
