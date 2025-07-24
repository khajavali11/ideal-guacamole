import os
from flask import Flask, request, render_template_string, url_for, send_from_directory
import qrcode
import subprocess
from datetime import datetime
import time

# Settings
PORT = 5000
UPLOAD_FOLDER = "uploads"

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flask App
app = Flask(__name__)

# HTML Templates
HTML_FORM = '''
<!doctype html>
<title>Upload File</title>
<h2>Upload a File from Phone</h2>
<form method=post enctype=multipart/form-data>
  <input type=file name=file required>
  <input type=submit value=Upload>
</form>
<p><a href="/files">View uploaded files</a></p>
'''

FILES_LIST_TEMPLATE = '''
<!doctype html>
<title>Uploaded Files</title>
<h2>Uploaded Files</h2>
<table style="width:100%; border-collapse: collapse;">
    <tr style="background-color: #f2f2f2;">
        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">File Name</th>
        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Upload Time</th>
        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Action</th>
    </tr>
    {% for file in files %}
    <tr>
        <td style="padding: 12px; border: 1px solid #ddd;">{{ file.name }}</td>
        <td style="padding: 12px; border: 1px solid #ddd;">{{ file.upload_time }}</td>
        <td style="padding: 12px; border: 1px solid #ddd;">
            <a href="/download/{{ file.name }}">Download</a>
        </td>
    </tr>
    {% endfor %}
</table>
<p><a href="/">Back to Upload</a></p>
'''

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file:
            save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
            uploaded_file.save(save_path)
            # Set the file's modification time to current time
            os.utime(save_path, (time.time(), time.time()))
            return f"<p>✅ File saved: {uploaded_file.filename}</p><a href='/'>Back</a>"
    return HTML_FORM

@app.route('/files')
def list_files():
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            mtime = os.path.getmtime(file_path)
            upload_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            files.append({
                'name': filename,
                'upload_time': upload_time,
                'timestamp': mtime
            })
    
    # Sort files by upload time, newest first
    files.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return render_template_string(FILES_LIST_TEMPLATE, files=files)

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except Exception as e:
        return f"Error downloading file: {str(e)}", 404

# Start Flask server
def run_server():
    print(f"🚀 Starting Flask server on http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT)

# Start ngrok tunnel
def start_ngrok():
    try:
        print("🌐 Starting ngrok tunnel...")
        ngrok = subprocess.Popen(["ngrok", "http", str(PORT)], stdout=subprocess.PIPE)
    except FileNotFoundError:
        print("❌ Ngrok not found. Please install it from https://ngrok.com and add to PATH.")
        return None

# Extract public URL from ngrok
def get_ngrok_url():
    import time
    import requests
    time.sleep(2)  # wait for ngrok to initialize
    try:
        tunnel_info = requests.get("http://localhost:4040/api/tunnels").json()
        public_url = tunnel_info['tunnels'][0]['public_url']
        return public_url
    except Exception as e:
        print(f"⚠️ Failed to get ngrok URL: {e}")
        return None

# Generate QR code from URL
def generate_qr(url):
    print(f"📱 Scan this QR code to upload a file:\n{url}")
    img = qrcode.make(url)
    img_path = "upload_qr.png"
    img.save(img_path)
    img.show()

if __name__ == "__main__":
    # Start ngrok in background
    start_ngrok()

    # Start server in a separate thread
    import threading
    threading.Thread(target=run_server, daemon=True).start()

    # Wait and then get the public URL
    import time
    time.sleep(3)
    public_url = get_ngrok_url()
    if public_url:
        generate_qr(public_url)
        print("📂 Files will be saved to the 'uploads/' folder.")
        print("🔒 Leave terminal open to keep server running.")
    else:
        print("❌ Failed to generate public URL.")
