import os
import logging
from flask import Flask, request, jsonify, render_template_string, send_from_directory

# લોગિંગ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# g4f સેટઅપ
try:
    import nest_asyncio
    nest_asyncio.apply()
    from g4f.client import Client
    client = Client()
    g4f_available = True
    logger.info("✅ g4f સફળતાપૂર્વક લોડ થયું")
except Exception as e:
    g4f_available = False
    logger.error(f"❌ g4f લોડ થવામાં ભૂલ: {e}")

# તમારો મૂળ HTML કોડ અહીં (વિડિઓ સાથે)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>વિદુષી ૨.૦</title>
    <style>
        body { font-family: sans-serif; background: #000; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; color: white; }
        
        .video-wrapper { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
        #vidushi-video { width: 100%; height: 100%; object-fit: cover; }

        #chat-box { 
            position: absolute; bottom: 140px; left: 15px; right: 15px; 
            max-height: 120px; overflow-y: auto; z-index: 10; display: none;
            background: rgba(0,0,0,0.6); border-radius: 12px; padding: 10px;
            font-size: 14px; border: 1px solid rgba(255,255,255,0.1);
        }

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

        .mode-switch { display: flex; align-items: center; gap: 12px; background: rgba(255,255,255,0.15); padding: 6px 16px; border-radius: 25px; align-self: center; font-size: 13px; border: 1px solid rgba(255,255,255,0.1); }
        
        input[type="text"] { 
            display: none; flex: 1; padding: 12px 18px; border-radius: 25px; 
            border: none; outline: none; background: rgba(255,255,255,0.95); color: #000; font-size: 15px;
        }

        .credit-line { text-align: center; color: rgba(255,255,255,0.5); font-size: 11px; margin-top: 4px; letter-spacing: 0.5px; }
        
        .status-badge {
            position: absolute; top: 20px; right: 20px; z-index: 30;
            background: rgba(0,0,0,0.5); padding: 5px 10px; border-radius: 20px;
            font-size: 12px; color: #4CAF50; border: 1px solid #4CAF50;
        }
    </style>
</head>
<body>
    <div class="status-badge" id="status-badge">🟢 ઑનલાઇન</div>
    
    <div class="video-wrapper">
        <video id="vidushi-video" autoplay loop muted playsinline>
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
            <label class="small-btn">📷<input type="file" accept="image/*" capture="environment" style="display:none" id="camera-input" onchange="handleImg(this)"></label>
            <input type="text" id="text-input" placeholder="પ્રશ્ન પૂછો...">
            <button id="main-action-btn" class="small-btn" onclick="triggerAI()">🎤</button>
            <label class="small-btn">📁<input type="file" accept="image/*" style="display:none" id="gallery-input" onchange="handleImg(this)"></label>
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
        const statusBadge = document.getElementById('status-badge');
        let base64Img = "";

        vPlayer.play().catch(e => console.log("વિડિઓ પ્લે ન થઈ:", e));

        function toggleMode() {
            if(modeToggle.checked) {
                mainBtn.innerText = "➔";
                textInp.style.display = "block";
                chatBox.style.display = "block";
                statusBadge.innerHTML = "🟢 ટેક્સ્ટ મોડ";
            } else {
                mainBtn.innerText = "🎤";
                textInp.style.display = "none";
                chatBox.style.display = "none";
                statusBadge.innerHTML = "🟢 વોઈસ મોડ";
                if(window.speechSynthesis) {
                    window.speechSynthesis.cancel();
                }
            }
        }

        function triggerAI() {
            if(!modeToggle.checked) { 
                startMic(); 
            } else { 
                const val = textInp.value.trim();
                if(val || base64Img) { 
                    askAI(val); 
                    textInp.value = ""; 
                }
            }
        }

        function setVideo(file) {
            vSource.src = "/videos/" + file;
            vPlayer.load();
            vPlayer.play().catch(e => console.log("વિડિઓ ચેન્જ ન થઈ:", e));
        }

        function handleImg(input) {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => { 
                    base64Img = e.target.result; 
                    statusBadge.innerHTML = "🟢 ઇમેજ સિલેક્ટ થઈ";
                    if(modeToggle.checked && textInp.value.trim()) {
                        askAI(textInp.value);
                    } else if(!modeToggle.checked) {
                        askAI("");
                    }
                };
                reader.readAsDataURL(input.files[0]);
            }
        }

        function speakText(text) {
            let cleanText = text.replace(/[*;:"']/g, ' '); 
            
            if(modeToggle.checked) {
                chatBox.innerHTML = `<div style="color: #fff;"><b>વિદુષી:</b> ${text}</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
                setVideo("smiling.mp4");
                return;
            }

            if(!window.speechSynthesis) {
                alert("તમારું બ્રાઉઝર સ્પીચ સિન્થેસિસ સપોર્ટ કરતું નથી");
                return;
            }

            const msg = new SpeechSynthesisUtterance(cleanText);
            
            if (/[અ-હ]/.test(text)) { msg.lang = 'gu-IN'; }
            else if (/[अ-ह]/.test(text)) { msg.lang = 'hi-IN'; }
            else { msg.lang = 'en-IN'; }

            msg.onstart = () => setVideo("talking.mp4");
            msg.onend = () => setVideo("smiling.mp4");
            msg.onerror = () => setVideo("silent.mp4");
            
            window.speechSynthesis.speak(msg);
        }

        async function askAI(uText) {
            setVideo("thinking.mp4");
            statusBadge.innerHTML = "🟡 વિચારી રહ્યું છે...";
            
            try {
                const res = await fetch('/get_response', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ 
                        message: uText, 
                        image: base64Img || null 
                    })
                });
                
                if(!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                
                const data = await res.json();
                speakText(data.reply);
                base64Img = "";
                statusBadge.innerHTML = "🟢 ઑનલાઇન";
                
            } catch (e) {
                console.error("AI ભૂલ:", e);
                setVideo("silent.mp4");
                statusBadge.innerHTML = "🔴 ભૂલ";
                speakText("ક્ષમા કરશો, કનેક્શનમાં સમસ્યા છે. ફરી પ્રયત્ન કરો.");
                base64Img = "";
            }
        }

        function startMic() {
            if(!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                alert("તમારું બ્રાઉઝર સ્પીચ રેકગ્નિશન સપોર્ટ કરતું નથી");
                return;
            }
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const rec = new SpeechRecognition();
            rec.lang = 'gu-IN';
            rec.continuous = false;
            rec.interimResults = false;
            
            statusBadge.innerHTML = "🟡 સાંભળી રહ્યું છે...";
            
            rec.onresult = (e) => { 
                const text = e.results[0][0].transcript;
                askAI(text); 
            };
            
            rec.onerror = (e) => {
                console.error("Mic error:", e);
                statusBadge.innerHTML = "🔴 માઇક ભૂલ";
                setVideo("silent.mp4");
            };
            
            rec.start();
        }

        textInp.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                triggerAI();
            }
        });

        window.onload = function() {
            setVideo("smiling.mp4");
        };
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/videos/<path:filename>')
def serve_video(filename):
    try:
        return send_from_directory('videos', filename)
    except:
        return "Video not found", 404

@app.route('/get_response', methods=['POST'])
def chat_api():
    try:
        data = request.json
        msg = data.get('message', '')
        img = data.get('image', '')
        
        logger.info(f"📝 પ્રશ્ન: {msg[:50]}...")
        
        if not g4f_available or not msg:
            return jsonify({'reply': "હું વિદુષી છું. તમે કેમ છો?"})
        
        try:
            from g4f.client import Client
            client = Client()
            
            system_prompt = """તમે વિદુષી છો - ગુજરાતી AI આસિસ્ટન્ટ. 
            તમારા બનાવનાર: દેવેન્દ્ર રામાનુજ (9276505035)
            હંમેશા ગુજરાતીમાં જ જવાબ આપો. મૈત્રીપૂર્ણ અને મદદરૂપ બનો."""
            
            if img and img.startswith('data:image'):
                # ઇમેજ સાથે રિક્વેસ્ટ
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"{system_prompt}\n\nપ્રશ્ન: {msg}"},
                            {"type": "image_url", "image_url": {"url": img}}
                        ]
                    }]
                )
            else:
                # ફક્ત ટેક્સ્ટ રિક્વેસ્ટ
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": msg or "હેલો"}
                    ]
                )
            
            reply = response.choices[0].message.content
            logger.info(f"✅ જવાબ મળ્યો")
            return jsonify({'reply': reply})
            
        except Exception as e:
            logger.error(f"❌ g4f ભૂલ: {e}")
            
            # ફોલબેક જવાબો
            fallback = {
                "હેલો": "નમસ્તે! હું વિદુષી. કેમ છો?",
                "કેમ છો": "હું સારી છું, આભાર! આપ કેમ છો?",
                "તમારું નામ શું છે": "મારું નામ વિદુષી છે. હું દેવેન્દ્ર રામાનુજ દ્વારા બનાવેલ AI છું."
            }
            
            reply = fallback.get(msg.lower().strip(), 
                f"હું વિદુષી છું. તમે પૂછ્યું: '{msg}'. હું તમારી સેવામાં છું.")
            
            return jsonify({'reply': reply})
        
    except Exception as e:
        logger.error(f"❌ ભૂલ: {e}")
        return jsonify({'reply': "ક્ષમા કરશો, ફરી પ્રયત્ન કરો."})

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "g4f_available": g4f_available,
        "message": "વિદુષી ૨.૦ ચાલુ છે"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
