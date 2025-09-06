import click
import logging
import pprint
from pathlib import Path

from hestia_earth.converters.simapro.pydantic_models.util import load_csv_file_to_sima_pro_obj
# from openlca_to_hestia import open_lca_process_to_hestia_converter
from hestia_earth.converters.simapro.pydantic_models import SimaProProcessBlock

# from hestia_earth.converters.base.pydantic_models.openlca_schema_utils import validate_openlca_file, insert_referenced_product_system, \
#     insert_referenced_processes

log_levels = {1: logging.WARNING, 2: logging.ERROR, 3: logging.DEBUG}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option('--output', default=Path.cwd() / "output",
              prompt='Please specify an output folder or hit enter to accept the default > ')
@click.option('--mapping_files_directory', default=None, help='optional location of flowmap files')
@click.argument('input_sima_pro_csv_file')
@click.option('-v', '--verbose', count=True, help='Enables verbose mode.')
@click.option('-d', '--debug_file', is_flag=True, help='Outputs conversion logs to debug file.')
def main(output, input_sima_pro_csv_file, mapping_files_directory, verbose, debug_file):
    """
    test program to load a sima pro csv file
    """

    if verbose:
        logging.basicConfig(level=log_levels.get(verbose, logging.INFO))

    if debug_file:
        fh = logging.FileHandler(f"debug_log_{__name__}.log")
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

    input_sima_pro_csv_file = Path(input_sima_pro_csv_file)

    if not input_sima_pro_csv_file.exists():
        raise FileNotFoundError(f"File {input_sima_pro_csv_file} not found.")
    logger.info(f"Loading '{input_sima_pro_csv_file.name}'")

    new_simapro_pydantic_obj= load_csv_file_to_sima_pro_obj(input_sima_pro_csv_file)

    found_processes = [block for block in new_simapro_pydantic_obj.blocks if isinstance(block, SimaProProcessBlock)]

    logger.debug(f"Found {len(found_processes)} Process blocks in file:")

    for i, found_process in enumerate(found_processes):
        logger.info(f"Processing result {i + 1} of {len(found_processes)}: "
                    f"[{found_process.platformId}] aka '{found_process.name}'")
        pprint.pprint(found_process)


if __name__ == '__main__':
    main()
