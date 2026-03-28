#!/home/wdr/.local/share/pipx/venvs/meshtastic/bin/python3
import meshtastic
import meshtastic.ble_interface
from pubsub import pub
import time
import subprocess
import re

def scan_ble_devices():
    """Scan for available BLE devices and return a list."""
    print("🔍 Scanne nach BLE-Geräten...")
    devices = []
    
    try:
        # Verwende meshtastic --ble-scan um Meshtastic-Geräte zu finden
        result = subprocess.run(
            ["meshtastic", "--ble-scan", "--timeout", "10"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                line = line.strip()
                if line and ('meshtastic' in line.lower() or 'ble' in line.lower() or '!' in line):
                    # Extrahiere MAC-Adresse
                    mac_pattern = r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
                    match = re.search(mac_pattern, line)
                    if match:
                        mac_address = match.group(0)
                        devices.append({
                            'address': mac_address,
                            'info': line
                        })
                    else:
                        # Versuche, andere Identifikatoren zu finden
                        devices.append({
                            'address': line.split()[0] if line.split() else line,
                            'info': line
                        })
        
        if not devices:
            print("⚠ Keine BLE-Geräte gefunden. Stelle sicher, dass:")
            print("  1. Meshtastic-Gerät eingeschaltet ist")
            print("  2. BLE aktiviert ist")
            print("  3. Gerät in Reichweite ist")
            return None
        
        return devices
        
    except Exception as e:
        print(f"⚠ Fehler beim Scannen: {e}")
        return None

def select_device(devices):
    """Lasse den Benutzer ein Gerät auswählen."""
    print("\n📱 Gefundene BLE-Geräte:")
    for i, device in enumerate(devices, 1):
        print(f"{i}. {device['info']}")
    
    while True:
        try:
            choice = input("\nWähle ein Gerät (Nummer) oder 'q' zum Beenden: ").strip()
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(devices):
                return devices[index]['address']
            else:
                print(f"⚠ Ungültige Auswahl. Bitte 1-{len(devices)} eingeben.")
        except ValueError:
            print("⚠ Bitte eine Zahl eingeben.")
        except KeyboardInterrupt:
            return None

def on_receive(packet, interface):
    try:
        from_id = packet.get("fromId", "unknown")
        to_id = packet.get("toId", "unknown")
        decoded = packet.get("decoded", {})
        msg = decoded.get("text", None)
        portnum = decoded.get("portnum", "unknown")
        snr = packet.get("rxSnr", "?")
        rssi = packet.get("rxRssi", "?")
        
        # DEBUG: Zeige alle verfügbaren Felder im Paket
        # print(f"DEBUG - Packet keys: {list(packet.keys())}")
        # print(f"DEBUG - Decoded keys: {list(decoded.keys())}")
        
        # Versuche, Kanalinformation aus verschiedenen Feldern zu extrahieren
        channel = "unknown"
        
        # 1. Versuche channel aus dem Hauptpaket
        if "channel" in packet:
            channel = packet["channel"]
        # 2. Versuche channelIndex aus decoded
        elif "channelIndex" in decoded:
            channel = decoded["channelIndex"]
        # 3. Versuche channelId aus decoded
        elif "channelId" in decoded:
            channel = decoded["channelId"]
        # 4. Versuche rxChannel aus dem Paket
        elif "rxChannel" in packet:
            channel = packet["rxChannel"]
        
        # Bestimme den Kanalnamen basierend auf der Kanalnummer
        channel_names = {
            0: "Primär",
            1: "Kanal 1",
            2: "Kanal 2",
            3: "Kanal 3",
            4: "Kanal 4",
            5: "Kanal 5",
            6: "Kanal 6",
            7: "Kanal 7",
            8: "Kanal 8",
            "PRIMARY": "Primär",
            "SECONDARY": "Sekundär",
            "ADMIN": "Admin",
            "unknown": "Unbekannt"
        }
        
        # Konvertiere channel zu String für den Lookup
        channel_str = str(channel)
        channel_name = channel_names.get(channel, channel_names.get(channel_str, f"Kanal {channel}"))
        
        # Bestimme die Quelle der Nachricht (MQTT oder Funk)
        rx_source = packet.get("rxSource", "unknown")
        
        # Übersetze die Quelle in lesbaren Text
        source_map = {
            "LOCAL": "Funk (lokal)",
            "MQTT": "MQTT",
            "BLE": "Bluetooth",
            "SERIAL": "Seriell",
            "NONE": "Unbekannt",
            "unknown": "Unbekannt"
        }
        
        source = source_map.get(rx_source, rx_source)
        
        if msg:
            print(f"💬 [{from_id} → {to_id}] Kanal:{channel_name} | Quelle:{source} | "
                  f"\"{msg}\" | SNR:{snr} RSSI:{rssi}")
        else:
            print(f"📦 [{from_id} → {to_id}] Kanal:{channel_name} | Quelle:{source} | "
                  f"type:{portnum} | SNR:{snr} RSSI:{rssi}")
    except Exception as e:
        print(f"⚠ Error: {e}")
        # Zeige das komplette Paket für Debugging
        print(f"DEBUG - Full packet: {packet}")

def on_connection(interface, topic=pub.AUTO_TOPIC):
    node = interface.getMyUser()
    print("=" * 60)
    print(f"✅ Verbunden mit Meshtastic Node")
    print(f"   Name     : {node.get('longName', '?')}")
    print(f"   Kurzname : {node.get('shortName', '?')}")
    print(f"   ID       : {node.get('id', '?')}")
    print(f"   Hardware : {node.get('hwModel', '?')}")
    print("=" * 60)
    print("👂 Höre auf Pakete... (Strg+C zum Beenden)\n")

def main():
    print("🚀 Meshtastic BLE Listener")
    print("=" * 40)
    
    # 1. Scanne nach verfügbaren Geräten
    devices = scan_ble_devices()
    if not devices:
        print("❌ Keine Geräte gefunden. Beende...")
        return
    
    # 2. Lasse Benutzer ein Gerät auswählen
    selected_address = select_device(devices)
    if not selected_address:
        print("👋 Beendet.")
        return
    
    print(f"\n🔗 Versuche Verbindung zu: {selected_address}")
    
    # 3. Event-Handler registrieren
    pub.subscribe(on_receive, "meshtastic.receive")
    pub.subscribe(on_connection, "meshtastic.connection.established")
    
    # 4. Verbindung herstellen
    try:
        iface = meshtastic.ble_interface.BLEInterface(selected_address)
        
        # 5. Hauptschleife
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Verbindung getrennt.")
            iface.close()
            
    except Exception as e:
        print(f"❌ Verbindungsfehler: {e}")
        print("Mögliche Lösungen:")
        print("1. Gerät neu starten")
        print("2. Bluetooth auf Host neu starten")
        print("3. Andere Adresse ausprobieren")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Programm beendet.")
    except Exception as e:
        print(f"\n💥 Unerwarteter Fehler: {e}")
