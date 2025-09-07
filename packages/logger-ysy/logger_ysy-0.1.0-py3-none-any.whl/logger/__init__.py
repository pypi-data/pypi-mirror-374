# 从core.py导出关键对象，用户导入时直接用
from .core import (
    logger as logger,
    set_default_config as set_default_config,
    get_logger as get_logger,
    DEFAULT_CONFIG as DEFAULT_CONFIG
)

# 导出常用日志级别（用户无需额外import logging）
from logging import (
    DEBUG as DEBUG,
    INFO as INFO,
    WARNING as WARNING,
    ERROR as ERROR,
    CRITICAL as CRITICAL
)

# 控制导入时的暴露内容（避免暴露内部细节）
__all__ = [
    "logger", "set_default_config", "get_logger", "DEFAULT_CONFIG",
    "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
]
