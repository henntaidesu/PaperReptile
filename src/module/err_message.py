import sys
from src.module.log import log
logger = log()


def err(e):
    logger.write_log(f"Err Message:,{str(e)}")
    logger.write_log(f"Err Type:, {type(e).__name__}")
    _, _, tb = sys.exc_info()
    logger.write_log(f"Err Local:, {tb.tb_frame.f_code.co_filename}, {tb.tb_lineno}")
