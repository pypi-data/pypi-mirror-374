"""
Schema parsing components for understanding Parquet's type system.

Teaching Points:
- Parquet schemas are hierarchical trees that mirror nested data structures
- Each schema element describes a field's type, repetition, and metadata
- The schema tree enables columnar storage of complex nested data
- Field relationships are encoded through parent-child structure and repetition levels
"""

import logging

from por_que.enums import ConvertedType, LogicalType, Repetition, TimeUnit, Type
from por_que.exceptions import ThriftParsingError
from por_que.logical import (
    BsonTypeInfo,
    DateTypeInfo,
    DecimalTypeInfo,
    EnumTypeInfo,
    Float16TypeInfo,
    GeographyTypeInfo,
    GeometryTypeInfo,
    IntTypeInfo,
    JsonTypeInfo,
    ListTypeInfo,
    LogicalTypeInfo,
    MapTypeInfo,
    SchemaElement,
    SchemaGroup,
    SchemaLeaf,
    SchemaRoot,
    StringTypeInfo,
    TimestampTypeInfo,
    TimeTypeInfo,
    UnknownTypeInfo,
    UuidTypeInfo,
    VariantTypeInfo,
)
from por_que.parsers.thrift.enums import ThriftFieldType
from por_que.parsers.thrift.parser import ThriftStructParser

from .base import BaseParser
from .enums import SchemaElementFieldId

logger = logging.getLogger(__name__)


class SchemaParser(BaseParser):
    """
    Parses Parquet schema elements and builds the schema tree.

    Teaching Points:
    - Schema elements define the structure and types of data in Parquet files
    - The root element represents the entire record structure
    - Child elements represent nested fields, arrays, and maps
    - Repetition types (REQUIRED, OPTIONAL, REPEATED) control nullability and arrays
    """

    def read_schema_element(self) -> SchemaRoot | SchemaGroup | SchemaLeaf:  # noqa: C901
        """
        Read a single SchemaElement struct from the Thrift stream.

        Teaching Points:
        - Each schema element encodes field metadata: name, type, repetition
        - Physical types (INT32, BYTE_ARRAY) describe storage format
        - Logical types (UTF8, TIMESTAMP) describe semantic meaning
        - num_children indicates how many child elements follow this one

        Returns:
            SchemaElement with parsed metadata
        """
        struct_parser = ThriftStructParser(self.parser)
        logger.debug('Reading schema element')
        name: str | None = None
        _type: Type | None = None
        type_length: int | None = None
        repetition: Repetition | None = None
        num_children: int | None = None
        converted_type: ConvertedType | None = None
        scale: int | None = None
        precision: int | None = None
        field_id: int | None = None
        logical_type: LogicalTypeInfo | None = None

        while True:
            field_type, field_id = struct_parser.read_field_header()
            if field_type == ThriftFieldType.STOP:
                break

            # `read_value` returns the primitive value, or None if it's a
            # complex type or should be skipped.
            value = struct_parser.read_value(field_type)
            if value is None:
                # This indicates a complex type that the caller must handle,
                # or a type that was skipped.
                continue

            match field_id:
                case SchemaElementFieldId.TYPE:
                    _type = Type(value)
                case SchemaElementFieldId.TYPE_LENGTH:
                    type_length = value
                case SchemaElementFieldId.REPETITION_TYPE:
                    repetition = Repetition(value)
                case SchemaElementFieldId.NAME:
                    name = value.decode('utf-8')
                case SchemaElementFieldId.NUM_CHILDREN:
                    num_children = value
                case SchemaElementFieldId.CONVERTED_TYPE:
                    converted_type = ConvertedType(value)
                case SchemaElementFieldId.SCALE:
                    scale = value
                case SchemaElementFieldId.PRECISION:
                    precision = value
                case SchemaElementFieldId.FIELD_ID:
                    field_id = value
                case SchemaElementFieldId.LOGICAL_TYPE:
                    logical_type = self._parse_logical_type()
                case _:
                    # This case is not strictly necessary since `read_value`
                    # already skipped unknown fields, but it's good practice.
                    pass

        element = SchemaElement.new(
            name=name,
            type=_type,
            type_length=type_length,
            repetition=repetition,
            num_children=num_children,
            converted_type=converted_type,
            scale=scale,
            precision=precision,
            field_id=field_id,
            logical_type=logical_type,
        )

        logger.debug('Read schema element: %s', element)
        return element

    def read_schema_tree(self, elements_iter) -> SchemaRoot | SchemaGroup | SchemaLeaf:
        """
        Recursively build nested schema tree from flat list of elements.

        Teaching Points:
        - Parquet stores schema as a depth-first traversal of the tree
        - Each parent element specifies how many children follow it
        - This enables efficient reconstruction of the full tree structure
        - The tree structure mirrors how nested data is stored in columns

        Args:
            elements_iter: Iterator over flat list of schema elements

        Returns:
            SchemaRoot with all children attached

        Raises:
            ThriftParsingError: If schema structure is malformed
        """
        try:
            element = next(elements_iter)
        except StopIteration:
            raise ThriftParsingError(
                'Unexpected end of schema elements. This suggests a malformed '
                'schema where a parent element claims more children than exist.',
            ) from None

        if isinstance(element, SchemaRoot | SchemaGroup):
            logger.debug(
                'Building schema tree for %s with %d children',
                element.name,
                element.num_children,
            )

            for i in range(element.num_children):
                child = self.read_schema_tree(elements_iter)

                if isinstance(child, SchemaRoot):
                    raise ThriftParsingError('Schema can have only one root')

                element.add_element(child)
                logger.debug(
                    '  Added child %d/%d: %s',
                    i + 1,
                    element.num_children,
                    child.name,
                )

        return element

    def parse_schema_field(self) -> SchemaRoot:
        """
        Parse the schema field from file metadata.

        Teaching Points:
        - The schema field contains a flat list of all schema elements
        - Elements are ordered in depth-first traversal of the schema tree
        - The first element is always the root (representing the full record)
        - Child elements are nested based on their parent's num_children value

        Returns:
            Root SchemaElement with complete tree structure
        """
        # Read flat list of schema elements
        schema_elements = self.read_list(self.read_schema_element)

        logger.debug('Read %d schema elements, building tree', len(schema_elements))

        schema_root = schema_elements[0]
        if not isinstance(schema_root, SchemaRoot):
            raise ThriftParsingError(
                f'Schema must start with SchemaRoot element, got {schema_root}',
            )

        # Convert flat list to tree structure
        elements_iter = iter(schema_elements)
        self.read_schema_tree(elements_iter)
        return schema_root

    def _parse_logical_type(self) -> LogicalTypeInfo | None:  # noqa: C901
        """
        Parse a LogicalType union from the Thrift stream.

        The LogicalType is a union with different types for different logical types.
        Each union variant has its own field ID and structure.
        """
        struct_parser = ThriftStructParser(self.parser)

        while True:
            field_type, field_id = struct_parser.read_field_header()
            if field_type == ThriftFieldType.STOP:
                break

            value = struct_parser.read_value(field_type)
            if value is None:
                # Complex type that needs special handling
                match field_id:
                    case LogicalType.STRING:
                        return StringTypeInfo()
                    case LogicalType.INTEGER:
                        return self._parse_int_type()
                    case LogicalType.DECIMAL:
                        return self._parse_decimal_type()
                    case LogicalType.TIME:
                        return self._parse_time_type()
                    case LogicalType.TIMESTAMP:
                        return self._parse_timestamp_type()
                    case LogicalType.DATE:
                        return DateTypeInfo()
                    case LogicalType.ENUM:
                        return EnumTypeInfo()
                    case LogicalType.JSON:
                        return JsonTypeInfo()
                    case LogicalType.BSON:
                        return BsonTypeInfo()
                    case LogicalType.UUID:
                        return UuidTypeInfo()
                    case LogicalType.FLOAT16:
                        return Float16TypeInfo()
                    case LogicalType.MAP:
                        return MapTypeInfo()
                    case LogicalType.LIST:
                        return ListTypeInfo()
                    case LogicalType.VARIANT:
                        return VariantTypeInfo()
                    case LogicalType.GEOMETRY:
                        return GeometryTypeInfo()
                    case LogicalType.GEOGRAPHY:
                        return GeographyTypeInfo()
                    case LogicalType.UNKNOWN:
                        return UnknownTypeInfo()
                    case _:
                        # Unknown type, skip it
                        continue
            else:
                # Simple value, shouldn't happen for union types
                continue

        return None

    def _parse_int_type(self) -> IntTypeInfo:
        """Parse an IntType struct."""
        struct_parser = ThriftStructParser(self.parser)
        bit_width = 32
        is_signed = True

        while True:
            field_type, field_id = struct_parser.read_field_header()
            if field_type == ThriftFieldType.STOP:
                break

            value = struct_parser.read_value(field_type)
            if value is not None:
                match field_id:
                    case 1:  # bitWidth
                        bit_width = value
                    case 2:  # isSigned
                        is_signed = value

        return IntTypeInfo(bit_width=bit_width, is_signed=is_signed)

    def _parse_decimal_type(self) -> DecimalTypeInfo:
        """Parse a DecimalType struct."""
        struct_parser = ThriftStructParser(self.parser)
        scale = 0
        precision = 10

        while True:
            field_type, field_id = struct_parser.read_field_header()
            if field_type == ThriftFieldType.STOP:
                break

            value = struct_parser.read_value(field_type)
            if value is not None:
                match field_id:
                    case 1:  # scale
                        scale = value
                    case 2:  # precision
                        precision = value

        return DecimalTypeInfo(scale=scale, precision=precision)

    def _parse_time_type(self) -> TimeTypeInfo:
        """Parse a TimeType struct."""
        struct_parser = ThriftStructParser(self.parser)
        is_adjusted_to_utc = False
        unit = TimeUnit.MILLIS

        while True:
            field_type, field_id = struct_parser.read_field_header()
            if field_type == ThriftFieldType.STOP:
                break

            value = struct_parser.read_value(field_type)
            if value is not None:
                match field_id:
                    case 1:  # isAdjustedToUTC
                        is_adjusted_to_utc = value
                    case 2:  # unit (TimeUnit union)
                        # Map int values to TimeUnit enum
                        unit = TimeUnit(value)

        return TimeTypeInfo(is_adjusted_to_utc=is_adjusted_to_utc, unit=unit)

    def _parse_timestamp_type(self) -> TimestampTypeInfo:
        """Parse a TimestampType struct."""
        struct_parser = ThriftStructParser(self.parser)
        is_adjusted_to_utc = False
        unit = TimeUnit.MILLIS

        while True:
            field_type, field_id = struct_parser.read_field_header()
            if field_type == ThriftFieldType.STOP:
                break

            value = struct_parser.read_value(field_type)
            if value is not None:
                match field_id:
                    case 1:  # isAdjustedToUTC
                        is_adjusted_to_utc = value
                    case 2:  # unit (TimeUnit union)
                        # Map int values to TimeUnit enum
                        unit = TimeUnit(value)

        return TimestampTypeInfo(is_adjusted_to_utc=is_adjusted_to_utc, unit=unit)
