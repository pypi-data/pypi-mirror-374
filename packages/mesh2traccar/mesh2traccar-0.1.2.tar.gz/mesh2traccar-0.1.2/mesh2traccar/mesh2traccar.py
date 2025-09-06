import paho.mqtt.client as mqtt
import requests
import json
import configparser
import logging
from datetime import datetime, timezone
import uuid
import os
import pkg_resources

# Set up logging with fallback to local directory
log_file_system = '/var/log/mesh2traccar/mesh2traccar.log'
log_file_local = 'mesh2traccar.log'
log_file = log_file_system

# Check if system log directory is writable, fallback to local
if not os.path.exists(os.path.dirname(log_file_system)) or not os.access(os.path.dirname(log_file_system), os.W_OK):  # noqa: E501
    log_file = log_file_local
    print(f'System log path {log_file_system} not writable, falling back to {log_file_local}')  # noqa: E501

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load configuration with fallbacks: system, package, local
config = configparser.ConfigParser()
config_file_system = '/etc/mesh2traccar/mesh2traccar.conf'
config_file_package = pkg_resources.resource_filename(
    'mesh2traccar', 'mesh2traccar.conf')
config_file_local = 'mesh2traccar.conf'

# Try system, then package, then local config file
if os.path.exists(config_file_system):
    config_file = config_file_system
elif os.path.exists(config_file_package):
    config_file = config_file_package
elif os.path.exists(config_file_local):
    config_file = config_file_local
else:
    logger.error(f'Configuration file not found in {config_file_system},{config_file_package}, or {config_file_local}')  # noqa: E501
    exit(1)

logger.info(f'Using configuration file: {config_file}')
config.read(config_file)

# MQTT configuration
MQTT_BROKER = config['mqtt'].get('broker', 'localhost')
MQTT_PORT = config['mqtt'].getint('port', 1883)
MQTT_USERNAME = config['mqtt'].get('username', '')
MQTT_PASSWORD = config['mqtt'].get('password', '')
MQTT_CLIENT_ID = f"{config['mqtt'].get('client_id_prefix', 'mesh2traccar')}-{uuid.uuid4()}"  # noqa: E501
MQTT_TOPIC_SUB = config['mqtt'].get('topic_sub', 'msh/ANZ/2/json/LongFast/+')

# Traccar configuration
TRACCAR_URL = config['traccar'].get('url', 'http://localhost:5055')
TRACCAR_DEVICE_ID = config['traccar'].get('device_id', 'mesh2traccar')
TRACCAR_API_KEY = config['traccar'].get('api_key', '')

# Callback when the client connects to the MQTT broker


def on_connect(client, userdata, flags, reason_code, properties):
    logger.info(f'Connected to MQTT broker with code {reason_code}')
    # Subscribe to the Meshtastic JSON topic
    try:
        client.subscribe(MQTT_TOPIC_SUB, qos=1)
        logger.info(f'Subscribed to topic: {MQTT_TOPIC_SUB}')
    except Exception as e:
        logger.error(f'Failed to subscribe to topic {MQTT_TOPIC_SUB}: {e}')

# Callback when a message is received from the MQTT broker


def on_message(client, userdata, msg):
    try:
        # Decode the JSON payload
        payload = json.loads(msg.payload.decode('utf-8'))
        logger.info(f'Received message: {payload}')

        # Check if the message is a position message
        if payload.get('type') == 'position':
            position = payload.get('payload', {})
            # Convert integer coordinates to decimal degrees
            latitude = position.get('latitude_i') / 1e7 if position.get('latitude_i') is not None else None  # noqa: E501
            longitude = position.get('longitude_i') / 1e7 if position.get('longitude_i') is not None else None  # noqa: E501
            altitude = position.get('altitude')  # Optional
            timestamp = position.get('time') or payload.get(
                'timestamp')  # Prefer payload.time
            # Format 'from' field, fallback to TRACCAR_DEVICE_ID
            from_id = payload.get('from')
            device_id = f"!{format(from_id, 'x')}" if from_id is not None else TRACCAR_DEVICE_ID  # noqa: E501

            # Validate required fields and ranges
            if (latitude is not None and longitude is not None and timestamp is not None and  # noqa: E501
                    -90 <= latitude <= 90 and -180 <= longitude <= 180):
                # Convert timestamp to ISO 8601 format with UTC timezone
                try:
                    timestamp_iso = datetime.fromtimestamp(
                        timestamp, tz=timezone.utc).isoformat()
                except (ValueError, TypeError) as e:
                    logger.error(f'Invalid timestamp {timestamp}: {e}')
                    return

                # Prepare Traccar-compatible parameters (OsmAnd protocol)
                params = {
                    'id': device_id,
                    'timestamp': timestamp_iso,
                    'lat': latitude,
                    'lon': longitude,
                    'altitude': altitude if altitude is not None else 0,
                    'speed': 0,  # Meshtastic typically doesn't include speed
                    'bearing': 0  # Optional, set to 0
                }

                # Add API key if provided
                headers = {}
                if TRACCAR_API_KEY:
                    headers['Authorization'] = f'Bearer {TRACCAR_API_KEY}'

                # Send data to Traccar
                try:
                    # Log the request URL for debugging
                    request_url = requests.Request(
                        'GET', TRACCAR_URL, params=params).prepare().url
                    logger.info(f'Sending to Traccar: {request_url}')
                    response = requests.get(
                        TRACCAR_URL, params=params, headers=headers)
                    if response.status_code == 200:
                        logger.info(f'Successfully sent to Traccar: {params}')
                    else:
                        logger.error(f'Failed to send to Traccar: {response.status_code} {response.text}')  # noqa: E501
                except requests.RequestException as e:
                    logger.error(f'Error sending to Traccar: {e}')
            else:
                logger.warning(f'Invalid position data: lat={latitude}, lon={longitude}, timestamp={timestamp}')  # noqa: E501
        else:
            logger.info('Message is not a position message')
    except json.JSONDecodeError:
        logger.error('Failed to decode JSON payload')
    except Exception as e:
        logger.error(f'Error processing message: {e}')


def main():
    # Initialize MQTT client with clean session
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, clean_session=True,
                         protocol=mqtt.MQTTv311,
                         callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Enable automatic reconnection
    client.reconnect_delay_set(min_delay=1, max_delay=120)

    # Connect to MQTT broker
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    except Exception as e:
        logger.error(f'Failed to connect to MQTT broker: {e}')
        return

    # Start the MQTT loop
    logger.info('Starting MQTT client...')
    client.loop_forever()


if __name__ == '__main__':
    main()
