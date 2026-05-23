# MODU-PDATER SERVER

## What is the MODU-PDATER SERVER?

MODU-PDATER SERVER is the backend component of the MODU-PDATER launcher: https://github.com/Hashimini/SPTMODU-PDATER

IF YOU ARE JUST USING MODU-PDATER BECAUSE YOUR TECH FRIEND TOLD YOU TO INSTALL IT, YOU DO NOT NEED TO SET THIS UP.

The MODU-PDATER SERVER is a lightweight Flask-based web server responsible for:

- Hosting update patches
- Managing the `versions.json`
- Providing download endpoints for launcher clients
- Handling large patch uploads through chunked transfers

---

# New in v1.1 "CHUNKY"

The server now supports chunked uploads for extremely large patch files.

Main improvements:

- Large file upload support
- An upload retry system
- Better VPN/unstable network handling
- Abismal, like, immeasurable performance boost for RAM and CPU
- Terminal logging

---

# Requirements

Required software:

- Python 3.10+
- Flask
- Waitress

---

# Installation

## 1. Install Python

Download Python from: [Python Official Website](https://www.python.org/downloads)

During installation, make sure to enable:

```text
Add Python to PATH
```

## 2. Install Dependencies

Open a terminal inside the server folder and run:

```bash
pip install flask waitress
```

---

# Running the Server

Create a folder for the server and run inside the folder:

```bash
python server.py
```

The server will start on:

```text
http://0.0.0.0:8080
```

Admin panel:

```text
http://YOURLOCAL_IP:8080/admin
```

Versions list:

```text
http://YOURLOCAL_IP:8080/versions.json
```

---

# Server Structure

Recommended structure:

```text
SERVER/
├── server.py
├── versions.json
├── files/
```

---

# Upload Flow

The upload process now works like this:

1. Select the `.zip` file.
2. The file then is split into chunks (Default as 64mb).
3. Chunks are uploaded sequentially, one by one.
4. Failed chunks uploads retry automatically.
5. Then the Server reconstructs the final `.zip`
6. Metadata is registered into `versions.json`

# Uploading a New Patch

Open the admin panel:

```text
http://YOURLOCAL_IP:8080/admin
```

The panel allows you to:

- Upload `.zip` files
- Register the new versions
- Register obsolete files for deletion
- Delete uploaded versions

# Chunked Upload System

Default chunk size:

```text
64MB per chunk
```

You can change freely on LINE 170
```JavaScript
const CHUNK_SIZE = 64 * 1024 * 1024;
```

Maximum upload size:

```text
100GB
```

---

# Creating the patch / `.zip`

A patch should contain only the files you want to update.

Example:

```text
BepInEx/plugins/BESTMOD.dll
user/mods/MyMod/
```

---

# Deleting Files

The `files_to_delete` field allows the launcher to automatically remove files from client installations.

Example:

```text
BepInEx/plugins/BrokenMod.dll
BepInEx/config/OldConfig.cfg
```

Each line represents one file or folder.

---

# VPN / WAN Usage

If you are hosting through:

- Radmin VPN
- Hamachi
- ZeroTier
- or any other VPN software

You must use the Virtual IP or Public IP inside the `Server IP` field when uploading patches.

Example:

```text
26.14.220.15:8080
```

---

# Using Your Own Web Server

You arent, by any means, required to use my Flask/Waitress server.

The MODU-PDATER launcher only requires:

- A valid `versions.json`
- Direct download links for patch files
- Accessible HTTP/HTTPS endpoints

This means you can host the system on:

- Nginx
- Apache
- Custom backends
- Cloud hosting providers
- Dedicated servers
- And so on...

---

# Required versions.json Structure

Example:

```json
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

Do NOT expose your admin panel to the public internet unless you REALLY know what you are doing.

This server does not include:

- Authentication
- Rate limiting
- HTTPS
- Upload restrictions
- Virus checking
- Hash verification

It is intended for:
- Private servers
- Friend groups
- Small communities
- VPN/LAN environments

---

# Recommended Usage

This project was mainly designed for:

- Small SPT communities
- Friend groups
- Private modpacks
- VPN-hosted servers
- Lightweight self-hosted deployments

It was NOT designed for:

- Enterprise usage
- Massive public hosting
- Large-scale CDN distribution

---

# General Workflow

1. Create the patch
2. Compress patch into `.zip`
3. Open `/admin`
4. Upload patch
5. Fill version information
6. Publish the update
7. Users update automatically through the launcher

---

# Developer Notes

Yes the interface was 95% made by vibe coding, Its just a admin panel so I didnt cared that much for something most users wont interact...
