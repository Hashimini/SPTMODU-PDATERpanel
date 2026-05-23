# MODU-PDATER SERVER

## What is the MODU-PDATER SERVER?

MODU-PDATER SERVER is the backend component of the MODU-PDATER launcher: https://github.com/Hashimini/SPTMODU-PDATER

IF YOU ARE JUST USING MODU-PDATER BECAUSE YOUR TECH FRIEND TOLD YOU TO INSTALL IT, YOU DO NOT NEED TO SET THIS UP.

The MODU-PDATER SERVER is a lightweight Flask-based web server responsible for:

* Hosting the update patches
* Managing the `versions.json`
* Providing download endpoints for launcher clients

---

# Requirements

Required software:

* Python 3.10+
* Flask

---

# Installation

## 1. Install Python

Download Python from:

[Python Official Website](https://www.python.org/downloads)

During installation, make sure to enable:

```text id="j0fylt"
Add Python to PATH
```

---

## 2. Install Flask

Open a terminal inside the server folder and run:

```bash id="b1ubf9"
pip install flask
```

---

# Running the Server

Inside the project folder, run:

```bash id="3v2j8m"
python app.py
```

The server will start on:

```text id="lvr7q0"
http://0.0.0.0:8080
```

Admin panel:

```text id="q6j1a3"
http://YOUR_IP:8080/admin
```

Version manifest:

```text id="1ck3d9"
http://YOUR_IP:8080/versions.json
```

---

# Server Structure

Recommended structure:

```text id="88e6d0"
SERVER/
├── server.py
├── versions.json
├── files/
```

---

# Uploading a New Patch

Open the admin panel:

```text id="y88t6k"
http://YOUR_IP:8080/admin
```

The panel allows you to:

* Upload `.zip` patches
* Register new versions
* Delete uploaded versions

---

# Creating a Patch

A patch should contain only the files you want to update.

Example:

```text id="l4uvtm"
BepInEx/plugins/MyNewMod.dll
user/mods/MyMod/
```

Compress the files into a `.zip` archive before uploading.

---

# files_to_delete

The `files_to_delete` field allows the launcher to automatically remove obsolete files from client installations.

Example:

```text id="26vv0o"
BepInEx/plugins/OldMod.dll
BepInEx/config/oldmod.cfg
```

Each line represents one file or folder.

---

# VPN / WAN Usage

If you are hosting through:

* Radmin VPN
* Hamachi
* or any other VPN software

You must use the Virtual IP or Public IP inside the `Server IP` field when uploading patches.

Example:

```text id="r56nxy"
26.14.220.15:8080
```

---

# Using Your Own Web Server

You are NOT required to use the included Flask server.

The launcher only requires:

* A valid `versions.json`
* Direct download links for patch files
* Accessible HTTP/HTTPS endpoints

This means you can host the system on:

* Nginx
* Apache
* Any custom web backend

---

# Required versions.json Structure

Example:

```json id="k9v1so"
[
    {
        "Version": "1.0.0",
        "Download": "http://YOUR_SERVER/files/patch_1.0.0.zip",
        "Changelog": "[+] Added Fontaine's FOV Fix",
        "files_to_delete": []
    },
    {
        "Version": "1.1.0",
        "Download": "http://YOUR_SERVER/files/patch_1.1.0.zip",
        "Changelog": "[-] Removed Fontaine's FOV Fix",
        "files_to_delete": [
            "BepInEx/plugins/FovFix.dll"
        ]
    }
]
```

---

# Security Notes

Do not expose your admin panel to the public internet unless you REALLY know what you are doing!!

This server does not include:
- Authentication
- Rate limiting
- HTTPS
- Upload restrictions
- Virus Checker or Hash checking

It is intended for private/community usage.

---

# Important Notes

* Version numbers should follow semantic versioning whenever possible
* Keep old patch files available for incremental updates

---

# General Workflow

1. Create update patch
2. Compress patch into `.zip`
3. Open `/admin`
4. Upload patch
5. Fill version information
6. Publish update
7. Users update automatically through the launcher
