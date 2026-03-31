# KAPUTT, DO NOT USE
# Meshtastic Status Board

A Linux CLI tool for managing and interacting with [Meshtastic](https://meshtastic.org/) LoRa mesh radio nodes. It discovers nearby devices, maintains a list of known nodes, tests connections (including BLE pairing), and can send scheduled messages through a node.

## What it does

- **Device discovery** — scans for Meshtastic devices via BLE, serial ports (`/dev/ttyUSB*`, `/dev/ttyACM*`), and Meshtastic's own auto-detection
- **Node management** — reads/writes a plain-text `nodes` file with your known devices and their labels
- **Connection testing** — connects to a node via `meshtastic --info`, handles BLE pairing through `bluetoothctl`, and sends a timestamped test message
- **Scheduled messaging** — sends a message through a selected node every minute for a configurable duration
- **System status** — reports Meshtastic CLI version, Bluetooth service state, and installed Python packages

## Quick start

```bash
chmod +x setup.sh run.sh
./setup.sh      # creates venv and installs dependencies
./run.sh        # launches the interactive menu
```

## Menu options

| # | Option | Status |
|---|--------|--------|
| 1 | Scan for devices | Working |
| 2 | Show known nodes | Working |
| 3 | Test connection to known nodes | Working |
| 4 | Monitor messages | Not yet implemented |
| 5 | Check system status | Working |
| 6 | Update nodes list (add discovered devices) | Working |
| 7 | Send message to node every 1 min | Working |
| 0 | Exit | — |

## Nodes file

The `nodes` file lists your known Meshtastic devices, one per line:

```
# Format: Address  # Label

E6:63:E5:E8:AB:07   # HEHO_ab07            — BLE MAC address
C7:C8:96:F3:CB:7E   # HEMO_cb7e Mobil      — BLE MAC address
/dev/ttyUSB0        # USB connected device  — serial port
!12345678           # Node ID format
192.168.1.100:4403  # TCP/IP connection
```

Lines starting with `#` are comments and are ignored. New devices found by a scan can be appended automatically via menu option 6.

## Prerequisites

- Linux with Bluetooth support (`bluetoothctl` / `bluez`)
- Python 3.7+
- Meshtastic CLI (`pip install meshtastic`)

### Serial port permissions

If serial devices show "Permission denied":

```bash
sudo usermod -a -G dialout $USER
# log out and back in
```

### Bluetooth service

```bash
sudo systemctl enable --now bluetooth
```

## Project layout

```
main.py                 # main interactive application
connectAndSendNews.py   # standalone installation checker
nodes                   # known nodes configuration
setup.sh                # creates venv and installs dependencies
run.sh                  # activates venv and starts main.py
Old do not touch/       # legacy test scripts (not used)
```

## Dependencies

Installed automatically by `setup.sh` from `requirements.txt`:

- `meshtastic` — Meshtastic Python library and CLI
- `pyserial` — serial port access

## Troubleshooting

**Virtual environment not found** — run `./setup.sh` first.

**BLE device not connecting** — the connection test flow will offer to pair via `bluetoothctl`. Common PINs for Meshtastic devices: `123456`, `000000`.

**No devices found** — confirm the device is powered on, Bluetooth is enabled on the host, and for serial devices that the cable is connected.
