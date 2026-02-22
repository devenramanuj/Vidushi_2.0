import g4f
import nest_asyncio
import os
from flask import Flask, request, jsonify, render_template_string, send_from_directory

nest_asyncio.apply()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

@app.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(os.getcwd(), filename)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>વિદુષી ૨.૦</title>
    <style>
        body { font-family: sans-serif; background: #000; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; color: white; }
        
        /* ફુલ સ્ક્રીન વિડિયો */
        .video-wrapper { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
        #vidushi-video { width: 100%; height: 100%; object-fit: cover; }

        /* ચેટ ડિસ્પ્લે (ટેક્સ્ટ મોડ માટે) */
        #chat-box { 
            position: absolute; bottom: 140px; left: 15px; right: 15px; 
            max-height: 120px; overflow-y: auto; z-index: 10; display: none;
            background: rgba(0,0,0,0.6); border-radius: 12px; padding: 10px;
            font-size: 14px; border: 1px solid rgba(255,255,255,0.1);
        }

        /* મોબાઈલ ફ્રેન્ડલી ફૂટર - બટન્સ નીચે પણ સુરક્ષિત */
        .footer-bar { 
            position: absolute; bottom: 0; left: 0; right: 0; 
            padding: 15px 20px; padding-bottom: calc(15px + env(safe-area-inset-bottom));
            display: flex; flex-direction: column; gap: 12px; z-index: 20;
            background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
        }

        .controls { display: flex; justify-content: space-around; align-items: center; width: 100%; gap: 10px; }
        
        .small-btn { 
            background: rgba(211, 84, 0, 0.9); color: white; border: none; 
            width: 45px; height: 45px; border-radius: 50%; cursor: pointer; 
            display: flex; align-items: center; justify-content: center; font-size: 20px;
        }

        #main-action-btn { width: 65px; height: 65px; font-size: 30px; background: #e67e22; border: 3px solid white; box-shadow: 0 0 20px rgba(230, 126, 34, 0.6); }

        /* મોડ સ્વિચ */
        .mode-switch { display: flex; align-items: center; gap: 12px; background: rgba(255,255,255,0.15); padding: 6px 16px; border-radius: 25px; align-self: center; font-size: 13px; border: 1px solid rgba(255,255,255,0.1); }
        
        input[type="text"] { 
            display: none; flex: 1; padding: 12px 18px; border-radius: 25px; 
            border: none; outline: none; background: rgba(255,255,255,0.95); color: #000; font-size: 15px;
        }

        .credit-line { text-align: center; color: rgba(255,255,255,0.5); font-size: 11px; margin-top: 4px; letter-spacing: 0.5px; }
    </style>
</head>
<body>
    <div class="video-wrapper">
        <video id="vidushi-video" loop muted playsinline>
            <source id="video-source" src="/videos/silent.mp4" type="video/mp4">
        </video>
    </div>

    <div id="chat-box"></div>

    <div class="footer-bar">
        <div class="mode-switch">
            <span>વોઈસ 🎤</span>
            <input type="checkbox" id="mode-toggle" onchange="toggleMode()" style="transform: scale(1.2);">
            <span>ટેક્સ્ટ ⌨️</span>
        </div>

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
            if(modeToggle.checked) {
                mainBtn.innerText = "➔";
                textInp.style.display = "block";
                chatBox.style.display = "block";
            } else {
                mainBtn.innerText = "🎤";
                textInp.style.display = "none";
                chatBox.style.display = "none";
                window.speechSynthesis.cancel();
            }
        }

        function triggerAI() {
            if(!modeToggle.checked) { startMic(); }
            else { 
                const val = textInp.value.trim();
                if(val || base64Img) { askAI(val); textInp.value = ""; }
            }
        }

        function setVideo(file) {
            vSource.src = "/videos/" + file;
            vPlayer.load();
            vPlayer.play();
        }

        function handleImg(input) {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => { base64Img = e.target.result; askAI(""); };
                reader.readAsDataURL(input.files[0]);
            }
        }

        function speakText(text) {
            // વાણી શુદ્ધિ: વધારાના ચિન્હો ફિલ્ટર કરવા
            let cleanText = text.replace(/[*;:"']/g, ' '); 
            
            if(modeToggle.checked) {
                chatBox.innerHTML = `<div><b>વિદુષી:</b> ${text}</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
                setVideo("smiling.mp4");
                return;
            }

            const msg = new SpeechSynthesisUtterance(cleanText);
            
            // ઓટો લેંગ્વેજ ડિટેક્શન
            if (/[અ-હ]/.test(text)) { msg.lang = 'gu-IN'; }
            else if (/[अ-ह]/.test(text)) { msg.lang = 'hi-IN'; }
            else { msg.lang = 'en-IN'; }

            msg.onstart = () => setVideo("talking.mp4");
            msg.onend = () => setVideo("smiling.mp4");
            window.speechSynthesis.speak(msg);
        }

        async function askAI(uText) {
            setVideo("thinking.mp4");
            try {
                const res = await fetch('/get_response', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: uText, image: base64Img })
                });
                const data = await res.json();
                speakText(data.reply);
                base64Img = "";
            } catch (e) { setVideo("silent.mp4"); }
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
        # મલ્ટીલિંગ્યુઅલ અને પર્સનલાઈઝ્ડ પ્રોમ્પ્ટ
        system_p = "તમારું નામ વિદુષી છે અને તમે દેવેન્દ્રભાઈ રામાનુજ દ્વારા બનાવાયેલ એઆઈ છો. તમારી મુખ્ય ભાષા ગુજરાતી છે. જો કોઈ બીજી ભાષામાં પૂછે તો તે જ ભાષામાં જવાબ આપો, પણ વિવેક ગુજરાતી મર્યાદા મુજબ રાખો. તમારી ઓળખ વિદુષી તરીકે જ આપો."
        
        if img:
            response = g4f.ChatCompletion.create(model=g4f.models.default, messages=[{"role": "user", "content": [{"type": "text", "text": f"{system_p} {msg}"}, {"type": "image_url", "image_url": {"url": img}}]}])
        else:
            response = g4f.ChatCompletion.create(model=g4f.models.default, messages=[{"role": "system", "content": system_p}, {"role": "user", "content": msg}])
        return jsonify({'reply': response})
    except Exception: return jsonify({'reply': "ક્ષમા કરશો, ફરી પ્રયત્ન કરો."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
