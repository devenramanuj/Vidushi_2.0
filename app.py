import os
import requests
from flask import Flask, request, jsonify, render_template_string, send_from_directory

app = Flask(__name__)

# GitHub પર ફોલ્ડરનું નામ 'Videos' (V કેપિટલ) છે
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>વિદુષી ૨.૦</title>
    <style>
        body { font-family: sans-serif; background: #000; margin: 0; color: white; height: 100vh; overflow: hidden; display: flex; flex-direction: column; }
        .video-wrapper { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
        #vidushi-video { width: 100%; height: 100%; object-fit: cover; }
        .footer-bar { position: absolute; bottom: 0; width: 100%; padding: 20px; z-index: 10; background: linear-gradient(transparent, rgba(0,0,0,0.9)); text-align: center; box-sizing: border-box; }
        #text-input { width: 75%; padding: 12px; border-radius: 25px; border: none; margin-bottom: 10px; color: #000; outline: none; }
        #send-btn { background: #e67e22; border: none; padding: 10px 25px; border-radius: 20px; color: white; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="video-wrapper">
        <video id="vidushi-video" loop muted playsinline>
            <source id="video-source" src="/Videos/silent.mp4" type="video/mp4">
        </video>
    </div>
    <div class="footer-bar">
        <input type="text" id="text-input" placeholder="પ્રશ્ન પૂછો...">
        <button id="send-btn" onclick="askAI()">મોકલો</button>
    </div>

    <script>
        const vPlayer = document.getElementById('vidushi-video');
        const vSource = document.getElementById('video-source');
        vPlayer.play().catch(() => {});

        async function askAI() {
            const msg = document.getElementById('text-input').value;
            if(!msg) return;
            
            vSource.src = "/Videos/thinking.mp4"; 
            vPlayer.load(); 
            vPlayer.play();
            
            try {
                const res = await fetch('/get_response', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: msg })
                });
                const data = await res.json();
                
                alert("વિદુષી: " + data.reply);
                vSource.src = "/Videos/talking.mp4";
                vPlayer.load();
                vPlayer.play();
            } catch (e) { 
                alert("સર્વર અત્યારે વ્યસ્ત છે.");
                vSource.src = "/Videos/silent.mp4";
                vPlayer.load();
                vPlayer.play();
            }
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
        user_msg = data.get('message', '')
        
        # પ્રોફેશનલ એપ માટે અત્યારે એક સ્ટેટિક જવાબ મોકલીએ છીએ 
        # કારણ કે Render પર ફ્રી AI લાઈબ્રેરીઓ વારંવાર બ્લોક થાય છે
        reply = f"મેં તમારો પ્રશ્ન '{user_msg}' સાંભળ્યો. હું અત્યારે અપડેટ થઈ રહી છું, ટૂંક સમયમાં તમને વિગતવાર જવાબ આપીશ."
        
        return jsonify({'reply': reply})
    except Exception:
        return jsonify({'reply': "ક્ષમા કરજો, અત્યારે સર્વર લોડ લઈ રહ્યું છે."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
