from pathlib import Path
from typing import Optional
from bw_simapro_csv import SimaProCSV
from bw_simapro_csv import blocks as bw_sp_blocks

from . import (
    SimaProHeader, SimaProFile, SimaProProcessBlock, ProductOutputRow, TechExchangeRow,
    SystemDescriptionBlock, QuantityBlock, QuantityRow,
    UnitBlock, UnitRow, ElementaryFlowRow
)
from .schema_enums import ElementaryFlowType, SubCompartment as SemaProSubCompartment

from ..log import logger


def load_csv_file_to_sima_pro_obj(input_sima_pro_csv_file: Path) -> SimaProFile:
    try:
        sp = SimaProCSV(input_sima_pro_csv_file)

        # bw_sima_pro_pydantic_obj = SimaProCSVHeader(**sp.header)

        # if isinstance(input_sima_pro_csv_file, Path):
        #     data = open(input_sima_pro_csv_file, encoding="sloppy-windows-1252")
        #
        # # taken from bw_simapro_csv.header import parse_header
        # header, header_lines = parse_header(data)

        logger.debug(f"Loaded file version:{sp.database_name}")

        simappro_header_obj = SimaProHeader.model_validate(sp.header)  # todo or map directly

        # lines = simappro_header_obj.model_dump(exclude_none=True, mode="json")

        new_simapro_pydantic_obj = SimaProFile(header=simappro_header_obj)
        new_block_obj = None
        for block in sp.blocks:
            if isinstance(block, bw_sp_blocks.Process):

                new_block_obj = SimaProProcessBlock(**block.parsed['metadata'])
                # new_p = SimaProProcessBlock.model_validate(block)
                new_simapro_pydantic_obj.blocks.append(new_block_obj)
                for p_block in block.blocks.values():
                    if isinstance(p_block, bw_sp_blocks.Products):
                        for prod_entry in p_block.parsed:
                            simapro_prod = ProductOutputRow.model_validate(prod_entry)
                            new_block_obj.products.append(simapro_prod)

                    if isinstance(p_block, bw_sp_blocks.TechnosphereEdges):
                        if p_block.category == 'Materials/fuels':
                            for entry in p_block.parsed:
                                tech_exchange_row = TechExchangeRow.model_validate(entry)
                                # {
                                #     "line_no": entry["line_no"],
                                #     "name": entry["name"],
                                #     "unit": entry["unit"],
                                #     "amount": entry["amount"],
                                #     "uncertainty_type": entry["uncertainty_type"],
                                # })
                                new_block_obj.materialsAndFuels.append(tech_exchange_row)  # TechExchangeRow
                        else:
                            pass

            elif isinstance(block, bw_sp_blocks.SystemDescription):
                new_block_obj = SystemDescriptionBlock(**{k:v for k,v in block.parsed.items() if v is not None})
                #
                # for name, comment in block.parsed.items():
                #     if comment is not None:
                #         new_sd_r = SystemDescriptionRow.model_validate({"name": name, "comment": comment})
                #         new_block_obj.rows.append(new_sd_r)

            elif isinstance(block, bw_sp_blocks.Quantities):
                new_block_obj = QuantityBlock(rows=[])

                for name, comment in block.parsed.items():
                    if comment is not None:
                        new_quant_entry = QuantityRow.model_validate({"name": name, "comment": comment})
                        new_block_obj.rows.append(new_quant_entry)

            elif isinstance(block, bw_sp_blocks.Units):
                new_block_obj = UnitBlock(rows=[])
                for x in block.parsed:
                    simapro_prod = UnitRow.model_validate(x)
                    new_block_obj.rows.append(simapro_prod)


            elif isinstance(block, bw_sp_blocks.GenericBiosphere):
                for entry in block.parsed:
                    raw_materials_row = ElementaryFlowRow.model_validate(entry)

                    if block.category == "Raw materials":
                        new_simapro_pydantic_obj._get_process_block.resources.append(raw_materials_row)
                    else:
                        pass
            else:
                pass
            if new_block_obj:
                new_simapro_pydantic_obj.blocks.append(new_block_obj)
                new_block_obj = None
        # simapro_obj = SimaProFile.model_validate(sp)
    except Exception as e:
        logger.error(e)
        raise e
    return new_simapro_pydantic_obj


# minified_compartment_map = {
#     'Airborne emissions(unspecified)': '',
#     'Airborne emissionshigh. pop.': 'high. pop.',
#     'Airborne emissionsindoor': 'indoor',
#     'Airborne emissionslow. pop.': 'low. pop.',
#     'Airborne emissionslow. pop., long-term': 'low. pop., long-term',
#     'Airborne emissionsstratosphere': 'stratosphere',
#     'Airborne emissionsstratosphere + troposphere': 'stratosphere + troposphere',
#
#     'Emissions to soil(unspecified)': '',
#     'Emissions to soilagricultural': 'agricultural',
#     'Emissions to soilforestry': 'forestry',
#     'Emissions to soilindustrial': 'industrial',
#     'Emissions to soilurban, non industrial': 'urban, non industrial',
#
#     'Waterborne emissions(unspecified)': '',
#     'Waterborne emissionsfossilwater': 'fossilwater',
#     'Waterborne emissionsgroundwater': 'groundwater',
#     'Waterborne emissionsgroundwater, long-term': 'groundwater, long-term',
#     'Waterborne emissionslake': 'lake',
#     'Waterborne emissionsocean': 'ocean',
#     'Waterborne emissionsriver': 'river',
#     'Waterborne emissionsriver, long-term': 'river, long-term',
#
#     'Emissions to air/(unspecified)': '',
#     'Emissions to air/high. pop.': 'high. pop.',
#     'Emissions to air/indoor': 'indoor',
#     'Emissions to air/low. pop.': 'low. pop.',
#     'Emissions to air/low. pop., long-term': 'low. pop., long-term',
#     'Emissions to air/stratosphere': 'stratosphere',
#     'Emissions to air/stratosphere + troposphere': 'stratosphere + troposphere',
#     'Emissions to soil/(unspecified)': '',
#     'Emissions to soil/agricultural': 'agricultural',
#     'Emissions to soil/forestry': 'forestry',
#     'Emissions to soil/industrial': 'industrial',
#     'Emissions to soil/urban, non industrial': 'urban, non industrial',
#
#     'Emissions to water/(unspecified)': '',
#     'Emissions to water/fossilwater': 'fossilwater',
#     'Emissions to water/groundwater': 'groundwater',
#     'Emissions to water/groundwater, long-term': 'groundwater, long-term',
#     'Emissions to water/lake': 'lake',
#     'Emissions to water/ocean': 'ocean',
#     'Emissions to water/river': 'river',
#     'Emissions to water/river, long-term': 'river, long-term',
#     'Resources/biotic': 'biotic',
#     'Resources/fossil well': 'fossil well',
#     'Resources/in air': 'in air',
#     'Resources/in ground': 'in ground',
#     'Resources/in water': 'in water',
#     'Resources/land': 'land',
#     'Raw materials': '',  # todo should not be minified when adding to ".resources"?
#     'Final waste flows': '',
#     'Substance': '',  # Todo what is the true context of Substances from SimaProSynergy?
#
#     'Airborne emissions': "",
#     'Waterborne emissions': "",
#
#     'Waterborne emissions/(unspecified)': '',
#     'Waterborne emissions/fossilwater': 'fossilwater',
#     'Waterborne emissions/groundwater': 'groundwater',
#     'Waterborne emissions/groundwater, long-term': 'groundwater, long-term',
#     'Waterborne emissions/lake': 'lake',
#     'Waterborne emissions/ocean': 'ocean',
#     'Waterborne emissions/river': 'river',
#     'Waterborne emissions/river, long-term': 'river, long-term',
# }


compartment_prefixes = {
    ElementaryFlowType.EMISSIONS_TO_AIR: ['Airborne emissions', 'Emissions to air/', 'Emissions to air'],
    ElementaryFlowType.EMISSIONS_TO_WATER: ['Waterborne emissions/', 'Waterborne emissions', 'Emissions to water'],
    ElementaryFlowType.EMISSIONS_TO_SOIL: ['Emissions to soil/', 'Emissions to soil', ],
    ElementaryFlowType.RESOURCES: ['Raw materials', 'Resources/', 'Substance'],
}


def _is_main_compartment(value, param: ElementaryFlowType) -> Optional[str]:
    for prefix in compartment_prefixes[param]:
        if value.startswith(prefix):
            return prefix
    return None


def parse_compartment(value: str) -> Optional[SemaProSubCompartment]:
    for compartment_obj in ElementaryFlowType:
        if prefix := _is_main_compartment(value, compartment_obj):
            subcompartment_str = value[len(prefix):]
            if not subcompartment_str:
                return None
            for subcompartmentType in [SemaProSubCompartment]:
                res = subcompartmentType.of((compartment_obj, subcompartment_str))
                if res:
                    return res
            return None
    return None


def minify_semapro_compartment(value) -> str:  # todo "Raw materials"
    try:
        emission_compartment = parse_compartment(value)
    except Exception as e:
        logger.error(e)
        emission_compartment = None

    if emission_compartment in [None, '']:
        return ""
    else:
        return emission_compartment.subcompartment_str()


def strip_formula_from_unit(hestia_unit_str: str) -> str:
    for prefix in ['kg']:
        if hestia_unit_str.startswith(prefix):
            return prefix
    return hestia_unit_str
