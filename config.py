import json
import logging


logging.basicConfig(filename="log.log", level=logging.INFO)

# Load config.json
with open("./configs/config.json", "r") as config:
    CONFIGS = json.load(config)

CUBA_URL = CONFIGS["CUBA_URL"]
TB_GATEWAY_TOKEN = CONFIGS["TB_GATEWAY_TOKEN"]
TB_TOTALS_DEVICE_NAME = CONFIGS["TB_TOTALS_DEVICE_NAME"]
TB_CLIENT_ID = CONFIGS["TB_CLIENT_ID"]
TB_DEVICE_PROFILE = CONFIGS["TB_DEVICE_PROFILE"]

PING_COUNT = CONFIGS["PING_COUNT"]
PING_INTERVAL = CONFIGS["PING_INTERVAL"]

# Load cameras.json
with open("./configs/cameras.json", "r") as cameras_config:
    CAMERAS = json.load(cameras_config)

DEVICES_COUNT = len(CAMERAS)

logging.info(f"Импортировано камер: {DEVICES_COUNT}")
