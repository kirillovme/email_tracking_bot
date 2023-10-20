import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='{%(pathname)s:%(lineno)d} %(asctime)s - %(levelname)s - %(message)s'
)
