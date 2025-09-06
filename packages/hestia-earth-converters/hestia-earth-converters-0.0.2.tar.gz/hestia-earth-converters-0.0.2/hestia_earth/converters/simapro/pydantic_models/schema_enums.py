from enum import Enum
from typing import List


class SimaProCSVType(str, Enum):
    stages = "product stages"
    methods = "methods"
    processes = "processes"


class ElementaryFlowTypeAlias(Enum):
    RESOURCES = ("Resources", "Raw materials", "Raw")
    EMISSIONS_TO_AIR = ("Emissions to air", "Airborne emissions", "Air")
    EMISSIONS_TO_WATER = ("Emissions to water", "Waterborne emissions", "Water")
    EMISSIONS_TO_SOIL = ("Emissions to soil", "Emissions to soil", "Soil")
    FINAL_WASTE_FLOWS = ("Final waste flows", "Final waste flows", "Waste")
    NON_MATERIAL_EMISSIONS = (
        "Non material emissions",
        "Non material emissions",
        "Non mat.",
    )
    SOCIAL_ISSUES = ("Social issues", "Social issues", "Social")
    ECONOMIC_ISSUES = ("Economic issues", "Economic issues", "Economic")

    def compartment_str(self):
        return self.value[0]

    def block_header(self):
        return self.value[1]

    def alias(self):
        return self.value[2]


class ProcessCategory(Enum):
    MATERIAL = "material"
    ENERGY = "energy"
    TRANSPORT = "transport"
    PROCESSING = "processing"
    USE = "use"
    WASTE_SCENARIO = "waste scenario"
    WASTE_TREATMENT = "waste treatment"

    @staticmethod
    def of(value):
        for category in ProcessCategory:
            if category.value.lower() == value.lower():
                return category
        return ProcessCategory.MATERIAL


class ProcessType(Enum):
    SYSTEM = "System"
    UNIT_PROCESS = "Unit process"

    @staticmethod
    def of(value):
        for type in ProcessType:
            if type.value == value:
                return type
        return ProcessType.UNIT_PROCESS


class ProductStageCategory(Enum):
    ASSEMBLY = "assembly"
    DISASSEMBLY = "disassembly"
    DISPOSAL_SCENARIO = "disposal scenario"
    LIFE_CYCLE = "life cycle"
    REUSE = "reuse"


class ProductType(Enum):
    AVOIDED_PRODUCTS = "Avoided products"
    ELECTRICITY_HEAT = "Electricity/heat"
    MATERIAL_FUELS = "Materials/fuels"
    WASTE_TO_TREATMENT = "Waste to treatment"


class Status(Enum):
    NONE = ""
    TEMPORARY = "Temporary"
    DRAFT = "Draft"
    TO_BE_REVISED = "To be revised"
    TO_BE_REVIEWED = "To be reviewed"
    FINISHED = "Finished"


class ElementaryFlowType(Enum):
    EMISSIONS_TO_AIR = "emissions_to_air"
    RESOURCES = "resources"
    EMISSIONS_TO_SOIL = "emissions_to_soil"
    EMISSIONS_TO_WATER = "emissions_to_water"


class SubCompartment(Enum):
    # emissions to air
    AIR_HIGH_POP = (ElementaryFlowType.EMISSIONS_TO_AIR, "high. pop.")
    AIR_INDOOR = (ElementaryFlowType.EMISSIONS_TO_AIR, "indoor")
    AIR_LOW_POP = (ElementaryFlowType.EMISSIONS_TO_AIR, "low. pop.")
    AIR_LOW_POP_LONG_TERM = (
        ElementaryFlowType.EMISSIONS_TO_AIR,
        "low. pop., long-term",
    )
    AIR_STRATOSPHERE = (ElementaryFlowType.EMISSIONS_TO_AIR, "stratosphere")
    AIR_STRATOSPHERE_TROPOSPHERE = (
        ElementaryFlowType.EMISSIONS_TO_AIR,
        "stratosphere + troposphere",
    )

    # resources
    RESOURCES_BIOTIC = (ElementaryFlowType.RESOURCES, "biotic")
    RESOURCES_IN_AIR = (ElementaryFlowType.RESOURCES, "in air")
    RESOURCES_IN_GROUND = (ElementaryFlowType.RESOURCES, "in ground")
    RESOURCES_IN_WATER = (ElementaryFlowType.RESOURCES, "in water")
    RESOURCES_LAND = (ElementaryFlowType.RESOURCES, "land")

    # emissions to soil
    SOIL_AGRICULTURAL = (ElementaryFlowType.EMISSIONS_TO_SOIL, "agricultural")
    SOIL_FORESTRY = (ElementaryFlowType.EMISSIONS_TO_SOIL, "forestry")
    SOIL_INDUSTRIAL = (ElementaryFlowType.EMISSIONS_TO_SOIL, "industrial")
    SOIL_URBAN = (ElementaryFlowType.EMISSIONS_TO_SOIL, "urban, non industrial")

    # emissions to water
    WATER_FOSSIL = (ElementaryFlowType.EMISSIONS_TO_WATER, "fossilwater")
    WATER_GROUND = (ElementaryFlowType.EMISSIONS_TO_WATER, "groundwater")
    WATER_GROUND_LONG_TERM = (
        ElementaryFlowType.EMISSIONS_TO_WATER,
        "groundwater, long-term",
    )
    WATER_LAKE = (ElementaryFlowType.EMISSIONS_TO_WATER, "lake")
    WATER_OCEAN = (ElementaryFlowType.EMISSIONS_TO_WATER, "ocean")
    WATER_RIVER = (ElementaryFlowType.EMISSIONS_TO_WATER, "river")
    WATER_RIVER_LONG_TERM = (ElementaryFlowType.EMISSIONS_TO_WATER, "river, long-term")

    UNSPECIFIED = (None, "")

    def elementary_flow_type_str(self):
        return self.value[0]

    def subcompartment_str(self):
        return self.value[1]

    def compartment_path_str(self):
        return f"{ElementaryFlowTypeAlias[self.elementary_flow_type_str().name].compartment_str()}/{self.subcompartment_str()}"

    def compartment_path_block_alias_str(self):
        return f"{ElementaryFlowTypeAlias[self.elementary_flow_type_str().name].block_header()}{self.subcompartment_str()}"

    @staticmethod
    def of(value: tuple):
        for sub in SubCompartment:
            if sub.value == value:
                return sub
        return SubCompartment.UNSPECIFIED


def emissions_to(flow_type_enum: ElementaryFlowType) -> List[str]:
    head = parent_compartment(flow_type_enum)
    out = [f"{head.compartment_str()}/(unspecified)"]

    for entry in SubCompartment:
        if entry.elementary_flow_type_str() == flow_type_enum:
            out.append(entry.compartment_path_str())
    return out


def parent_compartment(flow_type_enum: ElementaryFlowType):
    return ElementaryFlowTypeAlias[flow_type_enum.name]


def emissions_to_block_header(flow_type_enum: str) -> List[str]:
    head = parent_compartment(flow_type_enum)
    out = [f"{head.block_header()}/(unspecified)"]

    for entry in SubCompartment:
        if entry.elementary_flow_type_str() == flow_type_enum:
            out.append(entry.compartment_path_block_alias_str())
    return out


def emissions_to_and_alias_compactments(flow_type_enum: str) -> list:
    prefer = emissions_to(flow_type_enum) + emissions_to_block_header(flow_type_enum)
    return prefer


unit_categories = {
    "kg": "Mass",
    "g": "Mass",
    "ton": "Mass",
    "µg": "Mass",
    "mg": "Mass",
    "Mtn": "Mass",
    "kton": "Mass",
    "ng": "Mass",
    "pg": "Mass",
    "lb": "Mass",
    "oz": "Mass",
    "tn.sh": "Mass",
    "tn.lg": "Mass",

    "kWh": "Energy",
    "MJ": "Energy",
    "GJ": "Energy",
    "J": "Energy",
    "kJ": "Energy",
    "PJ": "Energy",
    "TJ": "Energy",
    "MWh": "Energy",
    "Btu": "Energy",
    "kcal": "Energy",
    "Wh": "Energy",

    "km": "Length",
    "m": "Length",
    "cm": "Length",
    "dm": "Length",
    "mm": "Length",
    "µm": "Length",
    "ft": "Length",
    "inch": "Length",
    "yard": "Length",
    "mile": "Length",

    "MJ": "Energy",
    "m3y": "Volume.Time",
    "kBq": "Radioactivity",
    "m3": "Volume",
    "m2a": "Land use",
    "m2": "Area",
    None: "Unknown",
}
