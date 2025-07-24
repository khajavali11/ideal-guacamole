# Flask File Upload Server with QR Code Access

A simple Flask server that allows you to upload files from your phone to your computer using QR codes. The server creates a secure tunnel using ngrok, generates a QR code for easy mobile access, and provides a web interface to upload and manage files.

## Features

- 📱 Upload files from your phone to your PC using QR codes
- 🌐 Accessible over the internet using ngrok tunnel
- 📂 View all uploaded files sorted by upload time
- ⬇️ Download files from the web interface
- 🔒 Secure file transfer over HTTPS (provided by ngrok)

## Prerequisites

1. Python 3.6 or higher
2. ngrok account and authtoken (free at [ngrok.com](https://ngrok.com))

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/khajavali11/ideal-guacamole.git
   cd ideal-guacamole
   ```

2. **Create and activate a virtual environment (recommended)**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install and configure ngrok**
   - Download ngrok from [ngrok.com](https://ngrok.com/download)
   - Extract the ngrok executable to a location in your system PATH
   - Sign up for a free ngrok account if you haven't already
   - Get your authtoken from the ngrok dashboard
   - Configure ngrok with your authtoken:
     ```bash
     ngrok config add-authtoken YOUR_AUTH_TOKEN
     ```

## Usage

1. **Start the server**
   ```bash
   python app.py
   ```

2. **What happens when you start the server:**
   - The Flask server starts on port 5000
   - An ngrok tunnel is created
   - A QR code is generated and displayed
   - The QR code is also saved as `upload_qr.png`

3. **Using the application:**
   - Scan the QR code with your phone
   - Upload files through the web interface
   - View uploaded files by clicking "View uploaded files"
   - Download files from the file list page

## Directory Structure

```
.
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── uploads/           # Directory for uploaded files
└── upload_qr.png      # Generated QR code (created on run)
```

## Important Notes

- Keep the terminal window open while using the server
- The `uploads/` directory is created automatically
- Files are sorted by upload time (newest first)
- The ngrok tunnel provides HTTPS encryption for secure file transfer
- Each time you start the server, a new URL and QR code will be generated

## Troubleshooting

1. **"Ngrok not found" error**
   - Make sure ngrok is properly installed and in your system PATH
   - Try running `ngrok --version` to verify the installation

2. **No QR code appears**
   - Ensure you have configured ngrok with your authtoken
   - Check if port 5000 is available
   - Look for any error messages in the terminal

3. **Cannot access the server from phone**
   - Ensure your phone has internet access
   - Verify that the ngrok tunnel is running (`http://localhost:4040`)
   - Try refreshing the ngrok tunnel by restarting the server

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements!