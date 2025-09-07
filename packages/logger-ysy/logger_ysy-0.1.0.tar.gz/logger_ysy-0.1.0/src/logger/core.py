import logging
from pathlib import Path
from typing import Optional, Dict, Any

# --------------------------
# 全局默认配置（可被用户覆盖）
# --------------------------
DEFAULT_CONFIG: Dict[str, Any] = {
    "log_file": "logs/logger.log", # 默认日志文件路径
    "level": logging.INFO,  # 默认级别
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s", # 默认格式
    "file_encoding": "utf-8-sig", # 默认编码（兼容中文）
    "datefmt": "%Y-%m-%d %H:%M:%S"  # 默认时间格式
}

# 预创建的默认logger实例（即导即用的核心）
logger: logging.Logger = None

def get_logger(
    logger_name: str = __name__,
    log_file: Optional[str] = None,
    level: Optional[int] = None,
    log_format: Optional[str] = None,
    file_encoding: Optional[str] = None,
    datefmt: Optional[str] = None,
    force_reconfig: bool = False
) -> logging.Logger:
    """
    创建并配置日志实例（支持自定义配置，未传则用默认值）
    
    Args:
        logger_name: 日志实例名（默认当前模块名）
        log_file: 日志文件路径（默认：DEFAULT_CONFIG["log_file"]）
        level: 日志级别（默认：DEFAULT_CONFIG["level"]，支持logging.INFO等）
        log_format: 日志格式（默认：DEFAULT_CONFIG["log_format"]）
        file_encoding: 日志文件编码（默认：DEFAULT_CONFIG["file_encoding"]）
        datefmt: 时间格式（默认：DEFAULT_CONFIG["datefmt"]）
    
    Returns:
        logging.Logger: 配置好的日志实例
    """
    # 优先级：用户传参 > 默认配置
    log_file = log_file or DEFAULT_CONFIG['log_file']
    level = level or DEFAULT_CONFIG["level"]
    log_format = log_format or DEFAULT_CONFIG["log_format"]
    file_encoding = file_encoding or DEFAULT_CONFIG["file_encoding"]
    datefmt = datefmt or DEFAULT_CONFIG["datefmt"]
    
    # 创建logger实例（避免重复创建）
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.propagate = False # 禁止传递给根日志（避免重复输出）
    
    if force_reconfig or len(logger.handlers) == 0:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
    
    # 1. 配置日志格式器
    formatter = logging.Formatter(fmt=log_format, datefmt=datefmt)
    
    # 2. 配置文件Handler（自动创建日志目录）
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True) # 没有目录则创建
    file_handler = logging.FileHandler(log_file, encoding=file_encoding)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # 3. 配置控制台Handler（终端输出）
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)  # 添加文件处理器
    logger.addHandler(stream_handler)  # 添加控制台处理器
    
    return logger

def set_default_config(
    log_file: Optional[str] = None,
    level: Optional[int] = None,
    log_format: Optional[str] = None,
    file_encoding: Optional[str] = None,
    datefmt: Optional[str] = None
) -> None:
    """
    覆盖全局默认配置（后续调用get_logger()或使用默认logger都会生效）
    
    Args:
        同get_logger()，未传则不修改对应默认值
    """
    global DEFAULT_CONFIG, logger
    # 更新默认配置（只更新用户传了的参数）
    if log_file:
        DEFAULT_CONFIG['log_file'] = log_file
    if level:
        DEFAULT_CONFIG["level"] = level
    if log_format:
        DEFAULT_CONFIG["log_format"] = log_format
    if file_encoding:
        DEFAULT_CONFIG["file_encoding"] = file_encoding
    if datefmt:
        DEFAULT_CONFIG["datefmt"] = datefmt
    
    # 重新初始化默认logger（让新配置生效）
    logger = get_logger(logger_name="my_logger_defult", force_reconfig=True)
    
# 初始化默认logger（程序启动时执行，即导即用的基础）
set_default_config() # 加载默认配置并创建logger