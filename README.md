# InstaGrab - Instagram Video Downloader

A simple, beautiful tool to download Instagram videos (Reels, Posts, IGTV).

![InstaGrab](https://img.shields.io/badge/InstaGrab-Video%20Downloader-ff2d55)

## Features

- 🚀 **Fast Downloads** - Download videos in seconds
- 🎨 **Beautiful UI** - Modern, dark-themed interface
- 🔒 **Private** - No data collection, runs locally
- 📱 **Supports All Formats** - Reels, Posts, IGTV, Stories

## Prerequisites

- Python 3.8+
- yt-dlp (command-line tool)

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd /Users/macbookpro/insta
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install yt-dlp (if not already installed):**
   ```bash
   # Using pip
   pip install yt-dlp
   
   # Or using Homebrew (macOS)
   brew install yt-dlp
   ```

## Usage

1. **Start the server:**
   ```bash
   python app.py
   ```

2. **Open your browser:**
   Navigate to `http://localhost:5000`

3. **Download a video:**
   - Paste an Instagram URL (Reel, Post, or Story)
   - Click "Download Video"
   - Save the file when ready

## Supported URL Formats

- `https://www.instagram.com/p/XXXXX/` - Posts
- `https://www.instagram.com/reel/XXXXX/` - Reels
- `https://www.instagram.com/tv/XXXXX/` - IGTV
- `https://www.instagram.com/stories/username/XXXXX/` - Stories

## Notes

- Downloaded videos are stored in the `downloads/` folder
- Files older than 1 hour are automatically cleaned up
- Only public videos can be downloaded
- Use responsibly and respect content creators' rights

## Troubleshooting

**"Could not fetch video information"**
- Make sure the video is public
- Check that the URL is correct
- Try updating yt-dlp: `pip install -U yt-dlp`

**"yt-dlp not found"**
- Install yt-dlp: `pip install yt-dlp` or `brew install yt-dlp`

## License

For personal use only. Respect Instagram's Terms of Service and content creators' rights.

