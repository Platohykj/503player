import os
import ffmpeg
import filelock
import threading
import signal
from queue import Queue
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)
CORS(app)

# 设置上传文件的存储路径
UPLOAD_FOLDER = './musics'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 创建一个队列来存储播放列表
playlist = Queue()

# 创建一个变量来存储当前的播放状态
is_playing = False

# 创建一个事件来控制播放线程的运行
play_event = threading.Event()

# Global player
player = None

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pause', methods=['POST'])
def pause():
    global player
    if player:
        player.send_signal(signal.SIGSTOP)
    return jsonify({"status": "Paused"}), 200


@app.route('/resume', methods=['POST'])
def resume():
    global player
    if player:
        player.send_signal(signal.SIGCONT)
    return jsonify({"status": "Resumed"}), 200


@app.route('/screenshot', methods=['GET'])
def screenshot():
    stream_url = 'http://192.168.31.164:8080/hls/test.m3u8'
    out_filename = '/tmp/screenshot.jpg'

    lock = filelock.FileLock(out_filename + ".lock")

    with lock:
        try:
            ffmpeg.input(stream_url).output(out_filename, vframes=1).run(overwrite_output=True)
        except ffmpeg.Error as e:
            print('Error:', e)
            return 'Error occurred', 500

    return send_file(out_filename, mimetype='image/jpeg')



def play_next():
    global is_playing
    global player
    while True:
        play_event.wait()  # Wait until the event is set
        if not playlist.empty() and not is_playing:
            filename = playlist.queue[0]
            is_playing = True
            player = subprocess.Popen(['ffplay', '-nodisp', '-autoexit', filename])
            player.wait()  # Wait for the player to finish
            playlist.get()  # Remove the filename from the playlist after the player has finished
            if os.path.basename(filename).startswith('bili_'):
                os.remove(filename)
            is_playing = False
        if playlist.empty():
            play_event.clear()  # Clear the event if the playlist is empty

# 创建一个新线程来处理播放列表
player_thread = threading.Thread(target=play_next)
player_thread.start()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'message': 'File uploaded successfully'}), 200


@app.route('/uploads', methods=['GET'])
def list_uploads():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(files), 200


@app.route('/play/<filename>', methods=['GET'])
def enqueue_and_play(filename):
    global is_playing
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    playlist.put(file_path)
    play_event.set()  # Set the event when a new file is added to the playlist
    return jsonify({'message': 'File added to playlist'}), 200

@app.route('/playlist', methods=['GET'])
def get_playlist():
    # ... (same as before)
    return jsonify(list(playlist.queue)), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
