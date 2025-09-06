import os
import json
import pytest
from pathlib import Path
from tests.utils import fixtures_path

from hestia_earth.converters.base.pydantic_models.hestia.hestia_file_tools import (
    sort_schema_dict,
    clean_impact_data
)
from hestia_earth.converters.base.pydantic_models.hestia import ImpactAssessment
from hestia_earth.converters.base.pydantic_models.hestia.hestia_schema_tools import recursively_expand_all_refs
from hestia_earth.converters.simapro.hestia_to_simapro import (
    hestia_to_simapro_converter_from_recalculated_impact_assessment
)

fixtures_folder = os.path.join(fixtures_path, 'converters', 'simapro')


@pytest.mark.parametrize(
    'process_type',
    ['System', 'Unit process']
)
def test_hestia_to_simapro_converter_oilPalmFruit_indonesia_latest_aggregation(process_type: str):
    node_id = 'oilPalmFruit-indonesia-2010-2025-20250812'
    target_folder_path = Path(os.path.join(fixtures_folder, 'hestia', node_id))
    impact_assessment_recalculated_file = Path(
        os.path.join(target_folder_path, 'data', 'recalculated', 'ImpactAssessment', f"{node_id}.jsonld")
    )

    with open(impact_assessment_recalculated_file) as f:
        data = json.load(f)

    expected_filename = f"expected_{process_type.lower().replace(' ', '_')}.csv"
    with open(os.path.join(target_folder_path, expected_filename), encoding='windows-1252') as f:
        expected = f.read().splitlines()

    data = recursively_expand_all_refs(data, os.path.join(target_folder_path, 'data'))
    data = clean_impact_data(data)
    data = sort_schema_dict(data, current_path=data["@type"])

    impact_assessment = ImpactAssessment.model_validate(data)
    new_simapro_pydantic_obj = hestia_to_simapro_converter_from_recalculated_impact_assessment(
        impact_assessment,
        mapping_files_directory=Path(os.path.join(fixtures_path, '..', '..', 'hestia-flowmaps')),
        process_type=process_type,
    )
    output = new_simapro_pydantic_obj.model_dump(exclude_unset=False, exclude_none=False, mode="json")

    e1 = "\n".join(expected)
    o1 = "\n".join(output).replace("\\n", "")
    assert e1 == o1
