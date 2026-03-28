#!/usr/bin/env python3
"""
Einfacher Meshtastic Test
Testet die grundlegende Meshtastic-Funktionalität
"""

import sys
import time

def test_meshtastic_import():
    """Testet ob Meshtastic importiert werden kann."""
    try:
        import meshtastic
        print("✅ Meshtastic kann importiert werden")
        print(f"   Version: {meshtastic.__version__ if hasattr(meshtastic, '__version__') else 'Unbekannt'}")
        return True
    except ImportError as e:
        print(f"❌ Meshtastic Import fehlgeschlagen: {e}")
        print("   Bitte installieren: pip install meshtastic")
        return False

def test_ble_scan():
    """Testet BLE-Scanning."""
    try:
        import meshtastic
        from meshtastic import ble_interface
        
        print("\n🔍 Teste BLE-Scanning...")
        
        # Versuche einen kurzen BLE-Scan
        import subprocess
        result = subprocess.run(
            ["meshtastic", "--ble-scan", "--timeout", "5"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ BLE-Scan erfolgreich")
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                devices_found = 0
                for line in lines:
                    if line and line != "BLE scan finished":
                        print(f"   Gerät: {line}")
                        devices_found += 1
                
                if devices_found == 0:
                    print("   ⚠ Keine Geräte gefunden")
                else:
                    print(f"   📱 {devices_found} Gerät(e) gefunden")
            return True
        else:
            print(f"❌ BLE-Scan fehlgeschlagen: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ BLE-Scan Test fehlgeschlagen: {e}")
        return False

def test_serial_ports():
    """Testet verfügbare serielle Ports."""
    print("\n🔌 Teste serielle Ports...")
    
    import os
    serial_ports = [
        "/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3",
        "/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3",
    ]
    
    found_ports = []
    for port in serial_ports:
        if os.path.exists(port):
            found_ports.append(port)
    
    if found_ports:
        print(f"✅ {len(found_ports)} serielle Port(s) gefunden:")
        for port in found_ports:
            print(f"   {port}")
        return True
    else:
        print("   ⚠ Keine serielle Ports gefunden")
        return False

def test_meshtastic_info():
    """Testet meshtastic --info Befehl."""
    print("\n📊 Teste Meshtastic Info...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["meshtastic", "--info", "--timeout", "3"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Meshtastic --info erfolgreich")
            if result.stdout:
                # Zeige erste paar Zeilen der Info
                lines = result.stdout.strip().split('\n')[:10]
                for line in lines:
                    if line:
                        print(f"   {line}")
                if len(result.stdout.strip().split('\n')) > 10:
                    print("   ... (weitere Ausgabe gekürzt)")
            return True
        else:
            print(f"❌ Meshtastic --info fehlgeschlagen")
            if result.stderr:
                print(f"   Fehler: {result.stderr[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Meshtastic Info Test fehlgeschlagen: {e}")
        return False

def test_simple_connection():
    """Testet eine einfache Verbindung zu einem bekannten Gerät."""
    print("\n🔗 Teste einfache Verbindung...")
    
    # Bekannte Test-Adressen (können angepasst werden)
    test_addresses = [
        "HEHO_ab07",  # Von der alten test.py
        "E6:63:E5:E8:AB:07",  # MAC-Adresse Format
        "E663E5E8AB07",  # MAC ohne Doppelpunkte
    ]
    
    for address in test_addresses:
        print(f"   Versuche Verbindung zu: {address}")
        try:
            import subprocess
            result = subprocess.run(
                ["meshtastic", "--ble", address, "--info", "--timeout", "2"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"   ✅ Verbindung zu {address} erfolgreich!")
                return True
            else:
                print(f"   ❌ Verbindung zu {address} fehlgeschlagen")
                
        except Exception as e:
            print(f"   ⚠ Fehler bei {address}: {str(e)[:50]}...")
    
    print("   ⚠ Keine Verbindung zu Test-Geräten möglich")
    return False

def main():
    """Hauptfunktion für Tests."""
    print("🚀 Starte Meshtastic Tests")
    print("=" * 40)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Import
    tests_total += 1
    if test_meshtastic_import():
        tests_passed += 1
    
    # Test 2: BLE Scan
    tests_total += 1
    if test_ble_scan():
        tests_passed += 1
    
    # Test 3: Serielle Ports
    tests_total += 1
    if test_serial_ports():
        tests_passed += 1
    
    # Test 4: Meshtastic Info
    tests_total += 1
    if test_meshtastic_info():
        tests_passed += 1
    
    # Test 5: Einfache Verbindung
    tests_total += 1
    if test_simple_connection():
        tests_passed += 1
    
    # Zusammenfassung
    print("\n" + "=" * 40)
    print(f"📊 TEST ZUSAMMENFASSUNG")
    print(f"   Bestanden: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("✅ Alle Tests bestanden!")
    elif tests_passed >= tests_total / 2:
        print("⚠ Einige Tests fehlgeschlagen")
    else:
        print("❌ Die meisten Tests fehlgeschlagen")
    
    print("\n💡 Nächste Schritte:")
    if tests_passed < tests_total:
        print("1. Meshtastic-Gerät einschalten")
        print("2. BLE auf Gerät aktivieren")
        print("3. Gerät in Pairing-Modus versetzen")
        print("4. 'sudo systemctl restart bluetooth' versuchen")
    else:
        print("1. Mit test_advanced.py fortfahren")
        print("2. Eigene Geräteadressen testen")
        print("3. Nachrichten senden/empfangen testen")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Tests abgebrochen")
    except Exception as e:
        print(f"\n💥 Unerwarteter Fehler: {e}")
        sys.exit(1)