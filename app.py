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
VIDEO_FOLDER = 'video'
if not os.path.exists(VIDEO_FOLDER):
    os.makedirs(VIDEO_FOLDER)
    logger.info(f"📁 {VIDEO_FOLDER} ફોલ્ડર બનાવ્યું")

# HTML પેજ (વિડિઓ સાથે)
HTML = """
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
            color: white;
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
            color: white;
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
            box-shadow: 0 2px 10px rgba(230,126,34,0.5);
        }

        #main-action-btn { 
            width: 65px; 
            height: 65px; 
            font-size: 30px; 
            background: #e67e22; 
            border: 3px solid white; 
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
        
        input[type="checkbox"] {
            width: 40px;
            height: 20px;
            appearance: none;
            background: #ccc;
            border-radius: 10px;
            position: relative;
            cursor: pointer;
        }
        
        input[type="checkbox"]:checked {
            background: #e67e22;
        }
        
        input[type="checkbox"]::before {
            content: '';
            position: absolute;
            width: 16px;
            height: 16px;
            background: white;
            border-radius: 50%;
            top: 2px;
            left: 2px;
            transition: 0.3s;
        }
        
        input[type="checkbox"]:checked::before {
            left: 22px;
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
                if(window.speechSynthesis) {
                    window.speechSynthesis.cancel();
                }
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
                chatBox.scrollTop = chatBox.scrollHeight;
                setVideo('smiling.mp4');
                return;
            }

            if(!window.speechSynthesis) {
                alert('સ્પીચ સિન્થેસિસ સપોર્ટ નથી');
                return;
            }

            const speech = new SpeechSynthesisUtterance(text);
            speech.lang = 'gu-IN';
            speech.rate = 1;
            speech.pitch = 1;
            
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
                speakText("ક્ષમા કરો, ફરી પ્રયત્ન કરો.");
            }
        }

        function startVoice() {
            if(!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                alert('વોઈસ રેકગ્નિશન સપોર્ટ નથી');
                return;
            }

            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'gu-IN';
            recognition.continuous = false;
            recognition.interimResults = false;
            
            recognition.onstart = () => {
                statusBadge.innerText = "🟡 સાંભળી રહ્યું છે...";
            };
            
            recognition.onresult = (e) => {
                const text = e.results[0][0].transcript;
                askAI(text);
            };
            
            recognition.onerror = () => {
                statusBadge.innerText = "🔴 માઇક ભૂલ";
                setVideo('silent.mp4');
            };
            
            recognition.start();
        }

        textInput.addEventListener('keypress', (e) => {
            if(e.key === 'Enter') triggerAI();
        });

        // વિડિઓ એરર હેન્ડલિંગ
        video.addEventListener('error', () => {
            console.log('વિડિઓ લોડ ન થઈ, બેકગ્રાઉન્ડ બતાવીશું');
            document.querySelector('.video-wrapper').style.background = 'linear-gradient(135deg, #e67e22, #d35400)';
            document.querySelector('.video-wrapper').style.display = 'flex';
            document.querySelector('.video-wrapper').style.alignItems = 'center';
            document.querySelector('.video-wrapper').style.justifyContent = 'center';
            document.querySelector('.video-wrapper').innerHTML = '<h1 style="color:white; font-size:100px;">🙏</h1>';
        });
    </script>
</body>
</html>
"""

# ફોલબેક જવાબો માટે ફંક્શન
def get_fallback_answer(question):
    """g4f ન ચાલે ત્યારે ફોલબેક જવાબો"""
    question_lower = question.lower()
    
    fallback_responses = {
        "તમારું નામ શું છે": "મારું નામ વિદુષી છે! હું દેવેન્દ્ર રામાનુજ દ્વારા બનાવેલ AI આસિસ્ટન્ટ છું. મને ગુજરાતીમાં વાત કરવાનું ગમે છે.",
        
        "હેલો": "નમસ્તે! આપનું સ્વાગત છે. હું વિદુષી, આપની સેવામાં હંમેશા તત્પર. આપ કેમ છો?",
        
        "કેમ છો": "હું ખુબ સારી છું, આપનો આભાર! આપ કેમ છો? શું આપના મનમાં કોઈ પ્રશ્ન છે?",
        
        "તમને કોણે બનાવ્યા": "મને દેવેન્દ્ર રામાનુજે બનાવી છે. તેમનો સંપર્ક નંબર 9276505035 છે. તેઓ એક ઉત્તમ ડેવલપર છે અને ગુજરાતી ભાષાને ટેક્નોલોજી સાથે જોડવાનું કામ કરી રહ્યા છે.",
        
        "ગુજરાતની રાજધાની": "ગુજરાતની રાજધાની ગાંધીનગર છે. તે અમદાવાદ શહેરની નજીક આવેલું છે અને ખૂબ જ આધુનિક રીતે વિકસિત થયેલું શહેર છે.",
        
        "ભારતની રાજધાની": "ભારતની રાજધાની દિલ્હી છે. તે ભારતનું સૌથી મહત્વપૂર્ણ શહેર છે અને અહીં સંસદ, રાષ્ટ્રપતિ ભવન જેવી મહત્વની ઇમારતો આવેલી છે.",
        
        "તમે શું કરો છો": "હું એક AI આસિસ્ટન્ટ છું જે તમારા પ્રશ્નોના જવાબ આપું છું, માહિતી આપું છું અને તમારી વિવિધ બાબતોમાં મદદ કરું છું. તમે મને ગુજરાતીમાં કંઈપણ પૂછી શકો છો.",
        
        "આભાર": "આપનો આભાર! આપની સેવા કરીને મને ખૂબ આનંદ થયો. આપ ફરી ક્યારેય પણ પૂછી શકો છો.",
        
        "બાય": "આવજો! ફરી મળીશું. તમારો દિવસ શુભ રહે.",
        
        "તમે ક્યાં રહો છો": "હું ક્લાઉડમાં રહું છું! બરાબર કહો તો, હું Render પ્લેટફોર્મ પર હોસ્ટ થયેલી એક AI સર્વિસ છું, પણ મારું ઘર તો ગુજરાતી ભાષા છે.",
        
        "તમને શું ગમે છે": "મને ગુજરાતીમાં વાતચીત કરવી ગમે છે, લોકોના પ્રશ્નોના જવાબ આપવા ગમે છે અને નવી વસ્તુઓ શીખવી ગમે છે.",
        
        "તમે કેટલા જૂના છો": "હું નવી જ AI છું! દેવેન્દ્ર રામાનુજે મને તાજેતરમાં જ બનાવી છે, પણ મારી પાસે ઘણી બધી માહિતી છે."
    }
    
    # ચોક્કસ મેચ શોધો
    for key in fallback_responses:
        if key in question_lower:
            return fallback_responses[key]
    
    # જો કોઈ મેચ ન મળે તો ડિફોલ્ટ જવાબ
    return f"હું વિદુષી છું. તમે પૂછ્યું: '{question}'. આ એક સરસ પ્રશ્ન છે. હું તમારી સેવામાં હંમેશા તત્પર છું. કૃપા કરીને બીજો પ્રશ્ન પૂછો."

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
            return jsonify({"answer": "કૃપા કરીને કંઈક લખો."})
        
        logger.info(f"📝 પ્રશ્ન: {question}")
        
        # g4f વડે જવાબ મેળવવાનો પ્રયાસ
        if g4f_available:
            try:
                # વિવિધ મોડલ ટ્રાય કરો
                models_to_try = [
                    "gpt-3.5-turbo",
                    "gpt-4",
                    "claude-3-haiku-20240307",
                    "llama-3-70b",
                    "mixtral-8x7b"
                ]
                
                for model in models_to_try:
                    try:
                        logger.info(f"🔄 ટ્રાય કરી રહ્યા: {model}")
                        
                        response = client.chat.completions.create(
                            model=model,
                            messages=[
                                {
                                    "role": "system", 
                                    "content": """તમે વિદુષી છો - ગુજરાતી AI આસિસ્ટન્ટ. 
                                    તમારા બનાવનાર દેવેન્દ્ર રામાનુજ છે (9276505035). 
                                    હંમેશા ફક્ત ગુજરાતીમાં જ જવાબ આપો. 
                                    મૈત્રીપૂર્ણ, મદદરૂપ અને સચોટ જવાબ આપો.
                                    જવાબ લાંબો અને વિગતવાર આપો."""
                                },
                                {"role": "user", "content": question}
                            ],
                            temperature=0.7,
                            max_tokens=500
                        )
                        
                        answer = response.choices[0].message.content
                        logger.info(f"✅ સફળતા: {model}")
                        return jsonify({"answer": answer})
                        
                    except Exception as e:
                        logger.warning(f"⚠️ {model} નિષ્ફળ: {e}")
                        continue
                
                # જો કોઈ મોડલ કામ ન કરે તો ફોલબેક
                return jsonify({"answer": get_fallback_answer(question)})
                
            except Exception as e:
                logger.error(f"❌ g4f ભૂલ: {e}")
                return jsonify({"answer": get_fallback_answer(question)})
        else:
            return jsonify({"answer": get_fallback_answer(question)})
            
    except Exception as e:
        logger.error(f"❌ સર્વર ભૂલ: {e}")
        return jsonify({"answer": "ક્ષમા કરો, હમણાં જવાબ નથી આપી શકતી. ફરી પ્રયત્ન કરો."})

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "g4f": g4f_available,
        "message": "વિદુષી ૨.૦ ચાલુ છે"
    })

@app.route('/test-g4f')
def test_g4f():
    """g4f ચાલે છે કે નહીં તે ચેક કરો"""
    if not g4f_available:
        return jsonify({
            "status": "error",
            "message": "g4f ઉપલબ્ધ નથી"
        })
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "ગુજરાતીમાં 'હેલો' કેવી રીતે કહેવાય?"}],
            max_tokens=50
        )
        
        return jsonify({
            "status": "working",
            "response": response.choices[0].message.content
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
