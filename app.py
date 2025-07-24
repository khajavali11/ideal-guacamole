import os
from flask import Flask, request, render_template_string, url_for, send_from_directory, send_file
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
app.config['PUBLIC_URL'] = None  # Will store the ngrok URL

# HTML Templates with shared styles
COMMON_STYLES = '''
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h2 {
            color: #333;
            margin-top: 0;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            font-size: 16px;
            margin: 5px 0;
        }
        .btn:hover {
            background-color: #0056b3;
        }
        .nav-links {
            margin-top: 20px;
        }
        .nav-links a {
            color: #007bff;
            text-decoration: none;
            margin-right: 15px;
        }
        .nav-links a:hover {
            text-decoration: underline;
        }
        .qr-section {
            margin-top: 2rem;
            text-align: center;
        }
        .qr-section img {
            max-width: 200px;
            margin: 1rem 0;
        }
    </style>
'''

HTML_FORM = f'''
<!doctype html>
<html>
<head>
    <title>Upload File</title>
    {COMMON_STYLES}
</head>
<body>
    <div class="container">
        <h2>📤 Upload Files from Phone</h2>
        <form method=post enctype=multipart/form-data>
            <input type=file name=file required style="margin-bottom: 1rem; display: block;">
            <button type=submit class="btn">Upload File</button>
        </form>
        
        
    </div>
</body>
</html>
'''

FILES_LIST_TEMPLATE = '''
<!doctype html>
<html>
<head>
    <title>Uploaded Files</title>
    ''' + COMMON_STYLES + '''
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
            font-weight: 500;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        tr:hover {
            background-color: #f2f2f2;
        }
        .download-btn {
            padding: 6px 12px;
            background-color: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
        }
        .download-btn:hover {
            background-color: #218838;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>📂 Uploaded Files</h2>
        {% if files %}
        <table>
            <tr>
                <th>File Name</th>
                <th>Upload Time</th>
                <th>Action</th>
            </tr>
            {% for file in files %}
            <tr>
                <td>{{ file.name }}</td>
                <td>{{ file.upload_time }}</td>
                <td>
                    <a href="/download/{{ file.name }}" class="download-btn">⬇️ Download</a>
                </td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p>No files uploaded yet.</p>
        {% endif %}
        <div class="nav-links">
            <a href="/">📤 Upload new file</a>
        </div>
        <div class="qr-section">
            <h3>📱 Scan to Upload from Another Device</h3>
            <img src="/qr" alt="QR Code">
            <p>Scan this QR code with your phone's camera to open this page</p>
        </div>
    </div>
</body>
</html>
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
        return (f"Error downloading file: {str(e)} 404")

@app.route('/qr')
def serve_qr():
    """Serve the QR code image for the current page"""
    # Use ngrok URL if available
    base_url = app.config['PUBLIC_URL'] or request.host_url
    
    # Remove trailing slash if present
    base_url = base_url.rstrip('/')
    
    # Add the correct path
    if 'files' in request.path:
        url = f"{base_url}/files"
    else:
        url = base_url
    
    # Generate QR code
    img = qrcode.make(url)
    
    # Save to bytes
    from io import BytesIO
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

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
        # Store the ngrok URL in the Flask app config
        app.config['PUBLIC_URL'] = public_url
        generate_qr(public_url)
        print("📂 Files will be saved to the 'uploads/' folder.")
        print("🔒 Leave terminal open to keep server running.")
        print(f"📱 Access from any device at: {public_url}")
    else:
        print("❌ Failed to generate public URL.")
