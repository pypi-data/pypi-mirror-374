from typing import Annotated, Callable, Dict, Type, get_args, get_origin

from bytex.annotations import (
    extract_type_and_value,
    get_list_type,
    is_list_type,
    is_sequence_type,
)
from bytex.codecs import (
    BaseCodec,
    DataCodec,
    EnumCodec,
    ExactBytesCodec,
    ExactListCodec,
    ExactStringCodec,
    FixedBytesCodec,
    FixedIntegersCodec,
    FixedStringCodec,
    IntegerCodec,
    PrefixBytesCodec,
    PrefixListCodec,
    PrefixStringCodec,
    StructureCodec,
    TerminatedBytesCodec,
    TerminatedListCodec,
    TerminatedStringCodec,
)
from bytex.errors import StructureCreationError, StructureEnumCreationError
from bytex.field import Field
from bytex.length_encodings import BaseLengthEncoding, Exact, Fixed, Prefix, Terminator
from bytex.structure._structure import _Structure
from bytex.structure.methods import (
    _create_dump,
    _create_dump_bits,
    _create_init,
    _create_parse,
    _create_parse_bits,
    _create_repr,
    _create_validate,
)
from bytex.structure.types import Codecs, Fields
from bytex.structure_enum import STRUCTURE_ENUM_CODEC_KEY, _StructureEnum

ANNOTATIONS_KEY: str = "__annotations__"
METHOD_CREATORS: Dict[str, Callable[[Fields], Callable]] = {
    "__init__": _create_init,
    "dump": _create_dump,
    "dump_bits": _create_dump_bits,
    "parse": _create_parse,
    "parse_bits": _create_parse_bits,
    "validate": _create_validate,
    "__repr__": _create_repr,
}


class StructureMeta(type):
    def __new__(mcs, name, bases, namespace):
        annotations = namespace.get(ANNOTATIONS_KEY, {})
        codecs = _construct_codecs(annotations)
        _validate_codecs(codecs)
        fields = _create_fields(namespace=namespace, codecs=codecs)

        for method_name, method_creator in METHOD_CREATORS.items():
            namespace[method_name] = method_creator(fields)

        return super().__new__(mcs, name, bases, namespace)


def _create_fields(namespace, codecs: Codecs) -> Fields:
    fields = {}
    for name, codec in codecs.items():
        default_value = namespace.get(name, None)
        if default_value is not None:
            field = Field(codec=codec, name=name, default=default_value)
        else:
            field = Field(codec=codec, name=name)

        fields[name] = field
        namespace[name] = field

    return fields


def _construct_codecs(annotations: Dict[str, type]) -> Codecs:
    codecs: Codecs = {}

    for field_name, annotation in annotations.items():
        codecs[field_name] = _construct_codec(annotation)

    return codecs


def _construct_codec(annotation: type) -> BaseCodec:
    if isinstance(annotation, type) and issubclass(annotation, _Structure):
        return StructureCodec(structure_class=annotation)
    if isinstance(annotation, type) and issubclass(annotation, _StructureEnum):
        return _construct_enum_codec(enum=annotation)

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is not Annotated:
        raise StructureCreationError(
            "All structure fields must be of type `typing.Annotated`"
        )

    if len(args) != 2:
        raise StructureCreationError(
            "All Structure fields must be of the form `typing.Annotated[Any, BaseCodec(...)]` or "
            "typing.Annotated[Sequence, BaseLengthEncoding(...)]"
        )

    base_type, value = args

    if isinstance(value, BaseCodec):
        return value
    if isinstance(value, BaseLengthEncoding):
        return _construct_length_encoded_codec(
            base_type=base_type, length_encoding=value
        )

    raise StructureCreationError(
        "All Structure fields must be of the form `typing.Annotated[Any, BaseCodec(...)]` or "
        "typing.Annotated[Sequence, BaseLengthEncoding(...)]"
    )


def _construct_enum_codec(enum: Type[_StructureEnum]) -> EnumCodec:
    codec = enum.__base__.__dict__.get(STRUCTURE_ENUM_CODEC_KEY, None)
    if codec is None:
        raise StructureEnumCreationError(
            f"Failed to retrieve codec from Enum - '{enum.__name__}'"
        )

    return EnumCodec(enum=enum, item_codec=codec)


def _construct_length_encoded_codec(
    base_type: type, length_encoding: BaseLengthEncoding
) -> BaseCodec:
    if not is_sequence_type(base_type):
        raise StructureCreationError(
            f"Only `Sequence` types can have a length encoding, got: `{str(base_type)}`"
        )

    if base_type is str:
        return _construct_str_length_encoded_codec(length_encoding)
    elif base_type is bytes:
        return _construct_bytes_length_encoded_codec(length_encoding)
    elif is_list_type(base_type):
        return _construct_list_length_encoded_codec(base_type, length_encoding)

    raise StructureCreationError(
        f"Could not create a length encoded codec, Unimplemented length encoded type: {base_type}"
    )


def _construct_str_length_encoded_codec(
    length_encoding: BaseLengthEncoding,
) -> BaseCodec:
    if isinstance(length_encoding, Terminator):
        return TerminatedStringCodec(terminator=length_encoding.get_terminator())
    if isinstance(length_encoding, Fixed):
        return FixedStringCodec(length=length_encoding.length)
    if isinstance(length_encoding, Exact):
        return ExactStringCodec(length=length_encoding.length)
    if isinstance(length_encoding, Prefix):
        return PrefixStringCodec(prefix_codec=length_encoding.codec)
    raise StructureCreationError(
        f"Unsupported length encoding `{length_encoding.__class__.__name__}` for `str`"
    )


def _construct_bytes_length_encoded_codec(
    length_encoding: BaseLengthEncoding,
) -> BaseCodec:
    if isinstance(length_encoding, Terminator):
        return TerminatedBytesCodec(terminator=length_encoding.get_terminator())
    if isinstance(length_encoding, Fixed):
        return FixedBytesCodec(length=length_encoding.length)
    if isinstance(length_encoding, Exact):
        return ExactBytesCodec(length=length_encoding.length)
    if isinstance(length_encoding, Prefix):
        return PrefixBytesCodec(prefix_codec=length_encoding.codec)
    raise StructureCreationError(
        f"Unsupported length encoding ('{length_encoding.__class__.__name__}') for `bytes`"
    )


def _construct_list_length_encoded_codec(
    base_type: type, length_encoding: BaseLengthEncoding
) -> BaseCodec:
    list_item_type = get_list_type(base_type)
    if list_item_type is None:
        raise StructureCreationError(
            "All list types must include the item type - `List[ItemType]`, got a list without an item type"
        )

    item_codec = _resolve_list_item_codec(list_item_type)

    if isinstance(length_encoding, Terminator):
        return TerminatedListCodec(
            item_codec=item_codec, terminator=length_encoding.get_terminator()
        )
    if isinstance(length_encoding, Fixed) and isinstance(item_codec, IntegerCodec):
        return FixedIntegersCodec(
            integer_codec=item_codec, length=length_encoding.length
        )
    if isinstance(length_encoding, Exact):
        return ExactListCodec(item_codec=item_codec, length=length_encoding.length)
    if isinstance(length_encoding, Prefix):
        return PrefixListCodec(
            item_codec=item_codec, prefix_codec=length_encoding.codec
        )

    raise StructureCreationError("Unsupported length encoding for `List[...]`.")


def _resolve_list_item_codec(list_item_type: type) -> BaseCodec:
    if get_origin(list_item_type) is Annotated:
        _, modifier = extract_type_and_value(list_item_type)

        if not isinstance(modifier, BaseCodec):
            raise StructureCreationError(
                "Invalid Annotated usage: expected `Annotated[type, BaseCodec]`"
            )

        return modifier

    if issubclass(list_item_type, _Structure):
        return StructureCodec(structure_class=list_item_type)

    raise StructureCreationError(
        "List item types must be either a `Structure` subclass or `Annotated[type, BaseCodec]`"
    )


def _validate_codecs(codecs: Codecs) -> None:
    if len(codecs) == 0:
        return

    for codec, _ in zip(codecs.values(), range(0, len(codecs) - 1)):
        if isinstance(codec, DataCodec):
            raise StructureCreationError(
                f"A field with codec `{DataCodec.__name__}` must singular and come last"
            )
