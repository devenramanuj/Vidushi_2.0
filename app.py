import g4f
import os
from flask import Flask, request, jsonify, render_template_string, send_from_directory

app = Flask(__name__)

# વીડિયો ફોલ્ડરનો પાથ (GitHub પર Videos નામ છે એટલે V કેપિટલ રાખ્યું છે)
VIDEO_FOLDER = os.path.join(os.getcwd(), 'Videos')

@app.route('/Videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)

# HTML માં પણ પાથ સુધારેલા છે
HTML_PAGE = """
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>વિદુષી ૨.૦</title>
    <style>
        body { font-family: sans-serif; background: #000; margin: 0; color: white; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
        .video-wrapper { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
        #vidushi-video { width: 100%; height: 100%; object-fit: cover; }
        .footer-bar { position: absolute; bottom: 0; width: 100%; padding: 20px; z-index: 10; background: linear-gradient(transparent, rgba(0,0,0,0.8)); display: flex; flex-direction: column; align-items: center; }
        #text-input { width: 80%; padding: 12px; border-radius: 25px; border: none; margin-bottom: 10px; }
        #main-btn { background: #e67e22; border: none; padding: 10px 25px; border-radius: 20px; color: white; font-weight: bold; }
    </style>
</head>
<body>
    <div class="video-wrapper">
        <video id="vidushi-video" loop muted playsinline>
            <source id="video-source" src="/Videos/silent.mp4" type="video/mp4">
        </video>
    </div>
    <div class="footer-bar">
        <input type="text" id="text-input" placeholder="અહીં લખો...">
        <button id="main-btn" onclick="askAI()">મોકલો</button>
        <p style="font-size: 10px; margin-top: 10px;">Developed by Devendra Ramanuj</p>
    </div>

    <script>
        const vPlayer = document.getElementById('vidushi-video');
        const vSource = document.getElementById('video-source');
        vPlayer.play();

        async function askAI() {
            const msg = document.getElementById('text-input').value;
            vSource.src = "/Videos/thinking.mp4"; vPlayer.load(); vPlayer.play();
            try {
                const res = await fetch('/get_response', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: msg })
                });
                const data = await res.json();
                alert(data.reply); // ચેક કરવા માટે એલર્ટ
                vSource.src = "/Videos/talking.mp4"; vPlayer.load(); vPlayer.play();
            } catch (e) { alert("Error connecting to server"); }
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
        msg = data.get('message', 'નમસ્તે')
        # g4f માં પ્રોવાઈડર ફોર્સ કરવો જેથી એરર ન આવે
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            provider=g4f.Provider.GigaChat, # અથવા અન્ય વર્કિંગ પ્રોવાઈડર
            messages=[{"role": "user", "content": msg}]
        )
        return jsonify({'reply': response})
    except Exception as e:
        return jsonify({'reply': f"Error: {str(e)}"})

if __name__ == '__main__':
    # Render માટે પોર્ટ સેટિંગ
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
