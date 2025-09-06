import datetime
from decimal import Decimal
from enum import Enum
from itertools import chain
from typing import List, Union, Literal, Annotated, Optional, Any
from uuid import UUID
from pydantic import (
    Field,
    AliasChoices,
    PlainSerializer,
    model_serializer,
    field_serializer,
    field_validator,
    WrapSerializer,
    model_validator,
    SerializerFunctionWrapHandler,
    BaseModel,
)
from pydantic.json_schema import SkipJsonSchema

from .schema_enums import ProcessCategory, ProcessType, Status, SimaProCSVType

CustomBoolean = Annotated[
    bool, PlainSerializer(lambda x: "Yes" if x is True else "No", return_type=str, when_used="json")
]

QuotedStr = Annotated[
    str, PlainSerializer(lambda x: repr(x.replace(";", "\\;")), return_type=str, when_used="json")
    # todo pull from context
]


def decimal_ser(v: Any, nxt: SerializerFunctionWrapHandler, **kwargs) -> str:
    return str(v)  # todo info.context decimal representation
    # return f"{v.normalize()}"  # todo info.context decimal representation


DecimalValue = Annotated[Decimal, WrapSerializer(decimal_ser, when_used="json")]


def output_date_formated_by_header(
        value: Any, handler, info, **kwargs
) -> datetime.date:
    partial_result = handler(value, info)
    if info.mode == "json":
        format_str = "%d/%m/%Y"
        result = value.strftime(format_str)
        return result
    return partial_result


class UncertaintyRecordEntry(BaseModel):
    slot1: str
    slot2: DecimalValue = Field(default=0)
    slot3: DecimalValue = Field(default=0)
    slot4: DecimalValue = Field(default=0)

    @model_serializer(mode="wrap", when_used="json")
    def output_uncertainty_as_line(self, handler, info) -> str:
        if info.context:
            seperator_char = info.context.get("csv_seperator", ";")
        else:
            seperator_char = ";"
        return f"{self.slot1}{seperator_char}{self.slot2}{seperator_char}{self.slot3}{seperator_char}{self.slot4}"


class UncertaintyRecordUndefined(UncertaintyRecordEntry):
    slot1: Literal["Undefined"] = "Undefined"


class UncertaintyRecordLognormal(UncertaintyRecordEntry):
    slot1: Literal["Lognormal"]
    slot2: DecimalValue  # Returns the squared geometric standard deviation.


class UncertaintyRecordNormal(UncertaintyRecordEntry):
    slot1: Literal["Normal"]
    slot2: DecimalValue


class UncertaintyRecordUniform(UncertaintyRecordEntry):
    slot1: Literal["Normal"]
    slot3: DecimalValue  # min
    slot4: DecimalValue  # max


class UncertaintyRecordTriangle(UncertaintyRecordEntry):
    slot1: Literal["Normal"]
    slot3: DecimalValue  # min
    slot4: DecimalValue  # max


UncertaintyRecord = Union[
    UncertaintyRecordUndefined,
    UncertaintyRecordLognormal,
    UncertaintyRecordNormal,
    UncertaintyRecordTriangle,
    UncertaintyRecordUniform,
]


class SimaProSectionHeader(Enum):
    pass


class Separators(str, Enum):
    SEMICOLON_STR = "Semicolon"
    SEMICOLON = ";"
    TAB = "\t"
    TAB_STR = "tab"
    COLON = "."
    DASH = "-"
    COMMA = ","
    COMMA_STR = "comma"
    SLASH = "/"


class SimaProHeader(BaseModel):
    """
    This header starts with the first line and each header entry is enclosed in curly brackets.
    Before you read the actual data from the file you need this information to parse the data into the correct format
    because things like the column or DecimalValue separator are defined in this header.
    This makes it a bit hard to read the format because you need to jump back to the top when starting reading the file
     with the assumption of another column separator until you come to the CSV separator entry.
    """

    class Config:
        use_enum_values = True

    version: str = Field(
        default="10.2.0.3",
        description="",
        examples=["{SimaPro 8.5.0.0}"],
        validation_alias=AliasChoices("SimaPro", "version", "simapro_version"),
        serialization_alias="SimaPro",
    )

    kind: SimaProCSVType = Field(
        default="processes",
        description="",
        examples=["{processes}"],
    )
    # PlainSerializer(lambda v: v.strftime("%d/%m/%Y"), return_type=str) #todo unnify date impmentation
    # date: Annotated[datetime.date,
    # WrapSerializer(output_date_formated_by_header, when_used="json"),
    # ] \

    date: datetime.date = Field(
        default="",
        description="",
        examples=["{Date: 2019-10-24}"],
        validation_alias=AliasChoices("Date", "date", "created"),
        serialization_alias="Date",
    )

    time: datetime.time = Field(
        default=datetime.time(0, 0, 0),
        description="",
        examples=["{Time: 18:35:10}"],
        validation_alias=AliasChoices("Time", "time", "created"),
        serialization_alias="Time",
    )

    project: Optional[str] = Field(
        default=None,
        description="The line {Project: NameOfYourProject} defines the source project "
                    "which the datasets were exported from.",
        examples=["{Projet: Exploration Base AGB 3.2}"],
        validation_alias=AliasChoices("Project", "Projet", "project"),
        serialization_alias="Project",
    )

    formatVersion: str = Field(
        default="9.0.0",
        description="",
        examples=["{CSV Format version: 9.0.0}"],
        validation_alias=AliasChoices(
            "CSV Format version", "csv_version", "formatVersion"
        ),
        serialization_alias="CSV Format version",
    )

    csv_seperator: Separators = Field(
        default=Separators.SEMICOLON_STR,
        description="",
        examples=["{CSV separator: Semicolon"],
        validation_alias=AliasChoices("CSV separator", "delimiter"),
        serialization_alias="CSV separator",
    )

    decimal_seperator: Separators = Field(
        default=Separators.COLON,
        description="",
        examples=["{Decimal separator: .}"],
        serialization_alias="Decimal separator",
    )

    date_seperator: str = Field(
        default=Separators.SLASH,
        description="",
        examples=["{Date separator: -}"],
        validation_alias=AliasChoices("Date separator", "date_seperator"),
        serialization_alias="Date separator",
    )

    short_date_format: str = Field(
        default="dd/MM/yyyy",
        description="",
        examples=["{Short date format: yyyy-MM-dd}"],
        validation_alias=AliasChoices("Short date format", "short_date_format"),
        serialization_alias="Short date format",
    )

    export_platform_ids: Optional[CustomBoolean] = Field(
        default=None,
        description="",
        examples=["{Export platform IDs: No}"],
        validation_alias=AliasChoices("Export platform IDs", "export_platform_ids"),
        serialization_alias="Export platform IDs",
    )

    skip_empty_fields: Optional[CustomBoolean] = Field(
        default=None,
        description="",
        examples=["{Skip empty fields: No}"],
        validation_alias=AliasChoices("Skip empty fields", "skip_empty_fields"),
        serialization_alias="Skip empty fields",
    )

    convert_expressions_to_constants: Optional[CustomBoolean] = Field(
        default=None,
        description="",
        examples=["{Convert expressions to constants: Yes}"],
        validation_alias=AliasChoices(
            "Convert expressions to constants:", "convert_expressions_to_constants"
        ),
        serialization_alias="Convert expressions to constants",
    )

    selection: Optional[str] = Field(
        default=None,
        description="",
        examples=["{Selection: Selection(1)}"],
        validation_alias=AliasChoices("Selection", "selection"),
        serialization_alias="Selection",
    )

    related_objects: Optional[CustomBoolean] = Field(
        default=None,
        description="",
        examples=[
            "{Related objects (system descriptions, substances, units, etc.): Yes}"
        ],
        validation_alias=AliasChoices(
            "Related objects (system descriptions, substances, units, etc.)",
            "related_objects",
        ),
        serialization_alias="Related objects (system descriptions, substances, units, etc.)",
    )

    include_sub_product_stages_and_processes: CustomBoolean = Field(
        default="",
        description="",
        examples=["{Include sub product stages and processes: No}"],
        validation_alias=AliasChoices(
            "Include sub product stages and processes",
            "include_sub_product_stages_and_processes",
        ),
        serialization_alias="Include sub product stages and processes",
    )

    open_library: Optional[str] = Field(
        default=None,
        description="",
        examples=["{Open library: 'Methods'}"],
    )

    open_project: Optional[str] = Field(
        default=None,
        description="",
        validation_alias=AliasChoices("open project", "open_project"),
        serialization_alias="open project",
    )

    libraries: List[str] = Field(
        default_factory=list,
        examples=["""{Biblioth�que 'AGRIBALYSE - unit'}\n{Biblioth�que 'Methods'}"""],
        serialization_alias="Library"
    )

    @field_serializer("date", when_used="json")
    def serialize_date(self, date: datetime.date, info) -> str:
        if info.context and "short_date_format" in info.context:
            format_str = (
                info.context["short_date_format"]
                .replace("dd", "%d")
                .replace("MM", "%m")
                .replace("yyyy", "%Y")
            )
        else:
            format_str = "%d/%m/%Y"
        result = date.strftime(format_str)
        return result

    @field_serializer("time", when_used="json")
    def serialize_time(self, time: datetime.time, info) -> str:
        result = time.strftime("%H:%M:%S")
        return result

    @model_serializer(mode="wrap", when_used="json", return_type=List[str])
    def surround_with_brackets(self, handler, info) -> List[str]:
        output_lines = []

        for field_display_name, field_value in handler(self).items():

            if isinstance(field_value, str):
                if field_display_name in ["kind"]:
                    output_lines.append("{" + f"{field_value}" + "}")
                else:
                    field_seperator = (
                        ""
                        if field_display_name
                           in [
                               "SimaPro",
                           ]
                        else ":"
                    )
                    output_lines.append("{" + f"{field_display_name}{field_seperator} {field_value}" + "}")

            elif isinstance(field_value, list):
                for item in field_value:
                    field_seperator = (
                        ""
                        if field_display_name
                           in [
                               "SimaPro", "Library",
                           ]
                        else ":"
                    )
                    if field_display_name in ["Library"]:
                        item_r = repr(item)
                    else:
                        item_r = item
                    output_lines.append(
                        "{" + f"{field_display_name}{field_seperator} {item_r}" + "}"
                    )

            else:
                pass

        return output_lines

    @field_validator("date", mode="before")
    def cast_to_date(cls, v):
        """allows assigning a datetime object to a date field"""
        if isinstance(v, datetime.datetime):
            return v.date()
        return v

    @field_validator("time", mode="before")
    def cast_to_time(cls, v):
        """allows assigning a datetime object to a time field"""
        if isinstance(v, datetime.datetime):
            return v.time()
        return v


class SimaProFile(BaseModel):
    """
    After the header, a SimaPro CSV file contains a set of blocks with data. All
    data blocks start with a header and end with the keyword `End`. For example the
    following is a block of quantities:
    ```
    Quantities
    Mass;Yes
    Length;Yes

    End
    ```

    A block can contain data rows directly, like in the example above, or contain
    sections with data rows. For example a process block starts with the header
    `Process` and contains a set of sections like `Category type`, `Process
    identifier`, etc:

    ```
    Process

    Category type
    material

    Process identifier
    DefaultX25250700002

    Type
    Unit process

    ...

    End
    ```
    """

    class Config:
        use_enum_values = True

    header: SimaProHeader
    blocks: List["SimaProBlock"] = Field(
        default=[],
        description="Import file size should be under 150 MB \nModel should contain less than 750 processes",
        examples=["SimaPro 8.5.0.0"],
    )

    @property
    def _get_process_block(self) -> Optional["SimaProProcessBlock"]:
        for block in self.blocks:
            if isinstance(block, SimaProProcessBlock):
                return block
        return None

    @model_serializer(mode="wrap", when_used="json")
    def output_as_csv_lines(self, handler, info) -> List[str]:
        output_lines = []

        output_lines.extend(
            self.header.model_dump(
                by_alias=True, exclude_unset=False, exclude_none=False, mode="json"
            )
        )
        output_lines.append("")

        if ((isinstance(self.header.csv_seperator, str) and self.header.csv_seperator == Separators.SEMICOLON_STR.value)
                or self.header.csv_seperator == Separators.SEMICOLON_STR):
            csv_seperator = Separators.SEMICOLON.value
        else:
            if isinstance(self.header.csv_seperator, Enum):
                csv_seperator = self.header.csv_seperator.value
            else:
                csv_seperator = self.header.csv_seperator

        for block in self.blocks:
            output_lines.extend(
                block.model_dump(
                    by_alias=True,
                    exclude_none=False,
                    exclude_unset=True,
                    mode="json",
                    context={
                        "decimal_seperator": self.header.decimal_seperator.value,
                        "date_seperator": self.header.date_seperator.value,
                        "short_date_format": self.header.short_date_format,
                        "csv_seperator": csv_seperator,
                    },
                )
            )
        # output_lines.append(self.file_terminator) #todo
        return output_lines


class SimaProBlock(BaseModel):
    """After the header, a SimaPro CSV file contains a set of blocks with data. All
    data blocks start with a header and end with the keyword `End`."""

    block_header: str
    block_terminator: Literal["End"] = "End"

    # block_content: List[Union["SimaProRow", "SimaProSection"]]  # todo named fields?

    @model_serializer(mode="wrap", when_used="json")
    def output_as_csv_lines(self, handler, info) -> List[str]:
        output_lines = []
        output_lines.append(self.block_header)
        output_lines.append("")

        if info.context:
            seperator_char = info.context.get("csv_seperator", ";")
        else:
            seperator_char = ";"
        for k, v in handler(self).items():  # todo replace with dump and context seperator_char
            if k in ["block_header", "block_terminator"]:
                continue

            if k not in ["rows"]:
                output_lines.append(k)

            if isinstance(v, str):
                output_lines.append(v)
                output_lines.append("")

            elif v is None:
                output_lines.append("Unspecified")
                output_lines.append("")

            elif isinstance(v, list):
                output_lines.extend(v)
                output_lines.append("")

            else:
                raise Exception("Not implemented")

        output_lines.append(self.block_terminator)
        output_lines.append("")
        output_lines.append("")
        return output_lines


class SimaProSection(BaseModel):
    section_header: SimaProSectionHeader
    rows: Optional[List["SimaProTwoRowsKeyValue"]] = []

    # section_content: List["SimaProRow"]

    @field_validator("rows", mode="before")
    def split_lines(cls, v, info):
        if isinstance(v, str):
            li = v.split(";")
            # from bw_simapro_csv.utils import alternating_key_value
            # dffdf = alternating_key_value(block) #todo
            val = cls.model_validate(li)
            return val
        return v

    @model_validator(mode="before")
    def line_load(cls, payload, validation_info):
        if isinstance(payload, dict):
            return payload
        elif isinstance(payload, str):  # todo use alternating_key_value()
            split_line = payload.split(";")
            ret = {"name": split_line[0]}
            if len(split_line) > 1:
                ret["comment"] = split_line[1]
            return {"rows": [ret]}
        elif isinstance(payload, list):  # todo use alternating_key_value()
            raise Exception("Not implemented")
        else:
            return payload

    @model_serializer(mode="wrap", when_used="json")
    def output_section_as_csv_lines(self, handler, info) -> List[str]:
        output_lines = []
        output_lines.append(self.section_header)
        output_lines.append("")
        for k, v in handler(self).items():  # todo replace with model dump
            if k in ["section_header"]:
                continue
            if isinstance(v, str):
                output_lines.append(k)
            elif isinstance(v, list):
                output_lines.extend(list(chain.from_iterable(v)))
                # output_lines.extend(v)
        # for field_name, field_val in self.model_fields.items():
        #     if field_name in ["section_header"]:
        #         continue
        #     output_lines.append(field_val.model_dump(by_alias=True, exclude_none=True, mode="json"))
        output_lines.append("aaaaa")
        return output_lines


class SimaProRow(BaseModel):
    line_no: Optional[int] = Field(
        None, description="line number in file", exclude=True
    )

    # data: Optional[Any] = None

    # @field_validator("data", mode="before")
    # def split_lines(cls, v, info):
    #     if isinstance(v, str):
    #         li = v.split(";")
    #         val = cls.model_validate(li)
    #         return val
    #     return v

    @model_validator(mode="before")
    def line_load(cls, payload, validation_info):
        if isinstance(payload, dict):
            return payload
        elif isinstance(payload, str):  # todo use alternating_key_value()
            pass
            # res = payload.split(";")

            return {"data": payload}
        else:
            return payload

    @model_serializer(mode="wrap", when_used="json")
    def output_row_as_line(self, handler, info) -> str:
        compacted_into_single_line = ""

        if info.context:
            seperator_char = info.context.get("csv_seperator", ";")
        else:
            seperator_char = ";"

        for k, v in handler(self).items():
            if k in ["line_no"]:  # todo replace with "line_no.exclude == True"
                continue
            if isinstance(v, str):
                compacted_into_single_line += v
            elif isinstance(v, (int, Decimal)):
                compacted_into_single_line += str(v)
            elif v is None:
                pass
            else:
                raise Exception("Not implemented")
            compacted_into_single_line += seperator_char
            # compacted_into_single_line += v
        return compacted_into_single_line.rstrip(seperator_char)


class SimaProTwoRowsKeyValue(BaseModel):
    line_no: Optional[int] = Field(
        None, description="line number in file", exclude=True
    )
    data: Optional[Any] = None

    @field_validator("data", mode="before")
    def split_lines(cls, v, info):
        if isinstance(v, str):
            li = v.split(";")
            val = cls.model_validate(li)
            return val
        return v

    @model_validator(mode="before")
    def line_load(cls, payload, validation_info):
        if isinstance(payload, dict):
            return payload
        elif isinstance(payload, str):  # todo use alternating_key_value()
            pass
            # res = payload.split(";")

            return {"data": payload}
        else:
            return payload

    @model_serializer(mode="wrap", when_used="json")
    def output_field_as_2_lines(self, handler, info) -> List[str]:
        output_lines = []
        for k, v in handler(self).items():
            if k in ["block_header", "block_terminator"]:
                continue
            output_lines.append(k)
            output_lines.append(v)
            output_lines.append("TODOTODOTODOTODO")  # todo
        return output_lines


class SystemDescriptionBlock(SimaProBlock):
    block_header: Literal["System description"] = "System description"
    # rows: Optional[List["SystemDescriptionRow"]] = []

    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    category: str = Field(
        validation_alias=AliasChoices("Category", "category"),
        serialization_alias="Category",
    )

    description: QuotedStr = Field(
        validation_alias=AliasChoices("Description", "description"),
        serialization_alias="Description",
    )

    sub_systems: str = Field(
        default=None,
        validation_alias=AliasChoices("Sub-systems", "sub_systems"),
        serialization_alias="Sub-systems",
    )

    cut_off_rules: str = Field(
        default=None,
        validation_alias=AliasChoices("Cut-off rules", "cut_off_rules"),
        serialization_alias="Cut-off rules",
    )

    energy_model: str = Field(
        default=None,
        validation_alias=AliasChoices("Energy model", "energy_model"),
        serialization_alias="Energy model",
    )

    transport_model: str = Field(
        default=None,
        validation_alias=AliasChoices("Transport model", "transport_model"),
        serialization_alias="Transport model",
    )

    waste_model: str = Field(
        default=None,
        validation_alias=AliasChoices("Waste model", "waste_model"),
        serialization_alias="Waste model",
    )

    other_assumptions: str = Field(
        default=None,
        validation_alias=AliasChoices("Other assumptions", "other_assumptions"),
        serialization_alias="Other assumptions",
    )

    other_information: str = Field(
        default=None,
        validation_alias=AliasChoices("Other information", "other_information"),
        serialization_alias="Other information",
    )

    allocation_rules: str = Field(
        default=None,
        validation_alias=AliasChoices("Allocation rules", "allocation_rules"),
        serialization_alias="Allocation rules",
    )


class SystemDescriptionSection(SimaProSection):
    section_header: Literal["System description"] = "System description"
    rows: Optional[List["SystemDescriptionTwoRowsKeyValue"]] = []


# refdata
class UnitRow(SimaProRow):
    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )
    dimension: Optional[str] = None

    conversion_factor: DecimalValue = Field(
        validation_alias=AliasChoices(
            "conversionFactor", "conversion_factor", "factor", "conversion"
        ),
        serialization_alias="conversionFactor",
    )
    reference_unit: str = Field(
        validation_alias=AliasChoices("reference unit name", "reference_unit"),
        serialization_alias="reference unit name",
    )


class QuantityRow(SimaProRow):
    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    comment: CustomBoolean = Field(default=True)

    # hasDimension: CustomBoolean = Field(
    #     default=True,
    #     validation_alias=AliasChoices("Has dimension", "hasDimension"),
    #     serialization_alias='Has dimension')


class InputParameterRow(SimaProRow):
    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    value: DecimalValue
    uncertainty: UncertaintyRecord
    isHidden: CustomBoolean
    comment: str


class ElementaryFlowRow(SimaProRow):
    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    unit: str
    cas: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("Cas", "cas", "cas_number"),
        serialization_alias="Cas",
    )

    comment: QuotedStr
    platformId: Optional[UUID] = Field(
        None,
        validation_alias=AliasChoices("PlatformId", "platformId"),
        serialization_alias="PlatformId",
    )

    @field_serializer("name", when_used="json")
    def format_name_fields(self, value: str, info) -> str:
        """
        Re-formats names according to "Database guidelines, Best practices for SimaPro database development" > "Database developer guidelines" 3.2
        """
        value = value.replace(";", " ")
        if len(value) < 100:
            return value[:1].upper() + value[1:]
        else:
            value = value[:97] + "..."
            return value[:1].upper() + value[1:]


class CalculatedParameterRow(SimaProRow):
    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    expression: str
    comment: str


# process
class ElementaryExchangeRow(SimaProRow):
    name: str = Field(
        description="substance name",
        validation_alias=AliasChoices("Name", "name"),
        serialization_alias="Name",
        max_length=100,
    )

    subCompartment: str = Field(max_length=26)
    unit: str = Field(max_length=10)
    amount: DecimalValue = Field(default=0.0)
    uncertainty: UncertaintyRecord = Field(default=UncertaintyRecordUndefined)
    comment: QuotedStr = Field(default="", max_length=1000)
    platformId: Optional[UUID] = Field(
        None,
        validation_alias=AliasChoices("PlatformId", "platformId"),
        serialization_alias="PlatformId",
        description="A GUID representing the substance within the main compartment."
    )

    flow_metadata: SkipJsonSchema[Optional[dict]] = Field(
        default={}, exclude=True, description="dev storage", repr=False
    )


class LiteratureRow(SimaProRow):
    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    comment: Optional[str] = Field(default=None)


class ExternalDocumentsRow(SimaProRow):
    url: str = Field()
    comment: Optional[str] = Field(default=None)


class ProductOutputRow(SimaProRow):
    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    unit: str
    amount: DecimalValue
    allocation: DecimalValue
    wasteType: str = Field(
        validation_alias=AliasChoices("wasteType", "waste_type"),
        serialization_alias="wasteType",
    )

    category: str = Field(
        description="The category path is a string of categories separated by a backward slash “\”. "
                    "The first category is the parent one, and the ones that follow are the (grand)children: e.g. "
                    "Parent category\\Child category\\Grandchild category. "
                    "If a category (path) is already existing in the database, SimaPro will then add the processes "
                    "to said category. Otherwise, a new category will be automatically created. "
                    "The main category (materials, processes, waste treatment, waste scenarios) is set in the "
                    "“Category type” section in the header block. "
                    "All processes must have at least one reference product exchange defined within the Products "
                    "section, except for waste treatment processes, where there is no Products section and instead "
                    "a “Waste treatment” section (see below)."
    )
    comment: QuotedStr
    platformId: Optional[UUID] = Field(
        None,
        description="PlatformId is generated by the SimaPro platform",
        validation_alias=AliasChoices("PlatformId", "platformId"),
        serialization_alias="PlatformId",
    )

    row_metadata: SkipJsonSchema[Optional[dict]] = Field(
        default={}, exclude=True, description="dev storage", repr=False
    )

    @field_serializer("name", when_used="json")
    def format_name_fields(self, value: str, info) -> str:
        """
        Re-formats names according to "Database guidelines, Best practices for SimaPro database development" > "Database developer guidelines" 3.2
        """
        value = value.replace(";", " ")
        if len(value) < 100:
            return value[:1].upper() + value[1:]
        else:
            value = value[:97] + "..."
            return value[:1].upper() + value[1:]


class ProductStageOutputRow(SimaProRow):
    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    unit: str
    amount: DecimalValue
    category: str
    comment: str
    platformId: Optional[UUID] = Field(
        None,
        validation_alias=AliasChoices("PlatformId", "platformId"),
        serialization_alias="PlatformId",
    )


class SystemDescriptionRow(SimaProRow):
    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    comment: Optional[str] = Field(None)

    @model_validator(mode="before")
    def line_load(cls, payload, validation_info):
        if isinstance(payload, dict):
            return payload
        elif isinstance(payload, str):
            split_line = payload.split(";")
            ret = {"name": split_line[0]}
            if len(split_line) > 1:
                ret["comment"] = split_line[1]
            return ret

        else:
            return payload


class SystemDescriptionTwoRowsKeyValue(SimaProTwoRowsKeyValue):
    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    comment: Optional[str] = Field(None)

    @model_validator(mode="before")
    def line_load(cls, payload, validation_info):
        if isinstance(payload, dict):
            return payload
        elif isinstance(payload, str):
            split_line = payload.split(";")
            ret = {"name": split_line[0]}
            if len(split_line) > 1:
                ret["comment"] = split_line[1]
            return ret

        else:
            return payload


class TechExchangeRow(SimaProRow):
    """ aka "TechnosphereEdges" ? in bw_simapro_csv/blocks/technosphere_edges.py"""
    name: str = Field(  # process name
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    unit: str = Field(max_length=10)
    amount: DecimalValue  # aka   value or formula?
    uncertainty: Optional[UncertaintyRecord]
    # uncertainty_type: Optional[int] = Field(
    #     None,
    #     validation_alias=AliasChoices("uncertainty type", "uncertainty_type"),
    #     serialization_alias="uncertainty type",
    # )
    comment: QuotedStr
    platformId: Optional[UUID] = Field(
        None,
        description="(optional) the UUID for the substance",
        validation_alias=AliasChoices("PlatformId", "platformId"),
        serialization_alias="PlatformId",
    )

    flow_metadata: SkipJsonSchema[Optional[dict]] = Field(
        default={}, exclude=True, description="dev storage", repr=False
    )

    @model_validator(mode="before")
    def load_uncertainty(cls, v):
        if isinstance(v, dict):
            if not "uncertainty" in v and v["uncertainty type"] == 0:
                v["uncertainty"] = UncertaintyRecordUndefined()
            return v
        return v


class EcoinventTechExchangeRow(TechExchangeRow):
    pass


class WasteFractionRow(SimaProRow):
    wasteTreatment: str
    wasteType: str
    fraction: DecimalValue
    comment: str


class WasteTreatmentRow(SimaProRow):
    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    unit: str
    amount: DecimalValue
    wasteType: str
    category: str
    comment: str
    platformId: Optional[UUID] = Field(
        None,
        validation_alias=AliasChoices("PlatformId", "platformId"),
        serialization_alias="PlatformId",
    )


# BLOCK_MAPPING = {
#     "Avoided products": TechnosphereEdges,
#     "Calculated parameters": DatasetCalculatedParameters,
#     "Economic issues": GenericUncertainBiosphere,
#     "Electricity/heat": TechnosphereEdges,
#     "Emissions to air": GenericUncertainBiosphere,
#     "Emissions to soil": GenericUncertainBiosphere,
#     "Emissions to water": GenericUncertainBiosphere,
#     "Final waste flows": GenericUncertainBiosphere,
#     "Input parameters": DatasetInputParameters,
#     "Materials/fuels": TechnosphereEdges,
#     "Non material emissions": GenericUncertainBiosphere,
#     "Products": Products,
#     "Remaining waste": RemainingWaste,
#     "Resources": GenericUncertainBiosphere,
#     "Separated waste": SeparatedWaste,
#     "Social issues": GenericUncertainBiosphere,
#     "Waste scenario": WasteScenario,
#     "Waste to treatment": TechnosphereEdges,
#     "Waste treatment": WasteTreatment,
# }


class SimaProProcessBlock(SimaProBlock):
    class Config:
        use_enum_values = True

    block_header: Literal["Process"] = "Process"

    category: ProcessCategory = Field(
        validation_alias=AliasChoices("Category type", "category"),
        serialization_alias="Category type",
    )

    platformId: Optional[UUID] = Field(
        None,
        validation_alias=AliasChoices("PlatformId", "platformId"),
        serialization_alias="PlatformId",
    )  # process has both platformID and platform identifier https://github.com/GreenDelta/olca-simapro-csv/pull/14/files

    identifier: Optional[str] = Field(
        default=None,
        description="""Unique identifier for the dataset. If left empty, it will be generated automatically by SimaPro.

                        The Process identifier is the unique identifier for the process in the database. It is a 23-
                        character long string. Having a Process identifier shorter than 23 characters would result
                        in an “Invalid process identifier” error at import.
                        The Process identifier consists of two parts: the process identifier prefix and the
                        numerical identifier. The process identifier prefix is specific for each library.
                        For a SimaPro CSV at import, the process identifier is not a mandatory section to fill in.
                        When empty, SimaPro will automatically generate the SimaPro identifier for the process
                        based on the process identifier prefix of the library it is imported into.

                        Each process in SimaPro has a unique process identifier for desktop and one for the platform.

                        The desktop process identifiers consist of 19 characters: 8 letters for the prefix + 11 numbers for
                        the main and sub-code. The prefix of the identifier (letters) are choosen by the database developer
                        and PRé based on the library abbreviation and should include a code for allocation type and
                        process type. The numbers for the main and sub-codes are generated automatically by the
                        software and start usually with 1 (00000000001) and adds one number to each following dataset
                        in the library.


                        For the platform Universal Unique Identifier are used, these are 128-bit values used to uniquely
                        identify a dataset, library or other objects in the SimaPro online environment. The value is
                        generated automatically by an algorithm and are composed by a sequence of characters per
                        hyphen (8-4-4-4-12), for example: fb69eeab-123e-4449-bc0e-1eb41827f3fc. The platform
                        identifiers for subtances and datasets are also stored in the desktop version of SimaPro so the
                        users can export a SimaPro csv and allow them to successfully link these elements in the platform.
                        """
        ,
        validation_alias=AliasChoices("Process identifier", "identifier"),
        serialization_alias="Process identifier",
        min_length=23,
        max_length=23,  # If not empty, must contain exactly 23 characters, no special characters allowed
    )
    processType: Optional[ProcessType] = Field(
        ProcessType.SYSTEM,
        validation_alias=AliasChoices("Type", "processType"),
        serialization_alias="Type",
    )
    name: str = Field(
        validation_alias=AliasChoices("Process name", "name"),
        serialization_alias="Process name",
    )

    status: Status = Field(
        default=Status.NONE,
        validation_alias=AliasChoices("Status", "status"),
        serialization_alias="Status",
    )

    time_period: Optional[str] = Field(
        default=None,
        deprecated="This field is no longer used in SimaPro Craft, but can be used without causing import errors. "
                   "It will be ignored by SimaPro Craft when reading the file.",
        examples=["Time period\nUnspecified"],
        validation_alias=AliasChoices("Time period", "time_period"),
        serialization_alias="Time period",
    )
    geography: Optional[str] = Field(
        default=None,
        deprecated="This field is no longer used in SimaPro Craft, but can be used without causing import errors. "
                   "It will be ignored by SimaPro Craft when reading the file.",
        examples=["Geography\nMixed data"],
        validation_alias=AliasChoices("Geography", "geography"),
        serialization_alias="Geography",
    )
    technology: Optional[str] = Field(
        default=None,
        deprecated="This field is no longer used in SimaPro Craft, but can be used without causing import errors. "
                   "It will be ignored by SimaPro Craft when reading the file.",
        examples=["Technology\nWorst case"],
        validation_alias=AliasChoices("Technology", "technology"),
        serialization_alias="Technology",
    )
    representativeness: Optional[str] = Field(
        default=None,
        deprecated="This field is no longer used in SimaPro Craft, but can be used without causing import errors. "
                   "It will be ignored by SimaPro Craft when reading the file.",
        validation_alias=AliasChoices("Representativeness", "representativeness"),
        serialization_alias="Representativeness",
    )
    cut_off_rules: Optional[str] = Field(
        default=None,
        deprecated="This field is no longer used in SimaPro Craft, but can be used without causing import errors. "
                   "It will be ignored by SimaPro Craft when reading the file.",
        validation_alias=AliasChoices("Cut off rules", "cut_off_rules"),
        serialization_alias="Cut off rules",
    )
    capital_goods: Optional[str] = Field(
        default=None,
        deprecated="This field is no longer used in SimaPro Craft, but can be used without causing import errors. "
                   "It will be ignored by SimaPro Craft when reading the file.",
        validation_alias=AliasChoices("Capital goods", "capital_goods"),
        serialization_alias="Capital goods",
    )
    boundary_with_nature: Optional[str] = Field(
        default=None,
        deprecated="This field is no longer used in SimaPro Craft, but can be used without causing import errors. "
                   "It will be ignored by SimaPro Craft when reading the file.",
        validation_alias=AliasChoices("Boundary with nature", "boundary_with_nature"),
        serialization_alias="Boundary with nature",
    )
    infrastructure: Optional[CustomBoolean] = Field(
        None,
        description="Whether the dataset represents infrastructure processes. "
                    "If set to yes, running impact assessment with the option “Exclude infrastructure processes” will "
                    "exclude this process from the calculation.",
        validation_alias=AliasChoices("Infrastructure", "infrastructure"),
        serialization_alias="Infrastructure",
    )
    date: datetime.date = Field(
        description="Field to store the date when the dataset was developed.",
        validation_alias=AliasChoices("Date", "date"),
        serialization_alias="Date",
    )
    record: Optional[str] = Field(
        "",
        validation_alias=AliasChoices("Record", "record"),
        serialization_alias="Record",
        max_length=1000,
    )
    generator: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("Generator", "generator"),
        serialization_alias="Generator",
        max_length=1000,
    )
    external_documents: Optional["ExternalDocumentsRow"] = Field(
        default=None,
        description="External documents allows storing links to documents. "
                    "They are composed of two values: A link (e.g. a url) and a comment separated by a semicolon",
        validation_alias=AliasChoices("External documents", "external_documents"),
        serialization_alias="External documents",
    )
    collectionMethod: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("Collection method", "collectionMethod"),
        serialization_alias="Collection method",
        max_length=50000,
    )
    verification: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("Verification", "verification"),
        serialization_alias="Verification",
        max_length=1000,
    )
    comment: str = Field(
        validation_alias=AliasChoices("Comment", "comment"),
        serialization_alias="Comment",
        max_length=50000,
    )
    allocationRules: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("Allocation rules", "allocationRules"),
        serialization_alias="Allocation rules",
        max_length=1000,
    )
    allocation_method: Optional[str] = Field(
        None,
        validation_alias=AliasChoices(
            "Multiple output allocation", "allocation_method"
        ),
        serialization_alias="Multiple output allocation",
    )
    dataTreatment: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("Data treatment", "dataTreatment"),
        serialization_alias="Data treatment",
        max_length=50000,
    )

    systemDescription: Optional[SystemDescriptionRow] = Field(
        None,
        validation_alias=AliasChoices("System description", "systemDescription"),
        serialization_alias="System description",
    )

    wasteTreatment: Optional[WasteTreatmentRow] = None

    wasteScenario: Optional[WasteTreatmentRow] = Field(
        None,
        validation_alias=AliasChoices("Waste scenario", "wasteScenario"),
        serialization_alias="Waste scenario",
    )

    literatures: Optional[List[LiteratureRow]] = Field(
        [],
        validation_alias=AliasChoices("Literature references", "literatures"),
        serialization_alias="Literature references",
    )

    products: Optional[List[ProductOutputRow]] = Field(
        [],
        validation_alias=AliasChoices("Products", "products"),
        serialization_alias="Products",
        min_length=1,
    )

    avoidedProducts: Optional[List[TechExchangeRow]] = Field(
        [],
        validation_alias=AliasChoices("Avoided products", "avoidedProducts"),
        serialization_alias="Avoided products",
    )

    resources: Optional[List[ElementaryExchangeRow]] = Field(
        [],
        validation_alias=AliasChoices("Resources", "Raw materials", "resources"),
        serialization_alias="Resources",
    )

    materialsAndFuels: Optional[List[TechExchangeRow]] = Field(
        [],
        validation_alias=AliasChoices("Materials/fuels", "materialsAndFuels"),
        serialization_alias="Materials/fuels",
    )

    electricityAndHeat: Optional[List[TechExchangeRow]] = Field(
        [],
        validation_alias=AliasChoices("Electricity/heat", "electricityAndHeat"),
        serialization_alias="Electricity/heat",
    )

    wasteToTreatment: Optional[List[TechExchangeRow]] = Field(
        [],
        validation_alias=AliasChoices("Waste to treatment", "wasteToTreatment"),
        serialization_alias="Waste to treatment",
        description="stores the exchange of waste as a product to a waste treatment process"
    )

    separatedWaste: Optional[List[WasteFractionRow]] = Field(
        [],
        validation_alias=AliasChoices("Separated waste", "separatedWaste"),
        serialization_alias="Separated waste",
    )

    remainingWaste: Optional[List[WasteFractionRow]] = Field(
        [],
        validation_alias=AliasChoices("Remaining waste", "remainingWaste"),
        serialization_alias="Remaining waste",
    )

    emissionsToAir: Optional[List[ElementaryExchangeRow]] = Field(
        [],
        validation_alias=AliasChoices("Emissions to air", "emissionsToAir"),
        serialization_alias="Emissions to air",
    )

    emissionsToWater: Optional[List[ElementaryExchangeRow]] = Field(
        [],
        validation_alias=AliasChoices("Emissions to water", "emissionsToWater"),
        serialization_alias="Emissions to water",
    )
    emissionsToSoil: Optional[List[ElementaryExchangeRow]] = Field(
        [],
        validation_alias=AliasChoices("Emissions to soil", "emissionsToSoil"),
        serialization_alias="Emissions to soil",
    )
    finalWasteFlows: Optional[List[ElementaryExchangeRow]] = Field(
        [],
        validation_alias=AliasChoices("Final waste flows", "finalWasteFlows"),
        serialization_alias="Final waste flows",
    )

    nonMaterialEmissions: Optional[List[ElementaryExchangeRow]] = Field(
        [],
        examples=["Noise, aircraft, freight;tkm;;\n"
                  "Noise, aircraft, passenger;personkm;;\n"
                  "Noise, rail, freight train;tkm;;\n"
                  "Noise, rail, passenger train, average;personkm;;\n"
                  "Noise, road, lorry, average;km;;\n"
                  "Noise, road, passenger car, average;km;;"],
        validation_alias=AliasChoices("Non material emissions", "nonMaterialEmissions"),
        serialization_alias="Non material emissions",
    )

    socialIssues: Optional[List[ElementaryExchangeRow]] = Field(
        [],
        validation_alias=AliasChoices("Social issues", "socialIssues"),
        serialization_alias="Social issues",
    )

    economicIssues: Optional[List[ElementaryExchangeRow]] = Field(
        [],
        validation_alias=AliasChoices("Economic issues", "economicIssues"),
        serialization_alias="Economic issues",
    )

    inputParameters: Optional[List[InputParameterRow]] = Field(
        [],
        validation_alias=AliasChoices("Input parameters", "inputParameters"),
        serialization_alias="Input parameters",
    )

    calculatedParameters: Optional[List[CalculatedParameterRow]] = Field(
        [],
        validation_alias=AliasChoices("Calculated parameters", "calculatedParameters"),
        serialization_alias="Calculated parameters",
    )

    @field_validator("products", mode="after")
    def product_allocation_sums_to_100(
            cls, products: List["ProductOutputRow"]
    ) -> List["ProductOutputRow"]:
        if sum([product.allocation for product in products]) != 100:
            raise ValueError(f"All products allocations must sum to 100%")
        return products

    @field_serializer("date", when_used="json")
    def serialize_date(self, date: datetime.date, info):
        if info.context:
            format_str = (
                info.context["short_date_format"]
                .replace("dd", "%d")
                .replace("MM", "%m")
                .replace("yyyy", "%Y")
            )
        else:
            format_str = "%d/%m/%Y"
        result = date.strftime(format_str)
        return result


# method
class DamageCategoryRow(SimaProRow):
    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    unit: str


class DamageFactorRow(SimaProRow):
    impactCategory: str
    factor: DecimalValue


class DamageCategoryBlock(SimaProBlock):
    block_header: Literal["Damage category"]

    info: DamageCategoryRow = Field(
        validation_alias=AliasChoices("Damage category", "info"),
        serialization_alias="Damage category",
    )
    factors: List[DamageFactorRow] = Field(
        validation_alias=AliasChoices("Impact categories", "factors"),
        serialization_alias="Impact categories",
    )


class ImpactCategoryRow(SimaProRow):
    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    unit: str


class ImpactFactorRow(SimaProRow):
    compartment: str
    sub_compartment: str
    flow: str
    cas_number: str
    factor: DecimalValue
    unit: str


class ImpactCategoryBlock(SimaProBlock):
    block_header: Literal["Impact category"]

    info: ImpactCategoryRow = Field(
        validation_alias=AliasChoices("Impact category", "info"),
        serialization_alias="Impact category",
    )
    factors: List[ImpactFactorRow] = Field(
        validation_alias=AliasChoices("Substances", "factors"),
        serialization_alias="Substances",
    )


class NwSetFactorRow(SimaProRow):
    impactCategory: str
    factor: DecimalValue


class NwSetBlock(SimaProBlock):
    block_header: Literal["Normalization-Weighting set"]

    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    normalization_factors: List[NwSetFactorRow]
    weighting_factors: List[NwSetFactorRow]


class ImpactMethodBlock(SimaProBlock):
    block_header: Literal["Method"]

    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    version: "VersionRow"
    comment: str
    category: str
    use_damage_assessment: CustomBoolean
    use_normalization: CustomBoolean
    use_weighting: CustomBoolean
    use_addition: CustomBoolean
    weighting_unit: str

    impact_categories: List[ImpactCategoryBlock]
    damage_categories: List[DamageCategoryBlock]
    nw_sets: List[NwSetBlock]


class VersionRow(SimaProRow):
    major: int
    minor: int


class QuantityBlock(SimaProBlock):
    block_header: Literal["Quantities"] = "Quantities"
    rows: List[QuantityRow]


class UnitBlock(SimaProBlock):
    block_header: Literal["Units"] = "Units"
    rows: List[UnitRow]


class GenericBiosphere(SimaProBlock):
    block_header: Literal[
        "Raw materials",
        "Airborne emissions",
        "Waterborne emissions",
        "Final waste flows",
        "Emissions to soil",
        "Non material emissions",
        "Social issues",
    ]
    rows: List[ElementaryFlowRow]


class LiteratureReferenceBlock(SimaProBlock):
    block_header: Literal["Literature reference"] = "Literature reference"

    name: str = Field(
        validation_alias=AliasChoices("Name", "name"), serialization_alias="Name"
    )

    documentation_link: str = Field(
        validation_alias=AliasChoices("Documentation link", "documentation_link"),
        serialization_alias="Documentation link",
    )
    category: str = Field(
        default="Others",
        examples=["Others"],
        validation_alias=AliasChoices("Category", "category"),
        serialization_alias="Category",
    )
    description: QuotedStr = Field(
        validation_alias=AliasChoices("Description", "description"),
        serialization_alias="Description",
    )
