# ArabSeed Scraper

A simple Flask web scraper for ArabSeed website to browse and stream Arabic movies and TV series.

## Description

This application scrapes content from ArabSeed website and provides a simple interface for watching Arabic movies and TV series.

## Features

- 🔍 Search functionality
- 🎬 Video streaming in multiple qualities (480p, 720p, 1080p)
- 📱 Mobile responsive
- ⬇️ Download support

## Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python app.py
   ```

3. **Open browser** and go to `http://localhost:5000`

## Deployment

The app is configured for Vercel deployment with the included `vercel.json` file.

## Routes

- `/` - Home page
- `/search` - Search content
- `/browse` - Browse content
- `/server/<path>` - Video streaming

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational purposes only. Users are responsible for complying with applicable laws and terms of service.