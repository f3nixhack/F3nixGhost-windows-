"""
🧅 TorChat Setup — Descargador automático de Tor para Windows
=============================================================
Ejecutar UNA SOLA VEZ antes de usar el chat.

    python setup.py

Descarga el experto de Tor para Windows y lo coloca en tor_bin/
No requiere instalar nada en el sistema.
"""

import urllib.request
import zipfile
import os
import sys
import hashlib
import shutil

# ─── Configuración ─────────────────────────────────────────────────────────────
# Tor Expert Bundle para Windows (64-bit) — sin interfaz gráfica, solo el binario
TOR_URL = "https://archive.torproject.org/tor-package-archive/torbrowser/13.5.7/tor-expert-bundle-windows-x86_64-13.5.7.tar.gz"
TOR_DIR = os.path.join(os.path.dirname(__file__), "tor_bin")
TOR_EXE = os.path.join(TOR_DIR, "tor", "tor.exe")
# ────────────────────────────────────────────────────────────────────────────────


def progreso(bloque, tam_bloque, tam_total):
    """Muestra barra de progreso en consola."""
    if tam_total > 0:
        porcentaje = min(int(bloque * tam_bloque * 100 / tam_total), 100)
        barras = porcentaje // 2
        barra = "█" * barras + "░" * (50 - barras)
        print(f"\r  [{barra}] {porcentaje}%", end="", flush=True)


def descargar_tor():
    print("\n🧅 TorChat Setup")
    print("=" * 55)

    if os.path.exists(TOR_EXE):
        print(f"✅ Tor ya está descargado en: {TOR_DIR}")
        print("   Si querés re-descargarlo, borrá la carpeta tor_bin/")
        return True

    os.makedirs(TOR_DIR, exist_ok=True)
    archivo_gz = os.path.join(TOR_DIR, "tor.tar.gz")

    print(f"📥 Descargando Tor Expert Bundle para Windows...")
    print(f"   Fuente: torproject.org")
    print(f"   Destino: {TOR_DIR}\n")

    try:
        urllib.request.urlretrieve(TOR_URL, archivo_gz, reporthook=progreso)
        print("\n\n✅ Descarga completa!")
    except Exception as e:
        print(f"\n❌ Error al descargar: {e}")
        print("   Verificá tu conexión a internet e intentá de nuevo.")
        return False

    print("📦 Extrayendo archivos...")
    try:
        import tarfile
        with tarfile.open(archivo_gz, "r:gz") as tar:
            tar.extractall(TOR_DIR)
        os.remove(archivo_gz)
        print("✅ Extracción completa!")
    except Exception as e:
        print(f"❌ Error al extraer: {e}")
        return False

    if os.path.exists(TOR_EXE):
        print(f"\n✅ tor.exe encontrado en: {TOR_EXE}")
    else:
        # Buscar tor.exe en subdirectorios por si la estructura cambió
        for root, dirs, files in os.walk(TOR_DIR):
            for f in files:
                if f == "tor.exe":
                    found = os.path.join(root, f)
                    print(f"✅ tor.exe encontrado en: {found}")
                    print("   (Ruta diferente a la esperada, actualizá TOR_EXE en tor_manager.py)")
                    break

    print("\n" + "=" * 55)
    print("🎉 Setup completo. Ahora podés usar:")
    print("   python server.py   ← para iniciar el servidor")
    print("   python client.py   ← para conectarte")
    print("=" * 55 + "\n")
    return True


def instalar_dependencias():
    print("📦 Instalando dependencias de Python...")
    deps = ["PySocks", "stem", "cryptography", "txtorcon", "twisted"]
    for dep in deps:
        print(f"   Instalando {dep}...", end=" ", flush=True)
        ret = os.system(f"{sys.executable} -m pip install {dep} -q")
        if ret == 0:
            print("✅")
        else:
            print("❌ (intentá manualmente: pip install " + dep + ")")
    print()


if __name__ == "__main__":
    instalar_dependencias()
    descargar_tor()
