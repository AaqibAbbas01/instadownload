import os
import uuid
import re
import subprocess
import json
import urllib.parse
from flask import Flask, render_template, request, jsonify, send_file, url_for
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

# Create downloads directory
DOWNLOAD_DIR = Path(__file__).parent / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Thread pool for parallel downloads
executor = ThreadPoolExecutor(max_workers=5)


def extract_video_info(url):
    """Extract video information using yt-dlp"""
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-warnings", url],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None
    except Exception as e:
        print(f"Error extracting info: {e}")
        return None


def download_video(url, output_path):
    """Download Instagram video using yt-dlp"""
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "-f", "best",
                "-o", str(output_path),
                "--no-warnings",
                url
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error downloading: {e}")
        return False


def is_valid_instagram_url(url):
    """Validate Instagram URL"""
    patterns = [
        r'https?://(www\.)?instagram\.com/(p|reel|tv)/[\w-]+',
        r'https?://(www\.)?instagram\.com/stories/[\w.]+/\d+',
    ]
    return any(re.match(pattern, url) for pattern in patterns)


def download_single_video(url):
    """Download a single video and return result"""
    url = url.strip()
    
    if not url:
        return {'url': url, 'success': False, 'error': 'Empty URL'}
    
    if not is_valid_instagram_url(url):
        return {'url': url, 'success': False, 'error': 'Invalid Instagram URL'}
    
    # Get video info first
    info = extract_video_info(url)
    
    # Generate unique filename
    file_id = str(uuid.uuid4())[:8]
    output_path = DOWNLOAD_DIR / f"insta_{file_id}.mp4"
    
    success = download_video(url, output_path)
    
    if success and output_path.exists():
        return {
            'url': url,
            'success': True,
            'file_id': file_id,
            'title': info.get('title', 'Instagram Video') if info else 'Instagram Video',
            'thumbnail': info.get('thumbnail', '') if info else '',
            'uploader': info.get('uploader', 'Unknown') if info else 'Unknown'
        }
    else:
        return {'url': url, 'success': False, 'error': 'Failed to download'}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/info', methods=['POST'])
def get_info():
    """Get video information before download"""
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'Please provide an Instagram URL'}), 400
    
    if not is_valid_instagram_url(url):
        return jsonify({'error': 'Invalid Instagram URL. Please use a valid post, reel, or story URL.'}), 400
    
    info = extract_video_info(url)
    if not info:
        return jsonify({'error': 'Could not fetch video information. The video might be private or unavailable.'}), 400
    
    return jsonify({
        'title': info.get('title', 'Instagram Video'),
        'thumbnail': info.get('thumbnail', ''),
        'duration': info.get('duration', 0),
        'uploader': info.get('uploader', 'Unknown'),
        'description': info.get('description', '')[:200] if info.get('description') else ''
    })


@app.route('/api/download', methods=['POST'])
def download():
    """Download the Instagram video"""
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'Please provide an Instagram URL'}), 400
    
    if not is_valid_instagram_url(url):
        return jsonify({'error': 'Invalid Instagram URL'}), 400
    
    # Generate unique filename
    file_id = str(uuid.uuid4())[:8]
    output_path = DOWNLOAD_DIR / f"insta_{file_id}.mp4"
    
    success = download_video(url, output_path)
    
    if success and output_path.exists():
        return jsonify({
            'success': True,
            'file_id': file_id,
            'message': 'Video downloaded successfully!'
        })
    else:
        return jsonify({'error': 'Failed to download video. Please try again.'}), 500


@app.route('/api/download-batch', methods=['POST'])
def download_batch():
    """Download multiple Instagram videos"""
    data = request.json
    urls = data.get('urls', [])
    
    if not urls:
        return jsonify({'error': 'Please provide at least one Instagram URL'}), 400
    
    # Limit to 10 videos at a time
    if len(urls) > 10:
        return jsonify({'error': 'Maximum 10 videos can be downloaded at once'}), 400
    
    results = []
    
    # Use thread pool for parallel downloads
    futures = {executor.submit(download_single_video, url): url for url in urls}
    
    for future in as_completed(futures):
        try:
            result = future.result()
            results.append(result)
        except Exception as e:
            url = futures[future]
            results.append({'url': url, 'success': False, 'error': str(e)})
    
    # Sort results in original order
    url_order = {url: i for i, url in enumerate(urls)}
    results.sort(key=lambda x: url_order.get(x['url'], 999))
    
    successful = sum(1 for r in results if r['success'])
    
    return jsonify({
        'results': results,
        'total': len(urls),
        'successful': successful,
        'failed': len(urls) - successful
    })


@app.route('/api/file/<file_id>')
def get_file(file_id):
    """Serve the downloaded file"""
    # Sanitize file_id to prevent path traversal
    if not re.match(r'^[a-f0-9]{8}$', file_id):
        return jsonify({'error': 'Invalid file ID'}), 400
    
    file_path = DOWNLOAD_DIR / f"insta_{file_id}.mp4"
    
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"instagram_video_{file_id}.mp4"
    )


@app.route('/api/share-url/<file_id>')
def get_share_url(file_id):
    """Generate a shareable URL for WhatsApp"""
    # Sanitize file_id to prevent path traversal
    if not re.match(r'^[a-f0-9]{8}$', file_id):
        return jsonify({'error': 'Invalid file ID'}), 400
    
    file_path = DOWNLOAD_DIR / f"insta_{file_id}.mp4"
    
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
    
    # Get file size
    file_size = file_path.stat().st_size
    file_size_mb = round(file_size / (1024 * 1024), 2)
    
    return jsonify({
        'file_id': file_id,
        'filename': f'instagram_video_{file_id}.mp4',
        'size_mb': file_size_mb
    })


# Cleanup old files periodically (files older than 1 hour)
def cleanup_old_files():
    import time
    current_time = time.time()
    for file in DOWNLOAD_DIR.glob("*.mp4"):
        if current_time - file.stat().st_mtime > 3600:  # 1 hour
            try:
                file.unlink()
            except:
                pass


if __name__ == '__main__':
    cleanup_old_files()
    app.run(debug=True, port=5000)
