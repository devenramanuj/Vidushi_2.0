import os
import logging
from flask import Flask, request, jsonify, render_template_string

# લોગિંગ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# g4f ઇમ્પોર્ટ ટ્રાય કરો
try:
    import nest_asyncio
    nest_asyncio.apply()
    import g4f
    g4f_available = True
    logger.info("✓ g4f સફળતાપૂર્વક લોડ થયું")
except Exception as e:
    g4f_available = False
    logger.error(f"✗ g4f લોડ ન થયું: {e}")

# HTML પેજ
HTML = """
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>વિદુષી ૨.૦ - AI આસિસ્ટન્ટ</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
        }
        
        h1 {
            color: #e67e22;
            font-size: 42px;
            text-align: center;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .developer {
            text-align: center;
            color: #666;
            font-size: 16px;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .status {
            text-align: center;
            color: #27ae60;
            font-size: 18px;
            margin-bottom: 30px;
            padding: 10px;
            background: #e8f5e9;
            border-radius: 10px;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input:focus {
            outline: none;
            border-color: #e67e22;
        }
        
        button {
            padding: 15px 30px;
            background: #e67e22;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        button:hover {
            background: #d35400;
        }
        
        .response-box {
            background: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            min-height: 100px;
            border-left: 4px solid #e67e22;
            font-size: 18px;
            line-height: 1.6;
            color: #333;
        }
        
        .response-title {
            font-weight: bold;
            color: #e67e22;
            margin-bottom: 10px;
            font-size: 18px;
        }
        
        .loader {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .loader img {
            width: 50px;
            height: 50px;
        }
        
        .g4f-status {
            text-align: center;
            margin-top: 20px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 10px;
            font-size: 14px;
            color: {% if g4f_available %}#27ae60{% else %}#e74c3c{% endif %};
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 20px;
            }
            
            h1 {
                font-size: 32px;
            }
            
            .input-group {
                flex-direction: column;
            }
            
            button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🙏 વિદુષી ૨.૦</h1>
        <div class="developer">Developed by Devendra Ramanuj | 9276505035</div>
        <div class="status">🚀 સર્વર ચાલુ છે!</div>
        
        <div class="g4f-status" id="g4fStatus">
            AI સ્ટેટસ: {% if g4f_available %}✅ g4f એક્ટિવ{% else %}⚠️ g4f ઉપલબ્ધ નથી (બેઝિક મોડ){% endif %}
        </div>
        
        <div class="input-group">
            <input type="text" id="question" placeholder="તમારો પ્રશ્ન પૂછો... (દા.ત. તમારું નામ શું છે?)">
            <button onclick="ask()">પૂછો</button>
        </div>
        
        <div class="loader" id="loader">
            <div>🤔 વિચારી રહ્યું છે...</div>
        </div>
        
        <div class="response-box" id="response">
            <div class="response-title">વિદુષીનો જવાબ:</div>
            <div id="answer">અહીં જવાબ દેખાશે...</div>
        </div>
    </div>

    <script>
        async function ask() {
            const question = document.getElementById('question').value;
            const answerDiv = document.getElementById('answer');
            const loader = document.getElementById('loader');
            
            if (!question.trim()) {
                answerDiv.innerHTML = 'કૃપા કરીને કંઈક લખો!';
                return;
            }
            
            loader.style.display = 'block';
            answerDiv.innerHTML = '...';
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: question })
                });
                
                const data = await response.json();
                answerDiv.innerHTML = data.answer;
            } catch (error) {
                answerDiv.innerHTML = '❌ ભૂલ: સર્વર સાથે કનેક્શન ન થઈ શક્યું';
                console.error(error);
            } finally {
                loader.style.display = 'none';
            }
        }
        
        // Enter key press
        document.getElementById('question').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                ask();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML, g4f_available=g4f_available)

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        question = data.get('question', '')
        
        logger.info(f"Question received: {question}")
        
        if not g4f_available:
            # Simple responses when g4f is not available
            responses = {
                "તમારું નામ શું છે": "મારું નામ વિદુષી છે! હું દેવેન્દ્ર રામાનુજ દ્વારા બનાવેલ AI આસિસ્ટન્ટ છું.",
                "હેલો": "નમસ્તે! કેમ છો?",
                "કેમ છો": "હું સારી છું, આપ કેમ છો?",
                "શું કરે છે": "હું તમારા પ્રશ્નોના જવાબ આપું છું અને તમારી મદદ કરું છું!"
            }
            
            # Check for similar questions
            answer = responses.get(question.strip(), f"તમે પૂછ્યું: '{question}'. હું હમણાં બેઝિક મોડમાં છું. g4f એક્ટિવ થયા પછી વધુ સારા જવાબ આપી શકીશ.")
            
        else:
            # Use g4f for AI responses
            try:
                system_prompt = """તમે વિદુષી છો - ગુજરાતી AI આસિસ્ટન્ટ. 
                તમારા બનાવનાર: દેવેન્દ્ર રામાનુજ (9276505035)
                હંમેશા ગુજરાતીમાં જ જવાબ આપો. મૈત્રીપૂર્ણ અને મદદરૂપ બનો."""
                
                response = g4f.ChatCompletion.create(
                    model=g4f.models.default,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ],
                    temperature=0.7,
                )
                answer = str(response)
                
            except Exception as e:
                logger.error(f"g4f error: {e}")
                answer = "ક્ષમા કરો, હમણાં AI સર્વિસ ઉપલબ્ધ નથી. થોડીવાર પછી ફરી પ્રયત્ન કરો."
        
        return jsonify({"answer": answer})
        
    except Exception as e:
        logger.error(f"General error: {e}")
        return jsonify({"answer": "કંઈક ભૂલ થઈ ગઈ. ફરી પ્રયત્ન કરો."}), 500

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
