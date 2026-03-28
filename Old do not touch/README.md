# Meshtastic Device Discovery - main.py

## What main.py Does

`main.py` is a comprehensive Meshtastic device discovery tool that performs multiple scanning methods to find and identify Meshtastic devices on your system.

### Key Functions:

1. **Meshtastic Installation Verification**
   - Checks if Meshtastic CLI is installed
   - Displays the installed version
   - Provides installation instructions if not found

2. **Bluetooth Capability Check**
   - Tests if Bluetooth is available on the system
   - Verifies Bluetooth service status
   - Attempts to start Bluetooth if not running

3. **Multi-Method Device Discovery**
   The script uses 4 different methods to find devices:
   
   a) **BLE Device Scanning**
      - Scans for Bluetooth Low Energy devices
      - Shows both connected and available devices
      - Uses both `bluetoothctl` and Meshtastic's own BLE scan
   
   b) **Auto-Detected Devices**
      - Runs `meshtastic --info` to find auto-detected devices
      - Parses device information from the output
   
   c) **Serial Port Scanning**
      - Checks common serial ports (/dev/ttyUSB*, /dev/ttyACM*)
      - Identifies potential USB-connected Meshtastic devices
   
   d) **Network Node Discovery**
      - Runs `meshtastic --nodes` to find nodes in the network
      - Shows network topology information

4. **Device Information Processing**
   - Parses device information from various sources
   - Removes duplicate devices based on identifiers
   - Formats information for clear display

5. **User-Friendly Output**
   - Color-coded output for better readability
   - Formatted device listings
   - Clear status indicators

### Output Example:
```
Found 3 device(s):
======================================================================

Device 1:
  Type: Bluetooth
  Name: Meshtastic T-Beam
  Address: E6:63:E5:E8:AB:07
  Connection: Connected
  Method: bluetoothctl
  Status: Active

Device 2:
  Type: USB Serial
  Port: /dev/ttyUSB0
  Method: Port scan
  Status: Port available

Device 3:
  Type: Network Node
  Info: !96f3cb7e TestNode
  Method: --nodes command
  Status: In network
```

## Usage

```bash
python3 main.py
```

## Requirements
- Python 3.x
- Meshtastic CLI (`pip install meshtastic`)
- Bluetooth support (for BLE scanning)
- Linux system (for serial port access)

## Error Handling
- Handles missing Meshtastic installation
- Manages Bluetooth connection issues
- Gracefully handles timeouts
- Provides helpful error messages

## Use Cases
- **Device Inventory**: Discover all Meshtastic devices on your system
- **Connection Testing**: Verify Bluetooth and serial connections
- **Network Monitoring**: Check which nodes are active in your network
- **Debugging**: Identify connection or discovery issues

## Related Files
- `test.py`: BLE listener for receiving and displaying Meshtastic messages

## Notes
- The script is designed to be non-intrusive
- All discovery methods have timeout protection
- No permanent connections are established (only discovery)
- Safe to run on systems with multiple Meshtastic devices