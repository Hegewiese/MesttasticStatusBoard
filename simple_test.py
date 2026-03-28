#!/usr/bin/env python3
"""Einfachster Meshtastic Test"""

print("🚀 Starte einfachen Test...")

# Test 1: Python-Umgebung
print("1. Python-Umgebung:")
import sys
print(f"   Python Version: {sys.version}")
print(f"   Python Pfad: {sys.executable}")

# Test 2: Meshtastic Import
print("\n2. Meshtastic Import:")
try:
    import meshtastic
    print("   ✅ Meshtastic importiert")
    if hasattr(meshtastic, '__version__'):
        print(f"   Version: {meshtastic.__version__}")
    else:
        print("   Version: Unbekannt")
except ImportError as e:
    print(f"   ❌ Import fehlgeschlagen: {e}")

# Test 3: Einfacher Befehl
print("\n3. Einfacher Meshtastic Befehl:")
try:
    import subprocess
    result = subprocess.run(
        ["meshtastic", "--version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(f"   ✅ Befehl erfolgreich")
    print(f"   Ausgabe: {result.stdout.strip()}")
except subprocess.TimeoutExpired:
    print("   ❌ Timeout - Befehl hängt")
except Exception as e:
    print(f"   ❌ Fehler: {type(e).__name__}: {str(e)[:50]}...")

print("\n✅ Test abgeschlossen")
