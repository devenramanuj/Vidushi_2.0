import os
import sys
import logging
from flask import Flask, request, jsonify, render_template_string, send_from_directory

# લોગિંગ સેટઅપ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# g4f ઇમ્પોર્ટ ટ્રાય કરો
try:
    import nest_asyncio
    nest_asyncio.apply()
    import g4f
    g4f_available = True
    print("✓ g4f સફળતાપૂર્વક લોડ થયું")
except Exception as e:
    g4f_available = False
    print(f"✗ g4f લોડ ન થયું: {e}")

HTML_PAGE = """
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>વિદુષી ૨.૦</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: #000; 
            color: white; 
            height: 100vh; 
            overflow: hidden; 
            position: relative;
        }
        
        .video-container {
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
            background: rgba(0,0,0,0.7);
            border-radius: 15px;
            padding: 12px;
            font-size: 14px;
            border: 1px solid #e67e22;
            backdrop-filter: blur(5px);
        }

        .footer-bar {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 20px;
            padding-bottom: max(20px, env(safe-area-inset-bottom));
            background: linear-gradient(to top, #000, transparent);
            z-index: 20;
        }

        .mode-switch {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 15px;
        }

        .mode-switch span {
            font-size: 14px;
            color: #fff;
            opacity: 0.8;
        }

        .mode-switch input[type="checkbox"] {
            width: 50px;
            height: 24px;
            appearance: none;
            background: #333;
            border-radius: 12px;
            position: relative;
            cursor: pointer;
        }

        .mode-switch input[type="checkbox"]:checked {
            background: #e67e22;
        }

        .mode-switch input[type="checkbox"]::before {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            background: white;
            border-radius: 50%;
            top: 2px;
            left: 2px;
            transition: 0.3s;
        }

        .mode-switch input[type="checkbox"]:checked::before {
            left: 28px;
        }

        .controls {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 10px;
        }

        .small-btn {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: rgba(230, 126, 34, 0.9);
            border: 2px solid white;
            color: white;
            font-size: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(230, 126, 34, 0.4);
        }

        #main-action-btn {
            width: 70px;
            height: 70px;
            font-size: 32px;
            background: #e67e22;
            border-width: 3px;
        }

        #text-input {
            flex: 1;
            height: 45px;
            border-radius: 25px;
            border: none;
            padding: 0 20px;
            font-size: 16px;
            display: none;
            background: rgba(255,255,255,0.95);
        }

        #text-input:focus {
            outline: 2px solid #e67e22;
        }

        .credit-line {
            text-align: center;
            color: rgba(255,255,255,0.5);
            font-size: 11px;
            margin-top: 10px;
        }

        .status-badge {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 30;
            background: rgba(0,0,0,0.6);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            border: 1px solid #e67e22;
            color: #e67e22;
        }
    </style>
</head>
<body>
    <div class="status-badge" id="status-badge">🟢 ઑનલાઇન</div>

    <div class="video-container">
        <video id="vidushi-video" autoplay loop muted playsinline>
            <source src="/videos/silent.mp4" type="video/mp4">
        </video>
    </div>

    <div id="chat-box"></div>

    <div class="footer-bar">
        <div class="mode-switch">
            <span>વૉઇસ</span>
            <input type="checkbox" id="modeToggle">
            <span>ટેક્સ્ટ</span>
        </div>

        <div class="controls">
            <label class="small-btn">
                📷
                <input type="file" accept="image/*" capture="environment" style="display:none" id="cameraInput">
            </label>
            
            <input type="text" id="textInput" placeholder="તમારો પ્રશ્ન લખો...">
            
            <button class="small-btn" id="mainActionBtn" onclick="handleMainAction()">🎤</button>
            
            <label class="small-btn">
                📁
                <input type="file" accept="image/*" style="display:none" id="galleryInput">
            </label>
        </div>

        <div class="credit-line">Developed by Devendra Ramanuj | 9276505035</div>
    </div>

    <script>
        const video = document.getElementById('vidushi-video');
        const chatBox = document.getElementById('chat-box');
        const textInput = document.getElementById('textInput');
        const modeToggle = document.getElementById('modeToggle');
        const mainActionBtn = document.getElementById('mainActionBtn');
        const statusBadge = document.getElementById('status-badge');
        
        let currentImage = null;
        let isTextMode = false;

        // મોડ ટોગલ
        modeToggle.addEventListener('change', function(e) {
            isTextMode = e.target.checked;
            if(isTextMode) {
                mainActionBtn.textContent = '➔';
                textInput.style.display = 'block';
                chatBox.style.display = 'block';
                statusBadge.textContent = '🟢 ટેક્સ્ટ મોડ';
            } else {
                mainActionBtn.textContent = '🎤';
                textInput.style.display = 'none';
                chatBox.style.display = 'none';
                statusBadge.textContent = '🟢 વૉઇસ મોડ';
                window.speechSynthesis?.cancel();
            }
        });

        // કૅમેરા ઇનપુટ
        document.getElementById('cameraInput').addEventListener('change', handleImageSelect);
        document.getElementById('galleryInput').addEventListener('change', handleImageSelect);

        function handleImageSelect(e) {
            const file = e.target.files[0];
            if(file) {
                const reader = new FileReader();
                reader.onload = function(ev) {
                    currentImage = ev.target.result;
                    statusBadge.textContent = '🟢 ઇમેજ સિલેક્ટ થઈ';
                    if(isTextMode && textInput.value.trim()) {
                        askAI(textInput.value);
                    } else if(!isTextMode) {
                        askAI('');
                    }
                };
                reader.readAsDataURL(file);
            }
        }

        // મુખ્ય એક્શન
        function handleMainAction() {
            if(isTextMode) {
                const text = textInput.value.trim();
                if(text || currentImage) {
                    askAI(text);
                    textInput.value = '';
                }
            } else {
                startVoiceRecognition();
            }
        }

        // વૉઇસ રેકગ્નિશન
        function startVoiceRecognition() {
            if(!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                alert('તમારું બ્રાઉઝર વૉઇસ રેકગ્નિશન સપોર્ટ કરતું નથી');
                return;
            }

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.lang = 'gu-IN';
            recognition.continuous = false;
            recognition.interimResults = false;
            
            statusBadge.textContent = '🟡 સાંભળી રહ્યું છે...';
            video.src = '/videos/thinking.mp4';
            video.play();
            
            recognition.onresult = function(event) {
                const text = event.results[0][0].transcript;
                askAI(text);
            };
            
            recognition.onerror = function() {
                statusBadge.textContent = '🔴 ભૂલ';
                video.src = '/videos/silent.mp4';
                video.play();
            };
            
            recognition.start();
        }

        // AI ને પૂછો
        async function askAI(question) {
            statusBadge.textContent = '🟡 વિચારી રહ્યું છે...';
            video.src = '/videos/thinking.mp4';
            video.play();
            
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
                currentImage = null;
                
                if(isTextMode) {
                    chatBox.innerHTML = `<div style="color:#e67e22; margin-bottom:5px;">વિદુષી:</div><div>${data.answer}</div>`;
                    chatBox.scrollTop = chatBox.scrollHeight;
                    video.src = '/videos/smiling.mp4';
                    video.play();
                    statusBadge.textContent = '🟢 ટેક્સ્ટ મોડ';
                } else {
                    speakText(data.answer);
                }
                
            } catch(error) {
                console.error('Error:', error);
                statusBadge.textContent = '🔴 ભૂલ';
                video.src = '/videos/silent.mp4';
                video.play();
            }
        }

        // ટેક્સ્ટ બોલો
        function speakText(text) {
            if(!window.speechSynthesis) {
                alert('તમારું બ્રાઉઝર સ્પીચ સિન્થેસિસ સપોર્ટ કરતું નથી');
                return;
            }

            window.speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            
            if(/[અ-હ]/.test(text)) {
                utterance.lang = 'gu-IN';
            } else if(/[अ-ह]/.test(text)) {
                utterance.lang = 'hi-IN';
            } else {
                utterance.lang = 'en-IN';
            }
            
            utterance.onstart = () => {
                video.src = '/videos/talking.mp4';
                video.play();
                statusBadge.textContent = '🟡 બોલી રહ્યું છે...';
            };
            
            utterance.onend = () => {
                video.src = '/videos/smiling.mp4';
                video.play();
                statusBadge.textContent = '🟢 વૉઇસ મોડ';
            };
            
            utterance.onerror = () => {
                video.src = '/videos/silent.mp4';
                video.play();
                statusBadge.textContent = '🟢 વૉઇસ મોડ';
            };
            
            window.speechSynthesis.speak(utterance);
        }

        // એન્ટર કી
        textInput.addEventListener('keypress', function(e) {
            if(e.key === 'Enter') {
                handleMainAction();
            }
        });

        // વિડિઓ પ્રીલોડ
        video.addEventListener('loadeddata', function() {
            video.play();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        question = data.get('question', '')
        image = data.get('image', '')
        
        logger.info(f"પ્રશ્ન: {question[:50]}...")
        
        if not g4f_available:
            answer = f"વિદુષી અહીં છે. તમે પૂછ્યું: '{question or 'નમસ્તે'}'"
        else:
            try:
                system_msg = "તમે વિદુષી છો - દેવેન્દ્ર રામાનુજ દ્વારા બનાવેલ ગુજરાતી AI. ગુજરાતીમાં જવાબ આપો."
                
                if image:
                    response = g4f.ChatCompletion.create(
                        model=g4f.models.default,
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"{system_msg} {question}"},
                                {"type": "image_url", "image_url": {"url": image}}
                            ]
                        }]
                    )
                else:
                    response = g4f.ChatCompletion.create(
                        model=g4f.models.default,
                        messages=[
                            {"role": "system", "content": system_msg},
                            {"role": "user", "content": question or "હેલો, તમે કેવી છો?"}
                        ]
                    )
                
                answer = str(response)
                
            except Exception as e:
                logger.error(f"g4f error: {e}")
                answer = "ક્ષમા કરશો, હમણાં જવાબ નથી આપી શકતી. ફરી પ્રયત્ન કરો."
        
        return jsonify({'answer': answer})
        
    except Exception as e:
        logger.error(f"Error in ask: {e}")
        return jsonify({'answer': "ક્ષમા કરશો, કંઈક ભૂલ થઈ છે."})

@app.route('/videos/<path:filename>')
def serve_video(filename):
    try:
        return send_from_directory('videos', filename)
    except:
        return "Video not found", 404

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'g4f': g4f_available,
        'mode': 'production'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
