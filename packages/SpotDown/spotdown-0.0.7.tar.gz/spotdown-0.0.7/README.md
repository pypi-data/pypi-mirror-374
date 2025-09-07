# SpotDown 🎵

<div align="center">

## 📊 Project Status & Info
[![PyPI Version](https://img.shields.io/pypi/v/spotdown?logo=pypi&logoColor=white&labelColor=2d3748&color=3182ce&style=for-the-badge)](https://pypi.org/project/spotdown)
[![Last Commit](https://img.shields.io/github/last-commit/Arrowar/spotdown?logo=git&logoColor=white&labelColor=2d3748&color=805ad5&style=for-the-badge)](https://github.com/Arrowar/spotdown/commits)
[![Issues](https://img.shields.io/github/issues/Arrowar/spotdown?logo=github&logoColor=white&labelColor=2d3748&color=ed8936&style=for-the-badge)](https://github.com/Arrowar/spotdown/issues)
[![License](https://img.shields.io/github/license/Arrowar/spotdown?logo=gnu&logoColor=white&labelColor=2d3748&color=e53e3e&style=for-the-badge)](https://github.com/Arrowar/spotdown/blob/main/LICENSE)

## 💝 Support the Project

[![Donate PayPal](https://img.shields.io/badge/💳_Donate-PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white&labelColor=2d3748)](https://www.paypal.com/donate/?hosted_button_id=UXTWMT8P6HE2C)
## 🚀 Download & Install

[![Windows](https://img.shields.io/badge/🪟_Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white&labelColor=2d3748)](https://github.com/Arrowar/spotdown/releases/latest/download/spotdown_win.exe)
[![macOS](https://img.shields.io/badge/🍎_macOS-000000?style=for-the-badge&logo=apple&logoColor=white&labelColor=2d3748)](https://github.com/Arrowar/spotdown/releases/latest/download/spotdown_mac)
[![Linux latest](https://img.shields.io/badge/🐧_Linux_latest-FCC624?style=for-the-badge&logo=linux&logoColor=black&labelColor=2d3748)](https://github.com/Arrowar/spotdown/releases/latest/download/spotdown_linux_latest)
[![Linux 22.04](https://img.shields.io/badge/🐧_Linux_22.04-FCC624?style=for-the-badge&logo=linux&logoColor=black&labelColor=2d3748)](https://github.com/Arrowar/spotdown/releases/latest/download/spotdown_linux_previous)

---

*⚡ **Quick Start:** `pip install spotdown` or download the executable for your platform above*

</div>

## 📋 Table of Contents

- [✨ Features](#features)
- [🛠️ Installation](#installation)
- [⚙️ Configuration](#configuration)
- [💻 Usage](#usage)
- [📁 Project Structure](#project-structure)
- [🔧 Dependencies](#dependencies)
- [⚠️ Disclaimer](#disclaimer)

## ✨ Features

- 🎵 **Download individual songs** from Spotify
- 📋 **Download entire playlists** with ease
- 🔍 **No authentication required** - uses web scraping
- 🎨 **Automatic cover art embedding** (JPEG format)

## 🛠️ Installation

### Prerequisites

- **Python 3.8+**
- **FFmpeg** (for audio processing)
- **yt-dlp** (for downloading)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright Chromium

```bash
playwright install chromium
```

### 3. Quick Start

Create a simple launcher script:

```python
from spotdown.run import main

if __name__ == "__main__":
    main()
```

## ⚙️ Configuration

SpotDown uses a JSON configuration file with the following structure:

```json
{
    "DEFAULT": {
        "clean_console": true,
        "show_message": true
    },
    "DOWNLOAD": {
        "auto_first": false,
        "quality": "320K"
    },
    "BROWSER": {
        "headless": true,
        "timeout": 6
    }
}
```

### Configuration Options

#### DEFAULT Settings
- **`clean_console`**: Clear console output for cleaner interface
- **`show_message`**: Display informational messages during execution

#### DOWNLOAD Settings
- **`auto_first`**: Automatically select first search result
- **`quality`**: Audio quality (320K recommended for best quality)

#### BROWSER Settings
- **`headless`**: Run browser in background (recommended: true)
- **`timeout`**: Browser timeout in seconds

## 💻 Usage

### Basic Usage

```bash
python run.py
```

### Download Individual Songs

1. Run the script
2. Paste the Spotify song URL when prompted
3. The script will automatically:
   - Extract song information
   - Search for the best quality version
   - Download as MP3 with embedded cover art

### Download Playlists

1. Run the script  
2. Paste the Spotify playlist URL when prompted
3. All songs in the playlist will be downloaded automatically

## 📝 To Do

- [ ] Implement batch download queue
- [ ] Add GUI interface option
- [ ] Support for additional music platforms

## ⚠️ Disclaimer

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. 

**Important**: This tool is intended for educational purposes and personal use only. Users are responsible for ensuring they comply with applicable laws and platform terms of service. The developers do not encourage or condone piracy or copyright infringement.

---

<div align="center">

**Made with ❤️ for music lovers**

*If you find this project useful, consider starring it! ⭐*

</div>