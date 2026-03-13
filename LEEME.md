# 👻 F3nixGhost v4 — Guía Completa

> Chat anónimo y cifrado sobre la red Tor. Sin servidores centrales. Sin registro. Sin rastreo.

---

## 📁 Archivos del proyecto

```
f3nixghost/
├── setup.py          ← PASO 1: Descarga Tor y dependencias
├── app.py            ← PASO 2: La app con interfaz gráfica
├── build_exe.py      ← PASO 3: Convierte a .exe distribuible
├── tor_manager.py    ← Módulo interno (no modificar)
├── LEEME.md          ← Esta guía
│
├── tor_bin/          ← Creado por setup.py (binario de Tor)
├── tor_data/         ← Datos de Tor (creado automáticamente)
├── hidden_service/   ← Dirección .onion del servidor
├── logs/             ← Logs de Tor
└── torchat_lang.json ← Idioma guardado
```

---

## 🚀 Pasos para usar

### PASO 1 — Setup (una sola vez)
```bash
python setup.py
```
Instala dependencias Python y descarga el binario de Tor (~30 MB).

### PASO 2 — Correr la app
```bash
python app.py
```

### PASO 3 (opcional) — Convertir a .exe
```bash
python build_exe.py
```
Genera `dist/F3nixGhost.exe` listo para distribuir sin instalar nada.

---

## 🌐 Selector de idioma

Al abrir la app por **primera vez** aparece el selector de idioma obligatorio. A partir de entonces la app recuerda tu elección y va directo al inicio. Para cambiar el idioma usá el botón `🌐 Idioma` en el panel izquierdo de la pantalla de inicio.

**Idiomas disponibles (15):** Español, English, 中文, हिन्दी, العربية, Português, Bahasa Indonesia, Русский, Français, Deutsch, 日本語, 한국어, Türkçe, Tiếng Việt, বাংলা

---

## 👥 Cómo chatear entre dos PCs

### PC 1 — Servidor (crea la sala)
1. Abrí la app → ingresá tu nombre de usuario
2. Click en **"Iniciar como Servidor →"**
3. Esperá ~1–2 min a que Tor se conecte
4. Copiá tu dirección `.onion` y compartila

### PC 2 — Cliente (se une)
1. Abrí la app → ingresá tu nombre de usuario
2. Pegá la `.onion` en el campo de cliente
3. Click en **"Conectar como Cliente →"**

---

## 💬 Comandos

Escribí `/help` en el chat para ver todos los comandos en pantalla. El sidebar solo muestra `/help` para no ocupar espacio — toda la referencia se despliega directamente en el área de chat. Referencia completa:

### 🔒 Privacidad & Seguridad

| Comando | Descripción |
|---|---|
| `/whoami` | Muestra tu nombre, país de salida, IP y dirección .onion |
| `/nodos` | Ver los 3 nodos del circuito Tor con país y bandera |
| `/newcircuit` | Cambiar el circuito Tor para salir por otro país |
| `/autokill <min>` | Cierra la app automáticamente en X minutos (dead man's switch) |
| `/clearscreen` | Limpia el historial visible del chat (solo en tu pantalla) |

### 💬 Chat

| Comando | Descripción |
|---|---|
| `/help` | Muestra todos los comandos disponibles |
| `/nick <nombre>` | Cambia tu nombre de usuario en tiempo real |
| `/usuarios` | Lista los usuarios conectados |
| `/uptime` | Tiempo de sesión activa |
| `/stats` | Uptime, mensajes enviados, país e IP de salida |
| `/salir` | Desconectarse del chat |

### 🛡️ Moderación (solo servidor)

| Comando | Descripción |
|---|---|
| `/msg <usuario> <texto>` | Mensaje privado a un usuario específico |
| `/kick <usuario>` | Expulsa al usuario de la sala |
| `/ban <usuario>` | Expulsa y bloquea reconexión en esta sesión |
| `/mute <usuario> [seg]` | Silencia al usuario X segundos (default: 60) |

---

## 🔍 Ventana de nodos Tor

Accedé con `/nodos` o el botón **"Ver Nodos"** en el sidebar.

| Nodo | Descripción |
|---|---|
| 🛡️ Guard (Entrada) | Primer nodo — conoce tu IP real |
| 🔀 Middle (Intermedio) | No sabe ni origen ni destino |
| 🚪 Exit (Salida) | Hace las conexiones reales a internet |

Por cada nodo se muestra: país con bandera, IP del relay, nickname y fingerprint. Los países se consultan en tiempo real a través del propio proxy Tor.

---

## 🔄 Cambiar circuito Tor

- Botón **"🔄 Nuevo Circuito"** en el sidebar, o `/newcircuit`
- Cambia el nodo de salida para aparecer en otro país
- No desconecta a nadie del chat
- Tarda ~3–5 segundos en establecerse

---

## 👥 Panel de usuarios en tiempo real

El sidebar del chat muestra cada usuario con:
- Dot verde de estado
- Nombre de usuario
- Bandera y país de su nodo de salida Tor

El contador en el header (`● 3`) muestra el total en tiempo real. Se actualiza cada 2 segundos. Solo el servidor ve a todos los usuarios; los clientes se ven solo a sí mismos.

---

## 🔐 ¿Qué queda oculto?

| Elemento | ¿Oculto? |
|---|---|
| Tu IP real | ✅ Sí |
| Tu ubicación | ✅ Sí |
| Contenido del chat | ✅ Sí (cifrado por Tor) |
| Dirección del servidor | ✅ Sí (.onion) |
| Tu nombre de usuario | ❌ No (visible para todos) |

---

## ❓ Problemas frecuentes

**"Tor: falta setup.py"** → Ejecutá `python setup.py` primero.

**Tor tarda mucho** → Normal la primera vez, esperá 2–3 min. Si persiste, revisá `logs/tor.log`.

**Windows Defender bloquea el .exe** → Falso positivo de PyInstaller. Click en "Más información" → "Ejecutar de todas formas".

**No aparece país en los nodos** → La consulta va por Tor y puede tardar. Hacé click en 🔄 dentro de la ventana de nodos.

**El ban no persiste al reiniciar** → El ban es por sesión. Al cerrar y reabrir la app se resetea.

---

## 🛠️ Requisitos

- **Python** 3.8+  ·  **Windows** 10/11 (64-bit)
- `pip install customtkinter PySocks`

---

*👻 F3nixGhost v4 — Anónimo · 15 idiomas · Nodos visibles · Moderación completa*