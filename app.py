import os
import subprocess
from flask import Flask, send_from_directory
from dotenv import load_dotenv  # Import load_dotenv to load .env file

app = Flask(__name__)

# Load the .env file
load_dotenv()

# Access the RTSP link from the environment variables
rtsp_link = os.getenv("RTSP_LINK")

# Function to clear old video files
def clear_old_videos(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)  # Delete the file
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

# Function to start the FFmpeg stream
def start_ffmpeg():
    hls_directory = 'C:/nginx/html/hls'
    clear_old_videos(hls_directory)  # Clear old HLS files before starting

    # Use the RTSP link from the .env file in the FFmpeg command
    ffmpeg_command = [
        'ffmpeg',
        '-rtsp_transport', 'tcp',
        '-i', rtsp_link,  # Use the RTSP link from .env
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-f', 'hls',
        '-hls_time', '10',
        '-hls_list_size', '10',
        '-hls_playlist_type', 'event',
        f'{hls_directory}/output.m3u8'
    ]
    subprocess.Popen(ffmpeg_command)

@app.route('/')
def index():
    return send_from_directory('C:/nginx/html', 'index.html')

@app.route('/hls/<path:path>')
def send_hls(path):
    return send_from_directory('C:/nginx/html/hls', path)

@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    hls_directory = 'C:/nginx/html/hls'
    clear_old_videos(hls_directory)  # Delete all HLS files
    return "Stream stopped and files deleted.", 200

if __name__ == '__main__':
    start_ffmpeg()  # Start FFmpeg when the app starts
    app.run(debug=True, host='0.0.0.0', port=5000)
