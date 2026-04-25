from flask import Flask, request, send_from_directory, redirect, url_for
import os
import random
import string

app = Flask(__name__)

# ✅ RENDER FIX (only writable dir)
UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

def generate_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# ======================
# UPLOAD PAGE
# ======================
@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            return redirect("/")

        ext = file.filename.split('.')[-1]
        clip_id = generate_id()
        filename = f"{clip_id}.{ext}"

        file.save(os.path.join(UPLOAD_FOLDER, filename))

        return redirect(url_for("clip", clip_id=clip_id))

    return '''
<!DOCTYPE html>
<html>
<head>
<title>Escape</title>

<style>
:root { --bg:#000; --card:#111; --text:white; }
.light { --bg:#f5f5f5; --card:white; --text:black; }

body {
    margin:0;
    background:var(--bg);
    color:var(--text);
    font-family:Arial;
}

.logo {
    position:absolute;
    top:20px;
    left:30px;
    font-weight:800;
    font-size:22px;
}
.logo span {
    color:#8b5cf6;
    text-shadow:0 0 10px #8b5cf6;
}

.wrapper {
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
}

.card {
    background:var(--card);
    padding:40px;
    border-radius:18px;
    width:450px;
    text-align:center;
    box-shadow:0 0 60px rgba(139,92,246,0.2);
}

.drop {
    border:2px dashed #444;
    padding:80px 20px;
    border-radius:14px;
    cursor:pointer;
}
.drop:hover { border-color:#8b5cf6; }

.file-info {
    display:none;
    margin-top:15px;
    padding:10px;
    background:#222;
    border-radius:10px;
    justify-content:space-between;
}

button {
    display:none;
    margin-top:15px;
    width:100%;
    padding:14px;
    border:none;
    border-radius:10px;
    background:linear-gradient(135deg,#7c3aed,#4f46e5);
    color:white;
    cursor:pointer;
}

.progress {
    display:none;
    margin-top:10px;
    height:6px;
    background:#333;
}
.bar { height:100%; width:0%; background:#8b5cf6; }

.error { color:red; display:none; margin-top:10px; }
input { display:none; }

.toggle {
    position:fixed;
    bottom:20px;
    right:20px;
    cursor:pointer;
}
</style>
</head>

<body>

<div class="logo">Escape<span>.</span></div>

<div class="wrapper">
<div class="card">

<h2>Upload File</h2>

<div class="drop" id="dropBox">
    <span id="text">Click or drag file here</span>
    <input type="file" id="fileInput">
</div>

<div class="file-info" id="fileInfo">
    <span id="fileName"></span>
    <span onclick="clearFile()" style="cursor:pointer;">✖</span>
</div>

<button id="uploadBtn">Upload File</button>

<div class="progress"><div class="bar" id="bar"></div></div>

<div class="error" id="error">File too big (max 100MB)</div>

</div>
</div>

<div class="toggle" onclick="toggleMode()">🌙</div>

<script>
const input = document.getElementById("fileInput");
const drop = document.getElementById("dropBox");
const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const uploadBtn = document.getElementById("uploadBtn");
const progress = document.querySelector(".progress");
const bar = document.getElementById("bar");
const error = document.getElementById("error");

drop.onclick = () => input.click();

input.onchange = () => handleFile(input.files[0]);

drop.ondrop = e => {
    e.preventDefault();
    handleFile(e.dataTransfer.files[0]);
};
drop.ondragover = e => e.preventDefault();

function handleFile(file){
    error.style.display = "none";

    if(file.size > 100 * 1024 * 1024){
        error.style.display = "block";
        return;
    }

    fileName.innerText = file.name;
    fileInfo.style.display = "flex";
    uploadBtn.style.display = "block";

    const dt = new DataTransfer();
    dt.items.add(file);
    input.files = dt.files;
}

function clearFile(){
    fileInfo.style.display = "none";
    uploadBtn.style.display = "none";
    input.value = "";
}

uploadBtn.onclick = () => {
    const formData = new FormData();
    formData.append("file", input.files[0]);

    progress.style.display = "block";

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/", true);

    xhr.upload.onprogress = e => {
        let percent = (e.loaded / e.total) * 100;
        bar.style.width = percent + "%";
    };

    xhr.onload = () => {
        window.location.href = xhr.responseURL;
    };

    xhr.send(formData);
};

function toggleMode(){
    document.body.classList.toggle("light");
}
</script>

</body>
</html>
'''

# ======================
# CLIP PAGE
# ======================
@app.route("/clip/<clip_id>")
def clip(clip_id):
    return f'''
<!DOCTYPE html>
<html>
<head>

<!-- DISCORD EMBED -->
<meta property="og:title" content="Escape Clip">
<meta property="og:type" content="video.other">
<meta property="og:url" content="{request.url}">
<meta property="og:video" content="{request.host_url}file/{clip_id}">
<meta property="og:video:type" content="video/mp4">

<style>
body {{
    margin:0;
    background:#000;
    color:white;
    font-family:Arial;
}}

.logo {{
    position:absolute;
    top:20px;
    left:30px;
    font-weight:800;
    font-size:22px;
}}
.logo span {{ color:#8b5cf6; }}

.wrapper {{
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
}}

.card {{
    background:#111;
    padding:25px;
    border-radius:18px;
    width:820px;
}}

.video-box {{
    width:100%;
    aspect-ratio:16/9;
    background:black;
}}

video {{
    width:100%;
    height:100%;
}}

.link-box {{
    margin-top:15px;
    display:flex;
    gap:10px;
}}

.link-box input {{
    flex:1;
    padding:10px;
    background:#222;
    border:none;
    color:white;
}}

.link-box button {{
    padding:10px;
    background:#7c3aed;
    border:none;
    color:white;
}}
</style>
</head>

<body>

<div class="logo">Escape<span>.</span></div>

<div class="wrapper">
<div class="card">

<div class="video-box">
<video controls autoplay>
    <source src="/file/{clip_id}">
</video>
</div>

<div class="link-box">
    <input value="{request.host_url}clip/{clip_id}" id="link" readonly>
    <button onclick="copyLink()">Copy</button>
</div>

</div>
</div>

<script>
function copyLink(){{
    navigator.clipboard.writeText(document.getElementById("link").value);
}}
</script>

</body>
</html>
'''

# ======================
# SERVE FILE
# ======================
@app.route("/file/<clip_id>")
def file(clip_id):
    for f in os.listdir(UPLOAD_FOLDER):
        if f.startswith(clip_id):
            return send_from_directory(UPLOAD_FOLDER, f)
    return "File not found"