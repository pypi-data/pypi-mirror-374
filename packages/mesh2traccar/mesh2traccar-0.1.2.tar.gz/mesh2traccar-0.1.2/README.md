# Mesh2Traccar

A Python application to forward Meshtastic MQTT location messages to a Traccar server.

## Installation

1. **Install the Package**:
   - **Option A: Via PyPI (Recommended)**:
     ```bash
     pip install mesh2traccar
     ```
   - **Option B: Via Git Clone** (for developers or custom versions):
     ```bash
     git clone https://gitlab.com/drid/mesh2traccar
     cd mesh2traccar
     pip install .
     ```
     **Note for Developers**: For local development, place `mesh2traccar.conf` in the current directory to use it instead of `/etc/mesh2traccar/mesh2traccar.conf`. Logs will be written to `./mesh2traccar.log` if `/var/log/mesh2traccar/` is not writable.

2. **Create a User and Group**:
   ```bash
   sudo groupadd mesh2traccar
   sudo useradd -r -g mesh2traccar -d /var/lib/mesh2traccar -s /sbin/nologin mesh2traccar
   ```

3. **Set Up Directories**:
   ```bash
   sudo mkdir -p /etc/mesh2traccar /var/lib/mesh2traccar /var/log/mesh2traccar
   sudo chown mesh2traccar:mesh2traccar /var/lib/mesh2traccar /var/log/mesh2traccar
   ```

4. **Copy Configuration File**:
   - For PyPI installation:
     ```bash
     sudo cp $(python -c "import pkg_resources; print(pkg_resources.resource_filename('mesh2traccar', 'mesh2traccar.conf'))") /etc/mesh2traccar/
     ```
   - For Git clone installation:
     ```bash
     sudo cp mesh2traccar.conf /etc/mesh2traccar/
     ```
   - Set permissions:
     ```bash
     sudo chown mesh2traccar:mesh2traccar /etc/mesh2traccar/mesh2traccar.conf
     sudo chmod 640 /etc/mesh2traccar/mesh2traccar.conf
     ```

5. **Edit Configuration**:
   Edit `/etc/mesh2traccar/mesh2traccar.conf` to set your MQTT and Traccar settings:
   - `mqtt.broker`: MQTT broker address.
   - `mqtt.port`: MQTT broker port (default 1883).
   - `mqtt.username` and `mqtt.password`: MQTT credentials (optional).
   - `mqtt.client_id_prefix`: Prefix for MQTT client ID.
   - `mqtt.topic_sub`: Meshtastic MQTT topic (e.g., `msh/ANZ/2/json/LongFast/+`).
   - `traccar.url`: Traccar server URL (e.g., `http://your-traccar-server:5055`).
   - `traccar.device_id`: Default device ID for Traccar.
   - `traccar.api_key`: Traccar API key (optional).

6. **Install Systemd Service**:
   - For PyPI installation:
     ```bash
     sudo cp $(python -c "import pkg_resources; print(pkg_resources.resource_filename('mesh2traccar', 'mesh2traccar.service'))") /etc/systemd/system/
     ```
   - For Git clone installation:
     ```bash
     sudo cp mesh2traccar.service /etc/systemd/system/
     ```
   - Enable the service:
     ```bash
     sudo systemctl daemon-reload
     sudo systemctl enable mesh2traccar.service
     ```

7. **Start the Service**:
   ```bash
   sudo systemctl start mesh2traccar.service
   ```

## Usage

- **Check Service Status**:
  ```bash
  sudo systemctl status mesh2traccar.service
  ```

- **View Logs**:
  ```bash
  tail -f /var/log/mesh2traccar/mesh2traccar.log
  ```

- **Stop or Restart**:
  ```bash
  sudo systemctl stop mesh2traccar.service
  sudo systemctl restart mesh2traccar.service
  ```

## Notes

- Ensure your MQTT broker and Traccar server are running and accessible.
- Register Meshtastic node IDs (e.g., `!2f8382cc`) in Traccar as device identifiers.
- If the `!` prefix causes issues, modify `mesh2traccar.py` to remove it:
  ```python
  device_id = format(from_id, 'x') if from_id is not None else TRACCAR_DEVICE_ID
  ```
- The software is licensed under the GNU General Public License v3 (GPLv3). See the `LICENSE` file for details.

## Troubleshooting

- Check `/var/log/mesh2traccar/mesh2traccar.log` (or `./mesh2traccar.log` for local development) for errors.
- Verify MQTT topic and Traccar URL in the configuration file.
- Ensure the `mesh2traccar` user has permissions to read `/etc/mesh2traccar/mesh2traccar.conf` (or `./mesh2traccar.conf` for development).

## License

This project is licensed under the GNU General Public License v3.0.