import logging
import sys
import re

class SensitiveFilter(logging.Filter):
    """Filters out potential tokens and API keys from logs"""
    PATTERNS = [
        re.compile(r'(ghp_[a-zA-Z0-9]{36})'),
        re.compile(r'(github_pat_[a-zA-Z0-9_]{82})'),
        re.compile(r'(AIza[0-9A-Za-z-_]{35})'),
        re.compile(r'(sk-[a-zA-Z0-9]{20,})'),
        re.compile(r'(Bearer\s+)[a-zA-Z0-9._-]+', re.IGNORECASE),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern in self.PATTERNS:
                record.msg = pattern.sub(r'[REDACTED_SECRET]', record.msg)
        return True

def setup_logging():
    logger = logging.getLogger("autoryx")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveFilter())
        logger.addHandler(handler)
        
    return logger

logger = setup_logging()
