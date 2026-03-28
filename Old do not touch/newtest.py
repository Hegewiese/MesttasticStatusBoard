#!/usr/bin/env python3
"""
Meshtastic Bluetooth Scanner & Connector
Scannt verfügbare Nodes, lässt den Nutzer eine auswählen,
zeigt Basisdaten an und sendet eine Nachricht.
"""

import sys
import time

try:
    import meshtastic
    import meshtastic.ble_interface
    from meshtastic import mesh_pb2
except ImportError:
    print("❌ Meshtastic ist nicht installiert.")
    print("   Installiere es mit: pip install meshtastic")
    sys.exit(1)

try:
    from bleak import BleakScanner
    import asyncio
except ImportError:
    print("❌ Bleak (BLE-Bibliothek) ist nicht installiert.")
    print("   Installiere es mit: pip install bleak")
    sys.exit(1)


TARGET_MAC = "E6:63:E5:E8:AB:07"


# ─────────────────────────────────────────────
#  1. Bluetooth-Scan
# ─────────────────────────────────────────────

async def scan_ble_devices(timeout: float = 10.0) -> list[dict]:
    """Scannt nach BLE-Geräten und gibt eine Liste zurück."""
    print(f"\n🔍 Scanne nach Bluetooth-Geräten ({timeout:.0f} Sekunden) ...\n")
    devices = await BleakScanner.discover(timeout=timeout)

    results = []
    for d in devices:
        results.append({
            "name": d.name or "(kein Name)",
            "address": d.address,
            "rssi": d.rssi if hasattr(d, "rssi") else "?",
        })

    # Meshtastic-Geräte zuerst, dann alphabetisch
    results.sort(key=lambda x: (
        0 if "meshtastic" in x["name"].lower() or x["address"] == TARGET_MAC else 1,
        x["name"]
    ))
    return results


def select_device(devices: list[dict]) -> dict | None:
    """Lässt den Nutzer ein Gerät aus der Liste auswählen."""
    if not devices:
        print("❌ Keine Bluetooth-Geräte gefunden.")
        return None

    print("─" * 55)
    print(f"{'Nr':>3}  {'Name':<28} {'Adresse':<20} RSSI")
    print("─" * 55)

    for i, d in enumerate(devices, start=1):
        marker = " ◀ Ziel" if d["address"].upper() == TARGET_MAC.upper() else ""
        print(f"{i:>3}  {d['name']:<28} {d['address']:<20} {d['rssi']}{marker}")

    print("─" * 55)

    while True:
        try:
            choice = input("\nGerät-Nummer eingeben (oder 0 zum Beenden): ").strip()
            idx = int(choice)
            if idx == 0:
                return None
            if 1 <= idx <= len(devices):
                return devices[idx - 1]
            print(f"  Bitte eine Zahl zwischen 1 und {len(devices)} eingeben.")
        except ValueError:
            print("  Ungültige Eingabe – bitte eine Zahl eingeben.")


# ─────────────────────────────────────────────
#  2. Verbinden & Basisdaten anzeigen
# ─────────────────────────────────────────────

def connect_and_show_info(address: str) -> meshtastic.ble_interface.BLEInterface | None:
    """Verbindet mit der Node per BLE und gibt Basisdaten aus."""
    print(f"\n🔗 Verbinde mit {address} ...")

    try:
        iface = meshtastic.ble_interface.BLEInterface(address)
        time.sleep(3)  # Verbindung stabilisieren
    except Exception as e:
        print(f"❌ Verbindung fehlgeschlagen: {e}")
        return None

    print("\n✅ Verbunden!\n")
    print("=" * 50)
    print("  📡 NODE BASISDATEN")
    print("=" * 50)

    try:
        info = iface.getMyNodeInfo()
        if info:
            print(f"  Node-ID       : {info.get('num', 'N/A')}")
            user = info.get("user", {})
            print(f"  Name          : {user.get('longName', 'N/A')}")
            print(f"  Kurzname      : {user.get('shortName', 'N/A')}")
            print(f"  Hardware      : {user.get('hwModel', 'N/A')}")
            print(f"  MAC / ID      : {user.get('id', 'N/A')}")
    except Exception as e:
        print(f"  (Node-Info nicht verfügbar: {e})")

    try:
        nodes = iface.nodes
        if nodes:
            print(f"\n  Bekannte Nodes im Mesh: {len(nodes)}")
            for nid, node in list(nodes.items())[:5]:
                u = node.get("user", {})
                print(f"    • {u.get('longName', nid):<20} [{nid}]")
            if len(nodes) > 5:
                print(f"    … und {len(nodes) - 5} weitere")
    except Exception as e:
        print(f"  (Node-Liste nicht verfügbar: {e})")

    try:
        pos = iface.localNode.localConfig
        print(f"\n  Kanal-Preset  : {pos}")
    except Exception:
        pass

    print("=" * 50)
    return iface


# ─────────────────────────────────────────────
#  3. Nachricht senden
# ─────────────────────────────────────────────

def send_message(iface: meshtastic.ble_interface.BLEInterface, message: str, dest: str) -> None:
    """Sendet eine Textnachricht an eine bestimmte Node."""
    print(f'\n📨 Sende Nachricht "{message}" an {dest} ...')

    try:
        iface.sendText(message, destinationId=dest)
        time.sleep(1)
        print("✅ Nachricht gesendet!")
    except Exception as e:
        print(f"❌ Senden fehlgeschlagen: {e}")


# ─────────────────────────────────────────────
#  Hauptprogramm
# ─────────────────────────────────────────────

def main():
    print("╔══════════════════════════════════════╗")
    print("║   Meshtastic BLE Connect Tool        ║")
    print("╚══════════════════════════════════════╝")

    # Scan
    devices = asyncio.run(scan_ble_devices(timeout=10.0))

    if not devices:
        print("\n❌ Keine Geräte gefunden. Prüfe, ob Bluetooth aktiv ist.")
        sys.exit(1)

    print(f"\n✔  {len(devices)} Gerät(e) gefunden.\n")

    # Auswahl
    selected = select_device(devices)
    if selected is None:
        print("\n👋 Abgebrochen.")
        sys.exit(0)

    print(f"\n➡  Ausgewählt: {selected['name']}  [{selected['address']}]")

    # Verbinden
    iface = connect_and_show_info(selected["address"])
    if iface is None:
        sys.exit(1)

    # Nachricht senden
    send_message(iface, "HEHO", dest=TARGET_MAC)

    # Verbindung trennen
    print("\n🔌 Trenne Verbindung ...")
    try:
        iface.close()
    except Exception:
        pass
    print("✅ Fertig.")


if __name__ == "__main__":
    main()