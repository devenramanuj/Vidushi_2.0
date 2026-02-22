import os
from flask import Flask, request, jsonify, render_template_string, send_from_directory

app = Flask(__name__)

# વીડિયો ફોલ્ડર સેટઅપ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_FOLDER = os.path.join(BASE_DIR, 'Videos')

@app.route('/Videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>વિદુષી ૨.૦</title>
    <style>
        body { font-family: sans-serif; background: #000; margin: 0; overflow: hidden; height: 100vh; color: white; }
        .video-wrapper { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
        #vidushi-video { width: 100%; height: 100%; object-fit: cover; }
        #user-cam { position: fixed; top: 20px; right: 20px; width: 90px; height: 120px; border: 2px solid #e67e22; border-radius: 12px; z-index: 100; object-fit: cover; background: #222; }
        .footer-ui { position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); width: 90%; z-index: 10; text-align: center; }
        #msg-box { background: rgba(0,0,0,0.85); padding: 15px; border-radius: 15px; margin-bottom: 15px; border-left: 5px solid #e67e22; display: none; font-size: 18px; color: #fff; }
        .input-bar { display: flex; background: rgba(255,255,255,0.15); padding: 8px; border-radius: 30px; backdrop-filter: blur(10px); align-items: center; }
        #text-input { flex: 1; background: transparent; border: none; color: white; padding: 10px; outline: none; font-size: 16px; }
        .btn { background: none; border: none; color: white; cursor: pointer; font-size: 22px; padding: 5px 10px; }
    </style>
</head>
<body>
    <video id="user-cam" autoplay playsinline muted></video>
    <div class="video-wrapper">
        <video id="vidushi-video" loop muted playsinline><source id="video-source" src="/Videos/silent.mp4" type="video/mp4"></video>
    </div>
    <div class="footer-ui">
        <div id="msg-box"></div>
        <div class="input-bar">
            <button class="btn" onclick="startMic()">🎤</button>
            <input type="text" id="text-input" placeholder="પ્રશ્ન પૂછો...">
            <button class="btn" onclick="askAI()">🚀</button>
        </div>
    </div>
    <script>
        const vPlayer = document.getElementById('vidushi-video');
        const vSource = document.getElementById('video-source');
        vPlayer.play().catch(() => {});

        async function initCam() {
            try { const s = await navigator.mediaDevices.getUserMedia({ video: true }); document.getElementById('user-cam').srcObject = s; } catch (e) {}
        }
        initCam();

        function startMic() {
            const r = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            r.lang = 'gu-IN'; r.start();
            r.onresult = (e) => { document.getElementById('text-input').value = e.results[0][0].transcript; askAI(); };
        }

        async function askAI() {
            const msg = document.getElementById('text-input').value;
            const box = document.getElementById('msg-box');
            if(!msg) return;
            vSource.src = "/Videos/thinking.mp4"; vPlayer.load(); vPlayer.play();
            box.style.display = "block"; box.innerText = "વિચારી રહી છું...";
            try {
                const res = await fetch('/get_response', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ message: msg }) });
                const data = await res.json();
                box.innerText = data.reply;
                vSource.src = "/Videos/talking.mp4"; vPlayer.load(); vPlayer.play();
            } catch (e) { box.innerText = "જોડાણમાં ભૂલ છે."; }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_PAGE)

@app.route('/get_response', methods=['POST'])
def chat_api():
    data = request.json
    msg = data.get('message', '')
    # ડાયરેક્ટ રિસ્પોન્સ જેથી ક્યારેય એરર ન આવે
    return jsonify({'reply': f"મેં તમારો પ્રશ્ન '{msg}' સાંભળ્યો. હું તમારી સહાય કરવા તૈયાર છું."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
