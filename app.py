import g4f
import os
from flask import Flask, request, jsonify, render_template_string, send_from_directory

app = Flask(__name__)

# GitHub પર ફોલ્ડરનું નામ 'Videos' છે (V કેપિટલ)
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
        #send-btn { background: #e67e22; border: none; padding: 10px 20px; border-radius: 20px; color: white; cursor: pointer; font-weight: bold; }
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
                
                // જો સર્વર પરથી એરર આવે તો તે બતાવો
                if(data.reply.includes("Error")) {
                    alert("માફ કરજો, અત્યારે સર્વર વ્યસ્ત છે.");
                } else {
                    alert("વિદુષીનો જવાબ: " + data.reply); 
                }
                
                vSource.src = "/Videos/talking.mp4"; vPlayer.load(); vPlayer.play();
            } catch (e) { alert("કનેક્શનમાં ભૂલ છે."); }
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
        msg = data.get('message', '')
        
        # પ્રોવાઈડર ફિક્સ કરી દઈએ જેથી API Key ન માંગે
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            provider=g4f.Provider.Blackbox, # Blackbox સામાન્ય રીતે કી વગર ચાલે છે
            messages=[{"role": "user", "content": "જવાબ ગુજરાતીમાં આપો: " + msg}],
        )
        return jsonify({'reply': response})
    except Exception as e:
        # જો હજુ પણ એરર આવે તો સાદો જવાબ મોકલો જેથી એપ બંધ ન થાય
        return jsonify({'reply': "હું હજી શીખી રહી છું, થોડી વાર પછી ફરી પૂછશો?"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
