"""
👻 F3nixGhost v4 — Multi-idioma, Nodos Tor, Kick, Cambio de Circuito
==================================================================
Nuevas funciones:
  - Selector de idioma al primer uso (16 idiomas)
  - Ver nodos del circuito Tor activo
  - Renovar circuito Tor (cambiar país)
  - Comando /kick <usuario> para el servidor
  - Persistencia de idioma elegido

Uso:  python app.py
"""

import customtkinter as ctk
import threading
import socket
import socks
import subprocess
import os
import sys
import time
import json
import re
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

C_BG       = "#0a0a0f"
C_PANEL    = "#0f0f1a"
C_CARD     = "#13131f"
C_BORDER   = "#1e1e2e"
C_ONION    = "#7c3aed"
C_ONION2   = "#a855f7"
C_GREEN    = "#22c55e"
C_RED      = "#ef4444"
C_YELLOW   = "#f59e0b"
C_BLUE     = "#38bdf8"
C_TEXT     = "#e2e8f0"
C_MUTED    = "#64748b"
C_INPUT_BG = "#1a1a2e"

SOCKS_PORT   = 19050
CONTROL_PORT = 19051
CHAT_PORT    = 7777

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOR_EXE  = os.path.join(BASE_DIR, "tor_bin", "tor", "tor.exe")
TOR_DATA = os.path.join(BASE_DIR, "tor_data")
TORRC    = os.path.join(BASE_DIR, "torrc")
HS_DIR   = os.path.join(BASE_DIR, "hidden_service")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
TOR_LOG  = os.path.join(LOGS_DIR, "tor.log")
LANG_FILE = os.path.join(BASE_DIR, "torchat_lang.json")

_tor_proc = None

# ══════════════════════════════════════════════════════════════
#  TRADUCCIONES
# ══════════════════════════════════════════════════════════════

LANGUAGES = {
    "es": "Español",
    "en": "English",
    "zh": "中文 (Mandarin)",
    "hi": "हिन्दी (Hindi)",
    "ar": "العربية (Árabe)",
    "pt": "Português (Brasil)",
    "id": "Bahasa Indonesia",
    "ru": "Русский (Ruso)",
    "fr": "Français (Francés)",
    "de": "Deutsch (Alemán)",
    "ja": "日本語 (Japonés)",
    "ko": "한국어 (Coreano)",
    "tr": "Türkçe (Turco)",
    "vi": "Tiếng Việt (Vietnamita)",
    "bn": "বাংলা (Bengalí)",
}

TRANSLATIONS = {
    "es": {
        "app_title": "👻 F3nixGhost",
        "select_language": "Elegí tu idioma",
        "select_language_sub": "Podés cambiarlo después desde el menú",
        "confirm": "Confirmar",
        "choose_role": "Elegí tu rol",
        "role_subtitle": "¿Vas a abrir el chat o conectarte a uno?",
        "your_username": "👤  Tu nombre de usuario",
        "username_hint": "Así te van a ver los demás en el chat.",
        "username_placeholder": "Ej: Alice, Bob, Anónimo...",
        "server_title": "🖥️  Servidor",
        "server_desc": "Abrís el chat y obtenés una dirección .onion para compartir.",
        "start_server": "Iniciar como Servidor →",
        "client_title": "💻  Cliente",
        "client_desc": "Tenés una dirección .onion y querés conectarte.",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "Conectar como Cliente →",
        "setup_hint": "Ejecutá setup.py la primera vez para descargar Tor",
        "tor_ready": "● Tor: listo ✓",
        "tor_missing": "● Tor: falta setup.py",
        "tor_checking": "● Tor: verificando...",
        "starting_server": "Iniciando Servidor...",
        "starting_tor": "Arrancando Tor portable...",
        "connecting_chat": "Conectando al Chat...",
        "connecting_tor": "Conectando a la red Tor...",
        "detecting_country": "🌍 Detectando país de salida Tor...",
        "generating_onion": "Generando dirección .onion...",
        "starting_chat_server": "Iniciando servidor de chat...",
        "connected": "● Conectado",
        "room": "SALA",
        "commands": "COMANDOS",
        "cmd_users": "/usuarios",
        "cmd_users_desc": "ver conectados",
        "cmd_leave": "/salir",
        "cmd_leave_desc": "desconectarse",
        "cmd_kick": "/kick <usuario>",
        "cmd_kick_desc": "expulsar usuario (solo servidor)",
        "cmd_nodes": "/nodos",
        "cmd_nodes_desc": "ver circuito Tor",
        "tor_exit": "SALIDA TOR",
        "your_address": "TU DIRECCIÓN",
        "copy_onion": "📋 Copiar .onion",
        "send": "Enviar",
        "write_message": "Escribí un mensaje...",
        "welcome": "👻 F3nixGhost iniciado. ¡Bienvenido!\n",
        "server_closed": "\n[!] El servidor cerró la conexión.\n",
        "error_tor_missing": "Falta tor.exe\nEjecutá setup.py primero.",
        "error_onion_invalid": "Ingresá una dirección .onion válida.",
        "error_tor_timeout": "Tor tardó demasiado.\nRevisá logs/tor.log",
        "error_connect": "No se pudo conectar:\n",
        "back": "← Volver",
        "server_ready": "[✅] Servidor listo\n",
        "user_label": "    👤 Usuario  : ",
        "exit_country": "     País salida: ",
        "onion_label": "    🌐 .onion   : ",
        "client_connected": "[✅] Conectado\n",
        "onion_copied": "[📋 Dirección .onion copiada al portapapeles]\n",
        "tor_nodes_title": "🔁 Nodos del Circuito Tor",
        "tor_nodes_loading": "Consultando circuito...",
        "tor_nodes_error": "No se pudo obtener el circuito.\nAsegurate que Tor esté conectado.",
        "tor_nodes_close": "Cerrar",
        "refresh_circuit": "🔄 Nuevo Circuito",
        "circuit_refreshing": "Solicitando nuevo circuito Tor...",
        "circuit_refreshed": "[🔄] Circuito Tor renovado. Detectando nuevo país...\n",
        "circuit_error": "[❌] No se pudo renovar el circuito.\n",
        "kicked": "[🚫] Fuiste expulsado de la sala.\n",
        "kick_ok": "[🚫] {user} fue expulsado.\n",
        "kick_notfound": "[!] Usuario '{user}' no encontrado.\n",
        "kick_usage": "[!] Uso: /kick <nombre_usuario>\n",
        "only_server_kick": "[!] Solo el servidor puede usar /kick.\n",
        "users_connected": "[Conectados]: ",
        "user_joined": "✅ {user} entró al chat  —  {country}\n",
        "user_left": "❌ {user} abandonó el chat.\n",
        "welcome_msg": "\n👻 ¡Bienvenido, {user}! ({count} conectados)\n   /usuarios  /salir  /kick  /nodos\n\n",
        "tor_circuit_label": "CIRCUITO TOR",
        "node_guard": "🛡️ Entrada (Guard)",
        "node_middle": "🔀 Intermedio",
        "node_exit": "🚪 Salida (Exit)",
        "unknown_country": "Desconocido",
        "language_menu": "🌐 Idioma",
        "tor_nodes_btn": "🔍 Ver Nodos",
        "ip_label": "IP: ",
        "circuit_node": "Nodo",
        "fingerprint": "Huella",
        "country_flag": "País",
        "no_circuit_data": "No hay datos de circuito disponibles.",
        "nodes_panel_title": "NODOS TOR",
    },
    "en": {
        "app_title": "👻 F3nixGhost",
        "select_language": "Choose your language",
        "select_language_sub": "You can change it later from the menu",
        "confirm": "Confirm",
        "choose_role": "Choose your role",
        "role_subtitle": "Are you opening a chat or connecting to one?",
        "your_username": "👤  Your username",
        "username_hint": "This is how others will see you in the chat.",
        "username_placeholder": "E.g.: Alice, Bob, Anonymous...",
        "server_title": "🖥️  Server",
        "server_desc": "Open the chat and get a .onion address to share.",
        "start_server": "Start as Server →",
        "client_title": "💻  Client",
        "client_desc": "You have a .onion address and want to connect.",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "Connect as Client →",
        "setup_hint": "Run setup.py the first time to download Tor",
        "tor_ready": "● Tor: ready ✓",
        "tor_missing": "● Tor: run setup.py",
        "tor_checking": "● Tor: checking...",
        "starting_server": "Starting Server...",
        "starting_tor": "Starting portable Tor...",
        "connecting_chat": "Connecting to Chat...",
        "connecting_tor": "Connecting to Tor network...",
        "detecting_country": "🌍 Detecting Tor exit country...",
        "generating_onion": "Generating .onion address...",
        "starting_chat_server": "Starting chat server...",
        "connected": "● Connected",
        "room": "ROOM",
        "commands": "COMMANDS",
        "cmd_users": "/users",
        "cmd_users_desc": "see connected",
        "cmd_leave": "/leave",
        "cmd_leave_desc": "disconnect",
        "cmd_kick": "/kick <user>",
        "cmd_kick_desc": "kick user (server only)",
        "cmd_nodes": "/nodes",
        "cmd_nodes_desc": "view Tor circuit",
        "tor_exit": "TOR EXIT",
        "your_address": "YOUR ADDRESS",
        "copy_onion": "📋 Copy .onion",
        "send": "Send",
        "write_message": "Write a message...",
        "welcome": "👻 F3nixGhost started. Welcome!\n",
        "server_closed": "\n[!] Server closed the connection.\n",
        "error_tor_missing": "tor.exe missing\nRun setup.py first.",
        "error_onion_invalid": "Enter a valid .onion address.",
        "error_tor_timeout": "Tor took too long.\nCheck logs/tor.log",
        "error_connect": "Could not connect:\n",
        "back": "← Back",
        "server_ready": "[✅] Server ready\n",
        "user_label": "    👤 User    : ",
        "exit_country": "     Exit country: ",
        "onion_label": "    🌐 .onion  : ",
        "client_connected": "[✅] Connected\n",
        "onion_copied": "[📋 .onion address copied to clipboard]\n",
        "tor_nodes_title": "🔁 Tor Circuit Nodes",
        "tor_nodes_loading": "Querying circuit...",
        "tor_nodes_error": "Could not get circuit.\nMake sure Tor is connected.",
        "tor_nodes_close": "Close",
        "refresh_circuit": "🔄 New Circuit",
        "circuit_refreshing": "Requesting new Tor circuit...",
        "circuit_refreshed": "[🔄] Tor circuit renewed. Detecting new country...\n",
        "circuit_error": "[❌] Could not renew circuit.\n",
        "kicked": "[🚫] You were kicked from the room.\n",
        "kick_ok": "[🚫] {user} was kicked.\n",
        "kick_notfound": "[!] User '{user}' not found.\n",
        "kick_usage": "[!] Usage: /kick <username>\n",
        "only_server_kick": "[!] Only the server can use /kick.\n",
        "users_connected": "[Connected]: ",
        "user_joined": "✅ {user} joined the chat  —  {country}\n",
        "user_left": "❌ {user} left the chat.\n",
        "welcome_msg": "\n👻 Welcome, {user}! ({count} connected)\n   /users  /leave  /kick  /nodes\n\n",
        "tor_circuit_label": "TOR CIRCUIT",
        "node_guard": "🛡️ Entry (Guard)",
        "node_middle": "🔀 Middle",
        "node_exit": "🚪 Exit",
        "unknown_country": "Unknown",
        "language_menu": "🌐 Language",
        "tor_nodes_btn": "🔍 View Nodes",
        "ip_label": "IP: ",
        "circuit_node": "Node",
        "fingerprint": "Fingerprint",
        "country_flag": "Country",
        "no_circuit_data": "No circuit data available.",
        "nodes_panel_title": "TOR NODES",
    },
    "zh": {
        "app_title": "👻 F3nixGhost",
        "select_language": "选择您的语言",
        "select_language_sub": "您可以稍后在菜单中更改",
        "confirm": "确认",
        "choose_role": "选择您的角色",
        "role_subtitle": "您是要开启聊天还是连接到聊天室？",
        "your_username": "👤  您的用户名",
        "username_hint": "其他人在聊天中会看到这个名字。",
        "username_placeholder": "例如：Alice、Bob、匿名...",
        "server_title": "🖥️  服务器",
        "server_desc": "开启聊天并获取可分享的 .onion 地址。",
        "start_server": "作为服务器启动 →",
        "client_title": "💻  客户端",
        "client_desc": "您有一个 .onion 地址并想要连接。",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "作为客户端连接 →",
        "setup_hint": "第一次运行 setup.py 来下载 Tor",
        "tor_ready": "● Tor: 就绪 ✓",
        "tor_missing": "● Tor: 请运行 setup.py",
        "tor_checking": "● Tor: 检查中...",
        "starting_server": "启动服务器中...",
        "starting_tor": "启动便携 Tor...",
        "connecting_chat": "连接到聊天...",
        "connecting_tor": "连接到 Tor 网络...",
        "detecting_country": "🌍 检测 Tor 出口国家...",
        "generating_onion": "生成 .onion 地址...",
        "starting_chat_server": "启动聊天服务器...",
        "connected": "● 已连接",
        "room": "房间",
        "commands": "命令",
        "cmd_users": "/users",
        "cmd_users_desc": "查看在线用户",
        "cmd_leave": "/leave",
        "cmd_leave_desc": "断开连接",
        "cmd_kick": "/kick <用户>",
        "cmd_kick_desc": "踢出用户（仅服务器）",
        "cmd_nodes": "/nodes",
        "cmd_nodes_desc": "查看 Tor 节点",
        "tor_exit": "TOR 出口",
        "your_address": "您的地址",
        "copy_onion": "📋 复制 .onion",
        "send": "发送",
        "write_message": "输入消息...",
        "welcome": "👻 F3nixGhost 已启动。欢迎！\n",
        "server_closed": "\n[!] 服务器关闭了连接。\n",
        "error_tor_missing": "缺少 tor.exe\n请先运行 setup.py。",
        "error_onion_invalid": "请输入有效的 .onion 地址。",
        "error_tor_timeout": "Tor 连接超时。\n请检查 logs/tor.log",
        "error_connect": "无法连接：\n",
        "back": "← 返回",
        "server_ready": "[✅] 服务器就绪\n",
        "user_label": "    👤 用户  : ",
        "exit_country": "     出口国家: ",
        "onion_label": "    🌐 .onion: ",
        "client_connected": "[✅] 已连接\n",
        "onion_copied": "[📋 .onion 地址已复制到剪贴板]\n",
        "tor_nodes_title": "🔁 Tor 电路节点",
        "tor_nodes_loading": "查询电路中...",
        "tor_nodes_error": "无法获取电路。\n请确保 Tor 已连接。",
        "tor_nodes_close": "关闭",
        "refresh_circuit": "🔄 新电路",
        "circuit_refreshing": "请求新 Tor 电路...",
        "circuit_refreshed": "[🔄] Tor 电路已更新。检测新国家...\n",
        "circuit_error": "[❌] 无法更新电路。\n",
        "kicked": "[🚫] 您已被踢出聊天室。\n",
        "kick_ok": "[🚫] {user} 已被踢出。\n",
        "kick_notfound": "[!] 用户 '{user}' 未找到。\n",
        "kick_usage": "[!] 用法：/kick <用户名>\n",
        "only_server_kick": "[!] 只有服务器可以使用 /kick。\n",
        "users_connected": "[在线]: ",
        "user_joined": "✅ {user} 加入了聊天  —  {country}\n",
        "user_left": "❌ {user} 离开了聊天。\n",
        "welcome_msg": "\n👻 欢迎, {user}！（{count} 人在线）\n   /users  /leave  /kick  /nodes\n\n",
        "tor_circuit_label": "TOR 电路",
        "node_guard": "🛡️ 入口（Guard）",
        "node_middle": "🔀 中间节点",
        "node_exit": "🚪 出口节点",
        "unknown_country": "未知",
        "language_menu": "🌐 语言",
        "tor_nodes_btn": "🔍 查看节点",
        "ip_label": "IP: ",
        "circuit_node": "节点",
        "fingerprint": "指纹",
        "country_flag": "国家",
        "no_circuit_data": "没有可用的电路数据。",
        "nodes_panel_title": "TOR 节点",
    },
    "hi": {
        "app_title": "👻 F3nixGhost",
        "select_language": "अपनी भाषा चुनें",
        "select_language_sub": "आप बाद में मेनू से बदल सकते हैं",
        "confirm": "पुष्टि करें",
        "choose_role": "अपनी भूमिका चुनें",
        "role_subtitle": "क्या आप चैट खोलेंगे या किसी से जुड़ेंगे?",
        "your_username": "👤  आपका उपयोगकर्ता नाम",
        "username_hint": "चैट में दूसरे आपको इसी नाम से देखेंगे।",
        "username_placeholder": "उदा.: Alice, Bob, अज्ञात...",
        "server_title": "🖥️  सर्वर",
        "server_desc": "चैट खोलें और .onion पता प्राप्त करें।",
        "start_server": "सर्वर के रूप में शुरू करें →",
        "client_title": "💻  क्लाइंट",
        "client_desc": "आपके पास .onion पता है और जुड़ना चाहते हैं।",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "क्लाइंट के रूप में जुड़ें →",
        "setup_hint": "Tor डाउनलोड करने के लिए पहली बार setup.py चलाएं",
        "tor_ready": "● Tor: तैयार ✓",
        "tor_missing": "● Tor: setup.py चलाएं",
        "tor_checking": "● Tor: जाँच रहा है...",
        "starting_server": "सर्वर शुरू हो रहा है...",
        "starting_tor": "Tor शुरू हो रहा है...",
        "connecting_chat": "चैट से जुड़ रहे हैं...",
        "connecting_tor": "Tor नेटवर्क से जुड़ रहे हैं...",
        "detecting_country": "🌍 Tor निकास देश का पता लगा रहे हैं...",
        "generating_onion": ".onion पता बना रहे हैं...",
        "starting_chat_server": "चैट सर्वर शुरू हो रहा है...",
        "connected": "● जुड़े हैं",
        "room": "कमरा",
        "commands": "कमांड",
        "cmd_users": "/users",
        "cmd_users_desc": "जुड़े लोग देखें",
        "cmd_leave": "/leave",
        "cmd_leave_desc": "डिस्कनेक्ट करें",
        "cmd_kick": "/kick <उपयोगकर्ता>",
        "cmd_kick_desc": "निकालें (केवल सर्वर)",
        "cmd_nodes": "/nodes",
        "cmd_nodes_desc": "Tor नोड देखें",
        "tor_exit": "TOR निकास",
        "your_address": "आपका पता",
        "copy_onion": "📋 .onion कॉपी करें",
        "send": "भेजें",
        "write_message": "संदेश लिखें...",
        "welcome": "👻 F3nixGhost शुरू हुआ। स्वागत है!\n",
        "server_closed": "\n[!] सर्वर ने कनेक्शन बंद किया।\n",
        "error_tor_missing": "tor.exe नहीं मिला\nपहले setup.py चलाएं।",
        "error_onion_invalid": "वैध .onion पता दर्ज करें।",
        "error_tor_timeout": "Tor बहुत धीमा है।\nlogs/tor.log जांचें",
        "error_connect": "कनेक्ट नहीं हो सका:\n",
        "back": "← वापस",
        "server_ready": "[✅] सर्वर तैयार\n",
        "user_label": "    👤 उपयोगकर्ता: ",
        "exit_country": "     निकास देश: ",
        "onion_label": "    🌐 .onion: ",
        "client_connected": "[✅] जुड़े\n",
        "onion_copied": "[📋 .onion पता क्लिपबोर्ड में कॉपी किया]\n",
        "tor_nodes_title": "🔁 Tor सर्किट नोड",
        "tor_nodes_loading": "सर्किट की जांच...",
        "tor_nodes_error": "सर्किट नहीं मिल सका।\nTor जुड़ा है यह सुनिश्चित करें।",
        "tor_nodes_close": "बंद करें",
        "refresh_circuit": "🔄 नया सर्किट",
        "circuit_refreshing": "नया Tor सर्किट मांग रहे हैं...",
        "circuit_refreshed": "[🔄] Tor सर्किट नवीनीकृत। नया देश खोज रहे हैं...\n",
        "circuit_error": "[❌] सर्किट नवीनीकृत नहीं हो सका।\n",
        "kicked": "[🚫] आपको कमरे से निकाल दिया गया।\n",
        "kick_ok": "[🚫] {user} को निकाल दिया गया।\n",
        "kick_notfound": "[!] उपयोगकर्ता '{user}' नहीं मिला।\n",
        "kick_usage": "[!] उपयोग: /kick <उपयोगकर्ता नाम>\n",
        "only_server_kick": "[!] केवल सर्वर /kick उपयोग कर सकता है।\n",
        "users_connected": "[जुड़े]: ",
        "user_joined": "✅ {user} चैट में आए  —  {country}\n",
        "user_left": "❌ {user} चैट छोड़ गए।\n",
        "welcome_msg": "\n👻 स्वागत, {user}! ({count} जुड़े)\n   /users  /leave  /kick  /nodes\n\n",
        "tor_circuit_label": "TOR सर्किट",
        "node_guard": "🛡️ प्रवेश (Guard)",
        "node_middle": "🔀 मध्य",
        "node_exit": "🚪 निकास",
        "unknown_country": "अज्ञात",
        "language_menu": "🌐 भाषा",
        "tor_nodes_btn": "🔍 नोड देखें",
        "ip_label": "IP: ",
        "circuit_node": "नोड",
        "fingerprint": "फिंगरप्रिंट",
        "country_flag": "देश",
        "no_circuit_data": "कोई सर्किट डेटा उपलब्ध नहीं।",
        "nodes_panel_title": "TOR नोड",
    },
    "ar": {
        "app_title": "👻 F3nixGhost",
        "select_language": "اختر لغتك",
        "select_language_sub": "يمكنك تغييرها لاحقاً من القائمة",
        "confirm": "تأكيد",
        "choose_role": "اختر دورك",
        "role_subtitle": "هل ستفتح دردشة أم ستتصل بواحدة؟",
        "your_username": "👤  اسم المستخدم",
        "username_hint": "هكذا سيراك الآخرون في الدردشة.",
        "username_placeholder": "مثال: Alice، Bob، مجهول...",
        "server_title": "🖥️  خادم",
        "server_desc": "افتح الدردشة واحصل على عنوان .onion للمشاركة.",
        "start_server": "بدء كخادم →",
        "client_title": "💻  عميل",
        "client_desc": "لديك عنوان .onion وتريد الاتصال.",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "الاتصال كعميل →",
        "setup_hint": "شغّل setup.py أول مرة لتنزيل Tor",
        "tor_ready": "● Tor: جاهز ✓",
        "tor_missing": "● Tor: شغّل setup.py",
        "tor_checking": "● Tor: جارٍ التحقق...",
        "starting_server": "جارٍ بدء الخادم...",
        "starting_tor": "جارٍ تشغيل Tor...",
        "connecting_chat": "الاتصال بالدردشة...",
        "connecting_tor": "الاتصال بشبكة Tor...",
        "detecting_country": "🌍 اكتشاف بلد مخرج Tor...",
        "generating_onion": "إنشاء عنوان .onion...",
        "starting_chat_server": "بدء خادم الدردشة...",
        "connected": "● متصل",
        "room": "الغرفة",
        "commands": "الأوامر",
        "cmd_users": "/users",
        "cmd_users_desc": "عرض المتصلين",
        "cmd_leave": "/leave",
        "cmd_leave_desc": "قطع الاتصال",
        "cmd_kick": "/kick <مستخدم>",
        "cmd_kick_desc": "طرد مستخدم (للخادم فقط)",
        "cmd_nodes": "/nodes",
        "cmd_nodes_desc": "عرض عقد Tor",
        "tor_exit": "مخرج TOR",
        "your_address": "عنوانك",
        "copy_onion": "📋 نسخ .onion",
        "send": "إرسال",
        "write_message": "اكتب رسالة...",
        "welcome": "👻 F3nixGhost بدأ. مرحباً!\n",
        "server_closed": "\n[!] أغلق الخادم الاتصال.\n",
        "error_tor_missing": "tor.exe مفقود\nشغّل setup.py أولاً.",
        "error_onion_invalid": "أدخل عنوان .onion صالحاً.",
        "error_tor_timeout": "استغرق Tor وقتاً طويلاً.\nتحقق من logs/tor.log",
        "error_connect": "تعذر الاتصال:\n",
        "back": "← رجوع",
        "server_ready": "[✅] الخادم جاهز\n",
        "user_label": "    👤 المستخدم: ",
        "exit_country": "     بلد المخرج: ",
        "onion_label": "    🌐 .onion: ",
        "client_connected": "[✅] متصل\n",
        "onion_copied": "[📋 تم نسخ عنوان .onion إلى الحافظة]\n",
        "tor_nodes_title": "🔁 عقد دائرة Tor",
        "tor_nodes_loading": "جارٍ الاستعلام عن الدائرة...",
        "tor_nodes_error": "تعذر الحصول على الدائرة.\nتأكد من اتصال Tor.",
        "tor_nodes_close": "إغلاق",
        "refresh_circuit": "🔄 دائرة جديدة",
        "circuit_refreshing": "طلب دائرة Tor جديدة...",
        "circuit_refreshed": "[🔄] تم تجديد دائرة Tor. اكتشاف بلد جديد...\n",
        "circuit_error": "[❌] تعذر تجديد الدائرة.\n",
        "kicked": "[🚫] تم طردك من الغرفة.\n",
        "kick_ok": "[🚫] تم طرد {user}.\n",
        "kick_notfound": "[!] المستخدم '{user}' غير موجود.\n",
        "kick_usage": "[!] الاستخدام: /kick <اسم_المستخدم>\n",
        "only_server_kick": "[!] /kick للخادم فقط.\n",
        "users_connected": "[المتصلون]: ",
        "user_joined": "✅ {user} دخل الدردشة  —  {country}\n",
        "user_left": "❌ {user} غادر الدردشة.\n",
        "welcome_msg": "\n👻 مرحباً, {user}! ({count} متصل)\n   /users  /leave  /kick  /nodes\n\n",
        "tor_circuit_label": "دائرة TOR",
        "node_guard": "🛡️ مدخل (Guard)",
        "node_middle": "🔀 وسيط",
        "node_exit": "🚪 مخرج",
        "unknown_country": "غير معروف",
        "language_menu": "🌐 اللغة",
        "tor_nodes_btn": "🔍 عرض العقد",
        "ip_label": "IP: ",
        "circuit_node": "عقدة",
        "fingerprint": "بصمة",
        "country_flag": "البلد",
        "no_circuit_data": "لا توجد بيانات دائرة متاحة.",
        "nodes_panel_title": "عقد TOR",
    },
    "pt": {
        "app_title": "👻 F3nixGhost",
        "select_language": "Escolha seu idioma",
        "select_language_sub": "Você pode mudar depois pelo menu",
        "confirm": "Confirmar",
        "choose_role": "Escolha seu papel",
        "role_subtitle": "Você vai abrir um chat ou se conectar a um?",
        "your_username": "👤  Seu nome de usuário",
        "username_hint": "Assim os outros te verão no chat.",
        "username_placeholder": "Ex.: Alice, Bob, Anônimo...",
        "server_title": "🖥️  Servidor",
        "server_desc": "Abra o chat e obtenha um endereço .onion para compartilhar.",
        "start_server": "Iniciar como Servidor →",
        "client_title": "💻  Cliente",
        "client_desc": "Você tem um endereço .onion e quer se conectar.",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "Conectar como Cliente →",
        "setup_hint": "Execute setup.py na primeira vez para baixar o Tor",
        "tor_ready": "● Tor: pronto ✓",
        "tor_missing": "● Tor: execute setup.py",
        "tor_checking": "● Tor: verificando...",
        "starting_server": "Iniciando Servidor...",
        "starting_tor": "Iniciando Tor portátil...",
        "connecting_chat": "Conectando ao Chat...",
        "connecting_tor": "Conectando à rede Tor...",
        "detecting_country": "🌍 Detectando país de saída Tor...",
        "generating_onion": "Gerando endereço .onion...",
        "starting_chat_server": "Iniciando servidor de chat...",
        "connected": "● Conectado",
        "room": "SALA",
        "commands": "COMANDOS",
        "cmd_users": "/usuarios",
        "cmd_users_desc": "ver conectados",
        "cmd_leave": "/sair",
        "cmd_leave_desc": "desconectar",
        "cmd_kick": "/kick <usuário>",
        "cmd_kick_desc": "expulsar usuário (só servidor)",
        "cmd_nodes": "/nos",
        "cmd_nodes_desc": "ver nós Tor",
        "tor_exit": "SAÍDA TOR",
        "your_address": "SEU ENDEREÇO",
        "copy_onion": "📋 Copiar .onion",
        "send": "Enviar",
        "write_message": "Escreva uma mensagem...",
        "welcome": "👻 F3nixGhost iniciado. Bem-vindo!\n",
        "server_closed": "\n[!] O servidor fechou a conexão.\n",
        "error_tor_missing": "tor.exe não encontrado\nExecute setup.py primeiro.",
        "error_onion_invalid": "Insira um endereço .onion válido.",
        "error_tor_timeout": "Tor demorou demais.\nVerifique logs/tor.log",
        "error_connect": "Não foi possível conectar:\n",
        "back": "← Voltar",
        "server_ready": "[✅] Servidor pronto\n",
        "user_label": "    👤 Usuário: ",
        "exit_country": "     País saída: ",
        "onion_label": "    🌐 .onion: ",
        "client_connected": "[✅] Conectado\n",
        "onion_copied": "[📋 Endereço .onion copiado para a área de transferência]\n",
        "tor_nodes_title": "🔁 Nós do Circuito Tor",
        "tor_nodes_loading": "Consultando circuito...",
        "tor_nodes_error": "Não foi possível obter o circuito.\nCertifique-se de que o Tor está conectado.",
        "tor_nodes_close": "Fechar",
        "refresh_circuit": "🔄 Novo Circuito",
        "circuit_refreshing": "Solicitando novo circuito Tor...",
        "circuit_refreshed": "[🔄] Circuito Tor renovado. Detectando novo país...\n",
        "circuit_error": "[❌] Não foi possível renovar o circuito.\n",
        "kicked": "[🚫] Você foi expulso da sala.\n",
        "kick_ok": "[🚫] {user} foi expulso.\n",
        "kick_notfound": "[!] Usuário '{user}' não encontrado.\n",
        "kick_usage": "[!] Uso: /kick <nome_usuário>\n",
        "only_server_kick": "[!] Só o servidor pode usar /kick.\n",
        "users_connected": "[Conectados]: ",
        "user_joined": "✅ {user} entrou no chat  —  {country}\n",
        "user_left": "❌ {user} saiu do chat.\n",
        "welcome_msg": "\n👻 Bem-vindo, {user}! ({count} conectados)\n   /usuarios  /sair  /kick  /nos\n\n",
        "tor_circuit_label": "CIRCUITO TOR",
        "node_guard": "🛡️ Entrada (Guard)",
        "node_middle": "🔀 Intermediário",
        "node_exit": "🚪 Saída (Exit)",
        "unknown_country": "Desconhecido",
        "language_menu": "🌐 Idioma",
        "tor_nodes_btn": "🔍 Ver Nós",
        "ip_label": "IP: ",
        "circuit_node": "Nó",
        "fingerprint": "Impressão Digital",
        "country_flag": "País",
        "no_circuit_data": "Sem dados de circuito disponíveis.",
        "nodes_panel_title": "NÓS TOR",
    },
    "id": {
        "app_title": "👻 F3nixGhost",
        "select_language": "Pilih bahasa Anda",
        "select_language_sub": "Anda bisa mengubahnya nanti dari menu",
        "confirm": "Konfirmasi",
        "choose_role": "Pilih peran Anda",
        "role_subtitle": "Apakah Anda akan membuka chat atau terhubung ke chat?",
        "your_username": "👤  Nama pengguna Anda",
        "username_hint": "Begitulah orang lain akan melihat Anda di chat.",
        "username_placeholder": "Mis.: Alice, Bob, Anonim...",
        "server_title": "🖥️  Server",
        "server_desc": "Buka chat dan dapatkan alamat .onion untuk dibagikan.",
        "start_server": "Mulai sebagai Server →",
        "client_title": "💻  Klien",
        "client_desc": "Anda memiliki alamat .onion dan ingin terhubung.",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "Terhubung sebagai Klien →",
        "setup_hint": "Jalankan setup.py pertama kali untuk mengunduh Tor",
        "tor_ready": "● Tor: siap ✓",
        "tor_missing": "● Tor: jalankan setup.py",
        "tor_checking": "● Tor: memeriksa...",
        "starting_server": "Memulai Server...",
        "starting_tor": "Memulai Tor portabel...",
        "connecting_chat": "Menghubungkan ke Chat...",
        "connecting_tor": "Menghubungkan ke jaringan Tor...",
        "detecting_country": "🌍 Mendeteksi negara keluar Tor...",
        "generating_onion": "Membuat alamat .onion...",
        "starting_chat_server": "Memulai server chat...",
        "connected": "● Terhubung",
        "room": "RUANGAN",
        "commands": "PERINTAH",
        "cmd_users": "/pengguna",
        "cmd_users_desc": "lihat yang terhubung",
        "cmd_leave": "/keluar",
        "cmd_leave_desc": "putus sambungan",
        "cmd_kick": "/kick <pengguna>",
        "cmd_kick_desc": "tendang pengguna (hanya server)",
        "cmd_nodes": "/nodes",
        "cmd_nodes_desc": "lihat node Tor",
        "tor_exit": "KELUAR TOR",
        "your_address": "ALAMAT ANDA",
        "copy_onion": "📋 Salin .onion",
        "send": "Kirim",
        "write_message": "Tulis pesan...",
        "welcome": "👻 F3nixGhost dimulai. Selamat datang!\n",
        "server_closed": "\n[!] Server menutup koneksi.\n",
        "error_tor_missing": "tor.exe tidak ditemukan\nJalankan setup.py terlebih dahulu.",
        "error_onion_invalid": "Masukkan alamat .onion yang valid.",
        "error_tor_timeout": "Tor terlalu lama.\nPeriksa logs/tor.log",
        "error_connect": "Tidak dapat terhubung:\n",
        "back": "← Kembali",
        "server_ready": "[✅] Server siap\n",
        "user_label": "    👤 Pengguna: ",
        "exit_country": "     Negara keluar: ",
        "onion_label": "    🌐 .onion: ",
        "client_connected": "[✅] Terhubung\n",
        "onion_copied": "[📋 Alamat .onion disalin ke papan klip]\n",
        "tor_nodes_title": "🔁 Node Sirkuit Tor",
        "tor_nodes_loading": "Menanyakan sirkuit...",
        "tor_nodes_error": "Tidak dapat mendapatkan sirkuit.\nPastikan Tor terhubung.",
        "tor_nodes_close": "Tutup",
        "refresh_circuit": "🔄 Sirkuit Baru",
        "circuit_refreshing": "Meminta sirkuit Tor baru...",
        "circuit_refreshed": "[🔄] Sirkuit Tor diperbarui. Mendeteksi negara baru...\n",
        "circuit_error": "[❌] Tidak dapat memperbarui sirkuit.\n",
        "kicked": "[🚫] Anda dikeluarkan dari ruangan.\n",
        "kick_ok": "[🚫] {user} dikeluarkan.\n",
        "kick_notfound": "[!] Pengguna '{user}' tidak ditemukan.\n",
        "kick_usage": "[!] Penggunaan: /kick <nama_pengguna>\n",
        "only_server_kick": "[!] Hanya server yang dapat menggunakan /kick.\n",
        "users_connected": "[Terhubung]: ",
        "user_joined": "✅ {user} masuk chat  —  {country}\n",
        "user_left": "❌ {user} meninggalkan chat.\n",
        "welcome_msg": "\n👻 Selamat datang, {user}! ({count} terhubung)\n   /pengguna  /keluar  /kick  /nodes\n\n",
        "tor_circuit_label": "SIRKUIT TOR",
        "node_guard": "🛡️ Masuk (Guard)",
        "node_middle": "🔀 Tengah",
        "node_exit": "🚪 Keluar (Exit)",
        "unknown_country": "Tidak Diketahui",
        "language_menu": "🌐 Bahasa",
        "tor_nodes_btn": "🔍 Lihat Node",
        "ip_label": "IP: ",
        "circuit_node": "Node",
        "fingerprint": "Sidik Jari",
        "country_flag": "Negara",
        "no_circuit_data": "Tidak ada data sirkuit tersedia.",
        "nodes_panel_title": "NODE TOR",
    },
    "ru": {
        "app_title": "👻 F3nixGhost",
        "select_language": "Выберите язык",
        "select_language_sub": "Можно изменить позже в меню",
        "confirm": "Подтвердить",
        "choose_role": "Выберите роль",
        "role_subtitle": "Вы открываете чат или подключаетесь?",
        "your_username": "👤  Имя пользователя",
        "username_hint": "Так вас будут видеть другие в чате.",
        "username_placeholder": "Пр.: Alice, Bob, Аноним...",
        "server_title": "🖥️  Сервер",
        "server_desc": "Откройте чат и получите .onion-адрес для обмена.",
        "start_server": "Запустить как сервер →",
        "client_title": "💻  Клиент",
        "client_desc": "У вас есть .onion-адрес и вы хотите подключиться.",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "Подключиться как клиент →",
        "setup_hint": "Запустите setup.py в первый раз для загрузки Tor",
        "tor_ready": "● Tor: готов ✓",
        "tor_missing": "● Tor: запустите setup.py",
        "tor_checking": "● Tor: проверка...",
        "starting_server": "Запуск сервера...",
        "starting_tor": "Запуск портативного Tor...",
        "connecting_chat": "Подключение к чату...",
        "connecting_tor": "Подключение к сети Tor...",
        "detecting_country": "🌍 Определение страны выхода Tor...",
        "generating_onion": "Генерация .onion-адреса...",
        "starting_chat_server": "Запуск сервера чата...",
        "connected": "● Подключено",
        "room": "КОМНАТА",
        "commands": "КОМАНДЫ",
        "cmd_users": "/users",
        "cmd_users_desc": "просмотр подключённых",
        "cmd_leave": "/leave",
        "cmd_leave_desc": "отключиться",
        "cmd_kick": "/kick <пользователь>",
        "cmd_kick_desc": "выгнать (только сервер)",
        "cmd_nodes": "/nodes",
        "cmd_nodes_desc": "просмотр узлов Tor",
        "tor_exit": "ВЫХОД TOR",
        "your_address": "ВАШ АДРЕС",
        "copy_onion": "📋 Копировать .onion",
        "send": "Отправить",
        "write_message": "Написать сообщение...",
        "welcome": "👻 F3nixGhost запущен. Добро пожаловать!\n",
        "server_closed": "\n[!] Сервер закрыл соединение.\n",
        "error_tor_missing": "tor.exe не найден\nЗапустите setup.py сначала.",
        "error_onion_invalid": "Введите корректный .onion-адрес.",
        "error_tor_timeout": "Tor занял слишком много времени.\nПроверьте logs/tor.log",
        "error_connect": "Не удалось подключиться:\n",
        "back": "← Назад",
        "server_ready": "[✅] Сервер готов\n",
        "user_label": "    👤 Пользователь: ",
        "exit_country": "     Страна выхода: ",
        "onion_label": "    🌐 .onion: ",
        "client_connected": "[✅] Подключено\n",
        "onion_copied": "[📋 .onion-адрес скопирован в буфер обмена]\n",
        "tor_nodes_title": "🔁 Узлы цепи Tor",
        "tor_nodes_loading": "Запрос цепи...",
        "tor_nodes_error": "Не удалось получить цепь.\nУбедитесь, что Tor подключён.",
        "tor_nodes_close": "Закрыть",
        "refresh_circuit": "🔄 Новая цепь",
        "circuit_refreshing": "Запрос новой цепи Tor...",
        "circuit_refreshed": "[🔄] Цепь Tor обновлена. Определение новой страны...\n",
        "circuit_error": "[❌] Не удалось обновить цепь.\n",
        "kicked": "[🚫] Вас выгнали из комнаты.\n",
        "kick_ok": "[🚫] {user} выгнан.\n",
        "kick_notfound": "[!] Пользователь '{user}' не найден.\n",
        "kick_usage": "[!] Использование: /kick <имя_пользователя>\n",
        "only_server_kick": "[!] Только сервер может использовать /kick.\n",
        "users_connected": "[Подключены]: ",
        "user_joined": "✅ {user} вошёл в чат  —  {country}\n",
        "user_left": "❌ {user} покинул чат.\n",
        "welcome_msg": "\n👻 Добро пожаловать, {user}! ({count} подключено)\n   /users  /leave  /kick  /nodes\n\n",
        "tor_circuit_label": "ЦЕПЬ TOR",
        "node_guard": "🛡️ Вход (Guard)",
        "node_middle": "🔀 Средний",
        "node_exit": "🚪 Выход (Exit)",
        "unknown_country": "Неизвестно",
        "language_menu": "🌐 Язык",
        "tor_nodes_btn": "🔍 Узлы",
        "ip_label": "IP: ",
        "circuit_node": "Узел",
        "fingerprint": "Отпечаток",
        "country_flag": "Страна",
        "no_circuit_data": "Нет данных о цепи.",
        "nodes_panel_title": "УЗЛЫ TOR",
    },
    "fr": {
        "app_title": "👻 F3nixGhost",
        "select_language": "Choisissez votre langue",
        "select_language_sub": "Vous pouvez la changer plus tard depuis le menu",
        "confirm": "Confirmer",
        "choose_role": "Choisissez votre rôle",
        "role_subtitle": "Allez-vous ouvrir un chat ou vous connecter à un?",
        "your_username": "👤  Votre nom d'utilisateur",
        "username_hint": "C'est ainsi que les autres vous verront dans le chat.",
        "username_placeholder": "Ex.: Alice, Bob, Anonyme...",
        "server_title": "🖥️  Serveur",
        "server_desc": "Ouvrez le chat et obtenez une adresse .onion à partager.",
        "start_server": "Démarrer comme Serveur →",
        "client_title": "💻  Client",
        "client_desc": "Vous avez une adresse .onion et voulez vous connecter.",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "Se connecter comme Client →",
        "setup_hint": "Exécutez setup.py la première fois pour télécharger Tor",
        "tor_ready": "● Tor: prêt ✓",
        "tor_missing": "● Tor: exécutez setup.py",
        "tor_checking": "● Tor: vérification...",
        "starting_server": "Démarrage du Serveur...",
        "starting_tor": "Démarrage de Tor portable...",
        "connecting_chat": "Connexion au Chat...",
        "connecting_tor": "Connexion au réseau Tor...",
        "detecting_country": "🌍 Détection du pays de sortie Tor...",
        "generating_onion": "Génération de l'adresse .onion...",
        "starting_chat_server": "Démarrage du serveur de chat...",
        "connected": "● Connecté",
        "room": "SALLE",
        "commands": "COMMANDES",
        "cmd_users": "/utilisateurs",
        "cmd_users_desc": "voir connectés",
        "cmd_leave": "/quitter",
        "cmd_leave_desc": "se déconnecter",
        "cmd_kick": "/kick <utilisateur>",
        "cmd_kick_desc": "expulser (serveur seulement)",
        "cmd_nodes": "/noeuds",
        "cmd_nodes_desc": "voir les nœuds Tor",
        "tor_exit": "SORTIE TOR",
        "your_address": "VOTRE ADRESSE",
        "copy_onion": "📋 Copier .onion",
        "send": "Envoyer",
        "write_message": "Écrivez un message...",
        "welcome": "👻 F3nixGhost démarré. Bienvenue!\n",
        "server_closed": "\n[!] Le serveur a fermé la connexion.\n",
        "error_tor_missing": "tor.exe manquant\nExécutez setup.py d'abord.",
        "error_onion_invalid": "Entrez une adresse .onion valide.",
        "error_tor_timeout": "Tor a pris trop de temps.\nVérifiez logs/tor.log",
        "error_connect": "Impossible de se connecter:\n",
        "back": "← Retour",
        "server_ready": "[✅] Serveur prêt\n",
        "user_label": "    👤 Utilisateur: ",
        "exit_country": "     Pays de sortie: ",
        "onion_label": "    🌐 .onion: ",
        "client_connected": "[✅] Connecté\n",
        "onion_copied": "[📋 Adresse .onion copiée dans le presse-papiers]\n",
        "tor_nodes_title": "🔁 Nœuds du Circuit Tor",
        "tor_nodes_loading": "Interrogation du circuit...",
        "tor_nodes_error": "Impossible d'obtenir le circuit.\nAssurez-vous que Tor est connecté.",
        "tor_nodes_close": "Fermer",
        "refresh_circuit": "🔄 Nouveau Circuit",
        "circuit_refreshing": "Demande d'un nouveau circuit Tor...",
        "circuit_refreshed": "[🔄] Circuit Tor renouvelé. Détection du nouveau pays...\n",
        "circuit_error": "[❌] Impossible de renouveler le circuit.\n",
        "kicked": "[🚫] Vous avez été expulsé de la salle.\n",
        "kick_ok": "[🚫] {user} a été expulsé.\n",
        "kick_notfound": "[!] Utilisateur '{user}' introuvable.\n",
        "kick_usage": "[!] Usage: /kick <nom_utilisateur>\n",
        "only_server_kick": "[!] Seul le serveur peut utiliser /kick.\n",
        "users_connected": "[Connectés]: ",
        "user_joined": "✅ {user} a rejoint le chat  —  {country}\n",
        "user_left": "❌ {user} a quitté le chat.\n",
        "welcome_msg": "\n👻 Bienvenue, {user}! ({count} connectés)\n   /utilisateurs  /quitter  /kick  /noeuds\n\n",
        "tor_circuit_label": "CIRCUIT TOR",
        "node_guard": "🛡️ Entrée (Guard)",
        "node_middle": "🔀 Intermédiaire",
        "node_exit": "🚪 Sortie (Exit)",
        "unknown_country": "Inconnu",
        "language_menu": "🌐 Langue",
        "tor_nodes_btn": "🔍 Voir Nœuds",
        "ip_label": "IP: ",
        "circuit_node": "Nœud",
        "fingerprint": "Empreinte",
        "country_flag": "Pays",
        "no_circuit_data": "Aucune donnée de circuit disponible.",
        "nodes_panel_title": "NŒUDS TOR",
    },
    "de": {
        "app_title": "👻 F3nixGhost",
        "select_language": "Wählen Sie Ihre Sprache",
        "select_language_sub": "Sie können es später im Menü ändern",
        "confirm": "Bestätigen",
        "choose_role": "Wählen Sie Ihre Rolle",
        "role_subtitle": "Öffnen Sie einen Chat oder verbinden Sie sich mit einem?",
        "your_username": "👤  Ihr Benutzername",
        "username_hint": "So sehen andere Sie im Chat.",
        "username_placeholder": "Z.B.: Alice, Bob, Anonym...",
        "server_title": "🖥️  Server",
        "server_desc": "Öffnen Sie den Chat und erhalten Sie eine .onion-Adresse zum Teilen.",
        "start_server": "Als Server starten →",
        "client_title": "💻  Client",
        "client_desc": "Sie haben eine .onion-Adresse und möchten sich verbinden.",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "Als Client verbinden →",
        "setup_hint": "Führen Sie setup.py beim ersten Mal aus, um Tor herunterzuladen",
        "tor_ready": "● Tor: bereit ✓",
        "tor_missing": "● Tor: setup.py ausführen",
        "tor_checking": "● Tor: wird überprüft...",
        "starting_server": "Server wird gestartet...",
        "starting_tor": "Portables Tor wird gestartet...",
        "connecting_chat": "Verbindung zum Chat...",
        "connecting_tor": "Verbindung zum Tor-Netzwerk...",
        "detecting_country": "🌍 Erkenne Tor-Ausgangsland...",
        "generating_onion": ".onion-Adresse wird generiert...",
        "starting_chat_server": "Chat-Server wird gestartet...",
        "connected": "● Verbunden",
        "room": "RAUM",
        "commands": "BEFEHLE",
        "cmd_users": "/benutzer",
        "cmd_users_desc": "Verbundene anzeigen",
        "cmd_leave": "/verlassen",
        "cmd_leave_desc": "Trennen",
        "cmd_kick": "/kick <benutzer>",
        "cmd_kick_desc": "Benutzer rauswerfen (nur Server)",
        "cmd_nodes": "/knoten",
        "cmd_nodes_desc": "Tor-Knoten anzeigen",
        "tor_exit": "TOR-AUSGANG",
        "your_address": "IHRE ADRESSE",
        "copy_onion": "📋 .onion kopieren",
        "send": "Senden",
        "write_message": "Nachricht schreiben...",
        "welcome": "👻 F3nixGhost gestartet. Willkommen!\n",
        "server_closed": "\n[!] Der Server hat die Verbindung geschlossen.\n",
        "error_tor_missing": "tor.exe fehlt\nFühren Sie zuerst setup.py aus.",
        "error_onion_invalid": "Geben Sie eine gültige .onion-Adresse ein.",
        "error_tor_timeout": "Tor hat zu lange gedauert.\nÜberprüfen Sie logs/tor.log",
        "error_connect": "Verbindung fehlgeschlagen:\n",
        "back": "← Zurück",
        "server_ready": "[✅] Server bereit\n",
        "user_label": "    👤 Benutzer: ",
        "exit_country": "     Ausgangsland: ",
        "onion_label": "    🌐 .onion: ",
        "client_connected": "[✅] Verbunden\n",
        "onion_copied": "[📋 .onion-Adresse in die Zwischenablage kopiert]\n",
        "tor_nodes_title": "🔁 Tor-Schaltungsknoten",
        "tor_nodes_loading": "Schaltung wird abgefragt...",
        "tor_nodes_error": "Schaltung konnte nicht abgerufen werden.\nStellen Sie sicher, dass Tor verbunden ist.",
        "tor_nodes_close": "Schließen",
        "refresh_circuit": "🔄 Neue Schaltung",
        "circuit_refreshing": "Neue Tor-Schaltung wird angefordert...",
        "circuit_refreshed": "[🔄] Tor-Schaltung erneuert. Neues Land wird erkannt...\n",
        "circuit_error": "[❌] Schaltung konnte nicht erneuert werden.\n",
        "kicked": "[🚫] Sie wurden aus dem Raum geworfen.\n",
        "kick_ok": "[🚫] {user} wurde rausgeworfen.\n",
        "kick_notfound": "[!] Benutzer '{user}' nicht gefunden.\n",
        "kick_usage": "[!] Verwendung: /kick <benutzername>\n",
        "only_server_kick": "[!] Nur der Server kann /kick verwenden.\n",
        "users_connected": "[Verbunden]: ",
        "user_joined": "✅ {user} dem Chat beigetreten  —  {country}\n",
        "user_left": "❌ {user} hat den Chat verlassen.\n",
        "welcome_msg": "\n👻 Willkommen, {user}! ({count} verbunden)\n   /benutzer  /verlassen  /kick  /knoten\n\n",
        "tor_circuit_label": "TOR-SCHALTUNG",
        "node_guard": "🛡️ Eingang (Guard)",
        "node_middle": "🔀 Mitte",
        "node_exit": "🚪 Ausgang (Exit)",
        "unknown_country": "Unbekannt",
        "language_menu": "🌐 Sprache",
        "tor_nodes_btn": "🔍 Knoten anzeigen",
        "ip_label": "IP: ",
        "circuit_node": "Knoten",
        "fingerprint": "Fingerabdruck",
        "country_flag": "Land",
        "no_circuit_data": "Keine Schaltungsdaten verfügbar.",
        "nodes_panel_title": "TOR-KNOTEN",
    },
    "ja": {
        "app_title": "👻 F3nixGhost",
        "select_language": "言語を選択してください",
        "select_language_sub": "メニューから後で変更できます",
        "confirm": "確認",
        "choose_role": "役割を選択",
        "role_subtitle": "チャットを開きますか、接続しますか?",
        "your_username": "👤  ユーザー名",
        "username_hint": "チャットで他の人にこの名前で表示されます。",
        "username_placeholder": "例：Alice、Bob、匿名...",
        "server_title": "🖥️  サーバー",
        "server_desc": "チャットを開いて共有用の.onionアドレスを取得します。",
        "start_server": "サーバーとして開始 →",
        "client_title": "💻  クライアント",
        "client_desc": ".onionアドレスをお持ちで接続したい場合。",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "クライアントとして接続 →",
        "setup_hint": "最初にsetup.pyを実行してTorをダウンロード",
        "tor_ready": "● Tor: 準備完了 ✓",
        "tor_missing": "● Tor: setup.pyを実行してください",
        "tor_checking": "● Tor: 確認中...",
        "starting_server": "サーバーを起動中...",
        "starting_tor": "ポータブルTorを起動中...",
        "connecting_chat": "チャットに接続中...",
        "connecting_tor": "Torネットワークに接続中...",
        "detecting_country": "🌍 Tor出口国を検出中...",
        "generating_onion": ".onionアドレスを生成中...",
        "starting_chat_server": "チャットサーバーを起動中...",
        "connected": "● 接続済み",
        "room": "ルーム",
        "commands": "コマンド",
        "cmd_users": "/users",
        "cmd_users_desc": "接続者を表示",
        "cmd_leave": "/leave",
        "cmd_leave_desc": "切断",
        "cmd_kick": "/kick <ユーザー>",
        "cmd_kick_desc": "追放（サーバーのみ）",
        "cmd_nodes": "/nodes",
        "cmd_nodes_desc": "Torノードを表示",
        "tor_exit": "TOR出口",
        "your_address": "あなたのアドレス",
        "copy_onion": "📋 .onionをコピー",
        "send": "送信",
        "write_message": "メッセージを書く...",
        "welcome": "👻 F3nixGhostが起動しました。ようこそ!\n",
        "server_closed": "\n[!] サーバーが接続を閉じました。\n",
        "error_tor_missing": "tor.exeが見つかりません\n最初にsetup.pyを実行してください。",
        "error_onion_invalid": "有効な.onionアドレスを入力してください。",
        "error_tor_timeout": "Torの接続がタイムアウトしました。\nlogs/tor.logを確認してください",
        "error_connect": "接続できませんでした:\n",
        "back": "← 戻る",
        "server_ready": "[✅] サーバー準備完了\n",
        "user_label": "    👤 ユーザー: ",
        "exit_country": "     出口国: ",
        "onion_label": "    🌐 .onion: ",
        "client_connected": "[✅] 接続済み\n",
        "onion_copied": "[📋 .onionアドレスをクリップボードにコピーしました]\n",
        "tor_nodes_title": "🔁 Tor回路ノード",
        "tor_nodes_loading": "回路を照会中...",
        "tor_nodes_error": "回路を取得できませんでした。\nTorが接続されていることを確認してください。",
        "tor_nodes_close": "閉じる",
        "refresh_circuit": "🔄 新しい回路",
        "circuit_refreshing": "新しいTor回路をリクエスト中...",
        "circuit_refreshed": "[🔄] Tor回路が更新されました。新しい国を検出中...\n",
        "circuit_error": "[❌] 回路を更新できませんでした。\n",
        "kicked": "[🚫] 部屋から追放されました。\n",
        "kick_ok": "[🚫] {user}が追放されました。\n",
        "kick_notfound": "[!] ユーザー'{user}'が見つかりません。\n",
        "kick_usage": "[!] 使用法: /kick <ユーザー名>\n",
        "only_server_kick": "[!] /kickはサーバーのみ使用できます。\n",
        "users_connected": "[接続中]: ",
        "user_joined": "✅ {user}がチャットに参加  —  {country}\n",
        "user_left": "❌ {user}がチャットを退出しました。\n",
        "welcome_msg": "\n👻 ようこそ, {user}! ({count}人接続中)\n   /users  /leave  /kick  /nodes\n\n",
        "tor_circuit_label": "TOR回路",
        "node_guard": "🛡️ 入口 (Guard)",
        "node_middle": "🔀 中間",
        "node_exit": "🚪 出口 (Exit)",
        "unknown_country": "不明",
        "language_menu": "🌐 言語",
        "tor_nodes_btn": "🔍 ノードを表示",
        "ip_label": "IP: ",
        "circuit_node": "ノード",
        "fingerprint": "フィンガープリント",
        "country_flag": "国",
        "no_circuit_data": "回路データがありません。",
        "nodes_panel_title": "TORノード",
    },
    "ko": {
        "app_title": "👻 F3nixGhost",
        "select_language": "언어를 선택하세요",
        "select_language_sub": "나중에 메뉴에서 변경할 수 있습니다",
        "confirm": "확인",
        "choose_role": "역할 선택",
        "role_subtitle": "채팅을 열거나 참여하시겠습니까?",
        "your_username": "👤  사용자 이름",
        "username_hint": "채팅에서 다른 사람들이 이 이름으로 당신을 봅니다.",
        "username_placeholder": "예: Alice, Bob, 익명...",
        "server_title": "🖥️  서버",
        "server_desc": "채팅을 열고 공유할 .onion 주소를 받으세요.",
        "start_server": "서버로 시작 →",
        "client_title": "💻  클라이언트",
        "client_desc": ".onion 주소가 있고 연결하고 싶습니다.",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "클라이언트로 연결 →",
        "setup_hint": "처음에 setup.py를 실행하여 Tor를 다운로드",
        "tor_ready": "● Tor: 준비됨 ✓",
        "tor_missing": "● Tor: setup.py 실행 필요",
        "tor_checking": "● Tor: 확인 중...",
        "starting_server": "서버 시작 중...",
        "starting_tor": "포터블 Tor 시작 중...",
        "connecting_chat": "채팅에 연결 중...",
        "connecting_tor": "Tor 네트워크에 연결 중...",
        "detecting_country": "🌍 Tor 출구 국가 감지 중...",
        "generating_onion": ".onion 주소 생성 중...",
        "starting_chat_server": "채팅 서버 시작 중...",
        "connected": "● 연결됨",
        "room": "방",
        "commands": "명령어",
        "cmd_users": "/users",
        "cmd_users_desc": "연결된 사용자 보기",
        "cmd_leave": "/leave",
        "cmd_leave_desc": "연결 끊기",
        "cmd_kick": "/kick <사용자>",
        "cmd_kick_desc": "추방 (서버만)",
        "cmd_nodes": "/nodes",
        "cmd_nodes_desc": "Tor 노드 보기",
        "tor_exit": "TOR 출구",
        "your_address": "내 주소",
        "copy_onion": "📋 .onion 복사",
        "send": "보내기",
        "write_message": "메시지 작성...",
        "welcome": "👻 F3nixGhost 시작됨. 환영합니다!\n",
        "server_closed": "\n[!] 서버가 연결을 종료했습니다.\n",
        "error_tor_missing": "tor.exe를 찾을 수 없습니다\n먼저 setup.py를 실행하세요.",
        "error_onion_invalid": "유효한 .onion 주소를 입력하세요.",
        "error_tor_timeout": "Tor 연결 시간 초과.\nlogs/tor.log를 확인하세요",
        "error_connect": "연결할 수 없습니다:\n",
        "back": "← 뒤로",
        "server_ready": "[✅] 서버 준비됨\n",
        "user_label": "    👤 사용자: ",
        "exit_country": "     출구 국가: ",
        "onion_label": "    🌐 .onion: ",
        "client_connected": "[✅] 연결됨\n",
        "onion_copied": "[📋 .onion 주소가 클립보드에 복사됨]\n",
        "tor_nodes_title": "🔁 Tor 회로 노드",
        "tor_nodes_loading": "회로 조회 중...",
        "tor_nodes_error": "회로를 가져올 수 없습니다.\nTor가 연결되어 있는지 확인하세요.",
        "tor_nodes_close": "닫기",
        "refresh_circuit": "🔄 새 회로",
        "circuit_refreshing": "새 Tor 회로 요청 중...",
        "circuit_refreshed": "[🔄] Tor 회로 갱신됨. 새 국가 감지 중...\n",
        "circuit_error": "[❌] 회로를 갱신할 수 없습니다.\n",
        "kicked": "[🚫] 방에서 추방되었습니다.\n",
        "kick_ok": "[🚫] {user}가 추방되었습니다.\n",
        "kick_notfound": "[!] 사용자 '{user}'를 찾을 수 없습니다.\n",
        "kick_usage": "[!] 사용법: /kick <사용자이름>\n",
        "only_server_kick": "[!] 서버만 /kick을 사용할 수 있습니다.\n",
        "users_connected": "[연결됨]: ",
        "user_joined": "✅ {user}가 채팅에 참여  —  {country}\n",
        "user_left": "❌ {user}가 채팅을 떠났습니다.\n",
        "welcome_msg": "\n👻 환영합니다, {user}! ({count}명 연결됨)\n   /users  /leave  /kick  /nodes\n\n",
        "tor_circuit_label": "TOR 회로",
        "node_guard": "🛡️ 입구 (Guard)",
        "node_middle": "🔀 중간",
        "node_exit": "🚪 출구 (Exit)",
        "unknown_country": "알 수 없음",
        "language_menu": "🌐 언어",
        "tor_nodes_btn": "🔍 노드 보기",
        "ip_label": "IP: ",
        "circuit_node": "노드",
        "fingerprint": "지문",
        "country_flag": "국가",
        "no_circuit_data": "사용 가능한 회로 데이터 없음.",
        "nodes_panel_title": "TOR 노드",
    },
    "tr": {
        "app_title": "👻 F3nixGhost",
        "select_language": "Dilinizi seçin",
        "select_language_sub": "Daha sonra menüden değiştirebilirsiniz",
        "confirm": "Onayla",
        "choose_role": "Rolünüzü seçin",
        "role_subtitle": "Sohbet açacak mısınız yoksa birine mi bağlanacaksınız?",
        "your_username": "👤  Kullanıcı adınız",
        "username_hint": "Diğerleri sizi sohbette bu isimle görecek.",
        "username_placeholder": "Örn.: Alice, Bob, Anonim...",
        "server_title": "🖥️  Sunucu",
        "server_desc": "Sohbeti açın ve paylaşmak için .onion adresi alın.",
        "start_server": "Sunucu Olarak Başlat →",
        "client_title": "💻  İstemci",
        "client_desc": ".onion adresiniz var ve bağlanmak istiyorsunuz.",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "İstemci Olarak Bağlan →",
        "setup_hint": "Tor'u indirmek için ilk kez setup.py çalıştırın",
        "tor_ready": "● Tor: hazır ✓",
        "tor_missing": "● Tor: setup.py çalıştırın",
        "tor_checking": "● Tor: kontrol ediliyor...",
        "starting_server": "Sunucu başlatılıyor...",
        "starting_tor": "Taşınabilir Tor başlatılıyor...",
        "connecting_chat": "Sohbete bağlanılıyor...",
        "connecting_tor": "Tor ağına bağlanılıyor...",
        "detecting_country": "🌍 Tor çıkış ülkesi tespit ediliyor...",
        "generating_onion": ".onion adresi oluşturuluyor...",
        "starting_chat_server": "Sohbet sunucusu başlatılıyor...",
        "connected": "● Bağlı",
        "room": "ODA",
        "commands": "KOMUTLAR",
        "cmd_users": "/kullanicilar",
        "cmd_users_desc": "bağlıları gör",
        "cmd_leave": "/cikis",
        "cmd_leave_desc": "bağlantıyı kes",
        "cmd_kick": "/kick <kullanici>",
        "cmd_kick_desc": "kullanıcıyı at (sadece sunucu)",
        "cmd_nodes": "/dugumler",
        "cmd_nodes_desc": "Tor düğümlerini gör",
        "tor_exit": "TOR ÇIKIŞI",
        "your_address": "ADRESİNİZ",
        "copy_onion": "📋 .onion kopyala",
        "send": "Gönder",
        "write_message": "Mesaj yaz...",
        "welcome": "👻 F3nixGhost başladı. Hoş geldiniz!\n",
        "server_closed": "\n[!] Sunucu bağlantıyı kapattı.\n",
        "error_tor_missing": "tor.exe bulunamadı\nÖnce setup.py çalıştırın.",
        "error_onion_invalid": "Geçerli bir .onion adresi girin.",
        "error_tor_timeout": "Tor çok uzun sürdü.\nlogs/tor.log'u kontrol edin",
        "error_connect": "Bağlanılamadı:\n",
        "back": "← Geri",
        "server_ready": "[✅] Sunucu hazır\n",
        "user_label": "    👤 Kullanıcı: ",
        "exit_country": "     Çıkış ülkesi: ",
        "onion_label": "    🌐 .onion: ",
        "client_connected": "[✅] Bağlandı\n",
        "onion_copied": "[📋 .onion adresi panoya kopyalandı]\n",
        "tor_nodes_title": "🔁 Tor Devre Düğümleri",
        "tor_nodes_loading": "Devre sorgulanıyor...",
        "tor_nodes_error": "Devre alınamadı.\nTor'un bağlı olduğundan emin olun.",
        "tor_nodes_close": "Kapat",
        "refresh_circuit": "🔄 Yeni Devre",
        "circuit_refreshing": "Yeni Tor devresi isteniyor...",
        "circuit_refreshed": "[🔄] Tor devresi yenilendi. Yeni ülke tespit ediliyor...\n",
        "circuit_error": "[❌] Devre yenilenemedi.\n",
        "kicked": "[🚫] Odadan atıldınız.\n",
        "kick_ok": "[🚫] {user} atıldı.\n",
        "kick_notfound": "[!] Kullanıcı '{user}' bulunamadı.\n",
        "kick_usage": "[!] Kullanım: /kick <kullanici_adi>\n",
        "only_server_kick": "[!] Sadece sunucu /kick kullanabilir.\n",
        "users_connected": "[Bağlı]: ",
        "user_joined": "✅ {user} sohbete katıldı  —  {country}\n",
        "user_left": "❌ {user} sohbetten ayrıldı.\n",
        "welcome_msg": "\n👻 Hoş geldiniz, {user}! ({count} bağlı)\n   /kullanicilar  /cikis  /kick  /dugumler\n\n",
        "tor_circuit_label": "TOR DEVRESİ",
        "node_guard": "🛡️ Giriş (Guard)",
        "node_middle": "🔀 Orta",
        "node_exit": "🚪 Çıkış (Exit)",
        "unknown_country": "Bilinmiyor",
        "language_menu": "🌐 Dil",
        "tor_nodes_btn": "🔍 Düğümleri Gör",
        "ip_label": "IP: ",
        "circuit_node": "Düğüm",
        "fingerprint": "Parmak İzi",
        "country_flag": "Ülke",
        "no_circuit_data": "Devre verisi mevcut değil.",
        "nodes_panel_title": "TOR DÜĞÜMLERİ",
    },
    "vi": {
        "app_title": "👻 F3nixGhost",
        "select_language": "Chọn ngôn ngữ của bạn",
        "select_language_sub": "Bạn có thể thay đổi sau từ menu",
        "confirm": "Xác nhận",
        "choose_role": "Chọn vai trò của bạn",
        "role_subtitle": "Bạn sẽ mở chat hay kết nối vào một cuộc chat?",
        "your_username": "👤  Tên người dùng",
        "username_hint": "Những người khác sẽ thấy bạn với tên này trong chat.",
        "username_placeholder": "Vd.: Alice, Bob, Ẩn danh...",
        "server_title": "🖥️  Máy chủ",
        "server_desc": "Mở chat và nhận địa chỉ .onion để chia sẻ.",
        "start_server": "Khởi động làm Máy chủ →",
        "client_title": "💻  Máy khách",
        "client_desc": "Bạn có địa chỉ .onion và muốn kết nối.",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "Kết nối làm Máy khách →",
        "setup_hint": "Chạy setup.py lần đầu để tải Tor",
        "tor_ready": "● Tor: sẵn sàng ✓",
        "tor_missing": "● Tor: chạy setup.py",
        "tor_checking": "● Tor: đang kiểm tra...",
        "starting_server": "Đang khởi động Máy chủ...",
        "starting_tor": "Đang khởi động Tor di động...",
        "connecting_chat": "Đang kết nối Chat...",
        "connecting_tor": "Đang kết nối mạng Tor...",
        "detecting_country": "🌍 Đang phát hiện quốc gia thoát Tor...",
        "generating_onion": "Đang tạo địa chỉ .onion...",
        "starting_chat_server": "Đang khởi động máy chủ chat...",
        "connected": "● Đã kết nối",
        "room": "PHÒNG",
        "commands": "LỆNH",
        "cmd_users": "/users",
        "cmd_users_desc": "xem đã kết nối",
        "cmd_leave": "/leave",
        "cmd_leave_desc": "ngắt kết nối",
        "cmd_kick": "/kick <nguoidung>",
        "cmd_kick_desc": "đuổi người dùng (chỉ máy chủ)",
        "cmd_nodes": "/nodes",
        "cmd_nodes_desc": "xem nút Tor",
        "tor_exit": "THOÁT TOR",
        "your_address": "ĐỊA CHỈ CỦA BẠN",
        "copy_onion": "📋 Sao chép .onion",
        "send": "Gửi",
        "write_message": "Viết tin nhắn...",
        "welcome": "👻 F3nixGhost đã khởi động. Chào mừng!\n",
        "server_closed": "\n[!] Máy chủ đã đóng kết nối.\n",
        "error_tor_missing": "Không tìm thấy tor.exe\nChạy setup.py trước.",
        "error_onion_invalid": "Nhập địa chỉ .onion hợp lệ.",
        "error_tor_timeout": "Tor mất quá nhiều thời gian.\nKiểm tra logs/tor.log",
        "error_connect": "Không thể kết nối:\n",
        "back": "← Quay lại",
        "server_ready": "[✅] Máy chủ sẵn sàng\n",
        "user_label": "    👤 Người dùng: ",
        "exit_country": "     Quốc gia thoát: ",
        "onion_label": "    🌐 .onion: ",
        "client_connected": "[✅] Đã kết nối\n",
        "onion_copied": "[📋 Địa chỉ .onion đã sao chép vào clipboard]\n",
        "tor_nodes_title": "🔁 Nút Mạch Tor",
        "tor_nodes_loading": "Đang truy vấn mạch...",
        "tor_nodes_error": "Không thể lấy mạch.\nĐảm bảo Tor đã kết nối.",
        "tor_nodes_close": "Đóng",
        "refresh_circuit": "🔄 Mạch Mới",
        "circuit_refreshing": "Yêu cầu mạch Tor mới...",
        "circuit_refreshed": "[🔄] Mạch Tor đã được làm mới. Đang phát hiện quốc gia mới...\n",
        "circuit_error": "[❌] Không thể làm mới mạch.\n",
        "kicked": "[🚫] Bạn đã bị đuổi khỏi phòng.\n",
        "kick_ok": "[🚫] {user} đã bị đuổi.\n",
        "kick_notfound": "[!] Không tìm thấy người dùng '{user}'.\n",
        "kick_usage": "[!] Cách dùng: /kick <tên_người_dùng>\n",
        "only_server_kick": "[!] Chỉ máy chủ mới có thể dùng /kick.\n",
        "users_connected": "[Đã kết nối]: ",
        "user_joined": "✅ {user} đã tham gia chat  —  {country}\n",
        "user_left": "❌ {user} đã rời chat.\n",
        "welcome_msg": "\n👻 Chào mừng, {user}! ({count} đã kết nối)\n   /users  /leave  /kick  /nodes\n\n",
        "tor_circuit_label": "MẠCH TOR",
        "node_guard": "🛡️ Vào (Guard)",
        "node_middle": "🔀 Giữa",
        "node_exit": "🚪 Thoát (Exit)",
        "unknown_country": "Không rõ",
        "language_menu": "🌐 Ngôn ngữ",
        "tor_nodes_btn": "🔍 Xem Nút",
        "ip_label": "IP: ",
        "circuit_node": "Nút",
        "fingerprint": "Dấu vân tay",
        "country_flag": "Quốc gia",
        "no_circuit_data": "Không có dữ liệu mạch.",
        "nodes_panel_title": "NÚT TOR",
    },
    "bn": {
        "app_title": "👻 F3nixGhost",
        "select_language": "আপনার ভাষা বেছে নিন",
        "select_language_sub": "পরে মেনু থেকে পরিবর্তন করতে পারবেন",
        "confirm": "নিশ্চিত করুন",
        "choose_role": "আপনার ভূমিকা বেছে নিন",
        "role_subtitle": "আপনি চ্যাট খুলবেন নাকি যোগ দেবেন?",
        "your_username": "👤  আপনার ব্যবহারকারীর নাম",
        "username_hint": "চ্যাটে অন্যরা এই নামে আপনাকে দেখবে।",
        "username_placeholder": "যেমন: Alice, Bob, বেনামী...",
        "server_title": "🖥️  সার্ভার",
        "server_desc": "চ্যাট খুলুন এবং শেয়ার করার জন্য .onion ঠিকানা পান।",
        "start_server": "সার্ভার হিসেবে শুরু করুন →",
        "client_title": "💻  ক্লায়েন্ট",
        "client_desc": "আপনার কাছে .onion ঠিকানা আছে এবং সংযুক্ত হতে চান।",
        "onion_placeholder": "abc123xyz.onion",
        "connect_client": "ক্লায়েন্ট হিসেবে সংযুক্ত হন →",
        "setup_hint": "Tor ডাউনলোড করতে প্রথমবার setup.py চালান",
        "tor_ready": "● Tor: প্রস্তুত ✓",
        "tor_missing": "● Tor: setup.py চালান",
        "tor_checking": "● Tor: যাচাই করা হচ্ছে...",
        "starting_server": "সার্ভার শুরু হচ্ছে...",
        "starting_tor": "পোর্টেবল Tor শুরু হচ্ছে...",
        "connecting_chat": "চ্যাটে সংযুক্ত হচ্ছে...",
        "connecting_tor": "Tor নেটওয়ার্কে সংযুক্ত হচ্ছে...",
        "detecting_country": "🌍 Tor বের হওয়ার দেশ শনাক্ত করা হচ্ছে...",
        "generating_onion": ".onion ঠিকানা তৈরি হচ্ছে...",
        "starting_chat_server": "চ্যাট সার্ভার শুরু হচ্ছে...",
        "connected": "● সংযুক্ত",
        "room": "রুম",
        "commands": "কমান্ড",
        "cmd_users": "/users",
        "cmd_users_desc": "সংযুক্তদের দেখুন",
        "cmd_leave": "/leave",
        "cmd_leave_desc": "সংযোগ বিচ্ছিন্ন করুন",
        "cmd_kick": "/kick <ব্যবহারকারী>",
        "cmd_kick_desc": "বের করুন (শুধু সার্ভার)",
        "cmd_nodes": "/nodes",
        "cmd_nodes_desc": "Tor নোড দেখুন",
        "tor_exit": "TOR প্রস্থান",
        "your_address": "আপনার ঠিকানা",
        "copy_onion": "📋 .onion কপি করুন",
        "send": "পাঠান",
        "write_message": "বার্তা লিখুন...",
        "welcome": "👻 F3nixGhost শুরু হয়েছে। স্বাগতম!\n",
        "server_closed": "\n[!] সার্ভার সংযোগ বন্ধ করেছে।\n",
        "error_tor_missing": "tor.exe পাওয়া যায়নি\nআগে setup.py চালান।",
        "error_onion_invalid": "একটি বৈধ .onion ঠিকানা দিন।",
        "error_tor_timeout": "Tor অনেক সময় নিয়েছে।\nlogs/tor.log পরীক্ষা করুন",
        "error_connect": "সংযুক্ত হওয়া যায়নি:\n",
        "back": "← ফিরে যান",
        "server_ready": "[✅] সার্ভার প্রস্তুত\n",
        "user_label": "    👤 ব্যবহারকারী: ",
        "exit_country": "     প্রস্থান দেশ: ",
        "onion_label": "    🌐 .onion: ",
        "client_connected": "[✅] সংযুক্ত\n",
        "onion_copied": "[📋 .onion ঠিকানা ক্লিপবোর্ডে কপি হয়েছে]\n",
        "tor_nodes_title": "🔁 Tor সার্কিট নোড",
        "tor_nodes_loading": "সার্কিট জিজ্ঞাসা করা হচ্ছে...",
        "tor_nodes_error": "সার্কিট পাওয়া যায়নি।\nTor সংযুক্ত আছে কিনা নিশ্চিত করুন।",
        "tor_nodes_close": "বন্ধ করুন",
        "refresh_circuit": "🔄 নতুন সার্কিট",
        "circuit_refreshing": "নতুন Tor সার্কিটের অনুরোধ...",
        "circuit_refreshed": "[🔄] Tor সার্কিট নবায়ন হয়েছে। নতুন দেশ শনাক্ত হচ্ছে...\n",
        "circuit_error": "[❌] সার্কিট নবায়ন করা যায়নি।\n",
        "kicked": "[🚫] আপনাকে রুম থেকে বের করা হয়েছে।\n",
        "kick_ok": "[🚫] {user} কে বের করা হয়েছে।\n",
        "kick_notfound": "[!] ব্যবহারকারী '{user}' পাওয়া যায়নি।\n",
        "kick_usage": "[!] ব্যবহার: /kick <ব্যবহারকারীর_নাম>\n",
        "only_server_kick": "[!] শুধু সার্ভার /kick ব্যবহার করতে পারে।\n",
        "users_connected": "[সংযুক্ত]: ",
        "user_joined": "✅ {user} চ্যাটে যোগ দিয়েছে  —  {country}\n",
        "user_left": "❌ {user} চ্যাট ছেড়েছে।\n",
        "welcome_msg": "\n👻 স্বাগতম, {user}! ({count} জন সংযুক্ত)\n   /users  /leave  /kick  /nodes\n\n",
        "tor_circuit_label": "TOR সার্কিট",
        "node_guard": "🛡️ প্রবেশ (Guard)",
        "node_middle": "🔀 মধ্যবর্তী",
        "node_exit": "🚪 প্রস্থান (Exit)",
        "unknown_country": "অজানা",
        "language_menu": "🌐 ভাষা",
        "tor_nodes_btn": "🔍 নোড দেখুন",
        "ip_label": "IP: ",
        "circuit_node": "নোড",
        "fingerprint": "ফিঙ্গারপ্রিন্ট",
        "country_flag": "দেশ",
        "no_circuit_data": "কোনো সার্কিট ডেটা নেই।",
        "nodes_panel_title": "TOR নোড",
    },
}

# Fallback: copy missing keys from 'es'
for lang_code, lang_data in TRANSLATIONS.items():
    for key, val in TRANSLATIONS["es"].items():
        if key not in lang_data:
            lang_data[key] = val

# ══════════════════════════════════════════════════════════════
#  GESTIÓN DE IDIOMA
# ══════════════════════════════════════════════════════════════

def cargar_idioma():
    if os.path.exists(LANG_FILE):
        try:
            with open(LANG_FILE, "r") as f:
                data = json.load(f)
                return data.get("lang", None)
        except Exception:
            pass
    return None

def guardar_idioma(code):
    with open(LANG_FILE, "w") as f:
        json.dump({"lang": code}, f)

_lang_code = cargar_idioma() or "es"

def T(key):
    """Obtiene texto traducido para la clave dada."""
    return TRANSLATIONS.get(_lang_code, TRANSLATIONS["es"]).get(key, TRANSLATIONS["es"].get(key, key))


# ══════════════════════════════════════════════════════════════
#  LÓGICA TOR
# ══════════════════════════════════════════════════════════════

def tor_disponible():
    return os.path.exists(TOR_EXE)

def escribir_torrc(es_servidor=False):
    os.makedirs(TOR_DATA, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    cfg = (
        f"SocksPort {SOCKS_PORT}\n"
        f"ControlPort {CONTROL_PORT}\n"
        f"CookieAuthentication 0\n"
        f"DataDirectory {TOR_DATA}\n"
        f"Log notice file {TOR_LOG}\n"
        f"CircuitBuildTimeout 60\n"
    )
    if es_servidor:
        os.makedirs(HS_DIR, exist_ok=True)
        cfg += f"\nHiddenServiceDir {HS_DIR}\n"
        cfg += f"HiddenServicePort {CHAT_PORT} 127.0.0.1:{CHAT_PORT}\n"
    with open(TORRC, "w") as f:
        f.write(cfg)

def iniciar_tor_proceso(es_servidor=False):
    global _tor_proc
    escribir_torrc(es_servidor)
    _tor_proc = subprocess.Popen(
        [TOR_EXE, "-f", TORRC],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

def esperar_tor(timeout=120):
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            s = socket.socket()
            s.settimeout(2)
            s.connect(("127.0.0.1", SOCKS_PORT))
            s.close()
            return True
        except Exception:
            time.sleep(2)
    return False

def leer_onion():
    f = os.path.join(HS_DIR, "hostname")
    for _ in range(20):
        if os.path.exists(f):
            return open(f).read().strip()
        time.sleep(1)
    return None

def detener_tor():
    global _tor_proc
    if _tor_proc and _tor_proc.poll() is None:
        _tor_proc.terminate()
    _tor_proc = None

def obtener_pais_tor():
    try:
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, "127.0.0.1", SOCKS_PORT)
        s.settimeout(15)
        s.connect(("ip-api.com", 80))
        s.sendall(b"GET /json/?fields=country,countryCode,query HTTP/1.0\r\nHost: ip-api.com\r\n\r\n")
        resp = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            resp += chunk
        s.close()
        body = resp.split(b"\r\n\r\n", 1)[-1].decode("utf-8", errors="ignore")
        data = json.loads(body)
        pais   = data.get("country", T("unknown_country"))
        codigo = data.get("countryCode", "??")
        ip     = data.get("query", "???")
        bandera = "".join(chr(0x1F1E6 + ord(c) - ord('A')) for c in codigo.upper())
        return {"pais": pais, "codigo": codigo, "bandera": bandera, "ip": ip}
    except Exception:
        return {"pais": T("unknown_country"), "codigo": "??", "bandera": "🌐", "ip": "???"}

def _tor_control_cmd(cmds, timeout=5):
    """Envía una lista de comandos al Control Port y retorna la respuesta completa."""
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect(("127.0.0.1", CONTROL_PORT))
        s.sendall(b"AUTHENTICATE\r\n")
        auth_resp = s.recv(256).decode("utf-8", errors="ignore")
        if "250" not in auth_resp:
            s.close()
            return ""
        result = ""
        for cmd in cmds:
            s.sendall((cmd + "\r\n").encode("utf-8"))
            data = b""
            s.settimeout(3)
            try:
                while True:
                    chunk = s.recv(8192)
                    if not chunk:
                        break
                    data += chunk
                    decoded = data.decode("utf-8", errors="ignore")
                    if decoded.strip().endswith("250 OK") or "\r\n250 " in decoded:
                        break
            except Exception:
                pass
            result += data.decode("utf-8", errors="ignore")
        s.close()
        return result
    except Exception:
        return ""

def _geoip_pais(ip):
    """Retorna (pais, bandera) para una IP pública usando ip-api.com via Tor SOCKS5."""
    if not ip or ip in ("??", "???", ""):
        return T("unknown_country"), "🌐"
    try:
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, "127.0.0.1", SOCKS_PORT)
        s.settimeout(10)
        s.connect(("ip-api.com", 80))
        req = f"GET /json/{ip}?fields=country,countryCode HTTP/1.0\r\nHost: ip-api.com\r\n\r\n"
        s.sendall(req.encode("utf-8"))
        resp = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            resp += chunk
        s.close()
        body = resp.split(b"\r\n\r\n", 1)[-1].decode("utf-8", errors="ignore")
        data = json.loads(body)
        pais   = data.get("country", T("unknown_country"))
        codigo = data.get("countryCode", "??")
        bandera = "".join(chr(0x1F1E6 + ord(c) - ord('A')) for c in codigo.upper()) if len(codigo) == 2 else "🌐"
        return pais, bandera
    except Exception:
        return T("unknown_country"), "🌐"

def obtener_nodos_circuito():
    """
    Consulta los nodos del circuito Tor activo via Control Port.
    Para cada nodo obtiene: nickname, fingerprint, IP y país.
    """
    nodes = []
    try:
        # 1) Obtener estado de circuitos
        resp_circ = _tor_control_cmd(["GETINFO circuit-status"])
        hops_raw = []
        for line in resp_circ.split("\n"):
            if "BUILT" in line:
                parts = line.split()
                if len(parts) >= 3:
                    route_str = parts[2]
                    hops_raw = route_str.split(",")
                    break

        if not hops_raw:
            return nodes

        # 2) Para cada hop extraer fingerprint completo y nickname
        for i, hop in enumerate(hops_raw[:3]):
            hop = hop.strip()
            fp_full = hop.lstrip("$").split("~")[0]
            fp_short = fp_full[:8] + "..." if len(fp_full) >= 8 else fp_full
            nickname = hop.split("~")[1] if "~" in hop else "???"
            role_key = ["node_guard", "node_middle", "node_exit"][min(i, 2)]

            # 3) Obtener IP del relay via GETINFO ns/id/<fingerprint>
            ip_relay = "??"
            if fp_full and fp_full != "??":
                ns_resp = _tor_control_cmd([f"GETINFO ns/id/{fp_full}"])
                # La línea "r <nickname> <base64id> <base64digest> <date> <time> <IP> <ORPort> <DirPort>"
                for ns_line in ns_resp.split("\n"):
                    if ns_line.startswith("r ") or "250+ns/id" in ns_line:
                        # buscar la línea 'r' en el bloque
                        pass
                    if re.match(r"r\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\d+\.\d+\.\d+\.\d+)", ns_line):
                        m = re.match(r"r\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\d+\.\d+\.\d+\.\d+)", ns_line)
                        if m:
                            ip_relay = m.group(1)
                            break

            # 4) Si tenemos IP, consultar país
            if ip_relay not in ("??", "???", ""):
                pais, bandera = _geoip_pais(ip_relay)
            else:
                # Intentar via GETINFO ip-to-country si está disponible
                pais, bandera = T("unknown_country"), "🌐"

            nodes.append({
                "role_key": role_key,
                "nickname": nickname,
                "fingerprint": fp_short,
                "ip": ip_relay,
                "country": pais,
                "flag": bandera,
            })

    except Exception:
        pass
    return nodes

def renovar_circuito():
    """Envía NEWNYM al Control Port para cambiar el circuito Tor."""
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect(("127.0.0.1", CONTROL_PORT))
        s.sendall(b"AUTHENTICATE\r\n")
        resp = s.recv(256).decode("utf-8", errors="ignore")
        if "250" not in resp:
            s.close()
            return False
        s.sendall(b"SIGNAL NEWNYM\r\n")
        resp2 = s.recv(256).decode("utf-8", errors="ignore")
        s.close()
        return "250" in resp2
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════
#  SERVIDOR DE CHAT
# ══════════════════════════════════════════════════════════════

clientes = {}          # socket → nombre
clientes_lock = threading.Lock()
_servidor_socket = None

# Banderas/país por usuario (para el panel lateral)
_usuarios_info = {}          # nombre → {"bandera": "🇨🇭", "pais": "Switzerland", "ip": "..."}
_usuarios_info_lock = threading.Lock()

# Ban y mute (servidor)
_baneados   = set()          # nombres baneados (no pueden reconectar)
_muteados   = {}             # nombre → timestamp hasta cuando está muteado
_topic      = ""             # tema actual de la sala

def ts():
    return datetime.now().strftime("%H:%M:%S")

def broadcast(msg, remitente=None, log_fn=None):
    with clientes_lock:
        muertos = []
        for s in clientes:
            if s != remitente:
                try:
                    s.sendall(msg.encode("utf-8"))
                except Exception:
                    muertos.append(s)
        for s in muertos:
            clientes.pop(s, None)

def kick_usuario(nombre_objetivo, log_fn):
    """Expulsa a un usuario de la sala por nombre."""
    with clientes_lock:
        objetivo = None
        for s, n in clientes.items():
            if n.lower() == nombre_objetivo.lower():
                objetivo = s
                break
    if objetivo:
        try:
            objetivo.sendall("__KICKED__".encode("utf-8"))
            time.sleep(0.2)
            objetivo.close()
        except Exception:
            pass
        with clientes_lock:
            clientes.pop(objetivo, None)
        return True
    return False

def ban_usuario(nombre_objetivo, log_fn):
    """Expulsa y banea a un usuario (no puede reconectar en esta sesión)."""
    _baneados.add(nombre_objetivo.lower())
    return kick_usuario(nombre_objetivo, log_fn)

def mute_usuario(nombre_objetivo, segundos, log_fn):
    """Silencia a un usuario por X segundos."""
    with clientes_lock:
        existe = any(n.lower() == nombre_objetivo.lower() for n in clientes.values())
    if not existe:
        return False
    _muteados[nombre_objetivo.lower()] = time.time() + segundos
    return True

def esta_muteado(nombre):
    exp = _muteados.get(nombre.lower(), 0)
    if time.time() < exp:
        return True
    _muteados.pop(nombre.lower(), None)
    return False

def broadcast_privado(nombre_destino, msg):
    """Envía un mensaje privado a un usuario específico."""
    with clientes_lock:
        for s, n in clientes.items():
            if n.lower() == nombre_destino.lower():
                try:
                    s.sendall(msg.encode("utf-8"))
                    return True
                except Exception:
                    pass
    return False


def manejar_cliente_srv(conn, addr, log_fn):
    nombre = "?"
    try:
        conn.sendall("__PEDIR_NOMBRE__".encode("utf-8"))
        nombre = conn.recv(1024).decode("utf-8", errors="ignore").strip() or f"User_{addr[1]}"

        # Verificar ban
        if nombre.lower() in _baneados:
            conn.sendall("__BANNED__".encode("utf-8"))
            conn.close()
            return

        conn.sendall("__PEDIR_PAIS__".encode("utf-8"))
        info_pais = conn.recv(1024).decode("utf-8", errors="ignore").strip()

        # Parsear bandera, país e IP del string "🇨🇭 Switzerland (IP: x.x.x.x)"
        bandera_usr, pais_usr, ip_usr = "🌐", info_pais, "?"
        m_ip = re.search(r'\(IP: ([^)]+)\)', info_pais)
        if m_ip:
            ip_usr   = m_ip.group(1)
            pais_usr = info_pais[:m_ip.start()].strip()
        if pais_usr and len(pais_usr) >= 2 and 0x1F1E6 <= ord(pais_usr[0]) <= 0x1F1FF:
            bandera_usr = pais_usr[:2]
            pais_usr    = pais_usr[2:].strip()
        with _usuarios_info_lock:
            _usuarios_info[nombre] = {"bandera": bandera_usr, "pais": pais_usr, "ip": ip_usr}

        with clientes_lock:
            clientes[conn] = nombre

        bienvenida = T("welcome_msg").format(user=nombre, count=len(clientes))
        conn.sendall(bienvenida.encode("utf-8"))

        aviso = f"[{ts()}] " + T("user_joined").format(user=nombre, country=info_pais)
        log_fn(aviso, "green")
        broadcast(aviso, remitente=conn, log_fn=log_fn)

        while True:
            data = conn.recv(4096)
            if not data:
                break
            txt = data.decode("utf-8", errors="ignore").strip()

            cmd_lower = txt.lower()
            # Comandos multi-idioma: /salir /leave /sair /cikis /keluar /quitter /verlassen
            leave_cmds = ["/salir", "/leave", "/sair", "/cikis", "/keluar", "/quitter", "/verlassen"]
            # Comandos /usuarios /users /pengguna /benutzer etc.
            users_cmds = ["/usuarios", "/users", "/pengguna", "/benutzer", "/utilisateurs",
                          "/kullanicilar", "/user", "/nos", "/noeuds"]

            if cmd_lower in leave_cmds:
                break
            elif cmd_lower in users_cmds:
                with clientes_lock:
                    lista = ", ".join(clientes.values())
                conn.sendall(f"{T('users_connected')}{lista}\n".encode("utf-8"))
            elif cmd_lower.startswith("/kick "):
                objetivo = txt[6:].strip()
                if kick_usuario(objetivo, log_fn):
                    msg_kick = f"[{ts()}] " + T("kick_ok").format(user=objetivo)
                    log_fn(msg_kick, "red")
                    broadcast(msg_kick, log_fn=log_fn)
                    conn.sendall(msg_kick.encode("utf-8"))
                else:
                    conn.sendall(T("kick_notfound").format(user=objetivo).encode("utf-8"))
            elif txt:
                if esta_muteado(nombre):
                    conn.sendall(f"[🔇] Estás muteado. Esperá antes de enviar.\n".encode("utf-8"))
                    continue
                msg = f"[{ts()}] {nombre}: {txt}\n"
                log_fn(msg, "normal")
                broadcast(msg, remitente=conn, log_fn=log_fn)

    except Exception:
        pass
    finally:
        with clientes_lock:
            clientes.pop(conn, None)
        with _usuarios_info_lock:
            _usuarios_info.pop(nombre, None)
        try:
            conn.close()
        except Exception:
            pass
        dep = f"[{ts()}] " + T("user_left").format(user=nombre)
        log_fn(dep, "red")
        broadcast(dep, log_fn=log_fn)

def correr_servidor(log_fn):
    global _servidor_socket
    _servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _servidor_socket.bind(("127.0.0.1", CHAT_PORT))
    _servidor_socket.listen(10)
    while True:
        try:
            conn, addr = _servidor_socket.accept()
            t = threading.Thread(target=manejar_cliente_srv, args=(conn, addr, log_fn), daemon=True)
            t.start()
        except Exception:
            break


# ══════════════════════════════════════════════════════════════
#  VENTANA DE SELECCIÓN DE IDIOMA
# ══════════════════════════════════════════════════════════════

class LangSelector(ctk.CTkToplevel):
    def __init__(self, parent, on_select, first_time=True):
        super().__init__(parent)
        self.title("🌐 F3nixGhost — Language / Idioma")
        self.geometry("440x590")
        self.resizable(False, False)
        self.configure(fg_color=C_BG)
        self.grab_set()
        self._on_select = on_select
        self._first_time = first_time
        self._selected_code = _lang_code
        self._btn_widgets = {}
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="🌐", font=("Segoe UI Emoji", 44)).pack(pady=(24,4))

        if self._first_time:
            ctk.CTkLabel(self, text="Choose your language / Elegí tu idioma",
                         font=("Consolas", 14, "bold"), text_color=C_ONION2).pack()
            ctk.CTkLabel(self, text="Select one to continue • Seleccioná para continuar",
                         font=("Consolas", 9), text_color=C_MUTED).pack(pady=(2,12))
        else:
            ctk.CTkLabel(self, text=T("language_menu"),
                         font=("Consolas", 15, "bold"), text_color=C_ONION2).pack()
            current_name = LANGUAGES.get(_lang_code, _lang_code)
            ctk.CTkLabel(self, text=f"  {current_name}  →  ?",
                         font=("Consolas", 9), text_color=C_MUTED).pack(pady=(2,12))

        scroll = ctk.CTkScrollableFrame(self, fg_color=C_PANEL, corner_radius=10,
                                         width=380, height=360)
        scroll.pack(padx=24, pady=(0,12))

        for code, name in LANGUAGES.items():
            is_sel = (code == self._selected_code)
            btn = ctk.CTkButton(
                scroll, text=("✓  " if is_sel else "    ") + name,
                fg_color=C_ONION if is_sel else C_CARD,
                hover_color=C_ONION2,
                font=("Segoe UI", 12, "bold" if is_sel else "normal"),
                height=36, corner_radius=7, anchor="w",
                command=lambda c=code: self._pick(c)
            )
            btn.pack(fill="x", padx=8, pady=2)
            self._btn_widgets[code] = btn

        confirm_text = "✓  Confirm / Confirmar" if self._first_time else f"✓  {T('confirm')}"
        self._btn_confirm = ctk.CTkButton(
            self, text=confirm_text,
            fg_color=C_ONION, hover_color=C_ONION2,
            font=("Consolas", 13, "bold"), height=38, corner_radius=8,
            command=self._confirmar
        )
        self._btn_confirm.pack(fill="x", padx=24, pady=(0,16))

    def _pick(self, code):
        # Deselect previous
        old = self._selected_code
        if old in self._btn_widgets:
            old_name = LANGUAGES.get(old, old)
            self._btn_widgets[old].configure(
                fg_color=C_CARD,
                font=("Segoe UI", 12, "normal"),
                text="    " + old_name
            )
        # Select new
        self._selected_code = code
        new_name = LANGUAGES.get(code, code)
        self._btn_widgets[code].configure(
            fg_color=C_ONION,
            font=("Segoe UI", 12, "bold"),
            text="✓  " + new_name
        )

    def _confirmar(self):
        self._on_select(self._selected_code)
        self.destroy()


# ══════════════════════════════════════════════════════════════
#  VENTANA DE NODOS TOR
# ══════════════════════════════════════════════════════════════

class NodosWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(T("tor_nodes_title"))
        self.geometry("520x500")
        self.resizable(False, True)
        self.configure(fg_color=C_BG)
        self.grab_set()
        self._construir()

    def _construir(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=C_PANEL, height=64, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="🔁", font=("Segoe UI Emoji", 28)).pack(side="left", padx=16, pady=10)
        title_col = ctk.CTkFrame(hdr, fg_color="transparent")
        title_col.pack(side="left", pady=10)
        ctk.CTkLabel(title_col, text=T("tor_nodes_title"),
                     font=("Consolas", 13, "bold"), text_color=C_ONION2).pack(anchor="w")
        ctk.CTkLabel(title_col, text=T("tor_nodes_loading"),
                     font=("Consolas", 9), text_color=C_MUTED).pack(anchor="w")

        # Progress bar while loading
        self._progress = ctk.CTkProgressBar(self, fg_color=C_CARD, progress_color=C_ONION)
        self._progress.pack(fill="x", padx=0, pady=0)
        self._progress.configure(mode="indeterminate")
        self._progress.start()

        # Scrollable frame for nodes
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=C_BG, corner_radius=0)
        self._scroll.pack(fill="both", expand=True, padx=0, pady=0)

        self._lbl_status = ctk.CTkLabel(self._scroll, text=T("tor_nodes_loading"),
                                         font=("Consolas", 11), text_color=C_MUTED)
        self._lbl_status.pack(pady=40)

        # Footer buttons
        footer = ctk.CTkFrame(self, fg_color=C_PANEL, height=48, corner_radius=0)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        ctk.CTkButton(footer, text=T("tor_nodes_close"),
                      fg_color=C_CARD, hover_color=C_BORDER,
                      font=("Consolas", 11), height=32, width=110, corner_radius=7,
                      command=self.destroy).pack(side="right", padx=12, pady=8)
        ctk.CTkButton(footer, text="🔄 " + T("refresh_circuit"),
                      fg_color="#1a2744", hover_color="#2d4080",
                      font=("Consolas", 10), height=32, width=140, corner_radius=7,
                      command=self._reload).pack(side="right", padx=(0,6), pady=8)

        threading.Thread(target=self._cargar_nodos, daemon=True).start()

    def _reload(self):
        # Limpiar y recargar
        for w in self._scroll.winfo_children():
            w.destroy()
        self._lbl_status = ctk.CTkLabel(self._scroll, text=T("tor_nodes_loading"),
                                         font=("Consolas", 11), text_color=C_MUTED)
        self._lbl_status.pack(pady=40)
        self._progress.start()
        threading.Thread(target=self._cargar_nodos, daemon=True).start()

    def _cargar_nodos(self):
        nodes = obtener_nodos_circuito()
        def _do():
            self._progress.stop()
            self._progress.set(1.0)
            try:
                self._lbl_status.destroy()
            except Exception:
                pass
            # Limpiar scroll por si es recarga
            for w in self._scroll.winfo_children():
                w.destroy()

            if not nodes:
                ctk.CTkLabel(self._scroll, text=T("tor_nodes_error"),
                             font=("Consolas", 11), text_color=C_RED,
                             justify="center").pack(pady=30)
                return

            role_colors = [C_GREEN, C_BLUE, C_YELLOW]
            role_icons  = ["🛡️", "🔀", "🚪"]
            hop_arrows  = ["", "  ↓\n", "  ↓\n"]

            for i, node in enumerate(nodes[:3]):
                if i > 0:
                    ctk.CTkLabel(self._scroll, text="  │", font=("Consolas", 11),
                                 text_color=C_MUTED).pack(anchor="w", padx=28, pady=0)

                card = ctk.CTkFrame(self._scroll, fg_color=C_CARD, corner_radius=10)
                card.pack(fill="x", padx=16, pady=4)

                # Header de la card: ícono + rol
                top = ctk.CTkFrame(card, fg_color="#1a1a2e", corner_radius=8)
                top.pack(fill="x", padx=8, pady=(8,0))
                icon = role_icons[i]
                role_label = T(node["role_key"])
                ctk.CTkLabel(top, text=f"  {icon}  {role_label}",
                             font=("Consolas", 12, "bold"),
                             text_color=role_colors[i]).pack(side="left", padx=8, pady=6)

                # País con bandera — lo más visible
                flag  = node.get("flag", "🌐")
                pais  = node.get("country", T("unknown_country"))
                ctk.CTkLabel(top, text=f"{flag}  {pais}",
                             font=("Segoe UI Emoji", 12),
                             text_color=C_TEXT).pack(side="right", padx=12, pady=6)

                # Detalles: nickname, fingerprint, IP
                details = ctk.CTkFrame(card, fg_color="transparent")
                details.pack(fill="x", padx=16, pady=(6,10))

                nick = node.get("nickname", "???")
                fp   = node.get("fingerprint", "???")
                ip   = node.get("ip", "??")

                rows = [
                    (T("circuit_node") + ":", nick, C_BLUE),
                    (T("fingerprint") + ":", fp, C_MUTED),
                    (T("ip_label").rstrip(": ") + ":", ip, C_MUTED),
                    (T("country_flag") + ":", f"{flag} {pais}", C_TEXT),
                ]
                for label, value, vcol in rows:
                    row = ctk.CTkFrame(details, fg_color="transparent")
                    row.pack(fill="x", pady=1)
                    ctk.CTkLabel(row, text=label, font=("Consolas", 9),
                                 text_color=C_MUTED, width=90, anchor="e").pack(side="left")
                    ctk.CTkLabel(row, text="  " + value, font=("Consolas", 9),
                                 text_color=vcol, anchor="w").pack(side="left")

        self.after(0, _do)


# ══════════════════════════════════════════════════════════════
#  APP PRINCIPAL
# ══════════════════════════════════════════════════════════════

class F3nixGhostApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        global _lang_code
        self.title(T("app_title"))
        self.geometry("900x640")
        self.minsize(740, 540)
        self.configure(fg_color=C_BG)
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar)

        self._modo        = None
        self._chat_socket = None
        self._onion       = None
        self._mi_nombre   = "Anónimo"
        self._mi_pais     = {}
        self._es_servidor = False
        self._session_start = None   # datetime de inicio de sesión
        self._msgs_enviados = 0      # contador de mensajes
        self._autokill_job  = None   # after() id para autokill

        # Si no hay idioma guardado → selector obligatorio primera vez
        # Si ya hay uno guardado → ir directo al splash (recuerda el último elegido)
        saved_lang = cargar_idioma()
        if saved_lang is None:
            self.withdraw()
            self.after(200, lambda: self._mostrar_selector_idioma_inicial(first_time=True))
        else:
            self._construir_splash()

    def _mostrar_selector_idioma_inicial(self, first_time=True):
        def on_select(code):
            global _lang_code
            _lang_code = code
            guardar_idioma(code)
            self.deiconify()
            self._construir_splash()

        win = LangSelector(self, on_select, first_time=True)
        # No permitir cerrar sin elegir — es la primera vez
        win.protocol("WM_DELETE_WINDOW", lambda: None)

    def _cambiar_idioma(self):
        def on_select(code):
            global _lang_code
            _lang_code = code
            guardar_idioma(code)
            # Rebuild splash
            try:
                self._frame_splash.destroy()
            except Exception:
                pass
            self._construir_splash()
        LangSelector(self, on_select, first_time=False)

    # ── SPLASH ────────────────────────────────────────────────
    def _construir_splash(self):
        self._frame_splash = ctk.CTkFrame(self, fg_color=C_BG)
        self._frame_splash.pack(fill="both", expand=True)

        left = ctk.CTkFrame(self._frame_splash, fg_color=C_PANEL, width=270, corner_radius=0)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="👻", font=("Segoe UI Emoji", 60)).pack(pady=(40,8))
        ctk.CTkLabel(left, text="F3nixGhost", font=("Consolas", 26, "bold"),
                     text_color=C_ONION2).pack()
        ctk.CTkLabel(left, text="Comunicación anónima\nsobre la red Tor",
                     font=("Consolas", 10), text_color=C_MUTED, justify="center").pack(pady=(6,24))

        for txt, col in [("🔒 Tráfico cifrado por Tor", C_GREEN),
                         ("🌐 Dirección .onion privada", C_GREEN),
                         ("👤 IP real oculta", C_GREEN),
                         ("🌍 País de salida visible", C_GREEN),
                         ("📦 Tor portable incluido", C_GREEN),
                         ("🔄 Cambio de circuito", C_GREEN),
                         ("🔍 Nodos visibles", C_GREEN)]:
            ctk.CTkLabel(left, text=txt, font=("Consolas", 10),
                         text_color=col, anchor="w").pack(anchor="w", padx=22, pady=1)

        self._lbl_tor_status = ctk.CTkLabel(left, text=T("tor_checking"),
                     font=("Consolas", 10), text_color=C_YELLOW)
        self._lbl_tor_status.pack(pady=(14,4))
        self.after(500, self._verificar_tor_splash)

        # Botón cambiar idioma en sidebar
        ctk.CTkButton(left, text=T("language_menu"), height=26,
                      fg_color=C_CARD, hover_color=C_BORDER,
                      font=("Consolas", 10), corner_radius=6,
                      command=self._cambiar_idioma).pack(side="bottom", fill="x", padx=16, pady=14)

        right = ctk.CTkFrame(self._frame_splash, fg_color=C_BG)
        right.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(right, text=T("choose_role"),
                     font=("Consolas", 20, "bold"), text_color=C_TEXT).pack(pady=(30,4))
        ctk.CTkLabel(right, text=T("role_subtitle"),
                     font=("Consolas", 10), text_color=C_MUTED).pack(pady=(0,12))

        # Campo nombre
        nombre_card = ctk.CTkFrame(right, fg_color=C_CARD, corner_radius=10)
        nombre_card.pack(fill="x", padx=40, pady=(0,10))
        ctk.CTkLabel(nombre_card, text=T("your_username"),
                     font=("Consolas", 12, "bold"), text_color=C_BLUE).pack(anchor="w", padx=18, pady=(12,2))
        ctk.CTkLabel(nombre_card, text=T("username_hint"),
                     font=("Consolas", 9), text_color=C_MUTED).pack(anchor="w", padx=18)
        self._entry_nombre = ctk.CTkEntry(nombre_card, placeholder_text=T("username_placeholder"),
                                           fg_color=C_INPUT_BG, border_color=C_BORDER,
                                           font=("Consolas", 12), height=32, corner_radius=8)
        self._entry_nombre.pack(fill="x", padx=18, pady=(6,12))

        # Tarjeta servidor
        card_srv = ctk.CTkFrame(right, fg_color=C_CARD, corner_radius=10)
        card_srv.pack(fill="x", padx=40, pady=4)
        ctk.CTkLabel(card_srv, text=T("server_title"),
                     font=("Consolas", 13, "bold"), text_color=C_ONION2).pack(anchor="w", padx=18, pady=(12,2))
        ctk.CTkLabel(card_srv, text=T("server_desc"),
                     font=("Consolas", 9), text_color=C_MUTED).pack(anchor="w", padx=18, pady=(0,8))
        ctk.CTkButton(card_srv, text=T("start_server"),
                      fg_color=C_ONION, hover_color=C_ONION2,
                      font=("Consolas", 12, "bold"), height=32, corner_radius=8,
                      command=self._iniciar_servidor).pack(fill="x", padx=18, pady=(0,12))

        # Tarjeta cliente
        card_cli = ctk.CTkFrame(right, fg_color=C_CARD, corner_radius=10)
        card_cli.pack(fill="x", padx=40, pady=4)
        ctk.CTkLabel(card_cli, text=T("client_title"),
                     font=("Consolas", 13, "bold"), text_color=C_GREEN).pack(anchor="w", padx=18, pady=(12,2))
        ctk.CTkLabel(card_cli, text=T("client_desc"),
                     font=("Consolas", 9), text_color=C_MUTED).pack(anchor="w", padx=18, pady=(0,4))
        self._entry_onion = ctk.CTkEntry(card_cli, placeholder_text=T("onion_placeholder"),
                                          fg_color=C_INPUT_BG, border_color=C_BORDER,
                                          font=("Consolas", 11), height=30, corner_radius=8)
        self._entry_onion.pack(fill="x", padx=18, pady=(0,6))
        ctk.CTkButton(card_cli, text=T("connect_client"),
                      fg_color="#166534", hover_color=C_GREEN,
                      font=("Consolas", 12, "bold"), height=32, corner_radius=8,
                      command=self._iniciar_cliente).pack(fill="x", padx=18, pady=(0,12))

        ctk.CTkLabel(right, text=T("setup_hint"),
                     font=("Consolas", 9), text_color=C_MUTED).pack(side="bottom", pady=8)

    def _verificar_tor_splash(self):
        if tor_disponible():
            self._lbl_tor_status.configure(text=T("tor_ready"), text_color=C_GREEN)
        else:
            self._lbl_tor_status.configure(text=T("tor_missing"), text_color=C_RED)

    def _leer_nombre(self):
        n = self._entry_nombre.get().strip()
        self._mi_nombre = n if n else "Anónimo"

    # ── LOADING ───────────────────────────────────────────────
    def _mostrar_loading(self, titulo, subtitulo):
        self._frame_splash.pack_forget()
        self._frame_loading = ctk.CTkFrame(self, fg_color=C_BG)
        self._frame_loading.pack(fill="both", expand=True)
        ctk.CTkLabel(self._frame_loading, text="👻", font=("Segoe UI Emoji", 52)).pack(pady=(80,10))
        ctk.CTkLabel(self._frame_loading, text=titulo,
                     font=("Consolas", 20, "bold"), text_color=C_ONION2).pack()
        self._lbl_loading_sub = ctk.CTkLabel(self._frame_loading, text=subtitulo,
                     font=("Consolas", 11), text_color=C_MUTED)
        self._lbl_loading_sub.pack(pady=8)
        self._progress = ctk.CTkProgressBar(self._frame_loading, width=340,
                                             fg_color=C_CARD, progress_color=C_ONION)
        self._progress.pack(pady=16)
        self._progress.configure(mode="indeterminate")
        self._progress.start()

    def _actualizar_loading(self, texto):
        try:
            self._lbl_loading_sub.configure(text=texto)
        except Exception:
            pass

    # ── CHAT ──────────────────────────────────────────────────
    def _construir_chat(self, titulo_extra=""):
        try:
            self._frame_loading.pack_forget()
        except Exception:
            pass

        self._frame_chat = ctk.CTkFrame(self, fg_color=C_BG)
        self._frame_chat.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(self._frame_chat, fg_color=C_PANEL, height=50, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="👻 F3nixGhost",
                     font=("Consolas", 13, "bold"), text_color=C_ONION2).pack(side="left", padx=14)
        ctk.CTkLabel(header, text=f"👤 {self._mi_nombre}",
                     font=("Consolas", 11, "bold"), text_color=C_BLUE).pack(side="left", padx=8)
        if self._mi_pais:
            p = self._mi_pais
            ctk.CTkLabel(header, text=f"{p.get('bandera','')} {p.get('pais','')}",
                         font=("Consolas", 10), text_color=C_MUTED).pack(side="left", padx=4)
        if titulo_extra:
            lbl = ctk.CTkLabel(header, text=titulo_extra,
                               font=("Consolas", 8), text_color=C_MUTED, cursor="hand2")
            lbl.pack(side="left", padx=6)
            lbl.bind("<Button-1>", lambda e: self._copiar_onion())
        ctk.CTkLabel(header, text=T("connected"),
                     font=("Consolas", 10), text_color=C_GREEN).pack(side="right", padx=(4,14))
        # Contador de usuarios en tiempo real
        self._lbl_contador = ctk.CTkLabel(header, text="● 1",
                     font=("Consolas", 11, "bold"), text_color=C_GREEN)
        self._lbl_contador.pack(side="right", padx=(14,2))

        # Sidebar
        sidebar = ctk.CTkScrollableFrame(self._frame_chat, fg_color=C_PANEL, width=182, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text=T("room"), font=("Consolas", 8, "bold"),
                     text_color=C_MUTED).pack(anchor="w", padx=14, pady=(14,2))
        ctk.CTkLabel(sidebar, text="# general", font=("Consolas", 11),
                     text_color=C_ONION2).pack(anchor="w", padx=14)

        ctk.CTkLabel(sidebar, text=T("commands"), font=("Consolas", 8, "bold"),
                     text_color=C_MUTED).pack(anchor="w", padx=14, pady=(14,2))
        ctk.CTkLabel(sidebar, text="/help", font=("Consolas", 10), text_color=C_ONION2).pack(anchor="w", padx=14)
        ctk.CTkLabel(sidebar, text="ver todos los comandos", font=("Consolas", 7), text_color=C_MUTED).pack(anchor="w", padx=14, pady=(0,2))

        # Badge de país de salida con bandera grande
        if self._mi_pais:
            p = self._mi_pais
            ctk.CTkLabel(sidebar, text=T("tor_exit"), font=("Consolas", 8, "bold"),
                         text_color=C_MUTED).pack(anchor="w", padx=14, pady=(14,4))
            pais_box = ctk.CTkFrame(sidebar, fg_color=C_CARD, corner_radius=7)
            pais_box.pack(fill="x", padx=10)
            # Bandera grande
            ctk.CTkLabel(pais_box, text=p.get('bandera', '🌐'),
                         font=("Segoe UI Emoji", 32)).pack(pady=(10,2))
            ctk.CTkLabel(pais_box, text=p.get('pais', '?'),
                         font=("Consolas", 11, "bold"), text_color=C_TEXT).pack()
            ctk.CTkLabel(pais_box, text=f"{T('ip_label')}{p.get('ip','???')}",
                         font=("Consolas", 8), text_color=C_MUTED).pack(pady=(0,8))

        # Panel de usuarios conectados con banderas
        ctk.CTkLabel(sidebar, text="USUARIOS ONLINE", font=("Consolas", 8, "bold"),
                     text_color=C_MUTED).pack(anchor="w", padx=14, pady=(14,4))
        self._frame_users_panel = ctk.CTkFrame(sidebar, fg_color="transparent")
        self._frame_users_panel.pack(fill="x", padx=8)
        self._dibujar_usuario_fila(
            self._frame_users_panel,
            self._mi_nombre,
            self._mi_pais.get("bandera", "🌐") if self._mi_pais else "🌐",
            self._mi_pais.get("pais", "?") if self._mi_pais else "?",
            es_yo=True
        )

        # Botones de nodos y nuevo circuito
        ctk.CTkLabel(sidebar, text=T("tor_circuit_label"), font=("Consolas", 8, "bold"),
                     text_color=C_MUTED).pack(anchor="w", padx=14, pady=(14,4))

        ctk.CTkButton(sidebar, text=T("tor_nodes_btn"), height=28,
                      fg_color=C_CARD, hover_color=C_BORDER,
                      font=("Consolas", 9), corner_radius=6,
                      command=self._abrir_nodos).pack(fill="x", padx=10, pady=(0,4))

        ctk.CTkButton(sidebar, text=T("refresh_circuit"), height=28,
                      fg_color="#1a2744", hover_color="#2d4080",
                      font=("Consolas", 9), corner_radius=6,
                      command=self._renovar_circuito).pack(fill="x", padx=10, pady=(0,4))

        # Tu dirección .onion (servidor)
        if self._es_servidor and self._onion:
            ctk.CTkLabel(sidebar, text=T("your_address"), font=("Consolas", 8, "bold"),
                         text_color=C_MUTED).pack(anchor="w", padx=14, pady=(14,4))
            ctk.CTkLabel(sidebar, text=self._onion[:22]+"...", font=("Consolas", 8),
                         text_color=C_GREEN, wraplength=155).pack(anchor="w", padx=14)
            ctk.CTkButton(sidebar, text=T("copy_onion"), height=26,
                          fg_color=C_CARD, hover_color=C_BORDER,
                          font=("Consolas", 9), corner_radius=6,
                          command=self._copiar_onion).pack(fill="x", padx=10, pady=5)

        # Área de mensajes
        main = ctk.CTkFrame(self._frame_chat, fg_color=C_BG)
        main.pack(side="right", fill="both", expand=True)

        self._textbox = ctk.CTkTextbox(main, fg_color=C_CARD, text_color=C_TEXT,
                                        font=("Consolas", 12), corner_radius=0,
                                        border_width=0, wrap="word")
        self._textbox.pack(fill="both", expand=True, padx=(1,0))
        self._textbox.configure(state="disabled")

        for tag, color in [("green", C_GREEN), ("red", C_RED), ("yellow", C_YELLOW),
                            ("onion", C_ONION2), ("muted", C_MUTED), ("blue", C_BLUE)]:
            self._textbox._textbox.tag_config(tag, foreground=color)

        # Barra input
        input_frame = ctk.CTkFrame(main, fg_color=C_PANEL, height=52, corner_radius=0)
        input_frame.pack(fill="x")
        input_frame.pack_propagate(False)

        ctk.CTkLabel(input_frame, text=f"{self._mi_nombre}:",
                     font=("Consolas", 11, "bold"), text_color=C_YELLOW).pack(side="left", padx=(12,4), pady=10)
        self._entry_msg = ctk.CTkEntry(input_frame, placeholder_text=T("write_message"),
                                        fg_color=C_INPUT_BG, border_color=C_BORDER,
                                        font=("Consolas", 12), height=32, corner_radius=8)
        self._entry_msg.pack(side="left", fill="x", expand=True, padx=(0,6), pady=10)
        self._entry_msg.bind("<Return>", lambda e: self._enviar_mensaje())
        ctk.CTkButton(input_frame, text=T("send"), width=78, height=32,
                      fg_color=C_ONION, hover_color=C_ONION2,
                      font=("Consolas", 12, "bold"), corner_radius=8,
                      command=self._enviar_mensaje).pack(side="right", padx=(0,12), pady=10)

        self._log_chat(T("welcome"), "onion")
        self._session_start = datetime.now()
        self._msgs_enviados = 0
        self._poll_usuarios()

    def _dibujar_usuario_fila(self, parent, nombre, bandera, pais, es_yo=False):
        """Dibuja una fila de usuario con dot verde, bandera y nombre."""
        row = ctk.CTkFrame(parent, fg_color=C_CARD if es_yo else "transparent", corner_radius=5)
        row.pack(fill="x", pady=2)
        # Dot verde
        ctk.CTkFrame(row, fg_color=C_GREEN, width=6, height=6, corner_radius=3
                     ).pack(side="left", padx=(8,4), pady=10)
        # Bandera + info
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, pady=4)
        name_txt = nombre + (" (vos)" if es_yo else "")
        ctk.CTkLabel(info, text=name_txt,
                     font=("Consolas", 9, "bold" if es_yo else "normal"),
                     text_color=C_ONION2 if es_yo else C_TEXT,
                     anchor="w").pack(anchor="w")
        ctk.CTkLabel(info, text=f"{bandera} {pais[:15]}",
                     font=("Segoe UI Emoji", 9),
                     text_color=C_MUTED, anchor="w").pack(anchor="w")

    def _poll_usuarios(self):
        """Actualiza contador y panel de usuarios cada 2 segundos."""
        try:
            # Actualizar contador
            if self._es_servidor:
                with clientes_lock:
                    total = len(clientes) + 1  # +1 = el servidor mismo
            else:
                total = 1
            self._lbl_contador.configure(text=f"● {total}")

            # Actualizar panel de usuarios (solo servidor tiene la info)
            if self._es_servidor:
                for w in self._frame_users_panel.winfo_children():
                    w.destroy()
                # Usuario propio primero
                p = self._mi_pais or {}
                self._dibujar_usuario_fila(
                    self._frame_users_panel,
                    self._mi_nombre,
                    p.get("bandera", "🌐"), p.get("pais", "?"),
                    es_yo=True
                )
                # Resto de usuarios
                with _usuarios_info_lock:
                    snap = dict(_usuarios_info)
                for nombre, info in snap.items():
                    self._dibujar_usuario_fila(
                        self._frame_users_panel,
                        nombre,
                        info.get("bandera", "🌐"), info.get("pais", "?"),
                        es_yo=False
                    )
        except Exception:
            pass
        self.after(2000, self._poll_usuarios)

    def _log_chat(self, texto, color="normal"):
        def _do():
            self._textbox.configure(state="normal")
            if color == "normal":
                self._textbox.insert("end", texto)
            else:
                self._textbox._textbox.insert("end", texto, color)
            self._textbox.configure(state="disabled")
            self._textbox.see("end")
        self.after(0, _do)

    def _enviar_mensaje(self):
        txt = self._entry_msg.get().strip()
        if not txt:
            return
        self._entry_msg.delete(0, "end")

        cmd_lower = txt.lower()

        # ── /help ─────────────────────────────────────────────
        if cmd_lower in ("/help", "/ayuda", "/hilfe", "/aide"):
            self._cmd_help()
            return

        # ── /clearscreen ──────────────────────────────────────
        if cmd_lower in ("/clearscreen", "/cls", "/clear", "/limpiar"):
            self._textbox.configure(state="normal")
            self._textbox.delete("0.0", "end")
            self._textbox.configure(state="disabled")
            self._log_chat("[🧹 Pantalla limpiada]\n", "muted")
            return

        # ── /whoami ───────────────────────────────────────────
        if cmd_lower in ("/whoami", "/yo", "/me"):
            self._cmd_whoami()
            return

        # ── /uptime ───────────────────────────────────────────
        if cmd_lower in ("/uptime", "/tiempo"):
            if self._session_start:
                delta = datetime.now() - self._session_start
                h, rem = divmod(int(delta.total_seconds()), 3600)
                m, s   = divmod(rem, 60)
                self._log_chat(f"[⏱] Sesión activa: {h:02d}h {m:02d}m {s:02d}s\n", "blue")
            return

        # ── /stats ────────────────────────────────────────────
        if cmd_lower in ("/stats", "/estadisticas"):
            self._cmd_stats()
            return

        # ── /autokill ─────────────────────────────────────────
        if cmd_lower.startswith("/autokill"):
            parts = txt.split()
            if len(parts) == 2 and parts[1].isdigit():
                mins = int(parts[1])
                if self._autokill_job:
                    self.after_cancel(self._autokill_job)
                ms = mins * 60 * 1000
                self._autokill_job = self.after(ms, self.al_cerrar)
                self._log_chat(f"[💣] AutoKill activado: la app se cerrará en {mins} min.\n", "yellow")
            else:
                self._log_chat("[!] Uso: /autokill <minutos>\n", "red")
            return

        # ── /nick ─────────────────────────────────────────────
        if cmd_lower.startswith("/nick "):
            nuevo = txt[6:].strip()
            if nuevo:
                viejo = self._mi_nombre
                self._mi_nombre = nuevo
                self._log_chat(f"[✏️] Nombre cambiado: {viejo} → {nuevo}\n", "green")
                # Notificar al servidor si somos cliente
                if self._modo == "cliente" and self._chat_socket:
                    try:
                        self._chat_socket.sendall(f"[✏️] {viejo} ahora es {nuevo}\n".encode("utf-8"))
                    except Exception:
                        pass
            return

        # ── /nodos ────────────────────────────────────────────
        nodes_cmds = ["/nodos", "/nodes", "/noeuds", "/knoten", "/dugumler"]
        if cmd_lower in nodes_cmds:
            self._abrir_nodos()
            return

        # ── /newcircuit ───────────────────────────────────────
        refresh_cmds = ["/newcircuit", "/nuevocircuito", "/neueschaltung"]
        if cmd_lower in refresh_cmds:
            self._renovar_circuito()
            return

        # ── Comandos modo CLIENTE ─────────────────────────────
        if self._modo == "cliente" and self._chat_socket:
            if cmd_lower.startswith("/kick"):
                self._log_chat(T("only_server_kick"), "red")
                return
            try:
                self._chat_socket.sendall(txt.encode("utf-8"))
                self._log_chat(f"[{ts()}] {self._mi_nombre}: {txt}\n", "yellow")
                self._msgs_enviados += 1
                leave_cmds = ["/salir", "/leave", "/sair", "/cikis", "/keluar", "/quitter", "/verlassen"]
                if cmd_lower in leave_cmds:
                    self.al_cerrar()
            except Exception as e:
                self._log_chat(f"[ERROR] {e}\n", "red")
            return

        # ── Comandos modo SERVIDOR ────────────────────────────
        if self._modo == "servidor":

            # /kick
            if cmd_lower.startswith("/kick "):
                objetivo = txt[6:].strip()
                if kick_usuario(objetivo, self._log_chat):
                    msg_kick = f"[{ts()}] " + T("kick_ok").format(user=objetivo)
                    self._log_chat(msg_kick, "red")
                    broadcast(msg_kick)
                else:
                    self._log_chat(T("kick_notfound").format(user=objetivo), "red")
                return

            # /ban
            if cmd_lower.startswith("/ban "):
                objetivo = txt[5:].strip()
                if ban_usuario(objetivo, self._log_chat):
                    msg_ban = f"[🚫] {objetivo} ha sido baneado.\n"
                    self._log_chat(msg_ban, "red")
                    broadcast(msg_ban)
                else:
                    self._log_chat(f"[!] Usuario '{objetivo}' no encontrado.\n", "red")
                return

            # /mute
            if cmd_lower.startswith("/mute "):
                parts = txt.split()
                if len(parts) >= 2:
                    objetivo = parts[1]
                    segs = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else 60
                    if mute_usuario(objetivo, segs, self._log_chat):
                        msg_mute = f"[🔇] {objetivo} muteado por {segs} segundos.\n"
                        self._log_chat(msg_mute, "yellow")
                        broadcast(msg_mute)
                    else:
                        self._log_chat(f"[!] Usuario '{objetivo}' no encontrado.\n", "red")
                return

            # /msg (privado desde servidor)
            if cmd_lower.startswith("/msg "):
                parts = txt.split(" ", 2)
                if len(parts) == 3:
                    dest, cuerpo = parts[1], parts[2]
                    pm = f"[📨 PM de {self._mi_nombre}]: {cuerpo}\n"
                    if broadcast_privado(dest, pm):
                        self._log_chat(f"[📨 PM → {dest}]: {cuerpo}\n", "blue")
                    else:
                        self._log_chat(f"[!] Usuario '{dest}' no encontrado.\n", "red")
                else:
                    self._log_chat("[!] Uso: /msg <usuario> <mensaje>\n", "red")
                return

            # /usuarios
            users_cmds = ["/usuarios", "/users", "/pengguna", "/benutzer",
                          "/utilisateurs", "/kullanicilar"]
            if cmd_lower in users_cmds:
                with clientes_lock:
                    lista = ", ".join(clientes.values())
                self._log_chat(f"{T('users_connected')}{lista}\n", "blue")
                return

            # Mensaje normal del servidor
            msg = f"[{ts()}] {self._mi_nombre} (srv): {txt}\n"
            self._log_chat(msg, "yellow")
            self._msgs_enviados += 1
            broadcast(msg)

    def _cmd_help(self):
        """Muestra todos los comandos disponibles."""
        es_srv = self._es_servidor
        lineas = [
            "\n╔══════════════════════════════════════════╗\n",
            "║         👻 F3nixGhost — COMANDOS         ║\n",
            "╚══════════════════════════════════════════╝\n",
            "\n🔒  PRIVACIDAD & SEGURIDAD\n",
            "  /whoami         → Tu IP, país, onion y circuito Tor\n",
            "  /nodos          → Ver los 3 nodos del circuito Tor\n",
            "  /newcircuit     → Cambiar circuito Tor (nuevo país)\n",
            "  /autokill <min> → Cerrar la app automáticamente en X min\n",
            "  /clearscreen    → Limpiar la pantalla del chat\n",
            "\n💬  CHAT\n",
            "  /nick <nombre>  → Cambiar tu nombre de usuario\n",
            "  /usuarios       → Ver quién está conectado\n",
            "  /uptime         → Tiempo de sesión activa\n",
            "  /stats          → Estadísticas de tu sesión\n",
            "  /salir          → Desconectarse\n",
        ]
        if es_srv:
            lineas += [
                "\n🛡️  MODERACIÓN (solo servidor)\n",
                "  /msg <usr> <txt>      → Mensaje privado a un usuario\n",
                "  /kick <usuario>       → Expulsar usuario\n",
                "  /ban  <usuario>       → Expulsar y banear\n",
                "  /mute <usr> [seg]     → Silenciar X segundos (def: 60)\n",
            ]
        lineas.append("\n")
        for l in lineas:
            color = "onion" if "╔" in l or "╚" in l or "║" in l else \
                    "yellow" if l.startswith("\n🔒") or l.startswith("\n💬") or l.startswith("\n🛡") else \
                    "blue" if l.startswith("  /") else "normal"
            self._log_chat(l, color)

    def _cmd_whoami(self):
        """Muestra resumen de identidad Tor."""
        p = self._mi_pais or {}
        lineas = [
            "\n╔══════════════════════════════════════════╗\n",
            "║           👻 WHOAMI — Tu identidad        ║\n",
            "╚══════════════════════════════════════════╝\n",
            f"  👤 Usuario   : {self._mi_nombre}\n",
            f"  {p.get('bandera','🌐')} País salida: {p.get('pais','?')}\n",
            f"  🌐 IP salida  : {p.get('ip','?')}\n",
        ]
        if self._onion:
            lineas.append(f"  🧅 .onion     : {self._onion}\n")
        lineas.append("  🔁 Circuito   : usar /nodos para ver los 3 saltos\n\n")
        for l in lineas:
            color = "onion" if "╔" in l or "╚" in l or "║" in l else "green"
            self._log_chat(l, color)

    def _cmd_stats(self):
        """Muestra estadísticas de sesión."""
        uptime = "?"
        if self._session_start:
            delta = datetime.now() - self._session_start
            h, rem = divmod(int(delta.total_seconds()), 3600)
            m, s   = divmod(rem, 60)
            uptime = f"{h:02d}h {m:02d}m {s:02d}s"
        if self._es_servidor:
            with clientes_lock:
                n_clientes = len(clientes)
        else:
            n_clientes = "?"
        p = self._mi_pais or {}
        lineas = [
            "\n╔══════════════════════════════════════════╗\n",
            "║           📊 STATS — Tu sesión           ║\n",
            "╚══════════════════════════════════════════╝\n",
            f"  ⏱ Uptime          : {uptime}\n",
            f"  💬 Msgs enviados   : {self._msgs_enviados}\n",
            f"  {p.get('bandera','🌐')} País de salida  : {p.get('pais','?')}\n",
            f"  🌐 IP de salida    : {p.get('ip','?')}\n",
            f"  👥 Usuarios online : {n_clientes if self._es_servidor else '(solo visible en servidor)'}\n\n",
        ]
        for l in lineas:
            color = "onion" if "╔" in l or "╚" in l or "║" in l else "blue"
            self._log_chat(l, color)

    def _copiar_onion(self):
        if self._onion:
            self.clipboard_clear()
            self.clipboard_append(self._onion)
            self._log_chat(T("onion_copied"), "muted")

    def _abrir_nodos(self):
        NodosWindow(self)

    def _renovar_circuito(self):
        self._log_chat(T("circuit_refreshing"), "muted")
        def _do():
            ok = renovar_circuito()
            if ok:
                time.sleep(3)
                self._mi_pais = obtener_pais_tor()
                p = self._mi_pais
                self.after(0, lambda: self._log_chat(
                    T("circuit_refreshed") +
                    f"    {p.get('bandera','')} {p.get('pais','?')} (IP: {p.get('ip','?')})\n",
                    "green"))
            else:
                self.after(0, lambda: self._log_chat(T("circuit_error"), "red"))
        threading.Thread(target=_do, daemon=True).start()

    # ── FLUJO SERVIDOR ────────────────────────────────────────
    def _iniciar_servidor(self):
        if not tor_disponible():
            self._mostrar_error(T("error_tor_missing"))
            return
        self._leer_nombre()
        self._es_servidor = True
        self._modo = "servidor"
        self._mostrar_loading(T("starting_server"), T("starting_tor"))
        threading.Thread(target=self._flujo_servidor, daemon=True).start()

    def _flujo_servidor(self):
        iniciar_tor_proceso(es_servidor=True)
        self.after(0, lambda: self._actualizar_loading(T("connecting_tor")))
        if not esperar_tor():
            self.after(0, lambda: self._mostrar_error(T("error_tor_timeout")))
            return
        self.after(0, lambda: self._actualizar_loading(T("detecting_country")))
        self._mi_pais = obtener_pais_tor()
        self.after(0, lambda: self._actualizar_loading(T("generating_onion")))
        self._onion = leer_onion()
        if self._onion:
            with open(os.path.join(BASE_DIR, "mi_direccion.txt"), "w") as f:
                f.write(self._onion)
        self.after(0, lambda: self._actualizar_loading(T("starting_chat_server")))
        threading.Thread(target=correr_servidor, args=(self._log_chat,), daemon=True).start()
        time.sleep(1)
        titulo = f"📡 {self._onion}" if self._onion else "📡 Sin .onion"
        self.after(0, lambda: self._construir_chat(titulo_extra=titulo))
        p = self._mi_pais
        self.after(200, lambda: self._log_chat(
            T("server_ready") +
            T("user_label") + self._mi_nombre + "\n" +
            T("exit_country") + f"{p.get('bandera','')} {p.get('pais','?')} (IP: {p.get('ip','?')})\n" +
            T("onion_label") + str(self._onion) + "\n\n", "green"))

    # ── FLUJO CLIENTE ─────────────────────────────────────────
    def _iniciar_cliente(self):
        if not tor_disponible():
            self._mostrar_error(T("error_tor_missing"))
            return
        host = self._entry_onion.get().strip()
        if not host or ".onion" not in host:
            self._mostrar_error(T("error_onion_invalid"))
            return
        self._leer_nombre()
        self._es_servidor = False
        self._modo = "cliente"
        self._host_destino = host
        self._mostrar_loading(T("connecting_chat"), T("starting_tor"))
        threading.Thread(target=self._flujo_cliente, daemon=True).start()

    def _flujo_cliente(self):
        iniciar_tor_proceso(es_servidor=False)
        self.after(0, lambda: self._actualizar_loading(T("connecting_tor")))
        if not esperar_tor():
            self.after(0, lambda: self._mostrar_error(T("error_tor_timeout")))
            return
        self.after(0, lambda: self._actualizar_loading(T("detecting_country")))
        self._mi_pais = obtener_pais_tor()
        self.after(0, lambda: self._actualizar_loading(f"Conectando a {self._host_destino}..."))
        try:
            self._chat_socket = socks.socksocket()
            self._chat_socket.set_proxy(socks.SOCKS5, "127.0.0.1", SOCKS_PORT)
            self._chat_socket.settimeout(60)
            self._chat_socket.connect((self._host_destino, CHAT_PORT))
            self._chat_socket.settimeout(None)
        except Exception as e:
            self.after(0, lambda: self._mostrar_error(T("error_connect") + str(e)))
            return
        self.after(0, lambda: self._construir_chat(titulo_extra=f"→ {self._host_destino}"))
        threading.Thread(target=self._recibir_mensajes_cliente, daemon=True).start()
        p = self._mi_pais
        self.after(200, lambda: self._log_chat(
            T("client_connected") +
            T("user_label") + self._mi_nombre + "\n" +
            T("exit_country") + f"{p.get('bandera','')} {p.get('pais','?')} (IP: {p.get('ip','?')})\n\n", "green"))

    def _recibir_mensajes_cliente(self):
        while True:
            try:
                data = self._chat_socket.recv(4096)
                if not data:
                    self._log_chat(T("server_closed"), "red")
                    break
                txt = data.decode("utf-8", errors="ignore")

                if "__PEDIR_NOMBRE__" in txt:
                    self._chat_socket.sendall(self._mi_nombre.encode("utf-8"))
                elif "__PEDIR_PAIS__" in txt:
                    p = self._mi_pais
                    info = f"{p.get('bandera','')} {p.get('pais','?')} (IP: {p.get('ip','?')})"
                    self._chat_socket.sendall(info.encode("utf-8"))
                elif "__KICKED__" in txt:
                    self._log_chat(T("kicked"), "red")
                    break
                elif "__BANNED__" in txt:
                    self._log_chat("[🚫] Has sido baneado de esta sala.\n", "red")
                    break
                else:
                    self._log_chat_con_color(txt)
            except Exception:
                break

    def _log_chat_con_color(self, txt):
        def _do():
            self._textbox.configure(state="normal")
            for linea in txt.split("\n"):
                if not linea:
                    self._textbox._textbox.insert("end", "\n")
                    continue
                if any(k in linea for k in ["✅", "❌", "🧅", "[✅]", T("welcome_msg")[:6]]):
                    color = "green" if "✅" in linea else ("red" if "❌" in linea else "onion")
                    self._textbox._textbox.insert("end", linea + "\n", color)
                    continue
                m = re.match(r"^(\[\d{2}:\d{2}:\d{2}\] )(.+?)(: )(.*)$", linea)
                if m:
                    hora   = m.group(1)
                    nombre = m.group(2)
                    sep    = m.group(3)
                    cuerpo = m.group(4)
                    self._textbox._textbox.insert("end", hora, "muted")
                    if nombre == self._mi_nombre:
                        self._textbox._textbox.insert("end", nombre + sep + cuerpo + "\n", "yellow")
                    elif "(srv)" in nombre:
                        self._textbox._textbox.insert("end", nombre + sep + cuerpo + "\n", "onion")
                    else:
                        self._textbox._textbox.insert("end", nombre, "blue")
                        self._textbox._textbox.insert("end", sep + cuerpo + "\n", "normal")
                else:
                    self._textbox._textbox.insert("end", linea + "\n", "normal")
            self._textbox.configure(state="disabled")
            self._textbox.see("end")
        self.after(0, _do)

    # ── ERRORES ───────────────────────────────────────────────
    def _mostrar_error(self, mensaje):
        def _do():
            for attr in ("_frame_loading", "_frame_splash"):
                try:
                    getattr(self, attr).pack_forget()
                except Exception:
                    pass
            frame_err = ctk.CTkFrame(self, fg_color=C_BG)
            frame_err.pack(fill="both", expand=True)
            ctk.CTkLabel(frame_err, text="⚠️", font=("Segoe UI Emoji", 48)).pack(pady=(80,10))
            ctk.CTkLabel(frame_err, text=mensaje, font=("Consolas", 13),
                         text_color=C_RED, justify="center").pack(pady=10)
            ctk.CTkButton(frame_err, text=T("back"), fg_color=C_CARD,
                          hover_color=C_BORDER, font=("Consolas", 12),
                          command=lambda: [frame_err.destroy(),
                                           self._frame_splash.pack(fill="both", expand=True)]
                          ).pack(pady=20)
        self.after(0, _do)

    def al_cerrar(self):
        detener_tor()
        if _servidor_socket:
            try:
                _servidor_socket.close()
            except Exception:
                pass
        if self._chat_socket:
            try:
                self._chat_socket.close()
            except Exception:
                pass
        self.destroy()


# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = F3nixGhostApp()
    app.mainloop()