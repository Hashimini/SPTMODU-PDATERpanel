import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, redirect
from waitress import serve

app = Flask(__name__)

UPLOAD_FOLDER = 'files'
JSON_FILE = 'versions.json'

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>[ OPERATOR CONSOLE ] - ModUpdater</title>
    <style>
        body { font-family: 'Courier New', Courier, monospace, sans-serif; background: #0A0B09; color: #D7D2C3; max-width: 700px; margin: 40px auto; padding: 20px; letter-spacing: 0.5px; }
        h1 { color: #E5DFC9; text-transform: uppercase; font-size: 24px; border-bottom: 2px solid #2A2E25; padding-bottom: 10px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }
        h1::after { content: "SYS_VERSION: 1.1 (CHUNKY)"; font-size: 11px; color: #6E7753; background: #1A1E17; padding: 4px 8px; border: 1px solid #2A2E25; }
        h2 { color: #FFD36A; font-size: 16px; text-transform: uppercase; margin-top: 0; margin-bottom: 15px; display: flex; align-items: center; }
        h2::before { content: "// "; color: #6E7753; margin-right: 5px; }
        .card { background: #11130F; padding: 25px; border: 1px solid #2A2E25; border-top: 4px solid #6E7753; margin-bottom: 25px; box-shadow: 0 10px 20px #050505; }
        label { display: block; font-size: 11px; text-transform: uppercase; color: #97927F; margin-top: 15px; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], textarea { width: 100%; padding: 12px; margin-bottom: 5px; border: 1px solid #2A2E25; background: #0A0B09; color: #D7D2C3; box-sizing: border-box; font-family: inherit; }
        button { background: #D5A63A; color: #0A0B09; padding: 14px 20px; border: 1px solid #8E6720; cursor: pointer; font-weight: bold; width: 100%; text-transform: uppercase; letter-spacing: 1px; margin-top: 20px; }
        button:hover { background: #F0C75E; }
        .version-item { background: #1A1E17; border: 1px solid #2A2E25; padding: 15px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
        .version-info { max-width: 75%; } .version-title { color: #E5DFC9; font-size: 15px; }
        .version-link { color: #6E7753; font-size: 11px; text-decoration: none; word-break: break-all; display: block; margin-top: 5px; }
        #drop-zone { border: 2px dashed #4E5740; padding: 30px 20px; text-align: center; margin: 15px 0; background: #0A0B09; cursor: pointer; color: #97927F; text-transform: uppercase; font-size: 12px; }
        #drop-zone.dragover { background: #2B3126; border-color: #8BCF5D; color: #E5DFC9; }
        .btn-delete { background: #2A2E25; color: #D36242; text-decoration: none; border: 1px solid #D36242; font-weight: bold; padding: 8px 14px; font-size: 12px; text-transform: uppercase; }
        .btn-delete:hover { background: #D36242; color: #0A0B09; }
        .help-text { color: #FFB13C; font-size: 11px; margin-top: 2px; margin-bottom: 12px; display: block; }
        .changelog-box { background: #0A0B09; border-left: 3px solid #D4A640; padding: 8px 12px; margin-top: 8px; font-size: 12px; color: #D7D2C3; white-space: pre-wrap; }
        .wipe-box { background: #1C0F0F; border-left: 3px solid #D36242; padding: 6px 12px; margin-top: 6px; font-size: 11px; color: #EAB2A2; }
        .wipe-box ul { margin: 4px 0 0 0; padding-left: 18px; }

        /* Estilos da Barra de Progresso */
        .progress-container { display: none; background: #0A0B09; border: 1px solid #2A2E25; padding: 4px; margin-top: 20px; }
        .progress-bar { height: 20px; background: #8BCF5D; width: 0%; transition: width 0.1s ease; }
        .progress-text { font-size: 11px; color: #97927F; margin-top: 6px; text-align: center; text-transform: uppercase; font-weight: bold; }
    </style>
</head>
<body>
    <h1>MODU-PDATER<span style="color: #6E7753; font-size:14px;">[ADMIN_PANEL]</span></h1>

    <div class="card">
        <h2>Registrar Novo Patch</h2>
        <form id="upload-form">
            <label>IP (Endpoints de Download):</label>
            <input type="text" id="server-ip-input" name="server_ip" value="{{ current_host }}" placeholder="ex: 200.10.23.14:8080" required />
            <span class="help-text">⚠ Se estiver usando VPN, use o IP virtual mantendo a porta do servidor.</span>

            <label>Identificador da Versão:</label>
            <input type="text" name="version" placeholder="Ex: v2.4.0" required />

            <label>Changelog:</label>
            <textarea name="changelog" rows="4" placeholder="[+] ADDED: Novo Mod&#10;[x] FIXED: Bug corrigido"></textarea>

            <label>Arquivos Obsoletos para Deletar nos Clientes (Um por linha):</label>
            <textarea name="files_to_delete" rows="3" placeholder="BepInEx/plugins/ModQuebrado.dll"></textarea>

            <label>Arquivo do Pacote (.zip):</label>
            <div id="drop-zone">Arrastar e solte o arquivo .ZIP aqui ou clique</div>
            <input type="file" id="file-input" name="file" accept=".zip" style="display:none;" required />
            <p id="file-name" style="color:#8BCF5D; font-size:12px; font-weight:bold; margin: 5px 0 0 0;"></p>

            <div class="progress-container" id="progress-container">
                <div class="progress-bar" id="progress-bar"></div>
            </div>
            <div class="progress-text" id="progress-text"></div>

            <button type="submit" id="btn-submit">Enviar Patch</button>
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
                            <a href="/delete/{{ v.Version }}" class="btn-delete" onclick="return confirm('Confirmar destruição permanente?')">Wipe</a>
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
        const btnSubmit = document.getElementById('btn-submit');

        const progressContainer = document.getElementById('progress-container');
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');

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
                fileName.innerText = '>>> PRONTO: ' + e.dataTransfer.files[0].name.toUpperCase();
            }
        };
        fileInput.onchange = () => {
            if(fileInput.files.length) fileName.innerText = '>>> PRONTO: ' + fileInput.files[0].name.toUpperCase();
        };

        uploadForm.onsubmit = async (e) => {
            e.preventDefault();
            localStorage.setItem('saved_server_ip', serverIpInput.value);

            if (!fileInput.files.length) return alert("Por favor, selecione um arquivo ZIP.");

            const file = fileInput.files[0];
            const version = uploadForm.elements['version'].value;
            const changelog = uploadForm.elements['changelog'].value;
            const filesToDeleteRaw = uploadForm.elements['files_to_delete'].value;
            const serverIp = serverIpInput.value;

            const files_to_delete = filesToDeleteRaw.split('\\n').map(l => l.trim()).filter(l => l);

            // Configuração do tamanho do pedaço: 10MB por pedaço
            const CHUNK_SIZE = 64 * 1024 * 1024;
            const totalChunks = Math.ceil(file.size / CHUNK_SIZE);

            btnSubmit.disabled = true;
            btnSubmit.innerText = "ENVIANDO...";
            progressContainer.style.display = 'block';

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
                        progressText.innerText = `[BLOCO ${i + 1}/${totalChunks}] Enviando dados... (Tentativa ${attempts + 1})`;
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
                        await new Promise(resolve => setTimeout(resolve, 2000)); // Espera 2 segundos antes de tentar de novo
                    }
                }

                if (!success) {
                    alert(`Erro crítico: Conexão perdida no bloco ${i+1}. O upload foi abortado.`);
                    btnSubmit.disabled = false;
                    btnSubmit.innerText = "Enviar Patch";
                    return;
                }

                const percentage = Math.round(((i + 1) / totalChunks) * 100);
                progressBar.style.width = percentage + '%';
                progressText.innerText = `PROGRESSO DE UPLOAD: ${percentage}%`;
            }

            progressText.innerText = "STATUS: SALVANDO METADADOS DO PATCH...";

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
                    progressText.style.color = '#8BCF5D';
                    progressText.innerText = ">>> SUCESSO! DEPLOY CONCLUÍDO COMPLEMENTE.";
                    setTimeout(() => window.location.href = '/admin', 1500);
                } else {
                    alert("Erro ao salvar os metadados no JSON final.");
                }
            } catch (err) {
                alert("Erro ao comunicar finalização do patch.");
            }
        };
    </script>
</body>
</html>"""

@app.route('/versions.json', methods=['GET'])
def get_json():
    log(f"Cliente requisitou versions.json | IP={request.remote_addr}")

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))


@app.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    from flask import send_from_directory

    log(f"Download solicitado: {filename} | IP={request.remote_addr}")

    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/admin', methods=['GET'])
def admin():
    log(f"Painel admin acessado | IP={request.remote_addr}")

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        versions = json.load(f)

    return render_template_string(
        HTML_TEMPLATE,
        versions=versions,
        current_host=request.host
    )


@app.route('/upload-chunk', methods=['POST'])
def upload_chunk():
    try:
        file_chunk = request.files.get('file')

        filename = request.form.get('filename') or (
            file_chunk.filename if file_chunk else "patch.zip"
        )

        chunk_index = int(request.form.get('chunk_index', 0))

        if not file_chunk or not filename:
            log("Upload inválido recebido.", "WARN")
            return "Dados inválidos.", 400

        file_path = os.path.join(UPLOAD_FOLDER, filename)

        mode = 'wb' if chunk_index == 0 else 'ab'

        chunk_data = file_chunk.read()

        with open(file_path, mode) as f:
            f.write(chunk_data)

        size_mb = round(len(chunk_data) / (1024 * 1024), 2)

        log(
            f"Chunk salvo | Arquivo={filename} | Chunk={chunk_index} | "
            f"Tamanho={size_mb}MB | Modo={mode}"
        )

        return jsonify({"status": "chunk_saved"}), 200

    except Exception as e:
        log(f"Erro ao salvar chunk: {e}", "ERROR")
        return jsonify({"status": "error"}), 500


@app.route('/register-version', methods=['POST'])
def register_version():
    try:
        data = request.json

        version = data.get('version')
        filename = data.get('filename')
        changelog = data.get('changelog', '')
        files_to_delete = data.get('files_to_delete', [])
        server_ip = data.get('server_ip') or request.host

        log(
            f"Registrando versão | Version={version} | "
            f"Arquivo={filename} | IP={server_ip}"
        )

        if not version or not filename:
            log("Falha ao registrar versão: parâmetros faltando.", "WARN")
            return jsonify({
                "status": "error",
                "message": "Faltam parâmetros"
            }), 400

        download_url = f"http://{server_ip}/files/{filename}"

        new_entry = {
            "Version": version,
            "Download": download_url,
            "Changelog": changelog,
            "files_to_delete": files_to_delete
        }

        with open(JSON_FILE, 'r+', encoding='utf-8') as f:
            versions = json.load(f)

            versions.append(new_entry)

            f.seek(0)

            json.dump(
                versions,
                f,
                indent=4,
                ensure_ascii=False
            )

            f.truncate()

        log(
            f"Versão registrada com sucesso | "
            f"Version={version}"
        )

        return jsonify({"status": "success"}), 200

    except Exception as e:
        log(f"Erro ao registrar versão: {e}", "ERROR")
        return jsonify({"status": "error"}), 500


@app.route('/delete/<version>', methods=['GET'])
def delete(version):
    log(f"Solicitação de wipe | Version={version}")

    with open(JSON_FILE, 'r+', encoding='utf-8') as f:
        data = json.load(f)

        item = next(
            (x for x in data if x['Version'] == version),
            None
        )

        if item:
            try:
                filename = item['Download'].split('/')[-1]

                file_path = os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )

                if os.path.exists(file_path):
                    os.remove(file_path)

                    log(
                        f"Arquivo físico deletado | "
                        f"Arquivo={filename}"
                    )

            except Exception as e:
                log(
                    f"Não foi possível deletar arquivo físico: {e}",
                    "WARN"
                )

            data.remove(item)

            f.seek(0)

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

            f.truncate()

            log(
                f"Versão removida do JSON | "
                f"Version={version}"
            )

        else:
            log(
                f"Tentativa de deletar versão inexistente: {version}",
                "WARN"
            )

    return redirect('/admin')


if __name__ == '__main__':
    print("==============================")
    print("    MODU-PDATER SERVER  ")
    print("==============================")

    log("Inicializando...")
    log("Host: 0.0.0.0")
    log("Porta: 8080")
    log("Threads: 32")
    log("Max Body Size: 100GB")

    try:
        serve(
            app,
            host='0.0.0.0',
            port=8080,
            max_request_body_size=107374182400,
            threads=32
        )

    except Exception as e:
        log(f"Erro fatal no servidor: {e}", "FATAL")
