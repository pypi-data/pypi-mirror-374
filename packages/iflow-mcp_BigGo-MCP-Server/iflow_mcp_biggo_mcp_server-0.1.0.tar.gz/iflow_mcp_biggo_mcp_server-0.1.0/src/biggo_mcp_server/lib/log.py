from logging import getLogger
from ..types.setting import LogLevel

logger = getLogger(__name__)


def setup_logging(log_level: LogLevel = LogLevel.INFO):
    logger = getLogger("biggo_mcp_server")
    logger.setLevel(log_level.value)
    msg = "BigGo MCP Server logging setup, log_level: %s"
    match log_level:
        case LogLevel.DEBUG:
            logger.debug(msg, log_level)
        case LogLevel.INFO:
            logger.info(msg, log_level)
        case LogLevel.WARNING:
            logger.warning(msg, log_level)
        case LogLevel.ERROR:
            logger.error(msg, log_level)
        case LogLevel.CRITICAL:
            logger.critical(msg, log_level)
