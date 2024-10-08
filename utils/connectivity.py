import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from requests.exceptions import ConnectionError
from utils.helper import load_config
import subprocess


def send_data_via_internet(rain, solar_V, battery_V, solar_I, battery_I: float) -> bool:
    """
    function to write data to influxdb using internet
    """
    try:
        # loading device details
        device_config = load_config("config.yaml")
        name = device_config["device_name"]
        location = device_config["device_location"]
        # loading influxDB credentials
        influxdb_config = load_config("influxdb_api.yaml")
        url = influxdb_config["url"]
        org = influxdb_config["org"]
        bucket = influxdb_config[name]["bucket"]
        token = influxdb_config[name]["token"]
        # creating an object of influxdb_client
        client = influxdb_client.InfluxDBClient(
            url=url, token=token, org=org, timeout=30_000
        )
        write_api = client.write_api(write_options=SYNCHRONOUS)
        p = (
            influxdb_client.Point("acoustic raingauge")
            .tag("location", location)
            .field("rain", rain)
            .field("solar voltage", solar_V)
            .field("battery voltage", battery_V)
            .field("solar current", solar_I)
            .field("battery current", battery_I)
        )

        write_api.write(bucket=bucket, org=org, record=p)
        client.close()
        return True
    except ConnectionError as e:
        print(f"Connection to InfluxDB failed: {e}")
        return False


def send_data_via_lorawan(mm_hat, solar_V, battery_V, solar_I, battery_I):
    """
    function to write data to chirpstack server using LoRa
    """
    # loading device details
    device_config = load_config("config.yaml")
    name = device_config["device_name"]
    # loading lora keys
    lorawan_config = load_config("lorawan_keys.yaml")
    dev_addr = lorawan_config[name]["dev_addr"]
    nwk_skey = lorawan_config[name]["nwk_skey"]
    app_skey = lorawan_config[name]["app_skey"]
    led_flag = lorawan_config["led_flag"]
    success = False
    while not success:
        try:
            result = subprocess.call(
                [
                    "ttn-abp-send",
                    dev_addr,
                    nwk_skey,
                    app_skey,
                    str(mm_hat),
                    str(solar_V),
                    str(battery_V),
                    str(solar_I),
                    str(battery_I),
                    str(led_flag),
                ]
            )

            if result == 0:
                success = True
            else:
                print("Subprocess call failed, retrying...")
        except subprocess.CalledProcessError as e:
            print(f"Error during subprocess call: {e}. Retrying...")
