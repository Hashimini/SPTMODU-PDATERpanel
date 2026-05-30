import os
import json
import threading
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, redirect
from werkzeug.utils import secure_filename
from waitress import serve

app = Flask(__name__)

UPLOAD_FOLDER = 'files'
JSON_FILE = 'versions.json'

versions_lock = threading.Lock()
cached_versions = []

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def _is_path_inside(base_dir, target_path):
    base = os.path.abspath(base_dir)
    target = os.path.abspath(target_path)
    return target == base or target.startswith(base + os.sep)

def load_versions_from_disk():
    global cached_versions
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            cached_versions = json.load(f)
    else:
        cached_versions = []

def get_versions():
    with versions_lock:
        return list(cached_versions)

def save_versions(versions):
    global cached_versions
    with versions_lock:
        cached_versions = list(versions)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(cached_versions, f, indent=4, ensure_ascii=False)

def append_version(entry):
    global cached_versions
    with versions_lock:
        cached_versions.append(entry)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(cached_versions, f, indent=4, ensure_ascii=False)

def remove_version(version_id):
    global cached_versions
    with versions_lock:
        item = next((x for x in cached_versions if x['Version'] == version_id), None)
        if not item:
            return None
        cached_versions = [x for x in cached_versions if x['Version'] != version_id]
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(cached_versions, f, indent=4, ensure_ascii=False)
        return item

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
UPLOAD_FOLDER_ABSPATH = os.path.abspath(UPLOAD_FOLDER)

if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

load_versions_from_disk()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MODU-PDATER [ ADMIN CONSOLE ]</title>
    <link href="https://fonts.googleapis.com/css2?family=Teko:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body, html {
            margin: 0; padding: 0; height: 100%;
            background-color: #000000;
            color: #D7D2C3;
            font-family: 'Teko', 'Courier New', Courier, monospace;
            overflow-x: hidden;
        }

        /* Background Effects (Carbon & Vignette) */
        .bg-pattern {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-image: repeating-linear-gradient(45deg, #050505 0, #050505 2px, transparent 2px, transparent 6px);
            opacity: 0.45; z-index: -3; pointer-events: none;
        }
        .bg-vignette {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at 50% 0%, rgba(0,0,0,0) 0%, rgba(0,0,0,0.8) 100%);
            z-index: -2; pointer-events: none;
        }

        /* Fixed Decorative Elements (HUD) */
        .hud { position: fixed; pointer-events: none; opacity: 0.15; z-index: -1; font-family: 'Courier New', monospace; font-size: 11px; }
        .hud-tl { top: 40px; left: 35px; color: #8C8C8C; }
        .hud-tr { top: 45px; right: 30px; color: #8C8C8C; }
        .hud-bl { bottom: 17px; left: 40px; color: #8C8C8C; font-size: 9px; }
        .hud-bc { bottom: 35px; left: 50%; transform: translateX(-50%); color: #F0C75E; font-size: 12px; letter-spacing: 2px; }
        .hud-lc { top: 50%; left: 30px; transform: translateY(-50%); display: flex; flex-direction: column; gap: 5px; align-items: center; }
        .hud-lc .sys { color: #D5A63A; font-weight: bold; font-size: 9px; writing-mode: vertical-rl; transform: rotate(180deg); }
        .hud-lc .line { color: #D7D2C3; }
        .hud-lc .lock { color: #8C8C8C; font-size: 9px; writing-mode: vertical-rl; }
        .hud-rc { top: 50%; right: 40px; transform: translateY(-50%); text-align: right; font-size: 9px; color: #8C8C8C; line-height: 1.5; }
        .hud-rc .divider { color: #333333; font-size: 10px; }

        /* Main Container */
        .container { max-width: 850px; margin: 40px auto; position: relative; padding: 20px; }
        .main-border { border: 1px solid rgba(255,255,255,0.13); border-radius: 4px; padding: 25px; background: rgba(0,0,0,0.4); position: relative; }

        /* Typography & Headings */
        h1 { margin-top: 0; font-size: 26px; font-weight: bold; color: #E5DFC9; letter-spacing: 1px; display: flex; flex-direction: column; line-height: 1.1; }
        h1 .sub { font-size: 14px; color: #8C8C8C; }
        h2 { font-size: 20px; font-weight: bold; color: #D5A63A; letter-spacing: 1px; border-bottom: 1px solid #333333; padding-bottom: 5px; margin-bottom: 15px; text-transform: uppercase; }

        /* Forms */
        label { display: block; font-size: 13px; font-weight: bold; color: #8C8C8C; margin: 15px 0 5px 0; letter-spacing: 0.5px; font-family: 'Courier New', monospace; text-transform: uppercase; }
        input[type="text"], textarea {
            width: 100%; padding: 10px; background: #141414; color: #D7D2C3;
            border: 1px solid #333333; border-radius: 0; outline: none;
            font-family: 'Courier New', monospace; font-size: 13px; box-sizing: border-box; transition: all 0.2s;
        }
        input[type="text"]:focus, textarea:focus { background: #252525; border-color: #4F4F4F; }

        /* Buttons */
        .btn-primary {
            background: linear-gradient(135deg, #5A6246, #2A2F22);
            border: 1px solid #4A3A14; color: #E5DFC9; width: 100%;
            padding: 12px; font-size: 20px; font-weight: bold; cursor: pointer;
            letter-spacing: 1px; margin-top: 20px; transition: opacity 0.2s;
            text-transform: uppercase; font-family: 'Teko', sans-serif;
        }
        .btn-primary:hover { opacity: 0.9; }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

        .btn-delete {
            background: #111111; border: 1px solid #552222; color: #D36242;
            padding: 6px 12px; font-size: 16px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; font-family: 'Teko', sans-serif; letter-spacing: 1px;
        }
        .btn-delete:hover { background: #331111; border-color: #D36242; color: #FFFFFF; }

        /* Drop Zone */
        #drop-zone {
            border: 1px dashed #4F4F4F; background: #141414; padding: 25px; text-align: center;
            color: #8C8C8C; cursor: pointer; margin: 10px 0; font-size: 13px; font-family: 'Courier New', monospace; transition: all 0.2s; text-transform: uppercase;
        }
        #drop-zone.dragover { border-color: #D5A63A; background: #252525; color: #D5A63A; }

        /* Progress Bar */
        .progress-wrapper { display: none; margin-top: 20px; }
        .progress-container { background: #1C1C1C; border: 1px solid #333333; height: 24px; position: relative; }
        .progress-bar {
            height: 100%; width: 0%;
            background: linear-gradient(to top, #8E6720 0%, #D5A63A 50%, #F0C75E 100%);
            transition: width 0.1s ease;
        }
        .progress-text {
            font-size: 13px; color: #FFFFFF; font-family: 'Courier New', monospace; text-shadow: 1px 1px 2px #000;
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); pointer-events: none; white-space: nowrap; font-weight: bold;
        }
        .progress-status-sub { text-align: center; font-size: 11px; color: #8C8C8C; margin-top: 6px; font-family: 'Courier New', monospace; text-transform: uppercase; }

        /* Panels / Cards */
        .panel { background: linear-gradient(to bottom, #191919, #111111); border: 1px solid #333333; padding: 20px; margin-bottom: 25px; position: relative; }

        /* Golden Border Accents (Tactical Corners) */
        .g-corner { position: absolute; background: #D5A63A; }
        .tl-h { top: 6px; left: 6px; width: 13px; height: 2px; } .tl-v { top: 6px; left: 6px; width: 2px; height: 13px; }
        .tr-h { top: 6px; right: 6px; width: 13px; height: 2px; } .tr-v { top: 6px; right: 6px; width: 2px; height: 13px; }
        .bl-h { bottom: 6px; left: 6px; width: 13px; height: 2px; } .bl-v { bottom: 6px; left: 6px; width: 2px; height: 13px; }
        .br-h { bottom: 6px; right: 6px; width: 13px; height: 2px; } .br-v { bottom: 6px; right: 6px; width: 2px; height: 13px; }

        /* Version List */
        .version-item { background: #141414; border: 1px solid #252525; border-left: 3px solid #D5A63A; padding: 15px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: flex-start; }
        .version-info { width: 80%; }
        .version-title { font-size: 22px; color: #D5A63A; font-weight: bold; margin-bottom: 5px; display: block; letter-spacing: 1px; }
        .version-link { color: #8C8C8C; font-size: 11px; font-family: 'Courier New', monospace; text-decoration: none; word-break: break-all; margin-top: 10px; display: inline-block; }
        .version-link:hover { color: #D7D2C3; }
        .changelog-box { background: #0A0A0A; border: 1px solid #252525; padding: 10px; margin-top: 10px; font-size: 12px; color: #D7D2C3; font-family: 'Courier New', monospace; white-space: pre-wrap; }
        .wipe-box { background: #1A1111; border-left: 2px solid #552222; padding: 8px 10px; margin-top: 10px; font-size: 11px; color: #D36242; font-family: 'Courier New', monospace; }
        .wipe-box ul { margin: 5px 0 0 0; padding-left: 20px; }
        .help-text { color: #8E6720; font-size: 11px; font-family: 'Courier New', monospace; display: block; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="bg-pattern"></div>
    <div class="bg-vignette"></div>

    <div class="hud hud-tl">udi: 0B1A0N0G0B0O1O0</div>
    <div class="hud hud-tr">.vv: 721     0.3.</div>
    <div class="hud hud-bl">LAT. 69.420 // LON. -67.67</div>
    <div class="hud hud-bc">____________________________________________________________________________________________</div>
    <div class="hud hud-lc">
        <span class="sys">● SYS_LINK</span>
        <span class="line">|</span>
        <span class="lock">LOCK.IN // N-402</span>
    </div>
    <div class="hud hud-rc">
        USEC_COPILOT_IA<br>
        <span class="divider">=================</span><br>
        .NET_SDK_OK
    </div>

    <div class="container">
        <div class="main-border">
            <h1>MOD MANAGER<span class="sub">ADMIN_PANEL v1.0.5</span></h1>

            <div class="panel">
                <div class="g-corner tl-h"></div><div class="g-corner tl-v"></div>
                <div class="g-corner tr-h"></div><div class="g-corner tr-v"></div>
                <div class="g-corner bl-h"></div><div class="g-corner bl-v"></div>
                <div class="g-corner br-h"></div><div class="g-corner br-v"></div>

                <h2>SERVER CONFIG // PATCH REGISTRATION</h2>
                <form id="upload-form">
                    <label>IP (Download Endpoints):</label>
                    <input type="text" id="server-ip-input" name="server_ip" value="{{ current_host }}" placeholder="e.g. 200.10.23.14:8080" required />
                    <span class="help-text">⚠ If using a VPN, use the virtual IP while keeping the server port.</span>

                    <label>Version Identifier:</label>
                    <input type="text" name="version" placeholder="e.g. v2.4.0" required />

                    <label>LATEST_CHANGELOG.TXT:</label>
                    <textarea name="changelog" rows="4" placeholder="[+] ADDED: New Mod&#10;[x] FIXED: Bug fix"></textarea>

                    <label>Obsolete Files for Removal (WIPE) - One per line:</label>
                    <textarea name="files_to_delete" rows="3" placeholder="BepInEx/plugins/BrokenMod.dll"></textarea>

                    <label>Package File (.zip):</label>
                    <div id="drop-zone">[ DRAG .ZIP FILE HERE OR CLICK ]</div>
                    <input type="file" id="file-input" name="file" accept=".zip" style="display:none;" required />
                    <p id="file-name" style="color:#D5A63A; font-size:12px; font-weight:bold; margin: 5px 0 0 0; font-family:'Courier New', monospace; text-align:center;"></p>

                    <div class="progress-wrapper" id="progress-wrapper">
                        <div class="progress-container">
                            <div class="progress-bar" id="progress-bar"></div>
                            <div class="progress-text" id="progress-text">WAITING</div>
                        </div>
                        <div class="progress-status-sub" id="progress-status-sub">STATUS</div>
                    </div>

                    <button type="submit" id="btn-submit" class="btn-primary">DEPLOY_PATCH</button>
                </form>
            </div>

            <div class="panel">
                <div class="g-corner tl-h"></div><div class="g-corner tl-v"></div>
                <div class="g-corner tr-h"></div><div class="g-corner tr-v"></div>
                <div class="g-corner bl-h"></div><div class="g-corner bl-v"></div>
                <div class="g-corner br-h"></div><div class="g-corner br-v"></div>

                <h2>REGISTERED VERSIONS ON SERVER</h2>
                <div id="versions-list">
                    {% if not versions %}
                        <p style="color: #555555; font-size: 13px; font-family: 'Courier New', monospace;">[ EMPTY DATABASE ]</p>
                    {% else %}
                        {% for v in versions %}
                            <div class="version-item">
                                <div class="version-info">
                                    <span class="version-title">DEPLOY_ID: {{ v.Version }}</span>
                                    {% if v.Changelog %}
                                        <div class="changelog-box">{{ v.Changelog }}</div>
                                    {% else %}
                                        <div class="changelog-box" style="color: #555555;">[ NO CHANGELOG REGISTERED ]</div>
                                    {% endif %}
                                    {% if v.files_to_delete %}
                                        <div class="wipe-box">
                                            FILES MARKED FOR REMOVAL:
                                            <ul>
                                                {% for file in v.files_to_delete %}
                                                    <li>{{ file }}</li>
                                                {% endfor %}
                                            </ul>
                                        </div>
                                    {% endif %}
                                    <a href="{{ v.Download }}" class="version-link" target="_blank">> TARGET_URL: {{ v.Download }}</a>
                                </div>
                                <div>
                                    <a href="/delete/{{ v.Version }}" class="btn-delete" onclick="return confirm('WARNING: Permanently delete this record and its physical file?')">WIPE</a>
                                </div>
                            </div>
                        {% endfor %}
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <script>
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const fileName = document.getElementById('file-name');
        const serverIpInput = document.getElementById('server-ip-input');
        const uploadForm = document.getElementById('upload-form');
        const btnSubmit = document.getElementById('btn-submit');

        const progressWrapper = document.getElementById('progress-wrapper');
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        const progressStatusSub = document.getElementById('progress-status-sub');

        const savedIp = localStorage.getItem('saved_server_ip');
        if (savedIp) { serverIpInput.value = savedIp; }

        dropZone.onclick = () => fileInput.click();
        dropZone.ondragover = (e) => { e.preventDefault(); dropZone.classList.add('dragover'); };
        dropZone.ondragleave = () => dropZone.classList.remove('dragover');
        dropZone.ondrop = (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if(e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                fileName.innerText = '>>> READY: ' + e.dataTransfer.files[0].name.toUpperCase();
            }
        };
        fileInput.onchange = () => {
            if(fileInput.files.length) fileName.innerText = '>>> READY: ' + fileInput.files[0].name.toUpperCase();
        };

        uploadForm.onsubmit = async (e) => {
            e.preventDefault();
            localStorage.setItem('saved_server_ip', serverIpInput.value);

            if (!fileInput.files.length) return alert("[ERROR] Please select a ZIP file.");

            const file = fileInput.files[0];
            const version = uploadForm.elements['version'].value;
            const changelog = uploadForm.elements['changelog'].value;
            const filesToDeleteRaw = uploadForm.elements['files_to_delete'].value;
            const serverIp = serverIpInput.value;

            const files_to_delete = filesToDeleteRaw.split('\n').map(l => l.trim()).filter(l => l);

            // Chunk configuration: 10MB per chunk (changed to 10MB logically, but kept original 64MB logic from Python string)
            const CHUNK_SIZE = 64 * 1024 * 1024;
            const totalChunks = Math.ceil(file.size / CHUNK_SIZE);

            btnSubmit.disabled = true;
            btnSubmit.innerText = "UPLOADING...";
            progressWrapper.style.display = 'block';

            for (let i = 0; i < totalChunks; i++) {
                const start = i * CHUNK_SIZE;
                const end = Math.min(start + CHUNK_SIZE, file.size);
                const chunk = file.slice(start, end);

                const formData = new FormData();
                formData.append('file', chunk);
                formData.append('filename', file.name);
                formData.append('chunk_index', i);

                let success = false;
                let attempts = 0;

                while (!success && attempts < 3) {
                    try {
                        progressStatusSub.innerText = `[CHUNK ${i + 1}/${totalChunks}] UPLOADING DATA... (ATTEMPT ${attempts + 1})`;
                        const response = await fetch('/upload-chunk', {
                            method: 'POST',
                            body: formData
                        });

                        if (response.ok) {
                            success = true;
                        } else {
                            attempts++;
                        }
                    } catch (err) {
                        attempts++;
                        await new Promise(resolve => setTimeout(resolve, 2000));
                    }
                }

                if (!success) {
                    alert(`[CRITICAL ERROR] Connection lost on chunk ${i+1}. Upload aborted.`);
                    btnSubmit.disabled = false;
                    btnSubmit.innerText = "DEPLOY_PATCH";
                    return;
                }

                const percentage = Math.round(((i + 1) / totalChunks) * 100);
                progressBar.style.width = percentage + '%';
                progressText.innerText = `${percentage}%`;
            }

            progressStatusSub.innerText = "[ SAVING PATCH METADATA... ]";

            try {
                const finalResponse = await fetch('/register-version', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        version,
                        filename: file.name,
                        changelog,
                        files_to_delete,
                        server_ip: serverIp
                    })
                });

                if (finalResponse.ok) {
                    progressText.innerText = "COMPLETE";
                    progressStatusSub.style.color = '#D5A63A';
                    progressStatusSub.innerText = ">>> SUCCESS! DEPLOY FINISHED COMPLETELY.";
                    setTimeout(() => window.location.href = '/admin', 1500);
                } else {
                    alert("[ERROR] Failed to save metadata to the final JSON.");
                }
            } catch (err) {
                alert("[ERROR] Communication failure during patch finalization.");
            }
        };
    </script>
</body>
</html>"""

@app.route('/versions.json', methods=['GET'])
def get_json():
    log(f"Client requested versions.json | IP={request.remote_addr}")
    return jsonify(get_versions())


@app.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    from flask import send_from_directory

    safe_name = secure_filename(filename)
    if not safe_name:
        log(f"Invalid download filename rejected | Raw={filename}", "WARN")
        return jsonify({"status": "error", "message": "Invalid filename"}), 400

    log(f"Download requested: {safe_name} | IP={request.remote_addr}")
    return send_from_directory(UPLOAD_FOLDER, safe_name)


@app.route('/admin', methods=['GET'])
def admin():
    log(f"Admin panel accessed | IP={request.remote_addr}")
    return render_template_string(
        HTML_TEMPLATE,
        versions=get_versions(),
        current_host=request.host
    )


@app.route('/upload-chunk', methods=['POST'])
def upload_chunk():
    try:
        file_chunk = request.files.get('file')

        raw_filename = request.form.get('filename') or (
            file_chunk.filename if file_chunk else "patch.zip"
        )
        filename = secure_filename(raw_filename)

        chunk_index = int(request.form.get('chunk_index', 0))

        if not file_chunk or not filename:
            log("Invalid upload received.", "WARN")
            return jsonify({"status": "error", "message": "Invalid data"}), 400

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        abs_path = os.path.abspath(file_path)

        if not _is_path_inside(UPLOAD_FOLDER, abs_path):
            log(f"Path traversal blocked on upload | Raw={raw_filename}", "WARN")
            return jsonify({"status": "error", "message": "Invalid filename"}), 400

        mode = 'wb' if chunk_index == 0 else 'ab'
        chunk_data = file_chunk.read()

        with open(abs_path, mode) as f:
            f.write(chunk_data)

        size_mb = round(len(chunk_data) / (1024 * 1024), 2)

        log(
            f"Chunk saved | File={filename} | Chunk={chunk_index} | "
            f"Size={size_mb}MB | Mode={mode}"
        )

        return jsonify({"status": "chunk_saved"}), 200

    except Exception as e:
        log(f"Failed to save chunk: {e}", "ERROR")
        return jsonify({"status": "error"}), 500


@app.route('/register-version', methods=['POST'])
def register_version():
    try:
        data = request.json

        version = data.get('version')
        raw_filename = data.get('filename', '')
        filename = secure_filename(raw_filename)
        changelog = data.get('changelog', '')
        files_to_delete = data.get('files_to_delete', [])
        server_ip = data.get('server_ip') or request.host

        log(
            f"Registering version | Version={version} | "
            f"File={filename} | IP={server_ip}"
        )

        if not version or not filename:
            log("Failed to register version: missing parameters.", "WARN")
            return jsonify({
                "status": "error",
                "message": "Missing parameters"
            }), 400

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not _is_path_inside(UPLOAD_FOLDER, os.path.abspath(file_path)):
            log(f"Path traversal blocked on register | Raw={raw_filename}", "WARN")
            return jsonify({
                "status": "error",
                "message": "Invalid filename"
            }), 400

        download_url = f"http://{server_ip}/files/{filename}"

        new_entry = {
            "Version": version,
            "Download": download_url,
            "Changelog": changelog,
            "files_to_delete": files_to_delete
        }

        append_version(new_entry)

        log(f"Version registered successfully | Version={version}")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        log(f"Failed to register version: {e}", "ERROR")
        return jsonify({"status": "error"}), 500


@app.route('/delete/<version>', methods=['GET'])
def delete(version):
    log(f"Wipe requested | Version={version}")

    with versions_lock:
        item = next((x for x in cached_versions if x['Version'] == version), None)

    if not item:
        log(f"Attempt to delete non-existent version: {version}", "WARN")
        return redirect('/admin')

    try:
        raw_filename = item['Download'].split('/')[-1]
        filename = secure_filename(raw_filename)

        if not filename:
            log(
                f"Invalid filename on delete | Version={version} | Raw={raw_filename}",
                "WARN"
            )
        else:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            abs_path = os.path.abspath(file_path)

            if not _is_path_inside(UPLOAD_FOLDER, abs_path):
                log(
                    f"Path traversal blocked on delete | Version={version} | "
                    f"Path={abs_path}",
                    "WARN"
                )
            elif os.path.exists(abs_path):
                os.remove(abs_path)
                log(f"Physical file deleted | File={filename}")
            else:
                log(f"Physical file not found | File={filename}", "WARN")

    except Exception as e:
        log(f"Could not delete physical file: {e}", "WARN")

    removed = remove_version(version)
    if removed:
        log(f"Version removed from JSON | Version={version}")

    return redirect('/admin')


if __name__ == '__main__':
    print("=======================================")
    print("    MODU-PDATER SERVER [TACTICAL]      ")
    print("=======================================")

    log("Starting server...")
    log("Host: 0.0.0.0")
    log("Port: 8080")
    log("Threads: 32")
    log("Max Body Size: 100GB")
    log(f"Loaded {len(cached_versions)} version(s) into memory cache")

    try:
        serve(
            app,
            host='0.0.0.0',
            port=8080,
            max_request_body_size=107374182400,
            threads=32
        )

    except Exception as e:
        log(f"Fatal server error: {e}", "FATAL")