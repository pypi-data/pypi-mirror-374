import logging
import sys
import os

# Create logs directory if it doesn't exist
log_dir = "/tmp"
os.makedirs(log_dir, exist_ok=True)

# Configure logging with both stdout and file handlers
handlers = [
    logging.StreamHandler(sys.stdout),
    logging.FileHandler(f"{log_dir}/marcas_bot.log", mode='a')
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=handlers,
)

logger = logging.getLogger("marcas_bot")
logger.setLevel(logging.DEBUG)

# Log startup message
logger.info("=== MARCAS_BOT LOGGER INITIALIZED ===")
logger.info(f"Logging to: {log_dir}/marcas_bot.log")
