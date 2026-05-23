import os
import json
from flask import Flask, request, jsonify, render_template_string, redirect

app = Flask(__name__)

UPLOAD_FOLDER = 'files'
JSON_FILE = 'versions.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>[ OPERATOR CONSOLE ] - ModUpdater</title>
    <style>
        body {
            font-family: 'Courier New', Courier, monospace, sans-serif;
            background: #0A0B09;
            color: #D7D2C3;
            max-width: 700px;
            margin: 40px auto;
            padding: 20px;
            letter-spacing: 0.5px;
        }

        h1 {
            color: #E5DFC9;
            text-transform: uppercase;
            font-size: 24px;
            border-bottom: 2px solid #2A2E25;
            padding-bottom: 10px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        h1::after {
            content: "SYS_VERSION: 1.0";
            font-size: 11px;
            color: #6E7753;
            background: #1A1E17;
            padding: 4px 8px;
            border: 1px solid #2A2E25;
        }

        h2 {
            color: #FFD36A;
            font-size: 16px;
            text-transform: uppercase;
            margin-top: 0;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        h2::before {
            content: "// ";
            color: #6E7753;
            margin-right: 5px;
        }

        .card {
            background: #11130F;
            padding: 25px;
            border: 1px solid #2A2E25;
            border-top: 4px solid #6E7753;
            margin-bottom: 25px;
            box-shadow: 0 10px 20px #050505;
        }

        label {
            display: block;
            font-size: 11px;
            text-transform: uppercase;
            color: #97927F;
            margin-top: 15px;
            margin-bottom: 5px;
            font-weight: bold;
        }

        input[type="text"], textarea {
            width: 100%;
            padding: 12px;
            margin-bottom: 5px;
            border: 1px solid #2A2E25;
            background: #0A0B09;
            color: #D7D2C3;
            box-sizing: border-box;
            font-family: inherit;
            transition: border-color 0.2s;
        }
        input[type="text"]:focus, textarea:focus {
            outline: none;
            border-color: #5E654E;
            background: #1A1E17;
        }

        button {
            background: #D5A63A;
            color: #0A0B09;
            padding: 14px 20px;
            border: 1px solid #8E6720;
            cursor: pointer;
            font-weight: bold;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 20px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.2);
            transition: background 0.2s;
        }
        button:hover {
            background: #F0C75E;
        }
        button:active {
            background: #8E6720;
        }

        .version-item {
            background: #1A1E17;
            border: 1px solid #2A2E25;
            padding: 15px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .version-info {
            max-width: 75%;
        }
        .version-title {
            color: #E5DFC9;
            font-size: 15px;
        }
        .version-link {
            color: #6E7753;
            font-size: 11px;
            text-decoration: none;
            word-break: break-all;
            display: block;
            margin-top: 5px;
        }
        .version-link:hover {
            color: #98A46F;
            text-decoration: underline;
        }

        #drop-zone {
            border: 2px dashed #4E5740;
            padding: 30px 20px;
            text-align: center;
            margin: 15px 0;
            background: #0A0B09;
            cursor: pointer;
            color: #97927F;
            text-transform: uppercase;
            font-size: 12px;
            transition: all 0.2s;
        }
        #drop-zone.dragover {
            background: #2B3126;
            border-color: #8BCF5D;
            color: #E5DFC9;
        }

        .btn-delete {
            background: #2A2E25;
            color: #D36242;
            text-decoration: none;
            border: 1px solid #D36242;
            font-weight: bold;
            padding: 8px 14px;
            font-size: 12px;
            text-transform: uppercase;
            transition: all 0.2s;
        }
        .btn-delete:hover {
            background: #D36242;
            color: #0A0B09;
        }

        .help-text {
            color: #FFB13C;
            font-size: 11px;
            margin-top: 2px;
            margin-bottom: 12px;
            display: block;
        }

        .changelog-box {
            background: #0A0B09;
            border-left: 3px solid #D4A640;
            padding: 8px 12px;
            margin-top: 8px;
            font-size: 12px;
            color: #D7D2C3;
            white-space: pre-wrap;
        }

        .wipe-box {
            background: #1C0F0F;
            border-left: 3px solid #D36242;
            padding: 6px 12px;
            margin-top: 6px;
            font-size: 11px;
            color: #EAB2A2;
        }
        .wipe-box ul {
            margin: 4px 0 0 0;
            padding-left: 18px;
        }
    </style>
</head>
<body>
    <h1>MODU-PDATER<span style="color: #6E7753; font-size:14px;">[ADMIN_PANEL]</span></h1>

    <div class="card">
        <h2>Registrar Novo Patch</h2>
        <form id="upload-form" action="/upload" method="POST" enctype="multipart/form-data">
            <label>IP (Endpoints de Download):</label>
            <input type="text" id="server-ip-input" name="server_ip" value="{{ current_host }}" placeholder="ex: 200.10.23.14:8080" required />
            <span class="help-text">⚠ Se estiver usando VPN, use o IP virtual mantendo a porta do servidor.</span>

            <label>Identificador da Versão:</label>
            <input type="text" name="version" placeholder="Ex: v2.4.0" required />

            <label>Changelog:</label>
            <textarea name="changelog" rows="4" placeholder="[+] ADDED: Novo Mod&#10;[x] FIXED: Bug corrigido&#10;[-] REMOVED: Arquivo obsoleto"></textarea>

            <label>Arquivos Obsoletos para Deletar nos Clientes (Um por linha):</label>
            <textarea name="files_to_delete" rows="3" placeholder="BepInEx/plugins/ModQuebrado.dll&#10;BepInEx/config/com.mod.quebrado.cfg"></textarea>
            <span class="help-text">⚠ Deixe em branco se nenhum arquivo precisar ser removido nesta versão.</span>

            <label>Arquivo do Pacote (.zip):</label>
            <div id="drop-zone">Arrastar e solte o arquivo .ZIP aqui ou clique</div>
            <input type="file" id="file-input" name="file" accept=".zip" style="display:none;" required />
            <p id="file-name" style="color:#8BCF5D; font-size:12px; font-weight:bold; margin: 5px 0 0 0;"></p>

            <button type="submit">Enviar</button>
        </form>
    </div>

    <div class="card">
        <h2>Versões registradas no Servidor</h2>
        <div id="versions-list">
            {% if not versions %}
                <p style="color: #666454; font-size: 13px;">Vazio</p>
            {% else %}
                {% for v in versions %}
                    <div class="version-item">
                        <div class="version-info">
                            <strong class="version-title">DEPLOY_ID: <span style="color: #FFD36A;">{{ v.Version }}</span></strong>

                            {% if v.Changelog %}
                                <div class="changelog-box">{{ v.Changelog }}</div>
                            {% else %}
                                <div class="changelog-box" style="color: #666454; border-color: #2A2E25;">Nenhum changelog.</div>
                            {% endif %}

                            {% if v.files_to_delete %}
                                <div class="wipe-box">
                                    ARQUIVOS MARCADOS PARA REMOÇÃO:
                                    <ul>
                                        {% for file in v.files_to_delete %}
                                            <li><code>{{ file }}</code></li>
                                        {% endfor %}
                                    </ul>
                                </div>
                            {% endif %}

                            <a href="{{ v.Download }}" class="version-link" target="_blank">Target URL: {{ v.Download }}</a>
                        </div>
                        <div>
                            <a href="/delete/{{ v.Version }}" class="btn-delete" onclick="return confirm('ATENÇÃO: Confirma a destruição permanente da versão {{ v.Version }} e do seu arquivo binário no disco?')">Wipe</a>
                        </div>
                    </div>
                {% endfor %}
            {% endif %}
        </div>
    </div>

    <script>
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const fileName = document.getElementById('file-name');
        const serverIpInput = document.getElementById('server-ip-input');
        const uploadForm = document.getElementById('upload-form');

        const savedIp = localStorage.getItem('saved_server_ip');
        if (savedIp) {
            serverIpInput.value = savedIp;
        }

        uploadForm.onsubmit = () => {
            localStorage.setItem('saved_server_ip', serverIpInput.value);
        };

        dropZone.onclick = () => fileInput.click();
        dropZone.ondragover = (e) => { e.preventDefault(); dropZone.classList.add('dragover'); };
        dropZone.ondragleave = () => dropZone.classList.remove('dragover');
        dropZone.ondrop = (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if(e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                fileName.innerText = '>>> PRONTO PARA ENVIO: ' + e.dataTransfer.files[0].name.toUpperCase();
            }
        };
        fileInput.onchange = () => {
            if(fileInput.files.length) fileName.innerText = '>>> PRONTO PARA ENVIO: ' + fileInput.files[0].name.toUpperCase();
        };
    </script>
</body>
</html>
"""

@app.route('/versions.json', methods=['GET'])
def get_json():
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))

@app.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    from flask import send_from_directory
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/admin', methods=['GET'])
def admin():
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        versions = json.load(f)
    return render_template_string(HTML_TEMPLATE, versions=versions, current_host=request.host)

@app.route('/upload', methods=['POST'])
def upload():
    server_ip = request.form.get('server_ip')
    version = request.form.get('version')
    changelog = request.form.get('changelog')

    files_to_delete_raw = request.form.get('files_to_delete', '')

    files_to_delete = [line.strip() for line in files_to_delete_raw.splitlines() if line.strip()]

    file = request.files.get('file')

    if not version or not file:
        return "Erro: Versão ou arquivo ausentes.", 400

    if not server_ip:
        server_ip = request.host

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    download_url = f"http://{server_ip}/files/{file.filename}"

    new_entry = {
        "Version": version,
        "Download": download_url,
        "Changelog": changelog,
        "files_to_delete": files_to_delete
    }

    with open(JSON_FILE, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        data.append(new_entry)
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.truncate()

    return redirect('/admin')

@app.route('/delete/<version>', methods=['GET'])
def delete(version):
    with open(JSON_FILE, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        item = next((x for x in data if x['Version'] == version), None)

        if item:
            try:
                filename = item['Download'].split('/')[-1]
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Aviso: Não foi possível deletar o arquivo físico: {e}")

            data.remove(item)

            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()

    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
