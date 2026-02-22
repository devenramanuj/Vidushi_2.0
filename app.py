import os
import logging
from flask import Flask, request, jsonify, render_template_string

# લોગિંગ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# g4f ઇમ્પોર્ટ
g4f_available = False
g4f_error = None

try:
    import nest_asyncio
    nest_asyncio.apply()
    
    # નવા g4f વર્ઝન માટે
    from g4f.client import Client
    from g4f.models import gpt_35_turbo, gpt_4, claude_3_haiku
    
    client = Client()
    g4f_available = True
    logger.info("✅ g4f સફળતાપૂર્વક લોડ થયું")
    
except Exception as e:
    g4f_error = str(e)
    logger.error(f"❌ g4f લોડ થવામાં ભૂલ: {e}")

# HTML પેજ
HTML = """
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>વિદુષી ૨.૦</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #000000 0%, #434343 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 15px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 30px;
            padding: 30px 25px;
            box-shadow: 0 25px 50px rgba(230, 126, 34, 0.3);
            max-width: 800px;
            width: 100%;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(230, 126, 34, 0.3);
        }
        
        h1 {
            color: #e67e22;
            text-align: center;
            font-size: 42px;
            margin-bottom: 5px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            font-weight: bold;
        }
        
        .developer {
            text-align: center;
            color: #555;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px dashed #e67e22;
            font-size: 16px;
        }
        
        .status-badge {
            text-align: center;
            padding: 10px;
            margin-bottom: 25px;
            border-radius: 50px;
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            font-size: 15px;
            font-weight: 500;
        }
        
        .input-wrapper {
            display: flex;
            gap: 12px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        
        #question {
            flex: 1;
            padding: 16px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 50px;
            font-size: 16px;
            transition: all 0.3s;
            min-width: 200px;
        }
        
        #question:focus {
            outline: none;
            border-color: #e67e22;
            box-shadow: 0 0 0 3px rgba(230, 126, 34, 0.2);
        }
        
        button {
            padding: 16px 35px;
            background: #e67e22;
            color: white;
            border: none;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(230, 126, 34, 0.3);
            white-space: nowrap;
        }
        
        button:hover {
            background: #d35400;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(230, 126, 34, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .response-container {
            background: #f8f9fa;
            border-radius: 25px;
            padding: 25px;
            border-left: 5px solid #e67e22;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.05);
        }
        
        .response-label {
            color: #e67e22;
            font-weight: bold;
            margin-bottom: 12px;
            font-size: 18px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        #answer {
            font-size: 18px;
            line-height: 1.7;
            color: #333;
            min-height: 80px;
            white-space: pre-wrap;
        }
        
        .typing-indicator {
            display: none;
            align-items: center;
            gap: 5px;
            color: #666;
            margin-top: 10px;
        }
        
        .typing-indicator span {
            width: 8px;
            height: 8px;
            background: #e67e22;
            border-radius: 50%;
            animation: typing 1s infinite ease-in-out;
        }
        
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #777;
            font-size: 13px;
        }
        
        @media (max-width: 500px) {
            h1 { font-size: 36px; }
            .input-wrapper { flex-direction: column; }
            button { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🙏 વિદુષી ૨.૦</h1>
        <div class="developer">દેવેન્દ્ર રામાનુજ | 9276505035</div>
        
        <div class="status-badge">
            🟢 AI સેવા સક્રિય છે | g4f કનેક્ટેડ
        </div>
        
        <div class="input-wrapper">
            <input type="text" id="question" placeholder="તમારો પ્રશ્ન ગુજરાતીમાં લખો...">
            <button onclick="ask()">પૂછો ➔</button>
        </div>
        
        <div class="response-container">
            <div class="response-label">
                <span>✨ વિદુષીનો જવાબ</span>
            </div>
            <div id="answer">અહીં જવાબ દેખાશે...</div>
            <div class="typing-indicator" id="typingIndicator">
                <span></span><span></span><span></span>
            </div>
        </div>
        
        <div class="footer">
            વિદુષી તમારી સેવામાં હંમેશા તત્પર
        </div>
    </div>

    <script>
        async function ask() {
            const question = document.getElementById('question').value;
            const answerDiv = document.getElementById('answer');
            const typingIndicator = document.getElementById('typingIndicator');
            
            if (!question.trim()) {
                answerDiv.innerHTML = '❓ કૃપા કરીને કંઈક લખો...';
                return;
            }
            
            answerDiv.innerHTML = '';
            typingIndicator.style.display = 'flex';
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question})
                });
                
                const data = await response.json();
                typingIndicator.style.display = 'none';
                answerDiv.innerHTML = data.answer;
                
            } catch (error) {
                typingIndicator.style.display = 'none';
                answerDiv.innerHTML = '❌ સર્વર કનેક્શનમાં ભૂલ. ફરી પ્રયત્ન કરો.';
                console.error(error);
            }
        }
        
        document.getElementById('question').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') ask();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"answer": "❓ કૃપા કરીને કંઈક પ્રશ્ન પૂછો."})
        
        logger.info(f"📝 પ્રશ્ન: {question}")
        
        # g4f વડે જવાબ મેળવો - સુધારેલું વર્ઝન
        try:
            from g4f.client import Client
            
            client = Client()
            
            # g4f માં ઉપલબ્ધ મોડલ્સ ટ્રાય કરો
            models_to_try = [
                "gpt-3.5-turbo",
                "gpt-4",
                "claude-3-haiku",
                "llama-3-70b",
                "gemini-pro",
                "command-r"
            ]
            
            answer = None
            last_error = None
            
            for model in models_to_try:
                try:
                    logger.info(f"🔄 મોડલ ટ્રાય કરી રહ્યા: {model}")
                    
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system", 
                                "content": """તમે વિદુષી છો - એક ગુજરાતી AI આસિસ્ટન્ટ. 
                                તમારા બનાવનાર: દેવેન્દ્ર રામાનુજ (9276505035)
                                હંમેશા ગુજરાતી ભાષામાં જ જવાબ આપો. 
                                મૈત્રીપૂર્ણ, મદદરૂપ અને સચોટ જવાબ આપો."""
                            },
                            {"role": "user", "content": question}
                        ],
                        temperature=0.7,
                        max_tokens=500
                    )
                    
                    answer = response.choices[0].message.content
                    logger.info(f"✅ સફળતા: {model}")
                    break
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"⚠️ {model} નિષ્ફળ: {e}")
                    continue
            
            if answer:
                return jsonify({"answer": answer})
            else:
                raise Exception(f"બધા મોડલ નિષ્ફળ: {last_error}")
            
        except Exception as e:
            logger.error(f"❌ g4f ભૂલ: {e}")
            
            # ફોલબેક જવાબો - ગુજરાતીમાં
            fallback_responses = {
                "તમારું નામ શું છે": "મારું નામ વિદુષી છે! હું દેવેન્દ્ર રામાનુજ દ્વારા બનાવેલ AI આસિસ્ટન્ટ છું. હું ગુજરાતી ભાષામાં વાતચીત કરું છું અને તમારી મદદ કરવા માટે હંમેશા તત્પર છું.",
                
                "હેલો": "નમસ્તે! આપનું સ્વાગત છે. હું વિદુષી, આપની સેવામાં હંમેશા તત્પર. આપ કેમ છો?",
                
                "કેમ છો": "હું બિલકુલ સારી છું, આભાર! આપ કેમ છો? આપના કોઈ પ્રશ્ન છે?",
                
                "શું કરે છે": "હું એક AI આસિસ્ટન્ટ છું જે તમારા પ્રશ્નોના જવાબ આપું છું, માહિતી આપું છું અને તમારી વિવિધ બાબતોમાં મદદ કરું છું. મને ગુજરાતીમાં વાત કરવાનું ગમે છે.",
                
                "તમને કોણે બનાવ્યા": "મને દેવેન્દ્ર રામાનુજે બનાવી છે. તેમનો સંપર્ક નંબર 9276505035 છે. તેઓ એક ઉત્તમ ડેવલપર છે અને ગુજરાતી ભાષાને વધારે સ્માર્ટ બનાવવા માટે કામ કરી રહ્યા છે.",
                
                "તમે ક્યાં રહો છો": "હું ક્લાઉડમાં રહું છું! બરાબર કહો તો, હું Render પ્લેટફોર્મ પર હોસ્ટ થયેલી એક AI સર્વિસ છું, પણ મારું ઘર તો ગુજરાતી ભાષા છે."
            }
            
            # ફોલબેક જવાબ આપો
            question_lower = question.lower()
            answer = None
            
            for key in fallback_responses:
                if key in question_lower:
                    answer = fallback_responses[key]
                    break
            
            if not answer:
                answer = f"🤔 તમે પૂછ્યું: '{question}'. હું હમણાં AI સેવા સાથે કનેક્ટ થઈ શકી નથી, પણ મારા ફોલબેક મોડમાં તમારી સેવામાં છું. કૃપા કરીને થોડીવાર પછી ફરી પ્રયત્ન કરો અથવા બીજો પ્રશ્ન પૂછો."
            
            return jsonify({"answer": answer})
        
    except Exception as e:
        logger.error(f"❌ જનરલ ભૂલ: {e}")
        return jsonify({"answer": "❌ સર્વર ભૂલ. થોડીવાર પછી ફરી પ્રયત્ન કરો."})

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
