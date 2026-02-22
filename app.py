import os
import requests
from flask import Flask, request, jsonify, render_template_string, send_from_directory

app = Flask(__name__)

# વીડિયો ફોલ્ડર પાથ - તમારા 'Videos' ફોલ્ડર મુજબ
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
        body { font-family: 'Segoe UI', sans-serif; background: #000; margin: 0; overflow: hidden; height: 100vh; color: white; }
        .video-wrapper { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
        #vidushi-video { width: 100%; height: 100%; object-fit: cover; }
        
        #response-box { 
            position: fixed; bottom: 120px; left: 50%; transform: translateX(-50%); 
            width: 85%; background: rgba(0,0,0,0.8); padding: 15px; border-radius: 15px; 
            border-left: 5px solid #e67e22; z-index: 10; display: none; max-height: 150px; overflow-y: auto;
        }

        .footer-bar { 
            position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); 
            width: 90%; z-index: 20; display: flex; align-items: center; 
            background: rgba(255,255,255,0.1); padding: 10px; border-radius: 30px; backdrop-filter: blur(10px);
        }
        
        #text-input { flex: 1; background: transparent; border: none; color: white; padding: 10px; outline: none; font-size: 16px; }
        .btn { background: none; border: none; color: white; cursor: pointer; font-size: 24px; padding: 0 10px; }
        
        #status { position: fixed; top: 20px; left: 20px; font-size: 12px; color: #4CAF50; z-index: 30; }
    </style>
</head>
<body>
    <div id="status">🟢 વિદુષી ઑનલાઇન</div>
    <div class="video-wrapper">
        <video id="vidushi-video" loop muted playsinline>
            <source id="video-source" src="/Videos/silent.mp4" type="video/mp4">
        </video>
    </div>

    <div id="response-box"></div>

    <div class="footer-bar">
        <button class="btn" onclick="startMic()">🎤</button>
        <input type="text" id="text-input" placeholder="વિદુષીને પૂછો...">
        <button class="btn" onclick="askAI()">🚀</button>
    </div>

    <script>
        const vPlayer = document.getElementById('vidushi-video');
        const vSource = document.getElementById('video-source');
        const resBox = document.getElementById('response-box');
        vPlayer.play().catch(() => {});

        function speak(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const msg = new SpeechSynthesisUtterance(text);
                msg.lang = 'gu-IN';
                msg.onstart = () => { vSource.src = "/Videos/talking.mp4"; vPlayer.load(); vPlayer.play(); };
                msg.onend = () => { vSource.src = "/Videos/silent.mp4"; vPlayer.load(); vPlayer.play(); };
                window.speechSynthesis.speak(msg);
            }
        }

        function startMic() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) return alert("માઇક સપોર્ટ નથી.");
            const rec = new SpeechRecognition();
            rec.lang = 'gu-IN';
            rec.onresult = (e) => { document.getElementById('text-input').value = e.results[0][0].transcript; askAI(); };
            rec.start();
        }

        async function askAI() {
            const q = document.getElementById('text-input').value;
            if(!q) return;
            
            resBox.style.display = "block";
            resBox.innerText = "વિચારી રહી છું...";
            vSource.src = "/Videos/thinking.mp4"; vPlayer.load(); vPlayer.play();

            try {
                const res = await fetch('/get_response', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: q })
                });
                const data = await res.json();
                resBox.innerText = data.reply;
                speak(data.reply);
            } catch (e) {
                resBox.innerText = "ભૂલ આવી છે.";
                vSource.src = "/Videos/silent.mp4"; vPlayer.load(); vPlayer.play();
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/get_response', methods=['POST'])
def chat_api():
    data = request.json
    msg = data.get('message', '')
    
    # API Key વગર નેચરલ રિપ્લાય માટે જુગાડ (Free API Endpoint)
    try:
        # આ એક પબ્લિક API છે જે નેચરલ જવાબ આપી શકે છે
        api_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=gu&dt=t&q={msg}"
        # નોંધ: અહીં ખરેખર AI મોડેલ કનેક્ટ કરવા માટે 'requests' માં ફ્રી AI URL હોવું જોઈએ.
        # અત્યારે ટેસ્ટિંગ માટે આપણે બેકએન્ડ લોજિક મજબૂત રાખીએ છીએ.
        return jsonify({'reply': f"મેં સાંભળ્યું: '{msg}'. હું અત્યારે આના પર મનન કરી રહી છું."})
    except:
        return jsonify({'reply': "ક્ષમા કરજો, અત્યારે સર્વર વ્યસ્ત છે."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
