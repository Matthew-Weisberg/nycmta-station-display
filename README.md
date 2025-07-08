# mta_train_tracker
Using MTA realtime API to develop raspberry_pi train tracking display


# NYC Subway + Weather Display in Pygame

[![Demo](https://github.com/Matthew-Weisberg/nycmta-station-display/blob/main/MTA_Station_Display.gif))

**A fullscreen Pygame interface that visualizes real-time NYC subway arrivals and current weather conditions using the MTA GTFS-RT feed and the Open-Meteo API.**

---

## 🗽 Overview

This Python package creates a customizable, touch-friendly UI using [Pygame](https://www.pygame.org/) to show:

- 🚇 **Real-time subway train arrival times** for a specified NYC station  
- 🌤️ **Current and daily weather conditions** using the [Open-Meteo API](https://open-meteo.com/)
- ⚙️ **Settings interface** to change the subway station dynamically

Perfect for wall-mounted displays, kiosks, Raspberry Pi setups, or personal dashboards.

---

## 📦 Features

- Real-time train arrival data from MTA GTFS-RT feeds
- Clean, responsive UI rendered with Pygame
- Dynamic weather updates including temperature, UV index, and conditions
- Modifiable settings for station selection
- Works on desktop or Raspberry Pi setups
- Optimized for touch input (no keyboard/mouse required)

---

## 📸 Demo

> Click the GIF above to see it in action.

---

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables (optional but recommended)**
   - Configure settings in a `.env` or `config.toml` file if applicable

---

## 🛠 Usage

```bash
python core.py
```

- The application will start in fullscreen mode
- Use the settings screen to choose your preferred subway station

---

## 🔧 Configuration

You can modify default settings via:

- `config.toml` (preferred for long-term use)
- In-app settings screen (touch-compatible)

Supported station IDs match those in MTA's GTFS `stops.txt`.

---

## 🌐 APIs Used

- **NYC MTA GTFS-RT** for real-time subway train arrival data  
- **Open-Meteo** for weather and forecast data  

---

## 📁 File Structure

```
your-repo-name/
├── src
|   └── nycmta_station_display/
|       └── core.py
|       └── gtfs_realtime_pb2.py
|       └── open_meteo_connector.py
|       └── utils.py
|       └── gui/
|           └── screen_manage.py
|           └── home_screen.py
|           └── settings_screen.py
|           └── bullet_select_screen.py
|           └── station_select_screen.py
|           └── base_screen.py
|           └── gui_utils.py
|       └── config/
|           └── config.toml
├── assets/
│   └── gtfs_subway/
|   └── images/
|           └── icons/
|           └── weather_icons/
|           └── bullets/
|           └── wpo_icons/
|           └── r211.png
├── LICENSE.txt
├── requirements.txt
├── setup.py
└── README.md
```

---

## License
This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

---

## 🙌 Acknowledgments

- NYC MTA for providing public GTFS and GTFS-RT feeds  
- Open-Meteo for free weather API access  
- [Pygame](https://www.pygame.org/) community for the awesome rendering engine

---

## 👨‍💻 Author

Matthew Weisberg  
Feel free to reach out or contribute!

