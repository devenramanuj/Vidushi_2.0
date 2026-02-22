import g4f
import nest_asyncio
import os
from flask import Flask, request, jsonify, render_template_string, send_from_directory

nest_asyncio.apply()
app = Flask(__name__)

@app.route('/Videos/<path:filename>')
def serve_Video(filename):
    return send_from_directory(os.getcwd(), filename)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>વિદુષી ૨.૦</title>
    <style>
        body { font-family: sans-serif; background: #000; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; color: white; }
        .video-wrapper { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
        #vidushi-video { width: 100%; height: 100%; object-fit: cover; }
        #chat-box { position: absolute; bottom: 140px; left: 15px; right: 15px; max-height: 120px; overflow-y: auto; z-index: 10; display: none; background: rgba(0,0,0,0.6); border-radius: 12px; padding: 10px; font-size: 14px; }
        .footer-bar { position: absolute; bottom: 0; left: 0; right: 0; padding: 15px 20px; padding-bottom: calc(15px + env(safe-area-inset-bottom)); display: flex; flex-direction: column; gap: 12px; z-index: 20; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); }
        .controls { display: flex; justify-content: space-around; align-items: center; width: 100%; gap: 10px; }
        .small-btn { background: rgba(211, 84, 0, 0.9); color: white; border: none; width: 45px; height: 45px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        #main-action-btn { width: 65px; height: 65px; font-size: 30px; background: #e67e22; border: 3px solid white; }
        .mode-switch { display: flex; align-items: center; gap: 12px; background: rgba(255,255,255,0.15); padding: 6px 16px; border-radius: 25px; align-self: center; font-size: 13px; }
        input[type="text"] { display: none; flex: 1; padding: 12px 18px; border-radius: 25px; border: none; background: rgba(255,255,255,0.95); color: #000; }
        .credit-line { text-align: center; color: rgba(255,255,255,0.5); font-size: 11px; }
    </style>
</head>
<body>
    <div class="video-wrapper"><video id="vidushi-video" loop muted playsinline><source id="video-source" src="/videos/silent.mp4" type="video/mp4"></video></div>
    <div id="chat-box"></div>
    <div class="footer-bar">
        <div class="mode-switch"><span>વોઈસ 🎤</span><input type="checkbox" id="mode-toggle" onchange="toggleMode()"><span>ટેક્સ્ટ ⌨️</span></div>
        <div class="controls">
            <label class="small-btn">📷<input type="file" accept="image/*" capture="environment" style="display:none" onchange="handleImg(this)"></label>
            <input type="text" id="text-input" placeholder="પ્રશ્ન પૂછો...">
            <button id="main-action-btn" class="small-btn" onclick="triggerAI()">🎤</button>
            <label class="small-btn">📁<input type="file" accept="image/*" style="display:none" onchange="handleImg(this)"></label>
        </div>
        <div class="credit-line">Developed by Devendra Ramanuj | 9276505035</div>
    </div>
    <script>
        const vPlayer = document.getElementById('vidushi-video');
        const vSource = document.getElementById('video-source');
        const mainBtn = document.getElementById('main-action-btn');
        const textInp = document.getElementById('text-input');
        const chatBox = document.getElementById('chat-box');
        const modeToggle = document.getElementById('mode-toggle');
        let base64Img = "";

        vPlayer.play();

        function toggleMode() {
            if(modeToggle.checked) { mainBtn.innerText = "➔"; textInp.style.display = "block"; chatBox.style.display = "block"; }
            else { mainBtn.innerText = "🎤"; textInp.style.display = "none"; chatBox.style.display = "none"; window.speechSynthesis.cancel(); }
        }

        function triggerAI() {
            if(!modeToggle.checked) { startMic(); }
            else { askAI(textInp.value); textInp.value = ""; }
        }

        function handleImg(input) {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const img = new Image();
                    img.onload = () => {
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        const scale = 800 / Math.max(img.width, img.height);
                        canvas.width = img.width * scale;
                        canvas.height = img.height * scale;
                        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                        base64Img = canvas.toDataURL('image/jpeg', 0.7);
                        askAI("");
                    };
                    img.src = e.target.result;
                };
                reader.readAsDataURL(input.files[0]);
            }
        }

        async function askAI(uText) {
            vSource.src = "/videos/thinking.mp4"; vPlayer.load(); vPlayer.play();
            try {
                const res = await fetch('/get_response', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: uText, image: base64Img })
                });
                const data = await res.json();
                speakText(data.reply);
                base64Img = "";
            } catch (e) { vSource.src = "/videos/silent.mp4"; vPlayer.load(); vPlayer.play(); }
        }

        function speakText(text) {
            let cleanText = text.replace(/[*;:"']/g, ' '); 
            if(modeToggle.checked) { chatBox.innerHTML = `<div>${text}</div>`; return; }
            const msg = new SpeechSynthesisUtterance(cleanText);
            msg.lang = (/[અ-હ]/.test(text)) ? 'gu-IN' : 'en-IN';
            msg.onstart = () => { vSource.src = "/videos/talking.mp4"; vPlayer.load(); vPlayer.play(); };
            msg.onend = () => { vSource.src = "/videos/smiling.mp4"; vPlayer.load(); vPlayer.play(); };
            window.speechSynthesis.speak(msg);
        }

        function startMic() {
            const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            rec.lang = 'gu-IN';
            rec.onresult = (e) => { askAI(e.results[0][0].transcript); };
            rec.start();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_PAGE)

@app.route('/get_response', methods=['POST'])
def chat_api():
    try:
        data = request.json
        msg, img = data.get('message', ''), data.get('image', '')
        system_p = "તમારું નામ વિદુષી છે, દેવેન્દ્રભાઈ રામાનુજ દ્વારા બનાવેલ AI. ગુજરાતીમાં જવાબ આપો."
        if img:
            response = g4f.ChatCompletion.create(model=g4f.models.default, messages=[{"role": "user", "content": [{"type": "text", "text": f"{system_p} {msg}"}, {"type": "image_url", "image_url": {"url": img}}]}])
        else:
            response = g4f.ChatCompletion.create(model=g4f.models.default, messages=[{"role": "system", "content": system_p}, {"role": "user", "content": msg}])
        return jsonify({'reply': response})
    except Exception: return jsonify({'reply': "Error."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
