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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>વિદુષી ૨.૦</title>
    <style>
        body { font-family: sans-serif; background: #000; margin: 0; color: white; height: 100vh; overflow: hidden; display: flex; flex-direction: column; }
        .video-wrapper { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
        #vidushi-video { width: 100%; height: 100%; object-fit: cover; }
        
        /* કેમેરા પ્રીવ્યૂ */
        #user-cam { position: fixed; top: 15px; right: 15px; width: 110px; height: 150px; border: 2px solid #e67e22; border-radius: 12px; z-index: 100; object-fit: cover; background: #222; }
        
        .footer-bar { position: absolute; bottom: 0; width: 100%; padding: 20px; z-index: 10; background: linear-gradient(transparent, rgba(0,0,0,0.9)); text-align: center; box-sizing: border-box; }
        #text-input { width: 65%; padding: 12px; border-radius: 25px; border: none; margin-bottom: 10px; color: #000; outline: none; }
        .btn-box { display: flex; justify-content: center; gap: 10px; }
        #mic-btn { background: #3498db; border: none; padding: 10px 15px; border-radius: 50%; color: white; cursor: pointer; font-size: 20px; }
        #send-btn { background: #e67e22; border: none; padding: 10px 25px; border-radius: 20px; color: white; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <video id="user-cam" autoplay playsinline muted></video>

    <div class="video-wrapper">
        <video id="vidushi-video" loop muted playsinline>
            <source id="video-source" src="/Videos/silent.mp4" type="video/mp4">
        </video>
    </div>

    <div class="footer-bar">
        <input type="text" id="text-input" placeholder="બોલો અથવા લખો...">
        <div class="btn-box">
            <button id="mic-btn" onclick="startMic()">🎤</button>
            <button id="send-btn" onclick="askAI()">મોકલો</button>
        </div>
    </div>

    <script>
        const vPlayer = document.getElementById('vidushi-video');
        const vSource = document.getElementById('video-source');
        vPlayer.play().catch(() => {});

        // ૧. કેમેરા શરૂ કરો
        async function initCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                document.getElementById('user-cam').srcObject = stream;
            } catch (err) { console.log("Camera Error: ", err); }
        }
        initCamera();

        // ૨. માઇક શરૂ કરો (Voice to Text)
        function startMic() {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'gu-IN';
            recognition.start();
            recognition.onresult = (event) => {
                document.getElementById('text-input').value = event.results[0][0].transcript;
                askAI();
            };
        }

        // ૩. AI જવાબ મેળવો
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
                alert("વિદુષી: " + data.reply);
                vSource.src = "/Videos/talking.mp4"; vPlayer.load(); vPlayer.play();
            } catch (e) { 
                alert("સર્વર જોડાણમાં સમસ્યા છે.");
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
        msg = data.get('message', '')
        # કી વગરનો ટેમ્પરરી જવાબ (બાદમાં Gemini સેટ કરીશું)
        return jsonify({'reply': f"તમારો પ્રશ્ન '{msg}' મેં સાંભળ્યો છે. હું હજી વિકાસના તબક્કામાં છું."})
    except:
        return jsonify({'reply': "ક્ષમા કરજો, સર્વર વ્યસ્ત છે."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
