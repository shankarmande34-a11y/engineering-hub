
import tkinter as tk
from tkinter import ttk, font
import requests
import json
import datetime
import re
import threading
import math
from typing import Optional, Dict, Any

# ═══════════════════════════════════════════════════════════════
# YOUR API KEY
# ═══════════════════════════════════════════════════════════════

WEATHER_API_KEY = "253f05fe222d4d32f9cd6c52b70d487a"
DEFAULT_CITY = "Mumbai"

# ═══════════════════════════════════════════════════════════════
# WEATHER CLASS
# ═══════════════════════════════════════════════════════════════

class RealWeather:
    def __init__(self, api_key: str = WEATHER_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.units = "metric"
        
    def get_weather(self, city: str) -> Optional[Dict[str, Any]]:
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            return {
                'error': 'API_KEY_MISSING',
                'message': 'Weather API key not configured.'
            }
        
        try:
            city = city.strip().title()
            params = {
                'q': city,
                'appid': self.api_key,
                'units': self.units,
                'lang': 'en'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_weather_data(data, city)
            else:
                return {
                    'error': 'CITY_NOT_FOUND',
                    'message': f"City '{city}' not found."
                }
        except Exception as e:
            return {
                'error': 'ERROR',
                'message': f"Error: {str(e)}"
            }
    
    def _parse_weather_data(self, data: Dict, city: str) -> Dict:
        try:
            weather_code = data['weather'][0]['id']
            return {
                'city': city,
                'country': data.get('sys', {}).get('country', ''),
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'temp_min': round(data['main']['temp_min']),
                'temp_max': round(data['main']['temp_max']),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'].capitalize(),
                'main_condition': data['weather'][0]['main'],
                'wind_speed': data['wind']['speed'],
                'wind_degree': data['wind'].get('deg', 0),
                'clouds': data.get('clouds', {}).get('all', 0),
                'sunrise': datetime.datetime.fromtimestamp(data['sys']['sunrise']).strftime('%I:%M %p'),
                'sunset': datetime.datetime.fromtimestamp(data['sys']['sunset']).strftime('%I:%M %p'),
                'visibility': data.get('visibility', 0) / 1000,
                'icon': self._get_weather_emoji(weather_code),
                'icon_code': data['weather'][0]['icon'],
                'raw': data
            }
        except KeyError as e:
            return {
                'error': 'PARSE_ERROR',
                'message': f"Error parsing weather data"
            }
    
    def _get_weather_emoji(self, code: int) -> str:
        if 200 <= code < 300: return '⛈️'
        elif 300 <= code < 400: return '🌧️'
        elif 500 <= code < 600: return '🌧️'
        elif 600 <= code < 700: return '❄️'
        elif 700 <= code < 800: return '🌫️'
        elif code == 800: return '☀️'
        elif code <= 802: return '🌤️'
        elif code <= 804: return '☁️'
        else: return '🌡️'


# ═══════════════════════════════════════════════════════════════
# PREMIUM WEATHER DASHBOARD (FIXED)
# ═══════════════════════════════════════════════════════════════

class PremiumWeatherDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌤️ NOVA - Weather Dashboard")
        self.root.geometry("900x750")
        self.root.configure(bg='#0a0a1a')
        self.root.resizable(False, False)
        
        # Weather instance
        self.weather = RealWeather(WEATHER_API_KEY)
        self.current_weather = None
        
        # Colors
        self.colors = {
            'bg': '#0a0a1a',
            'bg_card': '#111128',
            'bg_card2': '#0d0d22',
            'border': '#1a2a4a',
            'text_primary': '#e8f0ff',
            'text_secondary': '#88aacc',
            'text_dim': '#445577',
            'accent_blue': '#4a9eff',
            'accent_cyan': '#00d4ff',
            'accent_purple': '#7c3aed',
            'accent_green': '#00ff88',
            'accent_red': '#ff4466',
            'accent_orange': '#ff8844',
        }
        
        self._build_ui()
        self._bind_shortcuts()
        
        # Load default weather
        self.root.after(500, lambda: self.fetch_weather(DEFAULT_CITY))
    
    def _build_ui(self):
        """Build the dashboard UI"""
        
        # ── Main Container ──────────────────────────────────────
        self.main = tk.Frame(self.root, bg=self.colors['bg'])  # ← FIXED: Made self.main
        self.main.pack(fill='both', expand=True, padx=25, pady=20)
        
        # ── Header ──────────────────────────────────────────────
        header = tk.Frame(self.main, bg=self.colors['bg'])
        header.pack(fill='x', pady=(0, 20))
        
        # Logo
        tk.Label(
            header,
            text="🌤️ NOVA WEATHER",
            font=('Segoe UI', 20, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg']
        ).pack(side='left')
        
        # Status
        self.status_label = tk.Label(
            header,
            text="● ONLINE",
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['accent_green'],
            bg=self.colors['bg']
        )
        self.status_label.pack(side='right', pady=5)
        
        # ── Search Bar ──────────────────────────────────────────
        search_frame = tk.Frame(self.main, bg=self.colors['bg'])
        search_frame.pack(fill='x', pady=(0, 20))
        
        self.search_entry = tk.Entry(
            search_frame,
            font=('Segoe UI', 12),
            bg=self.colors['bg_card2'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_cyan'],
            relief='flat',
            highlightthickness=1,
            highlightcolor=self.colors['accent_cyan'],
            highlightbackground=self.colors['border']
        )
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10), ipady=8)
        self.search_entry.insert(0, "Search city...")
        self.search_entry.bind('<FocusIn>', self._clear_placeholder)
        self.search_entry.bind('<Return>', lambda e: self.fetch_weather(self.search_entry.get()))
        
        search_btn = tk.Button(
            search_frame,
            text="🔍 Search",
            font=('Segoe UI', 11, 'bold'),
            fg='white',
            bg=self.colors['accent_blue'],
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8,
            command=lambda: self.fetch_weather(self.search_entry.get())
        )
        search_btn.pack(side='right')
        
        # ── Weather Cards Grid ──────────────────────────────────
        self.cards_frame = tk.Frame(self.main, bg=self.colors['bg'])
        self.cards_frame.pack(fill='both', expand=True)
        
        # Build the cards
        self._build_cards()
        
        # ── Footer ──────────────────────────────────────────────
        footer = tk.Frame(self.main, bg=self.colors['bg'])  # ← FIXED: Now self.main exists
        footer.pack(fill='x', pady=(15, 0))
        
        tk.Label(
            footer,
            text="◆ NOVA AI WEATHER v3.0 ◆ Powered by OpenWeatherMap ◆",
            font=('Segoe UI', 9),
            fg=self.colors['text_dim'],
            bg=self.colors['bg']
        ).pack()
    
    def _build_cards(self):
        """Build all weather cards"""
        
        # ── Main Weather Card ────────────────────────────────────
        main_card = self._create_card(self.cards_frame, row=0, col=0, col_span=2)
        main_card.configure(height=250)
        
        # City and date
        self.city_label = tk.Label(
            main_card,
            text="📍 Loading...",
            font=('Segoe UI', 14),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_card']
        )
        self.city_label.pack(anchor='w', padx=25, pady=(20, 5))
        
        # Date
        self.date_label = tk.Label(
            main_card,
            text=datetime.datetime.now().strftime("%A, %B %d • %Y"),
            font=('Segoe UI', 10),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card']
        )
        self.date_label.pack(anchor='w', padx=25)
        
        # Weather icon and temperature row
        temp_row = tk.Frame(main_card, bg=self.colors['bg_card'])
        temp_row.pack(anchor='w', padx=25, pady=(15, 5))
        
        self.weather_icon = tk.Label(
            temp_row,
            text="🌍",
            font=('Segoe UI Emoji', 48),
            bg=self.colors['bg_card']
        )
        self.weather_icon.pack(side='left')
        
        self.temp_label = tk.Label(
            temp_row,
            text="--°",
            font=('Segoe UI', 52, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_card']
        )
        self.temp_label.pack(side='left', padx=(15, 0))
        
        # Condition
        self.condition_label = tk.Label(
            main_card,
            text="Waiting for data...",
            font=('Segoe UI', 16),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_card']
        )
        self.condition_label.pack(anchor='w', padx=25, pady=(5, 20))
        
        # ── Details Card ─────────────────────────────────────────
        details_card = self._create_card(self.cards_frame, row=0, col=2)
        
        # Details header
        tk.Label(
            details_card,
            text="📊 WEATHER DETAILS",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=20, pady=(15, 15))
        
        # Detail items
        detail_items = [
            ('💧 Humidity', 'humidity', '--%'),
            ('🌡️ Feels Like', 'feels', '--°'),
            ('💨 Wind Speed', 'wind', '-- m/s'),
            ('📊 Pressure', 'pressure', '-- hPa'),
            ('☁️ Cloud Cover', 'clouds', '--%'),
            ('👁️ Visibility', 'visibility', '-- km'),
        ]
        
        self.detail_labels = {}
        for i, (label, key, default) in enumerate(detail_items):
            item_frame = tk.Frame(details_card, bg=self.colors['bg_card'])
            item_frame.pack(fill='x', padx=20, pady=3)
            
            tk.Label(
                item_frame,
                text=label,
                font=('Segoe UI', 10),
                fg=self.colors['text_dim'],
                bg=self.colors['bg_card']
            ).pack(side='left')
            
            val_label = tk.Label(
                item_frame,
                text=default,
                font=('Segoe UI', 11, 'bold'),
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_card']
            )
            val_label.pack(side='right')
            self.detail_labels[key] = val_label
        
        # ── Sun Card ─────────────────────────────────────────────
        sun_card = self._create_card(self.cards_frame, row=1, col=0)
        
        tk.Label(
            sun_card,
            text="🌅 SUNRISE / SUNSET",
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=20, pady=(15, 10))
        
        sun_row = tk.Frame(sun_card, bg=self.colors['bg_card'])
        sun_row.pack(fill='x', padx=20, pady=5)
        
        self.sunrise_label = tk.Label(
            sun_row,
            text="🌅 --:-- AM",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['accent_orange'],
            bg=self.colors['bg_card']
        )
        self.sunrise_label.pack(side='left')
        
        self.sunset_label = tk.Label(
            sun_row,
            text="🌇 --:-- PM",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['accent_purple'],
            bg=self.colors['bg_card']
        )
        self.sunset_label.pack(side='right')
        
        # ── Wind Card ────────────────────────────────────────────
        wind_card = self._create_card(self.cards_frame, row=1, col=1)
        
        tk.Label(
            wind_card,
            text="💨 WIND INFORMATION",
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=20, pady=(15, 10))
        
        wind_row = tk.Frame(wind_card, bg=self.colors['bg_card'])
        wind_row.pack(fill='x', padx=20, pady=5)
        
        self.wind_speed_label = tk.Label(
            wind_row,
            text="-- m/s",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['accent_cyan'],
            bg=self.colors['bg_card']
        )
        self.wind_speed_label.pack(side='left')
        
        self.wind_dir_label = tk.Label(
            wind_row,
            text="Direction: --°",
            font=('Segoe UI', 11),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_card']
        )
        self.wind_dir_label.pack(side='right')
        
        # ── Extra Info Card ──────────────────────────────────────
        extra_card = self._create_card(self.cards_frame, row=1, col=2)
        
        tk.Label(
            extra_card,
            text="📈 ADDITIONAL INFO",
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_card']
        ).pack(anchor='w', padx=20, pady=(15, 10))
        
        extra_items = [
            ('Temperature Range', 'temp_range', '--° / --°'),
            ('Condition Code', 'condition_code', '--'),
        ]
        
        self.extra_labels = {}
        for label, key, default in extra_items:
            item_frame = tk.Frame(extra_card, bg=self.colors['bg_card'])
            item_frame.pack(fill='x', padx=20, pady=3)
            
            tk.Label(
                item_frame,
                text=label,
                font=('Segoe UI', 10),
                fg=self.colors['text_dim'],
                bg=self.colors['bg_card']
            ).pack(side='left')
            
            val_label = tk.Label(
                item_frame,
                text=default,
                font=('Segoe UI', 11, 'bold'),
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_card']
            )
            val_label.pack(side='right')
            self.extra_labels[key] = val_label
    
    def _create_card(self, parent, row, col, col_span=1):
        """Create a card widget"""
        card = tk.Frame(
            parent,
            bg=self.colors['bg_card'],
            relief='flat',
            highlightthickness=1,
            highlightcolor=self.colors['border'],
            highlightbackground=self.colors['border']
        )
        card.grid(row=row, column=col, columnspan=col_span, 
                  padx=5, pady=5, sticky='nsew')
        
        # Configure grid weights
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)
        
        return card
    
    def _clear_placeholder(self, event):
        if self.search_entry.get() == "Search city...":
            self.search_entry.delete(0, 'end')
    
    def _bind_shortcuts(self):
        self.root.bind('<Control-r>', lambda e: self.fetch_weather(self.search_entry.get()))
        self.root.bind('<Escape>', lambda e: self.root.quit())
    
    def fetch_weather(self, city: str):
        """Fetch weather for city"""
        if not city or city == "Search city...":
            city = DEFAULT_CITY
        
        self.status_label.config(text="● SCANNING", fg=self.colors['accent_cyan'])
        self.city_label.config(text=f"📍 {city.upper()}, scanning...")
        
        def fetch():
            data = self.weather.get_weather(city)
            self.root.after(0, lambda: self._update_dashboard(data))
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def _update_dashboard(self, data):
        """Update dashboard with weather data"""
        if 'error' in data:
            self.status_label.config(text="● OFFLINE", fg=self.colors['accent_red'])
            self.city_label.config(text="❌ City not found")
            self.temp_label.config(text="--°")
            self.condition_label.config(text=data['message'])
            self.weather_icon.config(text="🚨")
            return
        
        self.current_weather = data
        self.status_label.config(text="● ONLINE", fg=self.colors['accent_green'])
        
        # ── Main Card ────────────────────────────────────────────
        city_display = f"{data['city']}, {data['country']}" if data['country'] else data['city']
        self.city_label.config(text=f"📍 {city_display}")
        self.temp_label.config(text=f"{data['temperature']}°")
        self.condition_label.config(text=data['description'])
        self.weather_icon.config(text=data['icon'])
        
        # ── Details ──────────────────────────────────────────────
        self.detail_labels['humidity'].config(text=f"{data['humidity']}%")
        self.detail_labels['feels'].config(text=f"{data['feels_like']}°")
        self.detail_labels['wind'].config(text=f"{data['wind_speed']:.1f} m/s")
        self.detail_labels['pressure'].config(text=f"{data['pressure']} hPa")
        self.detail_labels['clouds'].config(text=f"{data['clouds']}%")
        self.detail_labels['visibility'].config(text=f"{data['visibility']:.1f} km")
        
        # ── Sun Card ─────────────────────────────────────────────
        self.sunrise_label.config(text=f"🌅 {data['sunrise']}")
        self.sunset_label.config(text=f"🌇 {data['sunset']}")
        
        # ── Wind Card ────────────────────────────────────────────
        self.wind_speed_label.config(text=f"{data['wind_speed']:.1f} m/s")
        self.wind_dir_label.config(text=f"Direction: {data['wind_degree']}°")
        
        # ── Extra Info ───────────────────────────────────────────
        self.extra_labels['temp_range'].config(
            text=f"{data['temp_min']}° / {data['temp_max']}°"
        )
        self.extra_labels['condition_code'].config(
            text=f"{data['main_condition']}"
        )
        
        # ── Speak ────────────────────────────────────────────────
        self._speak_weather(data)
    
    def _speak_weather(self, data):
        """Speak weather using TTS"""
        try:
            import pyttsx3
            speech = f"Weather in {data['city']}: {data['description']}. "
            speech += f"Temperature is {data['temperature']} degrees Celsius. "
            speech += f"Humidity is {data['humidity']} percent. "
            speech += f"Wind speed is {data['wind_speed']} meters per second."
            
            engine = pyttsx3.init()
            engine.say(speech)
            engine.runAndWait()
        except:
            pass
    
    def run(self):
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = PremiumWeatherDashboard()
    app.run()