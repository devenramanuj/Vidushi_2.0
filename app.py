import os
import logging
from flask import Flask, request, jsonify, render_template_string, send_from_directory

# લોગિંગ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# g4f સેટઅપ
g4f_available = False
try:
    import nest_asyncio
    nest_asyncio.apply()
    from g4f.client import Client
    client = Client()
    g4f_available = True
    logger.info("✅ g4f સફળતાપૂર્વક લોડ થયું")
except Exception as e:
    logger.error(f"❌ g4f લોડ ન થયું: {e}")

# વિડિઓ ફોલ્ડર ચેક કરો
VIDEO_FOLDER = 'video'  # તમારું ફોલ્ડર નામ 'video' છે
if not os.path.exists(VIDEO_FOLDER):
    os.makedirs(VIDEO_FOLDER)
    logger.info(f"📁 {VIDEO_FOLDER} ફોલ્ડર બનાવ્યું")

# વિડિઓ ફાઇલો ચેક કરો
video_files = ['silent.mp4', 'talking.mp4', 'thinking.mp4', 'smiling.mp4']
for video in video_files:
    video_path = os.path.join(VIDEO_FOLDER, video)
    if os.path.exists(video_path):
        logger.info(f"✅ {video} મળી")
    else:
        logger.warning(f"⚠️ {video} નથી")

# HTML પેજ (વિડિઓ સાથે)
HTML = """
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>વિદુષી ૨.૦</title>
    <style>
        body { 
            font-family: sans-serif; 
            background: #000; 
            margin: 0; 
            padding: 0; 
            display: flex; 
            flex-direction: column; 
            height: 100vh; 
            overflow: hidden; 
            color: white; 
        }
        
        .video-wrapper { 
            position: absolute; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%; 
            z-index: 1; 
        }
        
        #vidushi-video { 
            width: 100%; 
            height: 100%; 
            object-fit: cover; 
        }

        #chat-box { 
            position: absolute; 
            bottom: 140px; 
            left: 15px; 
            right: 15px; 
            max-height: 120px; 
            overflow-y: auto; 
            z-index: 10; 
            display: none;
            background: rgba(0,0,0,0.8); 
            border-radius: 12px; 
            padding: 10px;
            font-size: 14px; 
            border: 1px solid #e67e22;
        }

        .footer-bar { 
            position: absolute; 
            bottom: 0; 
            left: 0; 
            right: 0; 
            padding: 15px 20px; 
            padding-bottom: calc(15px + env(safe-area-inset-bottom));
            display: flex; 
            flex-direction: column; 
            gap: 12px; 
            z-index: 20;
            background: linear-gradient(to top, #000, transparent);
        }

        .controls { 
            display: flex; 
            justify-content: space-around; 
            align-items: center; 
            width: 100%; 
            gap: 10px; 
        }
        
        .small-btn { 
            background: #e67e22; 
            color: white; 
            border: none; 
            width: 45px; 
            height: 45px; 
            border-radius: 50%; 
            cursor: pointer; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-size: 20px;
        }

        #main-action-btn { 
            width: 65px; 
            height: 65px; 
            font-size: 30px; 
            background: #e67e22; 
            border: 3px solid white; 
        }

        .mode-switch { 
            display: flex; 
            align-items: center; 
            justify-content: center;
            gap: 12px; 
            background: rgba(255,255,255,0.2); 
            padding: 6px 16px; 
            border-radius: 25px; 
            align-self: center; 
            font-size: 13px; 
        }
        
        #text-input { 
            display: none; 
            flex: 1; 
            padding: 12px 18px; 
            border-radius: 25px; 
            border: none; 
            outline: none; 
            background: white; 
            color: #000; 
            font-size: 15px;
        }

        .credit-line { 
            text-align: center; 
            color: rgba(255,255,255,0.5); 
            font-size: 11px; 
            margin-top: 4px; 
        }
        
        #status-badge {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 30;
            background: rgba(0,0,0,0.7);
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            color: #4CAF50;
            border: 1px solid #4CAF50;
        }
    </style>
</head>
<body>
    <div id="status-badge">🟢 ઑનલાઇન</div>
    
    <div class="video-wrapper">
        <video id="vidushi-video" autoplay loop muted playsinline>
            <source src="/video/silent.mp4" type="video/mp4">
        </video>
    </div>

    <div id="chat-box"></div>

    <div class="footer-bar">
        <div class="mode-switch">
            <span>વોઈસ 🎤</span>
            <input type="checkbox" id="mode-toggle" onchange="toggleMode()">
            <span>ટેક્સ્ટ ⌨️</span>
        </div>

        <div class="controls">
            <label class="small-btn">📷
                <input type="file" accept="image/*" capture="environment" style="display:none" id="camera-input" onchange="handleImage(this)">
            </label>
            <input type="text" id="text-input" placeholder="પ્રશ્ન પૂછો...">
            <button id="main-action-btn" class="small-btn" onclick="triggerAI()">🎤</button>
            <label class="small-btn">📁
                <input type="file" accept="image/*" style="display:none" id="gallery-input" onchange="handleImage(this)">
            </label>
        </div>

        <div class="credit-line">Developed by Devendra Ramanuj | 9276505035</div>
    </div>

    <script>
        const video = document.getElementById('vidushi-video');
        const mainBtn = document.getElementById('main-action-btn');
        const textInput = document.getElementById('text-input');
        const chatBox = document.getElementById('chat-box');
        const modeToggle = document.getElementById('mode-toggle');
        const statusBadge = document.getElementById('status-badge');
        let currentImage = "";

        // વિડિઓ ચલાવો
        video.play().catch(e => console.log('વિડિઓ એરર:', e));

        function toggleMode() {
            if(modeToggle.checked) {
                mainBtn.innerText = "➔";
                textInput.style.display = "block";
                chatBox.style.display = "block";
                statusBadge.innerText = "🟢 ટેક્સ્ટ મોડ";
            } else {
                mainBtn.innerText = "🎤";
                textInput.style.display = "none";
                chatBox.style.display = "none";
                statusBadge.innerText = "🟢 વોઈસ મોડ";
            }
        }

        function triggerAI() {
            if(!modeToggle.checked) {
                startVoice();
            } else {
                const text = textInput.value.trim();
                if(text || currentImage) {
                    askAI(text);
                    textInput.value = "";
                }
            }
        }

        function setVideo(videoFile) {
            video.src = '/video/' + videoFile;
            video.load();
            video.play().catch(e => console.log('વિડિઓ ચેન્જ એરર:', e));
        }

        function handleImage(input) {
            if(input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    currentImage = e.target.result;
                    statusBadge.innerText = "🟢 ઇમેજ સિલેક્ટ થઈ";
                };
                reader.readAsDataURL(input.files[0]);
            }
        }

        function speakText(text) {
            if(modeToggle.checked) {
                chatBox.innerHTML = '<b>વિદુષી:</b> ' + text;
                setVideo('smiling.mp4');
                return;
            }

            const speech = new SpeechSynthesisUtterance(text);
            speech.lang = 'gu-IN';
            speech.onstart = () => setVideo('talking.mp4');
            speech.onend = () => setVideo('smiling.mp4');
            speech.onerror = () => setVideo('silent.mp4');
            window.speechSynthesis.speak(speech);
        }

        async function askAI(question) {
            setVideo('thinking.mp4');
            statusBadge.innerText = "🟡 વિચારી રહ્યું છે...";
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        question: question,
                        image: currentImage
                    })
                });
                
                const data = await response.json();
                speakText(data.answer);
                currentImage = "";
                statusBadge.innerText = "🟢 ઑનલાઇન";
                
            } catch(e) {
                console.error(e);
                setVideo('silent.mp4');
                statusBadge.innerText = "🔴 ભૂલ";
            }
        }

        function startVoice() {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'gu-IN';
            recognition.onresult = (e) => {
                const text = e.results[0][0].transcript;
                askAI(text);
            };
            recognition.start();
            statusBadge.innerText = "🟡 સાંભળી રહ્યું છે...";
        }

        textInput.addEventListener('keypress', (e) => {
            if(e.key === 'Enter') triggerAI();
        });

        // વિડિઓ એરર હેન્ડલિંગ
        video.addEventListener('error', () => {
            console.log('વિડિઓ લોડ ન થઈ, બેકગ્રાઉન્ડ બતાવીશું');
            document.querySelector('.video-wrapper').style.background = 'linear-gradient(135deg, #000, #1a1a1a)';
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/video/<path:filename>')
def serve_video(filename):
    """વિડિઓ ફાઇલો સર્વ કરો"""
    try:
        return send_from_directory('video', filename)
    except Exception as e:
        logger.error(f"વિડિઓ એરર: {e}")
        return "Video not found", 404

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"answer": "કૃપા કરીને કંઈક લખો"})
        
        if not g4f_available:
            return jsonify({"answer": f"હું વિદુષી છું. તમે પૂછ્યું: '{question}'"})
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "તમે વિદુષી છો - ગુજરાતી AI. હંમેશા ગુજરાતીમાં જવાબ આપો."},
                    {"role": "user", "content": question}
                ]
            )
            answer = response.choices[0].message.content
            return jsonify({"answer": answer})
        except:
            return jsonify({"answer": f"હું વિદુષી છું. તમે પૂછ્યું: '{question}'"})
            
    except Exception as e:
        return jsonify({"answer": "થોડીવાર પછી ફરી પ્રયત્ન કરો"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "g4f": g4f_available})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
