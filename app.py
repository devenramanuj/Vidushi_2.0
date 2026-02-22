import os
import requests
from flask import Flask, request, jsonify, render_template_string, send_from_directory

app = Flask(__name__)

# વીડિયો ફોલ્ડરનો પાથ - GitHub પર 'Videos' (V કેપિટલ) છે એટલે અહીં પણ તે જ રાખ્યું છે
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
        body { font-family: sans-serif; background: #000; margin: 0; color: white; height: 100vh; overflow: hidden; }
        .video-wrapper { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
        #vidushi-video { width: 100%; height: 100%; object-fit: cover; }
        .footer-bar { position: absolute; bottom: 0; width: 100%; padding: 20px; z-index: 10; background: linear-gradient(transparent, rgba(0,0,0,0.9)); text-align: center; }
        #text-input { width: 70%; padding: 12px; border-radius: 20px; border: none; margin-bottom: 10px; color: #000; }
        #send-btn { background: #e67e22; border: none; padding: 10px 20px; border-radius: 20px; color: white; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="video-wrapper">
        <video id="vidushi-video" loop muted playsinline>
            <source id="video-source" src="/Videos/silent.mp4" type="video/mp4">
        </video>
    </div>
    <div class="footer-bar">
        <input type="text" id="text-input" placeholder="અહીં તમારો પ્રશ્ન લખો...">
        <button id="send-btn" onclick="askAI()">મોકલો</button>
    </div>

    <script>
        const vPlayer = document.getElementById('vidushi-video');
        const vSource = document.getElementById('video-source');
        vPlayer.play();

        async function askAI() {
            const msg = document.getElementById('text-input').value;
            if(!msg) return;
            
            vSource.src = "/Videos/thinking.mp4"; vPlayer.load(); vPlayer.play();
            
            try {
                const res = await fetch('/get_response', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: msg })
                });
                const data = await res.json();
                
                // જવાબ આવતા જ વીડિયો બદલો
                vSource.src = "/Videos/talking.mp4"; vPlayer.load(); vPlayer.play();
                alert("વિદુષી: " + data.reply);
                
            } catch (e) { 
                alert("સર્વર સાથે કનેક્ટ થઈ શકતું નથી.");
                vSource.src = "/Videos/silent.mp4"; vPlayer.load(); vPlayer.play();
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
        
        # HuggingFace નું ફ્રી API વાપરીએ છીએ જે મજબૂત છે
        API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
        headers = {"Authorization": "Bearer hf_xxxx"} # અહીં ટોકન વગર પણ અમુક ટ્રાય ચાલે છે
        
        # સીધો જવાબ આપવા માટેનો જુગાડ
        prompt = f"તમારું નામ વિદુષી છે. આ પ્રશ્નનો ગુજરાતીમાં જવાબ આપો: {user_msg}"
        
        # અત્યારે ટેસ્ટિંગ માટે એક સાદો જવાબ મોકલીએ જો AI ન ચાલે તો
        return jsonify({'reply': f"મેં તમારો પ્રશ્ન '{user_msg}' સાંભળ્યો. હું તેના પર વિચાર કરી રહી છું."})

    except Exception as e:
        return jsonify({'reply': "ક્ષમા કરજો, અત્યારે સર્વર લોડ લઈ રહ્યું છે."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
