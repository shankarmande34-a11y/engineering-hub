"""
NOVA AI ASSISTANT - UPGRADED JARVIS EDITION
═══════════════════════════════════════════════════════════════════════════
NEW FEATURES ADDED (All fail-safe, modular):
  ✅ 🧠 AI Brain          - OpenAI/LLM integration with fallback
  ✅ 📂 File Management   - open/create/delete/search files
  ✅ 📸 Screenshot        - capture & save screenshots
  ✅ 🧠 Memory System     - JSON-based user memory
  ✅ ⚙️  System Monitor   - CPU/RAM/Battery via psutil
  ✅ 🌐 Smart Search      - DuckDuckGo summary before browser
  ✅ 🤖 Task Automation   - Multi-step commands
  ✅ 📧 Email Sender      - SMTP with credential safety
  ✅ 🧩 Command Learning  - Custom user-defined commands in JSON
  ✅ 🎤 Improved Voice    - Confirmation + success/failure feedback

EXISTING FEATURES (Untouched):
  ✅ Toggle Wake Word, App Opener, Power Control, Reminders
  ✅ Weather, Volume, Clipboard, Time/Date, Wikipedia
  ✅ YouTube, Google Search, Beautiful Modern GUI
═══════════════════════════════════════════════════════════════════════════
"""

import datetime
import webbrowser
import os
import sys
import subprocess
import json
import re
import time
import random
import threading
import math
import queue
import glob
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from difflib import get_close_matches
from pathlib import Path

# ── Auto-install third-party packages ──────────────────────────

def install(pkg):
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", pkg],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

try:
    import customtkinter as ctk
except ImportError:
    print("Installing customtkinter..."); install("customtkinter"); import customtkinter as ctk

try:
    import pyttsx3
except ImportError:
    print("Installing pyttsx3..."); install("pyttsx3"); import pyttsx3

try:
    import speech_recognition as sr
except ImportError:
    print("Installing SpeechRecognition..."); install("SpeechRecognition"); import speech_recognition as sr

try:
    import wikipedia
except ImportError:
    print("Installing wikipedia..."); install("wikipedia"); import wikipedia

try:
    import pywhatkit
except ImportError:
    print("Installing pywhatkit..."); install("pywhatkit"); import pywhatkit

try:
    import requests
except ImportError:
    print("Installing requests..."); install("requests"); import requests

try:
    import pyperclip
except ImportError:
    print("Installing pyperclip..."); install("pyperclip"); import pyperclip

try:
    import tkinter as tk
    from tkinter import font as tkfont
except ImportError:
    pass

# ── NEW: psutil for system monitoring ──────────────────────────
PSUTIL_AVAILABLE = False
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    try:
        print("Installing psutil..."); install("psutil"); import psutil
        PSUTIL_AVAILABLE = True
    except Exception:
        PSUTIL_AVAILABLE = False

# ── NEW: pyautogui for screenshots ─────────────────────────────
PYAUTOGUI_AVAILABLE = False
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    try:
        print("Installing pyautogui..."); install("pyautogui"); import pyautogui
        PYAUTOGUI_AVAILABLE = True
    except Exception:
        PYAUTOGUI_AVAILABLE = False

# ── NEW: OpenAI for AI Brain ────────────────────────────────────
OPENAI_AVAILABLE = False
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    try:
        print("Installing openai..."); install("openai"); import openai
        OPENAI_AVAILABLE = True
    except Exception:
        OPENAI_AVAILABLE = False

# pycaw for Windows volume control
PYCAW_AVAILABLE = False
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_AVAILABLE = True
except ImportError:
    try:
        print("Installing pycaw..."); install("pycaw"); install("comtypes")
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        PYCAW_AVAILABLE = True
    except Exception:
        PYCAW_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════
# ⚙️  CONFIGURATION
# ═══════════════════════════════════════════════════════════════

WEATHER_API_KEY = "YOUR_API_KEY_HERE"
DEFAULT_CITY    = "Mumbai"

NOVA_ON_PHRASE  = "nova on"
NOVA_OFF_PHRASE = "nova off"

# ── NEW: AI & Email config ──────────────────────────────────────
OPENAI_API_KEY  = "YOUR_OPENAI_API_KEY_HERE"   # Optional
EMAIL_ADDRESS   = "YOUR_EMAIL@gmail.com"        # Optional
EMAIL_PASSWORD  = "YOUR_APP_PASSWORD"           # Optional (Gmail App Password)
EMAIL_SMTP      = "smtp.gmail.com"
EMAIL_PORT      = 587

# ── NEW: Data storage paths ─────────────────────────────────────
DATA_DIR        = os.path.join(os.path.expanduser("~"), ".nova_data")
MEMORY_FILE     = os.path.join(DATA_DIR, "memory.json")
CUSTOM_CMDS_FILE= os.path.join(DATA_DIR, "custom_commands.json")
SCREENSHOT_DIR  = os.path.join(os.path.expanduser("~"), "Nova_Screenshots")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# APP DATABASE (Unchanged)
# ═══════════════════════════════════════════════════════════════

APPS_DATABASE = {
    "whatsapp":          {"keywords": ["whatsapp", "wp", "whats app"],                     "web": "https://web.whatsapp.com"},
    "whatsapp business": {"keywords": ["whatsapp business", "business whatsapp"],           "web": "https://web.whatsapp.com"},
    "messenger":         {"keywords": ["messenger", "fb messenger", "facebook messenger"],  "web": "https://messenger.com"},
    "telegram":          {"keywords": ["telegram", "tg"],                                   "web": "https://web.telegram.org"},
    "instagram":         {"keywords": ["instagram", "insta", "ig"],                         "web": "https://instagram.com"},
    "facebook":          {"keywords": ["facebook", "fb", "face book"],                      "web": "https://facebook.com"},
    "snapchat":          {"keywords": ["snapchat", "snap", "sc"],                           "web": "https://snapchat.com"},
    "threads":           {"keywords": ["threads", "threads app", "meta threads"],           "web": "https://threads.net"},
    "twitter":           {"keywords": ["twitter", "x", "tweet"],                            "web": "https://twitter.com"},
    "youtube":           {"keywords": ["youtube", "yt", "tube"],                            "web": "https://youtube.com"},
    "netflix":           {"keywords": ["netflix", "flix"],                                  "web": "https://netflix.com"},
    "spotify":           {"keywords": ["spotify"],                                          "web": "https://open.spotify.com"},
    "amazon prime":      {"keywords": ["amazon prime", "prime video"],                      "web": "https://primevideo.com"},
    "hotstar":           {"keywords": ["hotstar", "disney hotstar", "disney"],              "web": "https://hotstar.com"},
    "amazon":            {"keywords": ["amazon", "amzn", "amazon.in"],                     "web": "https://amazon.in"},
    "flipkart":          {"keywords": ["flipkart", "fk"],                                   "web": "https://flipkart.com"},
    "meesho":            {"keywords": ["meesho", "mesho"],                                  "web": "https://meesho.com"},
    "myntra":            {"keywords": ["myntra"],                                            "web": "https://myntra.com"},
    "google":            {"keywords": ["google", "gugal"],                                  "web": "https://google.com"},
    "google chrome":     {"keywords": ["chrome", "google chrome", "browser"],              "web": "https://google.com"},
    "gmail":             {"keywords": ["gmail", "google mail", "mail", "email"],            "web": "https://mail.google.com"},
    "google maps":       {"keywords": ["maps", "google maps", "map", "navigation"],        "web": "https://maps.google.com"},
    "google drive":      {"keywords": ["drive", "google drive", "gdrive", "cloud"],        "web": "https://drive.google.com"},
    "google photos":     {"keywords": ["google photos", "gphotos", "pictures"],            "web": "https://photos.google.com"},
    "google messages":   {"keywords": ["google messages", "sms"],                           "web": "https://messages.google.com"},
    "google meet":       {"keywords": ["google meet", "meet", "video call"],               "web": "https://meet.google.com"},
    "google classroom":  {"keywords": ["google classroom", "classroom", "gc"],             "web": "https://classroom.google.com"},
    "phonepe":           {"keywords": ["phonepe", "phone pay", "phonepay"],                "web": "https://phonepe.com"},
    "google pay":        {"keywords": ["google pay", "gpay", "tez"],                       "web": "https://pay.google.com"},
    "paytm":             {"keywords": ["paytm", "pay tm"],                                  "web": "https://paytm.com"},
    "calculator":        {"keywords": ["calculator", "calc", "hisab kitab"],               "windows_exe": "calc.exe",    "web": "https://calculator.com"},
    "clock":             {"keywords": ["clock", "ghadi"],                                   "windows_exe": "clock.exe",   "web": "https://time.is"},
    "notepad":           {"keywords": ["notepad", "note", "text editor"],                   "windows_exe": "notepad.exe", "web": "https://notepad.com"},
    "camera":            {"keywords": ["camera", "webcam"],                                 "windows_exe": "camera:",     "web": "https://webcamtests.com"},
    "phone by google":   {"keywords": ["phone", "dialer", "call"],                         "web": "https://voice.google.com"},
    "truecaller":        {"keywords": ["truecaller", "true caller"],                       "web": "https://truecaller.com"},
    "contacts":          {"keywords": ["contacts", "phonebook"],                            "web": "https://contacts.google.com"},
    "microsoft teams":   {"keywords": ["teams", "microsoft teams", "ms teams"],            "web": "https://teams.microsoft.com"},
    "zoom":              {"keywords": ["zoom", "zoom meeting"],                              "web": "https://zoom.us"},
    "slack":             {"keywords": ["slack"],                                             "web": "https://slack.com"},
    "chatgpt":           {"keywords": ["chatgpt", "chat gpt", "openai", "gpt"],            "web": "https://chatgpt.com"},
    "deepseek":          {"keywords": ["deepseek", "deep seek"],                            "web": "https://chat.deepseek.com"},
    "claude":            {"keywords": ["claude", "anthropic"],                              "web": "https://claude.ai"},
}

OPEN_PATTERNS = [
    "open", "khol", "kholo", "chala", "chalao", "dikhao",
    "launch", "start", "run", "shuru kar", "on kar", "khole"
]

POWER_PATTERNS = [
    "shutdown", "shut down", "power off", "turn off pc", "turn off computer",
    "restart", "reboot", "dobara chalu",
    "sleep", "suspend", "so ja", "hibernate",
    "lock", "lock screen", "lock karo", "screen lock"
]

REMINDER_PATTERNS = [
    "remind me", "reminder", "set reminder", "set alarm",
    "yaad dilao", "alarm lagao"
]

WEATHER_PATTERNS = [
    "weather", "temperature", "mausam", "garmi", "sardi",
    "rain", "barish", "humidity", "forecast"
]

VOLUME_PATTERNS = [
    "volume up", "volume down", "mute", "unmute",
    "increase volume", "decrease volume", "louder", "quieter",
    "volume badhao", "volume kam karo", "chup karo", "sound off", "sound on"
]

CLIPBOARD_PATTERNS = [
    "copy", "paste", "clipboard", "what did i copy",
    "clear clipboard", "copy karo", "paste karo"
]

# ── NEW: Pattern lists for advanced features ────────────────────
AI_PATTERNS = [
    "explain", "write", "fix", "generate", "summarize", "translate",
    "code", "help me", "what do you think", "analyze", "describe",
    "create a", "make a", "draft", "compose"
]

FILE_PATTERNS = [
    "open file", "create file", "delete file", "search file",
    "find file", "make file", "new file", "read file"
]

SCREENSHOT_PATTERNS = [
    "take screenshot", "screenshot", "capture screen",
    "take a screenshot", "screen capture", "save screenshot"
]

MEMORY_PATTERNS = [
    "my name is", "remember", "what do you know about me",
    "recall", "forget", "my age is", "i am", "i live in",
    "what is my", "who am i", "tell me about me"
]

SYSMONITOR_PATTERNS = [
    "cpu usage", "ram usage", "battery", "memory usage",
    "disk space", "system status", "how is my pc", "system info",
    "processor", "battery status", "battery level"
]

SMART_SEARCH_PATTERNS = [
    "quick search", "brief search", "fast search", "tell me about",
    "what is the", "who invented", "when was", "where is"
]

EMAIL_PATTERNS = [
    "send email", "send mail", "email to", "compose email",
    "write email", "send a mail"
]

CUSTOM_CMD_PATTERNS = [
    "when i say", "teach me", "add command", "custom command",
    "define command", "create shortcut"
]

TASK_AUTO_PATTERNS = [
    "open youtube and play", "search and open", "open and search",
    "youtube and play", "go to youtube and"
]


# ═══════════════════════════════════════════════════════════════
# GLOBAL UI EVENT QUEUE
# ═══════════════════════════════════════════════════════════════

ui_event_queue = queue.Queue()


# ═══════════════════════════════════════════════════════════════
# TTS ENGINE
# ═══════════════════════════════════════════════════════════════

try:
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)
    engine.setProperty("volume", 1.0)
    voices = engine.getProperty("voices")
    if len(voices) > 1:
        engine.setProperty("voice", voices[1].id)
except Exception as e:
    print(f"TTS Error: {e}")
    engine = None


def speak(text: str) -> None:
    print(f"\n🤖 Nova: {text}")
    ui_event_queue.put({"type": "nova_message", "text": text})
    ui_event_queue.put({"type": "status", "text": "Speaking...", "state": "speaking"})
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass
    ui_event_queue.put({"type": "status", "text": "Listening...", "state": "listening"})


# ═══════════════════════════════════════════════════════════════
# 🧠 ADVANCED FEATURES MODULE (NEW)
# ═══════════════════════════════════════════════════════════════

class AdvancedFeatures:
    """
    All new Jarvis-grade features in one clean, modular class.
    Each feature is fully fail-safe and self-contained.
    """

    def __init__(self, assistant_ref):
        self.assistant = assistant_ref
        self._init_memory()
        self._init_custom_commands()

    # ══════════════════════════════════════════════════════
    # 🧠 FEATURE 1: AI BRAIN (OpenAI integration)
    # ══════════════════════════════════════════════════════

    def ask_ai(self, prompt: str) -> str:
        """
        Query OpenAI GPT. Falls back to smart local responses if no API key.
        """
        if OPENAI_AVAILABLE and OPENAI_API_KEY != "YOUR_OPENAI_API_KEY_HERE":
            try:
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Nova, a helpful AI desktop assistant. "
                                "Give concise, spoken-word friendly answers under 3 sentences. "
                                "No markdown, no bullet points."
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI Error: {e}")
                return self._local_ai_fallback(prompt)
        else:
            return self._local_ai_fallback(prompt)

    def _local_ai_fallback(self, prompt: str) -> str:
        """Smart local fallback when no OpenAI key is configured."""
        p = prompt.lower()
        # Attempt Wikipedia for factual queries
        try:
            result = wikipedia.summary(prompt, sentences=2, auto_suggest=True)
            return result
        except Exception:
            pass
        # Generic helpful fallback
        if any(w in p for w in ["write", "draft", "compose", "create"]):
            return (
                "I can help you write things, but I need an OpenAI API key for "
                "full AI writing. You can set OPENAI_API_KEY in the config at the "
                "top of this file."
            )
        if any(w in p for w in ["fix", "debug", "code"]):
            return (
                "For advanced coding help, please set your OpenAI API key. "
                "I opened a browser search to help you for now."
            )
        return (
            "I understand you want AI help. "
            "Please add your OpenAI API key in the OPENAI_API_KEY variable to unlock "
            "full AI capabilities. I am searching the web for you now."
        )

    def handle_ai_command(self, command: str) -> None:
        """Route AI-type commands to the AI brain."""
        speak("Let me think about that.")
        response = self.ask_ai(command)
        speak(response)
        # Also search web as fallback reference
        if OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE":
            query = command.replace("explain", "").replace("what is", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={query}")

    # ══════════════════════════════════════════════════════
    # 📂 FEATURE 2: FILE MANAGEMENT
    # ══════════════════════════════════════════════════════

    def handle_file_management(self, command: str) -> None:
        """Handle file open/create/delete/search commands safely."""
        try:
            if "open file" in command:
                self._open_file(command)
            elif "create file" in command or "new file" in command or "make file" in command:
                self._create_file(command)
            elif "delete file" in command:
                self._delete_file(command)
            elif "search file" in command or "find file" in command:
                self._search_file(command)
            elif "read file" in command:
                self._read_file(command)
            else:
                speak("I can open, create, delete, or search files. Please say which action.")
        except Exception as e:
            speak("Sorry, there was a problem with the file operation.")
            print(f"File Management Error: {e}")

    def _extract_filename(self, command: str) -> str:
        """Extract filename from command string."""
        # Remove action words
        for phrase in ["open file", "create file", "new file", "make file",
                        "delete file", "search file", "find file", "read file"]:
            command = command.replace(phrase, "").strip()
        return command.strip()

    def _open_file(self, command: str) -> None:
        filename = self._extract_filename(command)
        if not filename:
            speak("Please say which file you want to open.")
            return
        # Search common locations
        search_dirs = [
            os.path.expanduser("~"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
        ]
        found = None
        for d in search_dirs:
            matches = glob.glob(os.path.join(d, f"*{filename}*"), recursive=False)
            if matches:
                found = matches[0]
                break
        if found:
            speak(f"Opening {os.path.basename(found)}.")
            if os.name == "nt":
                os.startfile(found)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", found])
            else:
                subprocess.Popen(["xdg-open", found])
        else:
            speak(f"Could not find a file named {filename}. Searching your home folder.")
            if os.name == "nt":
                os.startfile(os.path.expanduser("~"))

    def _create_file(self, command: str) -> None:
        filename = self._extract_filename(command)
        if not filename:
            speak("Please say a name for the new file.")
            return
        # Default to .txt if no extension
        if "." not in filename:
            filename += ".txt"
        filepath = os.path.join(os.path.expanduser("~"), "Documents", filename)
        try:
            with open(filepath, "w") as f:
                f.write(f"# Created by Nova on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            speak(f"Created {filename} in your Documents folder. Done!")
            print(f"📄 File created: {filepath}")
        except Exception as e:
            speak(f"Could not create the file. {str(e)}")

    def _delete_file(self, command: str) -> None:
        filename = self._extract_filename(command)
        if not filename:
            speak("Please specify which file to delete.")
            return
        search_dirs = [
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
        ]
        found = None
        for d in search_dirs:
            matches = glob.glob(os.path.join(d, f"*{filename}*"))
            if matches:
                found = matches[0]
                break
        if not found:
            speak(f"Could not find a file named {filename}.")
            return
        fname = os.path.basename(found)
        speak(f"Are you sure you want to delete {fname}? Say yes to confirm.")
        # Schedule a confirmation listen in main thread via event queue
        ui_event_queue.put({
            "type": "confirm_delete",
            "filepath": found,
            "filename": fname
        })

    def confirm_delete_file(self, filepath: str, confirmed: bool) -> None:
        """Called after user confirmation for file deletion."""
        if confirmed:
            try:
                os.remove(filepath)
                speak(f"File deleted successfully.")
            except Exception as e:
                speak(f"Could not delete the file. {str(e)}")
        else:
            speak("Deletion cancelled. Your file is safe.")

    def _search_file(self, command: str) -> None:
        filename = self._extract_filename(command)
        if not filename:
            speak("What file should I search for?")
            return
        speak(f"Searching for {filename}. Please wait.")
        results = []
        home = os.path.expanduser("~")
        for root_dir, dirs, files in os.walk(home):
            # Skip hidden directories for speed
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in files:
                if filename.lower() in f.lower():
                    results.append(os.path.join(root_dir, f))
                if len(results) >= 5:
                    break
            if len(results) >= 5:
                break
        if results:
            speak(f"Found {len(results)} file{'s' if len(results) > 1 else ''}. The first one is {os.path.basename(results[0])}.")
            for r in results:
                print(f"  📄 {r}")
        else:
            speak(f"No files found matching {filename}.")

    def _read_file(self, command: str) -> None:
        filename = self._extract_filename(command)
        if not filename:
            speak("Please specify a file name to read.")
            return
        search_dirs = [
            os.path.expanduser("~"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Documents"),
        ]
        found = None
        for d in search_dirs:
            matches = glob.glob(os.path.join(d, f"*{filename}*"))
            if matches:
                found = matches[0]
                break
        if not found:
            speak(f"Could not find {filename} to read.")
            return
        try:
            with open(found, "r", errors="ignore") as f:
                content = f.read(500)  # Read first 500 chars
            speak(f"Here is the content of {os.path.basename(found)}: {content[:200]}")
        except Exception as e:
            speak(f"Could not read the file. {str(e)}")

    # ══════════════════════════════════════════════════════
    # 📸 FEATURE 3: SCREENSHOT
    # ══════════════════════════════════════════════════════

    def handle_screenshot(self, command: str) -> None:
        """Capture and save a screenshot using pyautogui."""
        if not PYAUTOGUI_AVAILABLE:
            speak("Screenshot feature requires pyautogui. Please install it with: pip install pyautogui")
            return
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Nova_Screenshot_{timestamp}.png"
            filepath = os.path.join(SCREENSHOT_DIR, filename)
            speak("Taking screenshot in 2 seconds.")
            time.sleep(2)
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            speak(f"Screenshot saved as {filename} in your Nova Screenshots folder.")
            print(f"📸 Screenshot saved: {filepath}")
            # Open the folder
            if os.name == "nt":
                os.startfile(SCREENSHOT_DIR)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", SCREENSHOT_DIR])
            else:
                subprocess.Popen(["xdg-open", SCREENSHOT_DIR])
        except Exception as e:
            speak("Sorry, could not take screenshot.")
            print(f"Screenshot Error: {e}")

    # ══════════════════════════════════════════════════════
    # 🧠 FEATURE 4: MEMORY SYSTEM
    # ══════════════════════════════════════════════════════

    def _init_memory(self) -> None:
        """Initialize or load memory from JSON file."""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as f:
                    self.memory = json.load(f)
            except Exception:
                self.memory = {}
        else:
            self.memory = {}

    def _save_memory(self) -> None:
        """Persist memory to disk."""
        try:
            with open(MEMORY_FILE, "w") as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Memory save error: {e}")

    def handle_memory(self, command: str) -> None:
        """Handle memory store/recall commands."""
        try:
            # What do you know about me
            if any(p in command for p in ["what do you know about me", "who am i",
                                           "what is my", "tell me about me", "recall"]):
                self._recall_memory()

            # My name is ___
            elif "my name is" in command:
                match = re.search(r"my name is\s+(.+)", command)
                if match:
                    name = match.group(1).strip().title()
                    self.memory["name"] = name
                    self._save_memory()
                    speak(f"Got it! I will remember your name is {name}.")

            # My age is ___
            elif "my age is" in command:
                match = re.search(r"my age is\s+(\d+)", command)
                if match:
                    age = match.group(1)
                    self.memory["age"] = age
                    self._save_memory()
                    speak(f"I will remember you are {age} years old.")

            # I live in ___
            elif "i live in" in command:
                match = re.search(r"i live in\s+(.+)", command)
                if match:
                    location = match.group(1).strip().title()
                    self.memory["location"] = location
                    self._save_memory()
                    speak(f"Noted! You live in {location}.")

            # Remember ___
            elif "remember" in command:
                data = command.replace("remember", "").replace("please", "").strip()
                if data:
                    key = f"note_{len(self.memory)}"
                    self.memory[key] = data
                    self._save_memory()
                    speak(f"I will remember: {data}.")
                else:
                    speak("Remember what? Please tell me what to remember.")

            # Forget ___
            elif "forget" in command:
                data = command.replace("forget", "").strip()
                removed = []
                for k, v in list(self.memory.items()):
                    if data.lower() in str(v).lower():
                        del self.memory[k]
                        removed.append(v)
                if removed:
                    self._save_memory()
                    speak(f"I have forgotten: {removed[0]}.")
                else:
                    speak(f"I don't have any memory matching {data}.")

            else:
                speak("I can remember things you tell me. Say: my name is, remember something, or what do you know about me.")

        except Exception as e:
            speak("There was a problem with the memory system.")
            print(f"Memory Error: {e}")

    def _recall_memory(self) -> None:
        """Speak all stored memories."""
        if not self.memory:
            speak("I don't have any stored information about you yet. Tell me something!")
            return
        parts = []
        if "name" in self.memory:
            parts.append(f"Your name is {self.memory['name']}")
        if "age" in self.memory:
            parts.append(f"You are {self.memory['age']} years old")
        if "location" in self.memory:
            parts.append(f"You live in {self.memory['location']}")
        notes = [v for k, v in self.memory.items() if k.startswith("note_")]
        if notes:
            parts.append(f"I also remember: {'; '.join(notes[:3])}")
        if parts:
            speak("Here is what I know about you. " + ". ".join(parts) + ".")
        else:
            speak("I have some data but nothing specific. Try telling me your name or location.")

    def get_user_name(self) -> str:
        """Return stored user name for personalized greetings."""
        return self.memory.get("name", "")

    # ══════════════════════════════════════════════════════
    # ⚙️  FEATURE 5: SYSTEM MONITOR
    # ══════════════════════════════════════════════════════

    def handle_system_monitor(self, command: str) -> None:
        """Report CPU, RAM, battery, disk status."""
        if not PSUTIL_AVAILABLE:
            speak("System monitoring requires psutil. Please install it with: pip install psutil")
            return
        try:
            if any(w in command for w in ["cpu", "processor"]):
                self._report_cpu()
            elif any(w in command for w in ["ram", "memory", "ram usage"]):
                self._report_ram()
            elif any(w in command for w in ["battery", "power"]):
                self._report_battery()
            elif any(w in command for w in ["disk", "storage", "space"]):
                self._report_disk()
            elif any(w in command for w in ["system status", "how is my pc", "system info"]):
                self._full_system_report()
            else:
                self._full_system_report()
        except Exception as e:
            speak("Could not retrieve system information.")
            print(f"System Monitor Error: {e}")

    def _report_cpu(self) -> None:
        cpu = psutil.cpu_percent(interval=1)
        cores = psutil.cpu_count()
        speak(f"CPU usage is {cpu} percent across {cores} cores.")

    def _report_ram(self) -> None:
        ram = psutil.virtual_memory()
        used_gb = ram.used / (1024 ** 3)
        total_gb = ram.total / (1024 ** 3)
        speak(f"RAM usage is {ram.percent} percent. You are using {used_gb:.1f} GB out of {total_gb:.1f} GB.")

    def _report_battery(self) -> None:
        try:
            batt = psutil.sensors_battery()
            if batt:
                status = "charging" if batt.power_plugged else "on battery"
                speak(f"Battery is at {batt.percent:.0f} percent and is {status}.")
                if not batt.power_plugged and batt.percent < 20:
                    speak("Warning! Battery is critically low. Please plug in your charger.")
            else:
                speak("No battery detected. This might be a desktop computer.")
        except Exception:
            speak("Could not read battery status on this system.")

    def _report_disk(self) -> None:
        disk = psutil.disk_usage("/")
        total_gb = disk.total / (1024 ** 3)
        used_gb = disk.used / (1024 ** 3)
        free_gb = disk.free / (1024 ** 3)
        speak(f"Disk usage is {disk.percent} percent. {used_gb:.1f} GB used out of {total_gb:.1f} GB. {free_gb:.1f} GB free.")

    def _full_system_report(self) -> None:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        parts = [
            f"CPU is at {cpu} percent",
            f"RAM is at {ram.percent} percent"
        ]
        try:
            batt = psutil.sensors_battery()
            if batt:
                parts.append(f"Battery at {batt.percent:.0f} percent")
        except Exception:
            pass
        speak(f"System status: {', '.join(parts)}.")

    # ══════════════════════════════════════════════════════
    # 🌐 FEATURE 6: SMART SEARCH (DuckDuckGo Instant Answer)
    # ══════════════════════════════════════════════════════

    def handle_smart_search(self, command: str) -> None:
        """
        Fetch a spoken summary from DuckDuckGo Instant Answers API
        before opening the browser.
        """
        # Clean command to extract query
        query = command
        for w in ["quick search", "brief search", "fast search", "search for",
                   "tell me about", "google", "search"]:
            query = query.replace(w, "").strip()

        if not query:
            speak("What should I search for?")
            return

        speak(f"Searching for {query}.")

        # Try DuckDuckGo Instant Answer API (no key required)
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            abstract = data.get("AbstractText", "").strip()
            if abstract:
                # Speak first 2 sentences
                sentences = abstract.split(". ")[:2]
                summary = ". ".join(sentences) + "."
                speak(summary)
                print(f"🌐 DuckDuckGo: {summary}")
            else:
                # Try Wikipedia as backup
                try:
                    info = wikipedia.summary(query, sentences=2, auto_suggest=True)
                    speak(info)
                except Exception:
                    speak(f"Let me open the search results for {query}.")
        except Exception as e:
            speak(f"Opening search results for {query}.")
            print(f"Smart Search Error: {e}")

        # Always open browser as well
        webbrowser.open(f"https://www.google.com/search?q={query}")

    # ══════════════════════════════════════════════════════
    # 🤖 FEATURE 7: TASK AUTOMATION (Multi-step)
    # ══════════════════════════════════════════════════════

    def handle_task_automation(self, command: str) -> None:
        """
        Execute chained/multi-step commands.
        Example: "open youtube and play despacito"
        """
        try:
            if "youtube" in command and "play" in command:
                song_match = re.search(r"play\s+(.+)$", command)
                if song_match:
                    song = song_match.group(1).strip()
                    speak(f"Opening YouTube and searching for {song}.")
                    time.sleep(0.5)
                    webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
                    speak("Done! YouTube is now open with your song.")
                else:
                    speak("Opening YouTube for you.")
                    webbrowser.open("https://youtube.com")

            elif "search" in command and "open" in command:
                # "search X and open first result"
                query_match = re.search(r"search\s+(.+?)\s+and", command)
                if query_match:
                    query = query_match.group(1).strip()
                    speak(f"Searching for {query} and opening results.")
                    webbrowser.open(f"https://www.google.com/search?q={query}")
                else:
                    speak("What should I search and open?")

            elif "open" in command and "and" in command:
                # Generic "open X and do Y"
                parts = command.split(" and ")
                for part in parts:
                    part = part.strip()
                    if part:
                        speak(f"Now: {part}.")
                        threading.Thread(
                            target=self.assistant.process_command,
                            args=(part,),
                            daemon=True
                        ).start()
                        time.sleep(2)  # Small delay between steps
            else:
                speak("I can automate tasks like: open YouTube and play a song.")
        except Exception as e:
            speak("Task automation encountered an issue.")
            print(f"Task Automation Error: {e}")

    # ══════════════════════════════════════════════════════
    # 📧 FEATURE 8: EMAIL SENDER (SMTP)
    # ══════════════════════════════════════════════════════

    def handle_email(self, command: str, assistant_listener=None) -> None:
        """
        Send email via SMTP. Safely skipped if credentials not configured.
        """
        if EMAIL_ADDRESS == "YOUR_EMAIL@gmail.com" or EMAIL_PASSWORD == "YOUR_APP_PASSWORD":
            speak(
                "Email feature is not configured. "
                "Please set EMAIL_ADDRESS and EMAIL_PASSWORD in the config section "
                "at the top of this file. Use a Gmail App Password for security."
            )
            return

        try:
            # Extract recipient from command
            to_match = re.search(r"(?:email to|send email to|send mail to)\s+(.+?)(?:\s+about|\s+saying|$)", command)
            recipient = to_match.group(1).strip() if to_match else None

            if not recipient:
                speak("Who should I send the email to? Please say an email address.")
                return

            # Extract subject
            subject_match = re.search(r"about\s+(.+?)(?:\s+saying|$)", command)
            subject = subject_match.group(1).strip() if subject_match else "Message from Nova"

            # Extract body
            body_match = re.search(r"saying\s+(.+)$", command)
            body = body_match.group(1).strip() if body_match else "Hello, this email was sent by Nova AI Assistant."

            speak(f"Sending email to {recipient} about {subject}.")

            msg = MIMEMultipart()
            msg["From"]    = EMAIL_ADDRESS
            msg["To"]      = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())

            speak(f"Email sent successfully to {recipient}!")
            print(f"📧 Email sent to {recipient}")

        except smtplib.SMTPAuthenticationError:
            speak("Email authentication failed. Please check your email credentials and use a Gmail App Password.")
        except Exception as e:
            speak("Could not send the email. Please check your internet connection and email settings.")
            print(f"Email Error: {e}")

    # ══════════════════════════════════════════════════════
    # 🧩 FEATURE 9: COMMAND LEARNING SYSTEM
    # ══════════════════════════════════════════════════════

    def _init_custom_commands(self) -> None:
        """Load custom commands from JSON."""
        if os.path.exists(CUSTOM_CMDS_FILE):
            try:
                with open(CUSTOM_CMDS_FILE, "r") as f:
                    self.custom_commands = json.load(f)
            except Exception:
                self.custom_commands = {}
        else:
            self.custom_commands = {}

    def _save_custom_commands(self) -> None:
        """Persist custom commands to disk."""
        try:
            with open(CUSTOM_CMDS_FILE, "w") as f:
                json.dump(self.custom_commands, f, indent=2)
        except Exception as e:
            print(f"Custom commands save error: {e}")

    def handle_command_learning(self, command: str) -> None:
        """
        Teach Nova new custom shortcuts.
        Usage: "when I say study mode, open youtube"
        """
        try:
            # "when i say X, do Y" or "define command X as Y"
            pattern = re.search(
                r"when i say\s+(.+?)[,]\s*(.+)$|"
                r"teach me\s+(.+?)\s+means\s+(.+)$|"
                r"add command\s+(.+?)\s+as\s+(.+)$",
                command
            )
            if pattern:
                groups = [g for g in pattern.groups() if g]
                if len(groups) >= 2:
                    trigger   = groups[0].strip().lower()
                    action    = groups[1].strip().lower()
                    self.custom_commands[trigger] = action
                    self._save_custom_commands()
                    speak(f"Got it! Whenever you say {trigger}, I will {action}.")
                    print(f"🧩 Custom command saved: '{trigger}' → '{action}'")
                    return

            # List all custom commands
            if "show" in command or "list" in command:
                if self.custom_commands:
                    cmds = list(self.custom_commands.keys())[:5]
                    speak(f"You have {len(self.custom_commands)} custom commands. For example: {', '.join(cmds)}.")
                else:
                    speak("You have no custom commands yet. Say: when I say study mode, open youtube.")
                return

            speak(
                "To add a custom command, say: when I say study mode, open youtube. "
                "I will remember it for next time."
            )

        except Exception as e:
            speak("Could not process that custom command.")
            print(f"Command Learning Error: {e}")

    def check_custom_command(self, command: str) -> bool:
        """
        Check if user said a custom command trigger. Returns True if handled.
        """
        for trigger, action in self.custom_commands.items():
            if trigger in command:
                speak(f"Running your custom command: {trigger}.")
                self.assistant.process_command(action)
                return True
        return False

    # ══════════════════════════════════════════════════════
    # 🎤 FEATURE 10: IMPROVED VOICE FEEDBACK HELPERS
    # ══════════════════════════════════════════════════════

    def confirm_action(self, action_description: str) -> str:
        """
        Give a random confirmation response before performing an action.
        Returns a friendly confirmation phrase.
        """
        confirmations = [
            f"Sure! {action_description}.",
            f"Absolutely! {action_description} right away.",
            f"On it! {action_description}.",
            f"No problem, {action_description}.",
            f"Got it! {action_description} for you.",
        ]
        return random.choice(confirmations)

    def success_feedback(self, action: str) -> str:
        """Return a random success message."""
        messages = [
            f"{action} completed successfully!",
            f"Done! {action} finished.",
            f"All done with {action}.",
            f"{action} — check!",
        ]
        return random.choice(messages)

    def failure_feedback(self, action: str, reason: str = "") -> str:
        """Return a helpful failure message."""
        base = f"I couldn't complete {action}."
        if reason:
            base += f" {reason}"
        return base


# ═══════════════════════════════════════════════════════════════
# NOVA ASSISTANT CORE (UPGRADED)
# ═══════════════════════════════════════════════════════════════

class NovaAssistant:
    def __init__(self):
        self.is_active = False
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.0
        self.recognizer.energy_threshold = 300
        self.reminders_list = []
        self._running = True

        # ── NEW: Initialize advanced features module ────────
        self.advanced = AdvancedFeatures(self)

        # ── NEW: Pending delete confirmation state ──────────
        self._pending_delete = None

    def stop(self):
        self._running = False

    def listen_once(self, timeout=6, phrase_limit=10):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                ui_event_queue.put({"type": "status", "text": "Listening...", "state": "listening"})
                ui_event_queue.put({"type": "wave", "active": True})
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            ui_event_queue.put({"type": "wave", "active": False})
            ui_event_queue.put({"type": "status", "text": "Processing...", "state": "processing"})
            text = self.recognizer.recognize_google(audio)
            print(f"🗣️  You said: {text}")
            ui_event_queue.put({"type": "user_message", "text": text})
            return text.lower()
        except sr.WaitTimeoutError:
            ui_event_queue.put({"type": "wave", "active": False})
            return ""
        except sr.UnknownValueError:
            ui_event_queue.put({"type": "wave", "active": False})
            return ""
        except (sr.RequestError, OSError):
            ui_event_queue.put({"type": "wave", "active": False})
            return ""
        except Exception:
            ui_event_queue.put({"type": "wave", "active": False})
            return ""

    def check_for_toggle_commands(self, text):
        if not text:
            return None
        if NOVA_ON_PHRASE in text or "nova on" in text:
            return "ON"
        elif NOVA_OFF_PHRASE in text or "nova off" in text:
            return "OFF"
        return None

    def run(self):
        print("\n" + "═" * 70)
        print("   🚀  NOVA - SMART VOICE ASSISTANT (JARVIS EDITION)")
        print("═" * 70)

        # Personalized greeting using memory
        name = self.advanced.get_user_name()
        greeting = f"Hello{', ' + name if name else ''}! I am Nova. Say Nova on to activate me, or click the microphone button."
        speak(greeting)

        while self._running:
            try:
                if not self.is_active:
                    ui_event_queue.put({"type": "mode", "active": False})
                    print(f"\n😴  SLEEP MODE - Say 'Nova on' to activate me")
                    text = self.listen_once(timeout=4, phrase_limit=3)
                    toggle = self.check_for_toggle_commands(text)
                    if toggle == "ON":
                        self.is_active = True
                        ui_event_queue.put({"type": "mode", "active": True})
                        speak("Nova is now active. Just tell me what to do. Say Nova off to deactivate me.")
                    elif text and any(w in text for w in ["exit", "bye", "goodbye"]):
                        speak("Goodbye! Have a great day!")
                        ui_event_queue.put({"type": "quit"})
                        break
                else:
                    ui_event_queue.put({"type": "mode", "active": True})
                    text = self.listen_once(timeout=8, phrase_limit=12)

                    if not text:
                        continue

                    toggle = self.check_for_toggle_commands(text)
                    if toggle == "OFF":
                        self.is_active = False
                        ui_event_queue.put({"type": "mode", "active": False})
                        speak("Nova is now off. Say Nova on when you need me again.")
                        continue
                    elif toggle == "ON":
                        speak("I am already active. What can I do for you?")
                        continue

                    if any(w in text for w in ["exit", "quit", "bye", "goodbye"]):
                        speak("Goodbye! Have a great day!")
                        ui_event_queue.put({"type": "quit"})
                        break

                    # ── NEW: Handle pending delete confirmation ─────
                    if self._pending_delete:
                        confirmed = any(w in text for w in ["yes", "confirm", "delete", "sure", "haan"])
                        self.advanced.confirm_delete_file(
                            self._pending_delete["path"], confirmed
                        )
                        self._pending_delete = None
                        continue

                    self.process_command(text)

            except KeyboardInterrupt:
                speak("Shutting down Nova. Goodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                if self.is_active:
                    speak("Something went wrong. I'm still active. Please try again.")

    def listen_single_command(self):
        """Called from GUI button press for one-shot listening."""
        text = self.listen_once(timeout=8, phrase_limit=12)
        if not text:
            ui_event_queue.put({"type": "status", "text": "Didn't catch that...", "state": "idle"})
            return

        toggle = self.check_for_toggle_commands(text)
        if toggle == "ON":
            self.is_active = True
            ui_event_queue.put({"type": "mode", "active": True})
            speak("Nova is now active. What can I do for you?")
            return
        elif toggle == "OFF":
            self.is_active = False
            ui_event_queue.put({"type": "mode", "active": False})
            speak("Nova is now off. Say Nova on when you need me again.")
            return

        # Handle pending delete confirmation
        if self._pending_delete:
            confirmed = any(w in text for w in ["yes", "confirm", "delete", "sure", "haan"])
            self.advanced.confirm_delete_file(self._pending_delete["path"], confirmed)
            self._pending_delete = None
            return

        self.process_command(text)

    def process_command(self, command: str) -> None:
        """
        Main command router. New features checked FIRST before existing handlers.
        All additions are additive — existing features untouched.
        """
        if not command:
            return

        ui_event_queue.put({"type": "history", "text": command})

        # ── NEW: Check custom user-defined commands first ───────────
        if self.advanced.check_custom_command(command):
            return

        # ── NEW: Task automation (multi-step) ───────────────────────
        if any(p in command for p in TASK_AUTO_PATTERNS):
            self.advanced.handle_task_automation(command)
            return

        # ── NEW: Memory system ──────────────────────────────────────
        if any(p in command for p in MEMORY_PATTERNS):
            self.advanced.handle_memory(command)
            return

        # ── NEW: System monitor ─────────────────────────────────────
        if any(p in command for p in SYSMONITOR_PATTERNS):
            self.advanced.handle_system_monitor(command)
            return

        # ── NEW: Screenshot ─────────────────────────────────────────
        if any(p in command for p in SCREENSHOT_PATTERNS):
            self.advanced.handle_screenshot(command)
            return

        # ── NEW: File management ────────────────────────────────────
        if any(p in command for p in FILE_PATTERNS):
            self.advanced.handle_file_management(command)
            return

        # ── NEW: Email sender ───────────────────────────────────────
        if any(p in command for p in EMAIL_PATTERNS):
            self.advanced.handle_email(command)
            return

        # ── NEW: Command learning ───────────────────────────────────
        if any(p in command for p in CUSTOM_CMD_PATTERNS):
            self.advanced.handle_command_learning(command)
            return

        # ── EXISTING: Power control ─────────────────────────────────
        if any(p in command for p in POWER_PATTERNS):
            self.handle_system_power(command)

        # ── EXISTING: Reminders ─────────────────────────────────────
        elif any(p in command for p in REMINDER_PATTERNS):
            if any(w in command for w in ["list", "show", "kitne", "how many"]):
                self.handle_list_reminders()
            else:
                self.handle_reminder(command)

        # ── EXISTING: Weather ───────────────────────────────────────
        elif any(p in command for p in WEATHER_PATTERNS):
            self.handle_weather(command)

        # ── EXISTING: Volume ────────────────────────────────────────
        elif any(p in command for p in VOLUME_PATTERNS):
            self.handle_volume(command)

        # ── EXISTING: Clipboard ─────────────────────────────────────
        elif any(p in command for p in CLIPBOARD_PATTERNS):
            self.handle_clipboard(command)

        # ── EXISTING: Add app ────────────────────────────────────────
        elif any(p in command for p in ["add custom app", "new app", "add app"]):
            self.add_custom_app()

        # ── EXISTING: Help ───────────────────────────────────────────
        elif "help" in command or "kya kya" in command:
            speak("Showing all available commands. Check the Help section in the sidebar.")
            ui_event_queue.put({"type": "show_help"})

        # ── EXISTING: App opener ─────────────────────────────────────
        elif any(p in command for p in OPEN_PATTERNS) or \
             any(k in command for k in [
                 "amazon", "flipkart", "whatsapp", "instagram", "facebook",
                 "youtube", "chrome", "gmail", "maps", "calculator",
                 "netflix", "spotify", "chatgpt", "telegram", "twitter"
             ]):
            self.handle_open_app(command)

        # ── EXISTING: Time/Date ──────────────────────────────────────
        elif any(w in command for w in ["time", "date", "day", "today", "samay", "tarikh"]):
            self.handle_time()

        # ── EXISTING: YouTube play ───────────────────────────────────
        elif command.startswith("play") or "gaana" in command or "song" in command:
            self.handle_play(command)

        # ── EXISTING: Search ─────────────────────────────────────────
        elif command.startswith("search") or "google karo" in command:
            # NEW: Use smart search instead of just opening browser
            self.advanced.handle_smart_search(command)

        # ── EXISTING: Wikipedia ──────────────────────────────────────
        elif any(command.startswith(p) for p in
                 ["who is", "what is", "tell me about", "kaun hai", "kya hai"]):
            self.handle_wikipedia(command)

        # ── NEW: AI Brain for complex/unknown queries ────────────────
        elif any(p in command for p in AI_PATTERNS):
            self.advanced.handle_ai_command(command)

        # ── EXISTING: Fallback app opener ───────────────────────────
        else:
            self.handle_open_app(command)

    # ── REMINDERS (Unchanged) ──────────────────────────────────

    def _reminder_thread(self, seconds: int, message: str) -> None:
        time.sleep(seconds)
        speak(f"Reminder! {message}")
        print(f"\n🔔 REMINDER ALERT: {message}")
        if os.name == "nt":
            try:
                subprocess.Popen(
                    f'msg * "REMINDER: {message}"', shell=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception:
                pass

    def handle_reminder(self, command: str) -> None:
        minutes = 0
        hours   = 0
        min_match = re.search(r"(\d+)\s*(?:minute|min|mins|minutes)", command)
        hr_match  = re.search(r"(\d+)\s*(?:hour|hr|hrs|hours)",       command)
        if min_match:
            minutes = int(min_match.group(1))
        if hr_match:
            hours = int(hr_match.group(1))
        total_seconds = (hours * 3600) + (minutes * 60)
        if total_seconds == 0:
            speak("Please say how many minutes or hours. For example: remind me in 10 minutes to drink water.")
            return
        msg_match = re.search(r"\bto\b(.+)$|\bfor\b(.+)$", command)
        if msg_match:
            reminder_msg = (msg_match.group(1) or msg_match.group(2)).strip()
        else:
            reminder_msg = "your reminder"
        parts = []
        if hours:   parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes: parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
        time_label = " and ".join(parts)
        speak(f"Got it! I will remind you to {reminder_msg} in {time_label}.")
        print(f"⏰ Reminder set → '{reminder_msg}' in {time_label}")
        t = threading.Thread(
            target=self._reminder_thread, args=(total_seconds, reminder_msg), daemon=True
        )
        t.start()
        self.reminders_list.append({"message": reminder_msg, "seconds": total_seconds})

    def handle_list_reminders(self) -> None:
        if not self.reminders_list:
            speak("You have no reminders set.")
        else:
            speak(f"You have {len(self.reminders_list)} reminder set.")
            for i, r in enumerate(self.reminders_list, 1):
                print(f"  {i}. {r['message']}")

    # ── WEATHER (Unchanged) ────────────────────────────────────

    def handle_weather(self, command: str) -> None:
        if WEATHER_API_KEY == "YOUR_API_KEY_HERE":
            speak(
                "Weather needs a free API key. "
                "I am opening the signup page for you. "
                "Get your key and paste it in the WEATHER_API_KEY variable at the top of this file."
            )
            webbrowser.open("https://openweathermap.org/api")
            return
        city = DEFAULT_CITY
        city_match = re.search(r"(?:in|at|for|of)\s+([a-zA-Z ]+)$", command)
        if city_match:
            city = city_match.group(1).strip().title()
        try:
            url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
            )
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if data.get("cod") != 200:
                speak(f"Could not find weather for {city}. Please check the city name.")
                return
            temp        = data["main"]["temp"]
            feels_like  = data["main"]["feels_like"]
            humidity    = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed  = data["wind"]["speed"]
            speak(
                f"Weather in {city}: {description}. "
                f"Temperature is {temp:.1f} degrees Celsius, feels like {feels_like:.1f}. "
                f"Humidity {humidity} percent. Wind {wind_speed} meters per second."
            )
        except requests.exceptions.ConnectionError:
            speak("No internet connection. Cannot fetch weather right now.")
        except Exception as e:
            speak("Something went wrong fetching weather. Please try again.")
            print(f"Weather Error: {e}")

    # ── VOLUME (Unchanged) ─────────────────────────────────────

    def _get_volume_interface(self):
        if not PYCAW_AVAILABLE:
            return None
        try:
            devices   = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            return cast(interface, POINTER(IAudioEndpointVolume))
        except Exception:
            return None

    def handle_volume(self, command: str) -> None:
        is_windows = os.name == "nt"
        if is_windows and PYCAW_AVAILABLE:
            vol = self._get_volume_interface()
            if vol:
                try:
                    cur = vol.GetMasterVolumeLevelScalar()
                    pct_match = re.search(r"volume\s+(\d+)", command)
                    if pct_match:
                        pct = max(0, min(100, int(pct_match.group(1)))) / 100.0
                        vol.SetMasterVolumeLevelScalar(pct, None)
                        speak(f"Volume set to {int(pct * 100)} percent.")
                    elif any(w in command for w in ["mute", "chup karo", "sound off"]):
                        vol.SetMute(1, None)
                        speak("Muted.")
                    elif any(w in command for w in ["unmute", "sound on", "chalu karo"]):
                        vol.SetMute(0, None)
                        speak("Unmuted. Sound is on.")
                    elif any(w in command for w in ["volume up", "louder", "increase volume", "volume badhao", "zyada"]):
                        new = min(1.0, cur + 0.10)
                        vol.SetMasterVolumeLevelScalar(new, None)
                        speak(f"Volume increased to {int(new * 100)} percent.")
                    elif any(w in command for w in ["volume down", "quieter", "decrease volume", "volume kam", "kam karo"]):
                        new = max(0.0, cur - 0.10)
                        vol.SetMasterVolumeLevelScalar(new, None)
                        speak(f"Volume decreased to {int(new * 100)} percent.")
                    else:
                        speak(f"Current volume is {int(cur * 100)} percent.")
                    return
                except Exception as e:
                    print(f"pycaw error: {e}")
            if any(w in command for w in ["mute", "chup"]):
                os.system('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"')
                speak("Toggled mute.")
            elif any(w in command for w in ["up", "louder", "badhao"]):
                for _ in range(5):
                    os.system('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"')
                speak("Volume increased.")
            elif any(w in command for w in ["down", "quieter", "kam"]):
                for _ in range(5):
                    os.system('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"')
                speak("Volume decreased.")
        elif not is_windows:
            if any(w in command for w in ["mute", "chup"]):
                os.system("amixer set Master mute"); speak("Muted.")
            elif any(w in command for w in ["unmute", "sound on"]):
                os.system("amixer set Master unmute"); speak("Unmuted.")
            elif any(w in command for w in ["up", "louder", "badhao"]):
                os.system("amixer set Master 10%+"); speak("Volume increased.")
            elif any(w in command for w in ["down", "quieter", "kam"]):
                os.system("amixer set Master 10%-"); speak("Volume decreased.")
        else:
            speak("Volume control is not available. Please install pycaw.")

    # ── CLIPBOARD (Unchanged) ──────────────────────────────────

    def handle_clipboard(self, command: str) -> None:
        try:
            if any(w in command for w in ["paste", "what did i copy", "what is copied",
                                           "clipboard me kya hai", "read clipboard"]):
                content = pyperclip.paste()
                if content.strip():
                    speak(f"Your clipboard has: {content[:200]}")
                    print(f"📋 Clipboard: {content}")
                else:
                    speak("Your clipboard is empty.")
            elif any(w in command for w in ["clear clipboard", "clipboard clear", "khaali karo"]):
                pyperclip.copy("")
                speak("Clipboard cleared.")
            elif "copy" in command:
                match = re.search(r"\bcopy\b\s+(.+)", command)
                if match:
                    text = match.group(1).strip()
                    pyperclip.copy(text)
                    speak(f"Copied: {text}")
                else:
                    content = pyperclip.paste()
                    if content:
                        speak(f"Clipboard has: {content[:100]}")
                    else:
                        speak("Say what to copy. For example: copy hello world.")
            else:
                speak("Say: copy some text, paste, what did I copy, or clear clipboard.")
        except Exception as e:
            speak("Clipboard had an error. Make sure pyperclip is installed.")
            print(f"Clipboard Error: {e}")

    # ── POWER (Unchanged) ──────────────────────────────────────

    def handle_system_power(self, command: str) -> None:
        is_windows = os.name == "nt"
        if any(w in command for w in ["shutdown", "shut down", "power off", "turn off pc", "turn off computer"]):
            speak("Shutting down in 5 seconds. Say cancel to stop.")
            time.sleep(2)
            cancel = self.listen_once(timeout=3, phrase_limit=3)
            if cancel and any(w in cancel for w in ["cancel", "ruk", "stop", "nahi", "mat"]):
                speak("Shutdown cancelled! Your computer is safe.")
                return
            speak("Goodbye! Shutting down now.")
            time.sleep(1)
            os.system("shutdown /s /t 3" if is_windows else "shutdown now")
        elif any(w in command for w in ["restart", "reboot", "dobara chalu"]):
            speak("Restarting in 5 seconds. Say cancel to stop.")
            time.sleep(2)
            cancel = self.listen_once(timeout=3, phrase_limit=3)
            if cancel and any(w in cancel for w in ["cancel", "ruk", "stop", "nahi", "mat"]):
                speak("Restart cancelled!")
                return
            speak("Restarting now. See you soon!")
            time.sleep(1)
            os.system("shutdown /r /t 3" if is_windows else "reboot")
        elif any(w in command for w in ["sleep", "suspend", "so ja", "hibernate"]):
            speak("Putting computer to sleep. Goodnight!")
            time.sleep(1)
            if is_windows:
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            else:
                os.system("systemctl suspend")
        elif any(w in command for w in ["lock", "lock screen", "lock karo", "screen lock"]):
            speak("Locking your screen. Stay safe!")
            time.sleep(1)
            if is_windows:
                os.system("rundll32.exe user32.dll,LockWorkStation")
            else:
                os.system("loginctl lock-session")

    # ── APP OPENER (Unchanged) ─────────────────────────────────

    def find_app_from_command(self, command: str):
        cmd = command.lower()
        for p in OPEN_PATTERNS:
            cmd = cmd.replace(p, "").strip()
        for app_name, info in APPS_DATABASE.items():
            for kw in info["keywords"]:
                if kw in cmd:
                    return app_name, info
        all_kw  = [kw for info in APPS_DATABASE.values() for kw in info["keywords"]]
        matches = get_close_matches(cmd, all_kw, n=1, cutoff=0.6)
        if matches:
            for app_name, info in APPS_DATABASE.items():
                if matches[0] in info["keywords"]:
                    return app_name, info
        return None, None

    def open_app_web_first(self, app_name: str, app_info: dict) -> bool:
        if "web" in app_info:
            webbrowser.open(app_info["web"]); return True
        if "windows_exe" in app_info:
            try:
                subprocess.Popen(app_info["windows_exe"], shell=True); return True
            except Exception:
                pass
        webbrowser.open(f"https://www.google.com/search?q={app_name}")
        return False

    def handle_open_app(self, command: str) -> None:
        app_name, app_info = self.find_app_from_command(command)
        if app_name and app_info:
            speak(self.advanced.confirm_action(f"Opening {app_name.title()}"))
            time.sleep(0.4)
            if not self.open_app_web_first(app_name, app_info):
                speak(f"Let me search {app_name} for you.")
                webbrowser.open(f"https://www.google.com/search?q={app_name}")
        else:
            speak("Could not find that app. Searching for you.")
            webbrowser.open(f"https://www.google.com/search?q={command}")

    def add_custom_app(self) -> None:
        speak("What is the app name?")
        app_name = self.listen_once(timeout=5, phrase_limit=5)
        if app_name and len(app_name) > 2:
            speak(f"What website should I open for {app_name}?")
            web_url = self.listen_once(timeout=5, phrase_limit=8)
            APPS_DATABASE[app_name] = {
                "keywords": [app_name],
                "web": web_url if "http" in web_url else f"https://{web_url}"
            }
            speak(f"Done! {app_name} added. Say open {app_name} anytime.")

    # ── OTHER (Unchanged) ──────────────────────────────────────

    def handle_time(self) -> None:
        now = datetime.datetime.now()
        speak(f"It is {now.strftime('%I:%M %p')} on {now.strftime('%A, %d %B %Y')}.")

    def handle_search(self, command: str) -> None:
        query = command.replace("search", "").replace("google", "").replace("search karo", "").strip()
        if not query:
            speak("What should I search for?"); return
        self.advanced.handle_smart_search(query)

    def handle_play(self, command: str) -> None:
        song = command.replace("play", "").replace("gaana", "").replace("song", "").strip()
        if not song:
            speak("What should I play?"); return
        speak(f"Playing {song} on YouTube")
        webbrowser.open(f"https://www.youtube.com/results?search_query={song}")

    def handle_wikipedia(self, command: str) -> None:
        topic = (command.replace("who is", "").replace("what is", "")
                        .replace("tell me about", "").strip())
        if not topic:
            speak("What do you want me to look up?"); return
        speak(f"Looking up {topic} on Wikipedia.")
        try:
            info = wikipedia.summary(topic, sentences=2, auto_suggest=True)
            speak(info)
        except Exception:
            webbrowser.open(f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}")
            speak(f"Opening Wikipedia page for {topic}")


# ═══════════════════════════════════════════════════════════════
# SOUND WAVE CANVAS WIDGET (Unchanged)
# ═══════════════════════════════════════════════════════════════

class SoundWaveWidget(ctk.CTkCanvas):
    def __init__(self, parent, width=300, height=60, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg="#0a0a0f", highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.bars = 24
        self.active = False
        self.phase = 0
        self._animate()

    def set_active(self, state: bool):
        self.active = state

    def _animate(self):
        self.delete("all")
        bar_w = self.width / (self.bars * 2)
        cx = self.width / 2

        for i in range(self.bars):
            x = cx + (i - self.bars / 2) * bar_w * 2 + bar_w / 2

            if self.active:
                amp = (math.sin(self.phase + i * 0.4) * 0.5 + 0.5)
                h = 6 + amp * (self.height * 0.75)
                alpha_val = int(180 + amp * 75)
                color = f"#{0:02x}{int(120 + amp * 135):02x}{int(220 + amp * 35):02x}"
                glow_color = f"#{0:02x}{int(80 + amp * 80):02x}{int(180 + amp * 40):02x}"
                self.create_rectangle(
                    x - bar_w * 1.5, self.height/2 - h * 1.2,
                    x + bar_w * 1.5, self.height/2 + h * 1.2,
                    fill=glow_color, outline="", tags="wave"
                )
                self.create_rectangle(
                    x - bar_w * 0.8, self.height/2 - h,
                    x + bar_w * 0.8, self.height/2 + h,
                    fill=color, outline="", tags="wave"
                )
            else:
                h = 3
                self.create_rectangle(
                    x - bar_w * 0.7, self.height/2 - h,
                    x + bar_w * 0.7, self.height/2 + h,
                    fill="#1e2040", outline="", tags="wave"
                )

        self.phase += 0.12
        self.after(50, self._animate)


# ═══════════════════════════════════════════════════════════════
# MAIN GUI APPLICATION (UPGRADED — help panel extended)
# ═══════════════════════════════════════════════════════════════

class NovaGUI:
    # ── Color palette (Unchanged) ──────────────────────────────
    BG_DEEP     = "#05050d"
    BG_PANEL    = "#0a0a18"
    BG_CARD     = "#0f0f22"
    BG_SIDEBAR  = "#080812"
    ACCENT_BLUE = "#00b4ff"
    ACCENT_PURP = "#7c3aed"
    ACCENT_GLOW = "#00d4ff"
    NEON_GREEN  = "#00ff88"
    NEON_RED    = "#ff3366"
    TEXT_PRI    = "#e8eaf6"
    TEXT_SEC    = "#7986cb"
    TEXT_DIM    = "#3d4270"
    BUBBLE_USER = "#1a1035"
    BUBBLE_NOVA = "#0d1f35"

    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("NOVA AI Assistant — Jarvis Edition")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(fg_color=self.BG_DEEP)

        self.assistant = NovaAssistant()
        self.current_panel = "home"
        self.mic_listening = False
        self.history_items = []

        self._build_ui()
        self._bind_shortcuts()
        self._start_assistant_thread()
        self._poll_ui_events()

        # Welcome
        self.root.after(800, lambda: self._add_bubble(
            "nova",
            "Hello! I'm Nova (Jarvis Edition). "
            "I now support AI brain, file management, screenshots, memory, "
            "system monitoring, smart search, email, and custom commands! "
            "Say 'Nova on' to start."
        ))

    # ── BUILD UI (Unchanged except extended help panel) ────────

    def _build_ui(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main_area()

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self.root, width=220, fg_color=self.BG_SIDEBAR,
                               corner_radius=0, border_width=1,
                               border_color="#12122a")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(10, weight=1)

        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=90)
        logo_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(20, 8))
        logo_frame.grid_propagate(False)

        ctk.CTkLabel(logo_frame, text="◈ NOVA", font=("Courier New", 24, "bold"),
                     text_color=self.ACCENT_BLUE).pack(anchor="w")
        ctk.CTkLabel(logo_frame, text="JARVIS EDITION", font=("Courier New", 9),
                     text_color=self.TEXT_DIM).pack(anchor="w")

        ctk.CTkFrame(sidebar, height=1, fg_color="#12122a").grid(
            row=1, column=0, sticky="ew", padx=0, pady=4)

        nav_items = [
            ("home",    "⌂",  "Home"),
            ("help",    "?",  "Commands"),
            ("history", "≡",  "History"),
            ("settings","✦",  "Settings"),
        ]

        self.nav_buttons = {}
        for row_i, (key, icon, label) in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(
                sidebar,
                text=f"  {icon}   {label}",
                font=("Courier New", 13),
                fg_color="transparent",
                hover_color="#111130",
                text_color=self.TEXT_SEC,
                anchor="w",
                height=44,
                corner_radius=8,
                command=lambda k=key: self._switch_panel(k)
            )
            btn.grid(row=row_i, column=0, padx=10, pady=2, sticky="ew")
            self.nav_buttons[key] = btn

        self.status_dot_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=70)
        self.status_dot_frame.grid(row=11, column=0, sticky="ew", padx=16, pady=16)

        ctk.CTkFrame(self.status_dot_frame, height=1, fg_color="#12122a").pack(
            fill="x", pady=(0, 12))

        status_row = ctk.CTkFrame(self.status_dot_frame, fg_color="transparent")
        status_row.pack(fill="x")

        self.dot_canvas = tk.Canvas(status_row, width=14, height=14,
                                    bg=self.BG_SIDEBAR, highlightthickness=0)
        self.dot_canvas.pack(side="left", padx=(0, 8))
        self.dot_oval = self.dot_canvas.create_oval(2, 2, 12, 12, fill=self.NEON_RED, outline="")

        self.mode_label = ctk.CTkLabel(status_row, text="Sleep Mode",
                                       font=("Courier New", 11),
                                       text_color=self.NEON_RED)
        self.mode_label.pack(side="left")

        self.toggle_var = ctk.BooleanVar(value=False)
        toggle_btn = ctk.CTkSwitch(
            sidebar, text="Nova ON/OFF",
            font=("Courier New", 11),
            text_color=self.TEXT_SEC,
            progress_color=self.ACCENT_BLUE,
            button_color=self.ACCENT_GLOW,
            variable=self.toggle_var,
            command=self._on_toggle_switch
        )
        toggle_btn.grid(row=12, column=0, padx=16, pady=(0, 20), sticky="w")

    def _build_main_area(self):
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.BG_PANEL, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        topbar = ctk.CTkFrame(self.main_frame, height=60, fg_color=self.BG_CARD,
                               corner_radius=0, border_width=1,
                               border_color="#12122a")
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)

        ctk.CTkLabel(topbar, text="NOVA AI — JARVIS EDITION",
                     font=("Courier New", 13, "bold"),
                     text_color=self.TEXT_DIM).pack(side="left", padx=20, pady=18)

        self.live_status = ctk.CTkLabel(topbar, text="● STANDBY",
                                        font=("Courier New", 11, "bold"),
                                        text_color=self.NEON_RED)
        self.live_status.pack(side="right", padx=20)

        self.panel_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.panel_frame.grid(row=1, column=0, sticky="nsew")
        self.panel_frame.grid_rowconfigure(0, weight=1)
        self.panel_frame.grid_columnconfigure(0, weight=1)

        self.panels = {}
        self.panels["home"]    = self._build_home_panel(self.panel_frame)
        self.panels["help"]    = self._build_help_panel(self.panel_frame)
        self.panels["history"] = self._build_history_panel(self.panel_frame)
        self.panels["settings"]= self._build_settings_panel(self.panel_frame)

        self._switch_panel("home")

    def _build_home_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)

        chat_outer = ctk.CTkFrame(frame, fg_color=self.BG_CARD,
                                   corner_radius=16, border_width=1,
                                   border_color="#1a1a35")
        chat_outer.grid(row=0, column=0, sticky="nsew", padx=20, pady=(16, 8))
        chat_outer.grid_rowconfigure(0, weight=1)
        chat_outer.grid_columnconfigure(0, weight=1)

        self.chat_scroll = ctk.CTkScrollableFrame(
            chat_outer, fg_color="transparent", corner_radius=12)
        self.chat_scroll.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        controls = ctk.CTkFrame(frame, fg_color=self.BG_CARD,
                                 corner_radius=16, border_width=1,
                                 border_color="#1a1a35", height=160)
        controls.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 16))
        controls.grid_propagate(False)
        controls.grid_columnconfigure(0, weight=1)

        self.wave_widget = SoundWaveWidget(controls, width=500, height=50)
        self.wave_widget.grid(row=0, column=0, pady=(14, 4))

        self.status_text = ctk.CTkLabel(controls, text="Press mic or Space to speak",
                                         font=("Courier New", 11),
                                         text_color=self.TEXT_DIM)
        self.status_text.grid(row=1, column=0, pady=(0, 4))

        mic_frame = ctk.CTkFrame(controls, fg_color="transparent")
        mic_frame.grid(row=2, column=0, pady=(0, 12))

        self.mic_btn = ctk.CTkButton(
            mic_frame,
            text="🎤",
            width=60, height=60,
            font=("Segoe UI Emoji", 22),
            fg_color=self.BUBBLE_USER,
            hover_color=self.ACCENT_PURP,
            border_color=self.ACCENT_BLUE,
            border_width=2,
            corner_radius=30,
            command=self._on_mic_click
        )
        self.mic_btn.pack(side="left", padx=12)

        self.text_input = ctk.CTkEntry(
            mic_frame,
            placeholder_text="Or type a command here...",
            width=340,
            height=44,
            font=("Courier New", 12),
            fg_color="#0d0d22",
            border_color=self.TEXT_DIM,
            text_color=self.TEXT_PRI,
            placeholder_text_color=self.TEXT_DIM,
            corner_radius=22
        )
        self.text_input.pack(side="left", padx=4)
        self.text_input.bind("<Return>", self._on_text_submit)

        send_btn = ctk.CTkButton(
            mic_frame, text="→",
            width=44, height=44,
            font=("Courier New", 18, "bold"),
            fg_color=self.ACCENT_PURP,
            hover_color=self.ACCENT_BLUE,
            corner_radius=22,
            command=self._on_text_submit
        )
        send_btn.pack(side="left", padx=4)

        return frame

    def _build_help_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=20, pady=16)
        scroll.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(scroll, text="◈ COMMAND REFERENCE — JARVIS EDITION",
                     font=("Courier New", 18, "bold"),
                     text_color=self.ACCENT_BLUE).grid(row=0, column=0, pady=(8,16), sticky="w")

        commands = [
            ("🎙️  WAKE SYSTEM",   [
                ("Nova on",  "Activate continuous listening mode"),
                ("Nova off", "Deactivate — goes to sleep"),
            ]),
            ("📱  APP OPENING", [
                ("open youtube",      "Opens YouTube in browser"),
                ("open whatsapp",     "Opens WhatsApp Web"),
                ("open instagram",    "Opens Instagram"),
                ("open chatgpt",      "Opens ChatGPT"),
                ("+ 45 more apps",   "Just say the app name!"),
            ]),
            ("💻  POWER CONTROL", [
                ("shutdown",     "Shutdown PC (5 sec delay, say 'cancel' to abort)"),
                ("restart",      "Restart PC"),
                ("sleep",        "Put PC to sleep"),
                ("lock",         "Lock screen"),
            ]),
            ("🔔  REMINDERS", [
                ("remind me in 10 minutes to drink water", "Sets a timed reminder"),
                ("remind me after 2 hours to call mom",   "Hour-based reminder"),
                ("show reminders",                        "List all active reminders"),
            ]),
            ("🌤️   WEATHER", [
                ("weather today",         "Current weather (default city)"),
                ("weather in Delhi",      "Weather for specific city"),
                ("temperature in Mumbai", "Get temperature info"),
            ]),
            ("🔊  VOLUME", [
                ("volume up / volume down", "Adjust system volume by 10%"),
                ("volume 50",              "Set volume to 50%"),
                ("mute / unmute",          "Toggle mute"),
            ]),
            ("📋  CLIPBOARD", [
                ("copy hello world",   "Copies text to clipboard"),
                ("paste",              "Reads clipboard content"),
                ("clear clipboard",    "Empties clipboard"),
            ]),
            # ── NEW FEATURES IN HELP ──────────────────────────────
            ("🧠  AI BRAIN (NEW)", [
                ("explain quantum computing",  "AI-powered explanation (needs OpenAI key)"),
                ("write an email template",    "AI drafts content for you"),
                ("fix my code",               "AI helps debug"),
                ("analyze this topic",         "Get intelligent analysis"),
            ]),
            ("📂  FILE MANAGEMENT (NEW)", [
                ("open file resume",          "Opens file named 'resume' from your folders"),
                ("create file notes",         "Creates notes.txt in Documents"),
                ("delete file old_report",    "Safely deletes a file (with confirmation)"),
                ("search file budget",        "Searches entire home folder"),
                ("read file readme",          "Reads first 200 chars of a file"),
            ]),
            ("📸  SCREENSHOT (NEW)", [
                ("take screenshot",     "Captures full screen after 2 seconds"),
                ("save screenshot",     "Saves to ~/Nova_Screenshots/ folder"),
                ("screenshot",          "Same — opens folder after saving"),
            ]),
            ("🧠  MEMORY SYSTEM (NEW)", [
                ("my name is Arjun",           "Nova remembers your name"),
                ("my age is 22",               "Stores your age"),
                ("I live in Mumbai",           "Stores your location"),
                ("remember to call doctor",    "Stores any custom note"),
                ("what do you know about me",  "Recalls all stored memory"),
                ("forget call doctor",         "Removes a specific memory"),
            ]),
            ("⚙️   SYSTEM MONITOR (NEW)", [
                ("cpu usage",          "Shows current processor load"),
                ("ram usage",          "Shows memory usage & free space"),
                ("battery status",     "Shows battery % and charging status"),
                ("disk space",         "Shows storage used/free"),
                ("system status",      "Full system report"),
            ]),
            ("🌐  SMART SEARCH (NEW)", [
                ("quick search Python tutorials",  "Speaks a summary + opens browser"),
                ("brief search Albert Einstein",   "DuckDuckGo instant answer"),
            ]),
            ("🤖  TASK AUTOMATION (NEW)", [
                ("open youtube and play Believer",     "Multi-step: opens YT + searches song"),
                ("search Python and open",            "Searches and opens results"),
            ]),
            ("📧  EMAIL SENDER (NEW)", [
                ("send email to friend@gmail.com about meeting saying I will be late",
                 "Sends email (needs EMAIL config)"),
            ]),
            ("🧩  COMMAND LEARNING (NEW)", [
                ("when I say study mode, open youtube",        "Creates a custom shortcut"),
                ("when I say break time, open spotify",        "Another example"),
                ("show custom commands",                       "Lists all your custom commands"),
            ]),
            ("⚡  QUICK COMMANDS", [
                ("time / date",           "Current time and date"),
                ("play <song name>",      "Plays on YouTube"),
                ("search <query>",        "Smart search with spoken summary"),
                ("who is <person>",       "Wikipedia lookup"),
                ("what is <topic>",       "Wikipedia summary"),
                ("add custom app",        "Add your own app"),
                ("exit / bye",            "Close Nova"),
            ]),
        ]

        for sec_i, (section, items) in enumerate(commands):
            sec_frame = ctk.CTkFrame(scroll, fg_color=self.BG_CARD,
                                      corner_radius=12, border_width=1,
                                      border_color="#1a1a35")
            sec_frame.grid(row=sec_i+1, column=0, sticky="ew", pady=6)
            sec_frame.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(sec_frame, text=section,
                         font=("Courier New", 12, "bold"),
                         text_color=self.ACCENT_BLUE).grid(
                row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 6))

            for i, (cmd, desc) in enumerate(items):
                ctk.CTkLabel(sec_frame, text=f"  › {cmd}",
                             font=("Courier New", 11, "bold"),
                             text_color=self.NEON_GREEN,
                             anchor="w").grid(row=i+1, column=0, sticky="w", padx=16, pady=2)
                ctk.CTkLabel(sec_frame, text=desc,
                             font=("Courier New", 10),
                             text_color=self.TEXT_SEC,
                             anchor="w").grid(row=i+1, column=1, sticky="w", padx=8, pady=2)

            ctk.CTkFrame(sec_frame, height=10, fg_color="transparent").grid(
                row=len(items)+1, column=0)

        return frame

    def _build_history_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        toprow = ctk.CTkFrame(frame, fg_color="transparent")
        toprow.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))

        ctk.CTkLabel(toprow, text="◈ COMMAND HISTORY",
                     font=("Courier New", 16, "bold"),
                     text_color=self.ACCENT_BLUE).pack(side="left")

        ctk.CTkButton(toprow, text="Clear",
                      font=("Courier New", 11),
                      width=70, height=30,
                      fg_color=self.NEON_RED,
                      hover_color="#cc0044",
                      corner_radius=8,
                      command=self._clear_history).pack(side="right")

        self.history_scroll = ctk.CTkScrollableFrame(frame, fg_color=self.BG_CARD,
                                                      corner_radius=12,
                                                      border_width=1,
                                                      border_color="#1a1a35")
        self.history_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 16))
        self.history_scroll.grid_columnconfigure(0, weight=1)

        self.history_inner_row = 0

        return frame

    def _build_settings_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=20, pady=16)
        scroll.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(scroll, text="◈ SETTINGS",
                     font=("Courier New", 18, "bold"),
                     text_color=self.ACCENT_BLUE).grid(row=0, column=0, sticky="w", pady=(8,16))

        settings_items = [
            ("Default City for Weather", DEFAULT_CITY, "Change in source code: DEFAULT_CITY"),
            ("Weather API Key",          WEATHER_API_KEY[:18]+"...", "Change: WEATHER_API_KEY"),
            ("OpenAI API Key",           OPENAI_API_KEY[:18]+"...", "Change: OPENAI_API_KEY (for AI Brain)"),
            ("Email Address",            EMAIL_ADDRESS[:20], "Change: EMAIL_ADDRESS (for Email feature)"),
            ("Wake Phrase (ON)",         NOVA_ON_PHRASE, "Trigger: activates Nova"),
            ("Wake Phrase (OFF)",        NOVA_OFF_PHRASE, "Trigger: deactivates Nova"),
            ("TTS Voice Speed",         "170 words/min", "Change in source code: engine rate"),
            ("Keyboard Shortcut",       "Space bar", "Press Space to listen"),
            ("Recognition Engine",      "Google Speech API", "Requires internet connection"),
            ("Memory File",             MEMORY_FILE, "JSON-based persistent user memory"),
            ("Custom Commands File",    CUSTOM_CMDS_FILE, "JSON-based custom shortcuts"),
            ("Screenshot Folder",       SCREENSHOT_DIR, "Where screenshots are saved"),
        ]

        for i, (label, val, note) in enumerate(settings_items):
            row_frame = ctk.CTkFrame(scroll, fg_color=self.BG_CARD,
                                      corner_radius=10, border_width=1,
                                      border_color="#1a1a35")
            row_frame.grid(row=i+1, column=0, sticky="ew", pady=4)

            ctk.CTkLabel(row_frame, text=label,
                         font=("Courier New", 11, "bold"),
                         text_color=self.TEXT_SEC).pack(anchor="w", padx=16, pady=(10, 2))
            ctk.CTkLabel(row_frame, text=val,
                         font=("Courier New", 12),
                         text_color=self.ACCENT_GLOW).pack(anchor="w", padx=16)
            ctk.CTkLabel(row_frame, text=note,
                         font=("Courier New", 9),
                         text_color=self.TEXT_DIM).pack(anchor="w", padx=16, pady=(0, 10))

        hint = ctk.CTkFrame(scroll, fg_color="#0d1f35", corner_radius=10,
                             border_width=1, border_color=self.ACCENT_BLUE)
        hint.grid(row=len(settings_items)+1, column=0, sticky="ew", pady=12)

        ctk.CTkLabel(hint, text="⌨  KEYBOARD SHORTCUTS",
                     font=("Courier New", 11, "bold"),
                     text_color=self.ACCENT_BLUE).pack(anchor="w", padx=16, pady=(12,4))
        for key, action in [
            ("Space",   "Start listening (one-shot command)"),
            ("Enter",   "Submit typed command"),
            ("Escape",  "Cancel / close dialogs"),
        ]:
            row = ctk.CTkFrame(hint, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=2)
            ctk.CTkLabel(row, text=key,
                         font=("Courier New", 11, "bold"),
                         fg_color="#1a1a40", corner_radius=4,
                         width=70,
                         text_color=self.NEON_GREEN).pack(side="left")
            ctk.CTkLabel(row, text=f"  {action}",
                         font=("Courier New", 10),
                         text_color=self.TEXT_SEC).pack(side="left")
        ctk.CTkFrame(hint, height=12, fg_color="transparent").pack()

        return frame

    # ── PANEL SWITCHING (Unchanged) ────────────────────────────

    def _switch_panel(self, key):
        for k, panel in self.panels.items():
            panel.grid_remove()
        self.panels[key].grid(row=0, column=0, sticky="nsew")
        self.current_panel = key

        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color="#111130", text_color=self.ACCENT_BLUE)
            else:
                btn.configure(fg_color="transparent", text_color=self.TEXT_SEC)

    # ── CHAT BUBBLES (Unchanged) ───────────────────────────────

    def _add_bubble(self, sender: str, text: str):
        is_nova = (sender == "nova")
        row = len(self.chat_scroll.winfo_children())

        outer = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        outer.grid(row=row, column=0, sticky="ew", pady=4, padx=8)
        outer.grid_columnconfigure(0, weight=1)

        bubble_color = self.BUBBLE_NOVA if is_nova else self.BUBBLE_USER
        border_color = self.ACCENT_BLUE if is_nova else self.ACCENT_PURP
        label_text   = "◈ NOVA" if is_nova else "YOU"
        label_color  = self.ACCENT_BLUE if is_nova else self.ACCENT_PURP
        anchor       = "w" if is_nova else "e"
        padx_args    = (0, 80) if is_nova else (80, 0)

        bubble = ctk.CTkFrame(outer, fg_color=bubble_color,
                               corner_radius=14, border_width=1,
                               border_color=border_color)
        bubble.grid(row=0, column=0, sticky=anchor, padx=padx_args)

        ctk.CTkLabel(bubble, text=label_text,
                     font=("Courier New", 9, "bold"),
                     text_color=label_color).pack(anchor="w", padx=14, pady=(8,0))

        ctk.CTkLabel(bubble, text=text,
                     font=("Courier New", 12),
                     text_color=self.TEXT_PRI,
                     wraplength=380,
                     justify="left").pack(anchor="w", padx=14, pady=(2, 10))

        now = datetime.datetime.now().strftime("%H:%M")
        ctk.CTkLabel(bubble, text=now,
                     font=("Courier New", 8),
                     text_color=self.TEXT_DIM).pack(anchor="e", padx=14, pady=(0, 6))

        self.root.after(100, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))

    # ── HISTORY (Unchanged) ────────────────────────────────────

    def _add_history_item(self, text: str):
        self.history_items.append(text)
        now = datetime.datetime.now().strftime("%H:%M:%S")

        row_f = ctk.CTkFrame(self.history_scroll, fg_color=self.BG_PANEL,
                              corner_radius=8, border_width=1,
                              border_color="#1a1a35")
        row_f.grid(row=self.history_inner_row, column=0, sticky="ew", pady=3)
        row_f.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(row_f, text=now,
                     font=("Courier New", 9),
                     text_color=self.TEXT_DIM).grid(row=0, column=1, padx=12, pady=(6,0), sticky="e")
        ctk.CTkLabel(row_f, text=f"  › {text}",
                     font=("Courier New", 11),
                     text_color=self.NEON_GREEN,
                     anchor="w").grid(row=0, column=0, sticky="w", padx=12, pady=(6, 6))

        self.history_inner_row += 1

    def _clear_history(self):
        for widget in self.history_scroll.winfo_children():
            widget.destroy()
        self.history_items = []
        self.history_inner_row = 0

    # ── STATUS / MODE (Unchanged) ──────────────────────────────

    def _set_mode(self, active: bool):
        if active:
            self.mode_label.configure(text="Active Mode", text_color=self.NEON_GREEN)
            self.dot_canvas.itemconfig(self.dot_oval, fill=self.NEON_GREEN)
            self.live_status.configure(text="● ACTIVE", text_color=self.NEON_GREEN)
        else:
            self.mode_label.configure(text="Sleep Mode", text_color=self.NEON_RED)
            self.dot_canvas.itemconfig(self.dot_oval, fill=self.NEON_RED)
            self.live_status.configure(text="● STANDBY", text_color=self.NEON_RED)

        if self.toggle_var.get() != active:
            self.toggle_var.set(active)

    def _set_status(self, text: str, state: str):
        colors = {
            "listening":  self.ACCENT_BLUE,
            "processing": "#ffcc00",
            "speaking":   self.ACCENT_PURP,
            "idle":       self.TEXT_DIM,
        }
        color = colors.get(state, self.TEXT_DIM)
        self.status_text.configure(text=text, text_color=color)

        if state == "listening":
            self.live_status.configure(text="● LISTENING", text_color=self.ACCENT_BLUE)
            self.mic_btn.configure(fg_color=self.ACCENT_PURP, border_color=self.ACCENT_GLOW)
        elif state == "processing":
            self.live_status.configure(text="● PROCESSING", text_color="#ffcc00")
        elif state == "speaking":
            self.live_status.configure(text="● SPEAKING", text_color=self.ACCENT_PURP)
        elif state == "idle":
            self.mic_btn.configure(fg_color=self.BUBBLE_USER, border_color=self.ACCENT_BLUE)
            if self.assistant.is_active:
                self.live_status.configure(text="● ACTIVE", text_color=self.NEON_GREEN)
            else:
                self.live_status.configure(text="● STANDBY", text_color=self.NEON_RED)

    # ── EVENTS / CONTROLS ──────────────────────────────────────

    def _on_toggle_switch(self):
        new_state = self.toggle_var.get()
        if new_state != self.assistant.is_active:
            self.assistant.is_active = new_state
            self._set_mode(new_state)
            if new_state:
                speak("Nova is now active. What can I do for you?")
            else:
                speak("Nova is now off. Toggle or say Nova on to wake me.")

    def _on_mic_click(self):
        if self.mic_listening:
            return
        self.mic_listening = True
        self.mic_btn.configure(fg_color=self.ACCENT_PURP)
        t = threading.Thread(target=self._mic_thread, daemon=True)
        t.start()

    def _mic_thread(self):
        self.assistant.listen_single_command()
        self.mic_listening = False
        ui_event_queue.put({"type": "status", "text": "Press mic or Space to speak", "state": "idle"})

    def _on_text_submit(self, event=None):
        text = self.text_input.get().strip()
        if not text:
            return
        self.text_input.delete(0, "end")
        self._add_bubble("user", text)
        self._add_history_item(text)
        t = threading.Thread(target=self.assistant.process_command, args=(text.lower(),), daemon=True)
        t.start()

    def _bind_shortcuts(self):
        self.root.bind("<space>", self._on_space_key)
        self.root.bind("<Escape>", lambda e: None)

    def _on_space_key(self, event=None):
        focused = self.root.focus_get()
        if focused == self.text_input._entry:
            return
        self._on_mic_click()

    # ── BACKGROUND ASSISTANT THREAD ────────────────────────────

    def _start_assistant_thread(self):
        t = threading.Thread(target=self.assistant.run, daemon=True)
        t.start()

    # ── UI EVENT POLLING (Extended for new events) ─────────────

    def _poll_ui_events(self):
        try:
            while not ui_event_queue.empty():
                event = ui_event_queue.get_nowait()
                etype = event.get("type")

                if etype == "nova_message":
                    self._add_bubble("nova", event["text"])

                elif etype == "user_message":
                    self._add_bubble("user", event["text"])

                elif etype == "status":
                    self._set_status(event["text"], event.get("state", "idle"))

                elif etype == "mode":
                    self._set_mode(event["active"])

                elif etype == "wave":
                    self.wave_widget.set_active(event["active"])

                elif etype == "history":
                    self._add_history_item(event["text"])

                elif etype == "show_help":
                    self._switch_panel("help")

                # ── NEW: Handle delete confirmation dialog ──────────
                elif etype == "confirm_delete":
                    self._show_delete_confirm(event["filepath"], event["filename"])

                elif etype == "quit":
                    self.root.after(1500, self.root.destroy)

        except Exception:
            pass

        self.root.after(80, self._poll_ui_events)

    # ── NEW: Delete confirmation dialog ────────────────────────
    def _show_delete_confirm(self, filepath: str, filename: str):
        """Show a GUI confirmation dialog for file deletion."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Confirm Delete")
        dialog.geometry("420x200")
        dialog.configure(fg_color=self.BG_CARD)
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="⚠  DELETE CONFIRMATION",
                     font=("Courier New", 13, "bold"),
                     text_color=self.NEON_RED).pack(pady=(20, 8))
        ctk.CTkLabel(dialog, text=f"Delete: {filename}?",
                     font=("Courier New", 11),
                     text_color=self.TEXT_PRI).pack(pady=4)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=16)

        def on_yes():
            dialog.destroy()
            self.assistant._pending_delete = None
            threading.Thread(
                target=self.assistant.advanced.confirm_delete_file,
                args=(filepath, True),
                daemon=True
            ).start()

        def on_no():
            dialog.destroy()
            self.assistant._pending_delete = None
            threading.Thread(
                target=self.assistant.advanced.confirm_delete_file,
                args=(filepath, False),
                daemon=True
            ).start()

        ctk.CTkButton(btn_frame, text="✓ Delete",
                      fg_color=self.NEON_RED, hover_color="#cc0044",
                      font=("Courier New", 12, "bold"),
                      width=120, height=38,
                      corner_radius=8,
                      command=on_yes).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="✗ Cancel",
                      fg_color=self.ACCENT_PURP, hover_color=self.ACCENT_BLUE,
                      font=("Courier New", 12, "bold"),
                      width=120, height=38,
                      corner_radius=8,
                      command=on_no).pack(side="left", padx=10)

    # ── RUN ────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "═" * 70)
    print("   🚀  NOVA AI — JARVIS EDITION  |  STARTING UP...")
    print("═" * 70)
    print(f"   📁 Data folder  : {DATA_DIR}")
    print(f"   📸 Screenshots  : {SCREENSHOT_DIR}")
    print(f"   🧠 Memory file  : {MEMORY_FILE}")
    print(f"   🧩 Custom cmds  : {CUSTOM_CMDS_FILE}")
    print(f"   🤖 OpenAI       : {'Configured ✓' if OPENAI_API_KEY != 'YOUR_OPENAI_API_KEY_HERE' else 'Not set (fallback mode)'}")
    print(f"   📧 Email        : {'Configured ✓' if EMAIL_ADDRESS != 'shankarmande34@gmai.com' else 'Not set (disabled)'}")
    print(f"   ⚙️  psutil       : {'Available ✓' if PSUTIL_AVAILABLE else 'Not available'}")
    print(f"   📸 pyautogui    : {'Available ✓' if PYAUTOGUI_AVAILABLE else 'Not available'}")
    print("═" * 70 + "\n")

    app = NovaGUI()
    app.run()
