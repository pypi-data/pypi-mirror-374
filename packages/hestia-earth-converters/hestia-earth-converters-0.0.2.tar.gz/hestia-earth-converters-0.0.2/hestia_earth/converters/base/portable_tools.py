import logging
from werkzeug.utils import secure_filename as werkzeug_secure_filename

logger = logging.getLogger(__name__)


def secure_filename(input_str: str) -> str:
    new_str = werkzeug_secure_filename(
        input_str.replace("<", "_smaller_than_").replace(">", "_larger_than_").replace("&", "_and_"))

    return new_str


def _common_name_glo(process_openlca_uuid: str, product_name: str) -> str:
    return secure_filename(process_openlca_uuid + "_" + product_name).replace("__", "_")
