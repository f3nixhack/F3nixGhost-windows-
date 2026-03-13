"""
🧅 tor_manager.py — Gestor del proceso Tor portable
====================================================
Este módulo lanza y controla el binario de Tor incluido en tor_bin/.
No requiere que Tor esté instalado en el sistema.

Uso interno — no ejecutar directamente.
"""

import os
import sys
import time
import socket
import subprocess
import threading
import tempfile

# ─── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
TOR_DIR     = os.path.join(BASE_DIR, "tor_bin")
TOR_EXE     = os.path.join(TOR_DIR, "tor", "tor.exe")
TOR_DATA    = os.path.join(BASE_DIR, "tor_data")   # datos de Tor (creado automáticamente)
TOR_LOG     = os.path.join(BASE_DIR, "logs", "tor.log")
TORRC_PATH  = os.path.join(BASE_DIR, "torrc")       # configuración de Tor

# ─── Puertos ───────────────────────────────────────────────────────────────────
SOCKS_PORT    = 19050   # Puerto SOCKS5 de Tor (evitamos 9050 para no chocar con Tor instalado)
CONTROL_PORT  = 19051   # Puerto de control de Tor
CHAT_PORT     = 5555    # Puerto del chat
# ────────────────────────────────────────────────────────────────────────────────

_proceso_tor = None
_onion_address = None


def verificar_tor_exe():
    """Verifica que el binario de Tor exista."""
    if not os.path.exists(TOR_EXE):
        print(f"❌ No se encontró tor.exe en: {TOR_EXE}")
        print("   Ejecutá primero:  python setup.py")
        sys.exit(1)


def crear_torrc(es_servidor=False, hidden_service_dir=None):
    """
    Crea el archivo de configuración torrc para Tor.
    Si es_servidor=True, habilita el Hidden Service para exponer el chat.
    """
    os.makedirs(TOR_DATA, exist_ok=True)
    os.makedirs(os.path.dirname(TOR_LOG), exist_ok=True)
    os.makedirs(os.path.dirname(TORRC_PATH), exist_ok=True)

    config = f"""# torrc generado automáticamente por TorChat
SocksPort {SOCKS_PORT}
ControlPort {CONTROL_PORT}
DataDirectory {TOR_DATA.replace(os.sep, "/")}
Log notice file {TOR_LOG.replace(os.sep, "/")}

# Rendimiento
CircuitBuildTimeout 30
LearnCircuitBuildTimeout 0
"""

    if es_servidor and hidden_service_dir:
        hs_dir = hidden_service_dir.replace(os.sep, "/")
        config += f"""
# Hidden Service del chat
HiddenServiceDir {hs_dir}
HiddenServicePort {CHAT_PORT} 127.0.0.1:{CHAT_PORT}
"""

    with open(TORRC_PATH, "w") as f:
        f.write(config)

    return TORRC_PATH


def esperar_tor_listo(timeout=120):
    """
    Espera hasta que Tor esté listo para aceptar conexiones SOCKS5.
    Muestra progreso al usuario.
    """
    print("⏳ Conectando a la red Tor", end="", flush=True)
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            s = socket.socket()
            s.settimeout(2)
            s.connect(("127.0.0.1", SOCKS_PORT))
            s.close()
            print(" ✅")
            return True
        except Exception:
            print(".", end="", flush=True)
            time.sleep(2)
    print(" ❌")
    return False


def leer_log_tor():
    """Lee el log de Tor y muestra mensajes relevantes."""
    if not os.path.exists(TOR_LOG):
        return
    try:
        with open(TOR_LOG, "r", errors="ignore") as f:
            lineas = f.readlines()
        # Mostrar últimas líneas relevantes
        for linea in lineas[-5:]:
            if any(k in linea for k in ["Bootstrapped", "ERROR", "WARN", "opened"]):
                print(f"   [Tor] {linea.strip()}")
    except Exception:
        pass


def iniciar_tor(es_servidor=False):
    """
    Lanza el proceso Tor portable.
    Retorna True si arrancó correctamente.
    """
    global _proceso_tor

    verificar_tor_exe()

    # Directorio del Hidden Service (solo servidor)
    hidden_service_dir = None
    if es_servidor:
        hidden_service_dir = os.path.join(BASE_DIR, "hidden_service")
        os.makedirs(hidden_service_dir, exist_ok=True)

    torrc = crear_torrc(es_servidor=es_servidor, hidden_service_dir=hidden_service_dir)

    print(f"\n🧅 Iniciando Tor portable...")
    print(f"   Binario : {TOR_EXE}")
    print(f"   Config  : {torrc}")
    print(f"   Log     : {TOR_LOG}")

    try:
        _proceso_tor = subprocess.Popen(
            [TOR_EXE, "-f", torrc],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW  # Windows: sin ventana extra
        )
    except Exception as e:
        print(f"❌ No se pudo iniciar Tor: {e}")
        return False

    print(f"   PID     : {_proceso_tor.pid}")

    # Esperar a que Tor esté listo
    if not esperar_tor_listo():
        print("❌ Tor tardó demasiado en iniciar.")
        leer_log_tor()
        detener_tor()
        return False

    return True


def obtener_direccion_onion():
    """
    Lee la dirección .onion generada por Tor para el Hidden Service.
    Solo disponible después de iniciar_tor(es_servidor=True).
    """
    global _onion_address
    hostname_file = os.path.join(BASE_DIR, "hidden_service", "hostname")

    intentos = 0
    while not os.path.exists(hostname_file) and intentos < 15:
        time.sleep(1)
        intentos += 1

    if os.path.exists(hostname_file):
        with open(hostname_file, "r") as f:
            _onion_address = f.read().strip()
        return _onion_address
    else:
        return None


def detener_tor():
    """Termina el proceso Tor."""
    global _proceso_tor
    if _proceso_tor and _proceso_tor.poll() is None:
        _proceso_tor.terminate()
        try:
            _proceso_tor.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _proceso_tor.kill()
        print("[*] Tor detenido.")
    _proceso_tor = None
