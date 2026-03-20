# Rev Shell Payload Generator

Generates reverse shell payloads for Bash, Python, Netcat, PHP, PowerShell, and CMD.

Features:
- Automatic IP detection
- Port validation
- Generates raw and URL-encoded payloads
- Ready-to-copy listener commands

Usage (CLI):

Run the script:
   python3 shevshell.py

The CLI displays incoming requests and generated payload data. Payload generation is handled through the web interface.

Web Version:

A Flask-based web interface is included for generating payloads.

To run the web app:

1. Install dependencies:
   pip install flask

2. Start the server:
   python3 shevshell.py

3. Open your browser and go to:
   http://127.0.0.1:5000

4. Use the web interface to:
   - Select shell type
   - Enter IP and port
   - Generate payloads
   - Copy listener commands

Requirements:
- Python 3.x
- Flask (for web interface)
- Netcat (optional, for listener)

Notes:
This tool is intended for penetration testing and educational use only.
Only use it on systems you own or have explicit permission to test. Of course 😉
