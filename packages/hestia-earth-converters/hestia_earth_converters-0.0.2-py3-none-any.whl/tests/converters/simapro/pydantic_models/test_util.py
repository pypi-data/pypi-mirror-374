import os
from pathlib import Path
import pytest
from tests.utils import fixtures_path

from hestia_earth.converters.simapro.pydantic_models.util import load_csv_file_to_sima_pro_obj

fixtures_folder = os.path.join(fixtures_path, 'pydantic_models', 'simapro')


@pytest.mark.skip(reason="Loading file via bw_simapro_csv package currently broken")
def test_load_csv_file_to_sima_pro_obj():
    file_path = Path(os.path.join(fixtures_folder, 'schema_samples', 'Banana_WestIndies.CSV'))

    with open(file_path, encoding='sloppy-windows-1252') as f:
        expected = f.read().splitlines()

    new_simapro_pydantic_obj = load_csv_file_to_sima_pro_obj(file_path)

    output = new_simapro_pydantic_obj.model_dump(exclude_unset=True, exclude_none=True, mode="json")

    expected_str = "\n".join(expected)
    output_str = "\n".join(output).replace("\\n", "")
    assert expected_str == output_str
