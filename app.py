import os
import logging
from flask import Flask, request, jsonify, render_template_string

# લોગિંગ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# g4f ઇમ્પોર્ટ ટ્રાય કરો
g4f_available = False
g4f_error = None

try:
    import nest_asyncio
    nest_asyncio.apply()
    import g4f
    from g4f.client import Client
    
    # ટેસ્ટ કરો કે g4f કામ કરે છે કે નહીં
    client = Client()
    g4f_available = True
    logger.info("✅ g4f સફળતાપૂર્વક લોડ થયું")
    
except ImportError as e:
    g4f_error = f"Import Error: {e}"
    logger.error(f"❌ g4f ઇમ્પોર્ટ ન થયું: {e}")
    
except Exception as e:
    g4f_error = f"Other Error: {e}"
    logger.error(f"❌ g4f લોડ થવામાં ભૂલ: {e}")

# HTML પેજ
HTML = """
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>વિદુષી ૨.૦</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            margin: 0;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #e67e22;
            text-align: center;
            font-size: 36px;
            margin-bottom: 10px;
        }
        .developer {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input {
            flex: 1;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
        }
        button {
            padding: 12px 24px;
            background: #e67e22;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #d35400;
        }
        .response {
            background: #f9f9f9;
            border-radius: 8px;
            padding: 20px;
            min-height: 100px;
            border-left: 4px solid #e67e22;
        }
        .status {
            text-align: center;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 8px;
            background: #f0f0f0;
        }
        .error-details {
            background: #fee;
            color: #c00;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🙏 વિદુષી ૨.૦</h1>
        <div class="developer">Developed by Devendra Ramanuj | 9276505035</div>
        
        <div class="status" id="status">
            {% if g4f_available %}
                🟢 AI સેવા સક્રિય છે
            {% else %}
                🔴 AI સેવા સક્રિય નથી
                {% if g4f_error %}
                <div class="error-details">{{ g4f_error }}</div>
                {% endif %}
            {% endif %}
        </div>
        
        <div class="input-group">
            <input type="text" id="question" placeholder="તમારો પ્રશ્ન લખો...">
            <button onclick="ask()">પૂછો</button>
        </div>
        
        <div class="response" id="response">
            <div id="answer">અહીં જવાબ દેખાશે...</div>
        </div>
    </div>

    <script>
        async function ask() {
            const question = document.getElementById('question').value;
            const answerDiv = document.getElementById('answer');
            
            if (!question) {
                answerDiv.innerHTML = 'કૃપા કરીને કંઈક લખો!';
                return;
            }
            
            answerDiv.innerHTML = '🤔 વિચારી રહ્યું છે...';
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question})
                });
                
                const data = await response.json();
                answerDiv.innerHTML = data.answer;
                
            } catch (error) {
                answerDiv.innerHTML = '❌ ભૂલ: ' + error.message;
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
    return render_template_string(HTML, g4f_available=g4f_available, g4f_error=g4f_error)

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        question = data.get('question', '')
        
        logger.info(f"Question: {question}")
        
        if not g4f_available:
            return jsonify({"answer": "⚠️ AI સેવા હાલમાં ઉપલબ્ધ નથી. ટેકનિકલ સપોર્ટ માટે 9276505035 પર સંપર્ક કરો."})
        
        try:
            # g4f થી જવાબ મેળવવાનો પ્રયાસ
            from g4f.client import Client
            
            client = Client()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "તમે વિદુષી છો - ગુજરાતી AI આસિસ્ટન્ટ. હંમેશા ગુજરાતીમાં જવાબ આપો."},
                    {"role": "user", "content": question}
                ]
            )
            
            answer = response.choices[0].message.content
            return jsonify({"answer": answer})
            
        except Exception as e:
            logger.error(f"g4f error: {e}")
            return jsonify({"answer": f"❌ g4f ભૂલ: {str(e)[:100]}"})
            
    except Exception as e:
        logger.error(f"General error: {e}")
        return jsonify({"answer": "❌ કંઈક ભૂલ થઈ"})

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "g4f_available": g4f_available,
        "g4f_error": str(g4f_error) if g4f_error else None
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
