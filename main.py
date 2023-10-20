import config

import asyncio
import subprocess

import logging
from time import time

from tb_gateway_mqtt import TBGatewayMqttClient


logging.basicConfig(filename="log.log", level=logging.INFO)


# Create dictionary for previous values
devices_previous_connection_status = {}
for device in config.CAMERAS:
    deviceName = device["deviceName"]
    devices_previous_connection_status[deviceName] = None


async def connect_devices(
    gateway: TBGatewayMqttClient, devices: list, device_type: str = "default"
):
    for device in devices:
        gateway.gw_connect_device(device["deviceName"], device_type)
        await asyncio.sleep(0.0001)

    logging.info(f"{len(devices)} devices successfully connected")


async def disconnect_devices(gateway: TBGatewayMqttClient, devices: list):
    for device in devices:
        gateway.gw_disconnect_device(device["deviceName"])
        await asyncio.sleep(0.0001)


async def send_device_connection_status(
    gateway: TBGatewayMqttClient, deviceName: str, ip: str
):
    connection_status = 0
    try:
        # Ping device
        process = await asyncio.create_subprocess_exec(
            "ping",
            "-c",
            config.PING_COUNT,
            "-i",
            config.PING_INTERVAL,
            ip,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        await process.communicate()
        connection_status = 1 if process.returncode == 0 else 0

        # Send telemetry on connection status change
        if devices_previous_connection_status[deviceName] != connection_status:
            telemetry = {"online": connection_status}
            gateway.gw_send_telemetry(deviceName, telemetry)

            devices_previous_connection_status[deviceName] = connection_status
            global devices_connections_changed
            devices_connections_changed += 1

    except Exception as e:
        error_msg = f"Error in getting device {0} ({1}) connection: {2}"
        error_msg.format(deviceName, ip, e)
        logging.error(error_msg)

    return connection_status


async def main():
    global devices_previous_connection_status

    # Initialize gateway
    gateway = TBGatewayMqttClient(
        config.CUBA_URL, 1883, config.TB_GATEWAY_TOKEN, client_id=config.TB_CLIENT_ID
    )

    gateway.connect()
    logging.info(f"Gateway connected on {config.CUBA_URL}")

    # Connect devices
    await connect_devices(gateway, config.CAMERAS, device_type=config.TB_DEVICE_PROFILE)

    # Ping devices and send data to platform
    while True:
        # Initialize counter
        global devices_connections_changed
        devices_connections_changed = 0

        loop_st = time()
        try:
            # Create tasks
            tasks = []
            for device in config.CAMERAS:
                tasks.append(
                    send_device_connection_status(
                        gateway,
                        device["deviceName"],
                        device["IP"],
                    )
                )

            # Waiting for tasks execution
            results = await asyncio.gather(*tasks)

            # Count active devices
            total_devices = len(results)
            active_devices = sum(results)
            inactive_devices = total_devices - active_devices

            totals_telemetry = {
                "total devices": total_devices,
                "active devices": active_devices,
                "inactive devices": inactive_devices,
            }
            # Send totals to platform
            gateway.gw_send_telemetry(config.TB_TOTALS_DEVICE_NAME, totals_telemetry)
        except Exception as e:
            logging.critical(f"Error in main loop: {e}")

        loop_et = time()
        loop_exec_t = loop_et - loop_st
        print(f"Loop execution time: {loop_exec_t} seconds")
        print(f"Devices connections changed: {devices_connections_changed}")

    # Disconnect devices
    await disconnect_devices(gateway, config.CAMERAS)
    logging.info("Devices disconnected")

    # Disconnect gateway
    gateway.disconnect()
    logging.info("Gateway disconnected")


if __name__ == "__main__":
    asyncio.run(main())
