"""
F3nixGhost -- build_exe.py
Genera F3nixGhost.exe con PyInstaller.

USO:   python build_exe.py
Necesitas: pip install pyinstaller customtkinter PySocks
El .exe queda en: dist/F3nixGhost.exe
"""

import subprocess, sys, os

BASE = os.path.dirname(os.path.abspath(__file__))
ok   = lambda m: print(f"  [OK] {m}")
info = lambda m: print(f"  [..] {m}")
err  = lambda m: print(f"  [!!] {m}")

print()
print("=" * 44)
print("   F3nixGhost -- Generando .exe")
print("=" * 44)
print()

# Dependencias
info("Verificando PyInstaller...")
try:
    import PyInstaller; ok(f"PyInstaller {PyInstaller.__version__}")
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    ok("PyInstaller instalado")

for pkg, inst in [("customtkinter","customtkinter"),("socks","PySocks")]:
    try:
        __import__(pkg); ok(f"{pkg} OK")
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", inst])
        ok(f"{inst} instalado")

# tor_bin
tor_bin = os.path.join(BASE, "tor_bin")
if not os.path.exists(tor_bin):
    err("tor_bin/ no encontrado -- corre setup.py primero"); sys.exit(1)
ok("tor_bin encontrado")

for f in ["tor_data", "hidden_service", "logs"]:
    os.makedirs(os.path.join(BASE, f), exist_ok=True)

add_data = []
for folder in ["tor_bin", "tor_data", "hidden_service", "logs"]:
    full = os.path.join(BASE, folder)
    if os.path.exists(full):
        add_data += ["--add-data", f"{full};{folder}"]
for file in ["torrc", "torchat_lang.json"]:
    full = os.path.join(BASE, file)
    if os.path.exists(full):
        add_data += ["--add-data", f"{full};."]

info("Construyendo .exe (1-3 minutos)...")
print()
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile", "--windowed",
    "--name", "F3nixGhost",
    "--clean", "--noconfirm",
    "--hidden-import=customtkinter",
    "--hidden-import=socks",
    "--hidden-import=darkdetect",
    "--hidden-import=packaging",
    "--hidden-import=PIL._tkinter_finder",
] + add_data + ["app.py"]

r = subprocess.run(cmd, cwd=BASE)
print()
if r.returncode == 0:
    exe = os.path.join(BASE, "dist", "F3nixGhost.exe")
    if os.path.exists(exe):
        mb = os.path.getsize(exe) / 1024 / 1024
        print("=" * 44)
        print("   BUILD EXITOSO")
        print("=" * 44)
        ok(f"dist/F3nixGhost.exe  ({mb:.1f} MB)")
        print()
        print("  -> Copia dist/F3nixGhost.exe para distribuir")
        print("  -> Incluye Tor, no necesita instalacion")
else:
    print("=" * 44)
    print("   BUILD FALLIDO")
    print("=" * 44)
    print()
    print("  Soluciones:")
    print("  -> pip install pyinstaller --upgrade")
    print("  -> Borra la carpeta build/ y reintenta")
    print("  -> Ejecuta como Administrador si hay permisos")
    sys.exit(1)