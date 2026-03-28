#!/home/wdr/.local/share/pipx/venvs/meshtastic/bin/python3

print("Quick test...")

# Test 1: Datei lesen
try:
    with open('nodes', 'r') as f:
        content = f.read()
    print(f"✅ nodes Datei gelesen, {len(content)} Zeichen")
    
    # Zeige erste paar Zeilen
    lines = content.split('\n')
    print(f"   Erste 3 Zeilen:")
    for i, line in enumerate(lines[:3], 1):
        print(f"   {i}. {line}")
        
except Exception as e:
    print(f"❌ Fehler: {e}")

# Test 2: Meshtastic Import
try:
    import meshtastic
    print(f"\n✅ Meshtastic importiert")
except ImportError as e:
    print(f"\n❌ Meshtastic Import fehlgeschlagen: {e}")

print("\n✅ Test abgeschlossen")