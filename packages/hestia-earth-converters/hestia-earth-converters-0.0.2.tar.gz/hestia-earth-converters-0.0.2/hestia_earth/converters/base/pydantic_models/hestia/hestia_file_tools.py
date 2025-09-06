import json
import logging
import os
from pathlib import Path
from typing import List
import tempfile
import zipfile
from hestia_earth.schema import NodeType
from hestia_earth.schema.utils.sort import get_sort_key

from . import ImpactAssessment
from .hestia_schema_tools import recursively_expand_all_refs
from .api_utils import download_hestia

logger = logging.getLogger(__name__)


def _remove_keys(data: dict, keys: list):
    for key in keys:
        data.pop(key, None)


def clean_impact_data(data):
    new_aggregatedSources = []
    for source_node in data['cycle'].get('aggregatedSources', []):
        if set(source_node.keys()) == {"@id", "@type"}:
            populated_source = download_hestia(source_node.get("@id"), node_type="Source")
            new_aggregatedSources.append(populated_source)

    if data.get('aggregatedSources', []) == data['cycle'].get('aggregatedSources', []):
        data['aggregatedSources'] = new_aggregatedSources

    data['cycle']['aggregatedSources'] = new_aggregatedSources

    if 'site' in data['cycle']:
        data['cycle']['site']['dataPrivate'] = False
        _remove_keys(data['cycle']['site'], ['aggregatedSites', 'aggregatedSources'])

    if 'site' in data:
        data['site']['dataPrivate'] = False
        _remove_keys(data['site'], ['aggregatedSites', 'aggregatedSources'])

    return data


def load_hestia_model_from_id(id: str):
    impact = download_hestia(id, NodeType.IMPACTASSESSMENT, data_state='recalculated')
    if not impact:
        raise Exception(f"Could not find ImpactAssessment with id: {id}")

    data_state = 'original' if impact.get('aggregated') else 'recalculated'

    cycle = download_hestia(impact.get('cycle', {})['@id'], NodeType.CYCLE, data_state)
    site = download_hestia(
        (impact.get('site') or impact.get('cycle', {}).get('site', {})).get('@id'), NodeType.SITE, data_state
    )
    source = download_hestia(impact.get('source', {})['@id'], NodeType.SOURCE)

    site = site | {'defaultSource': source}
    cycle = cycle | {'site': site, 'defaultSource': source}

    from hestia_earth.converters.base.pydantic_models.hestia.hestia_file_tools import clean_impact_data
    data = clean_impact_data(impact | {
        'cycle': cycle,
        'site': site,
        'source': source
    })

    from hestia_earth.converters.base.pydantic_models.hestia import ImpactAssessment
    return ImpactAssessment.model_validate(data)


def load_hestia_model_from_file(input_folder: Path, name: str) -> ImpactAssessment:
    with open(name) as f:
        data = json.load(f)
    data = recursively_expand_all_refs(data, target_folder_path=input_folder)

    # TODO this should only be done on aggregated data
    data = clean_impact_data(data)

    target_impactassessment = ImpactAssessment.model_validate(data)
    return target_impactassessment


def sort_schema_dict(data: dict, current_path: str = "") -> dict:
    new_d = {}
    data2 = dict(sorted(data.items(), key=lambda x: get_sort_key(current_path + "." + x[0])))
    for k, v in data2.items():
        if isinstance(v, dict):
            new_d[k] = sort_schema_dict(v, current_path=current_path + "." + k)
        else:
            new_d[k] = v
    return new_d


def save_impact_assessment_to_file(new_impact: ImpactAssessment, saved_impact_assessments_folder: Path,
                                   full_path: Path = None):
    data = new_impact.model_dump(exclude_none=True, by_alias=True, mode="json")

    sorted_d = sort_schema_dict(data, current_path=data["@type"])

    if not full_path:
        # filename = secure_filename(data['name'])
        filename = data.get('@id', None) or data.get("id")  # already _common_name_glo
        output_path = saved_impact_assessments_folder
        os.makedirs(output_path, exist_ok=True)
        full_path = f"{output_path}/{filename}.json"

    else:
        os.makedirs(str(full_path.parent), exist_ok=True)
    logger.info(f"Saving to: {full_path}")

    if Path(full_path).exists():
        raise Exception("File exists {}".format(full_path))

    with open(full_path, "w") as f:
        f.write(json.dumps(sorted_d, indent=4, sort_keys=False))


def extract_impact_assessments_from_zip_file(filepath: str) -> List[ImpactAssessment]:
    input_zip_file = Path(filepath)

    if not input_zip_file.exists():
        raise FileNotFoundError(f"File {input_zip_file} not found.")

    logger.info(f"Loading '{input_zip_file.name}'")
    zf = zipfile.ZipFile(input_zip_file)

    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)
        input_folder = Path(tempdir)
        # if validate_hestia_fileh_header: # todo

        recalculated_folder = Path(os.path.join(input_folder, "recalculated", "ImpactAssessment"))

        if not recalculated_folder.exists():
            raise FileNotFoundError(f"File {input_zip_file} does not contain a 'recalculated' folder.")

        impact_assessments: List[ImpactAssessment] = []
        for name in recalculated_folder.iterdir():
            if name.suffix == '.jsonld':
                try:
                    target_impactassessment = load_hestia_model_from_file(input_folder, name)
                except Exception as e:
                    logger.error(e)
                    raise e

                impact_assessments.append(target_impactassessment)

        return impact_assessments
