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

# સરળ HTML પેજ (વિડિઓ વગર)
HTML = """
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>વિદુષી ૨.૦</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #000, #1a1a1a);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 30px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            border: 2px solid #e67e22;
            box-shadow: 0 20px 40px rgba(230, 126, 34, 0.3);
        }
        h1 {
            color: #e67e22;
            text-align: center;
            font-size: 48px;
            margin-bottom: 10px;
        }
        .developer {
            text-align: center;
            color: #fff;
            margin-bottom: 30px;
            font-size: 18px;
        }
        .status {
            text-align: center;
            color: #4CAF50;
            margin-bottom: 30px;
            padding: 10px;
            background: rgba(76, 175, 80, 0.1);
            border-radius: 10px;
        }
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }
        input {
            flex: 1;
            padding: 15px;
            border: 2px solid #333;
            border-radius: 10px;
            font-size: 16px;
            background: #333;
            color: white;
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
        .response {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #e67e22;
        }
        .response-title {
            color: #e67e22;
            margin-bottom: 10px;
        }
        #answer {
            color: white;
            font-size: 18px;
            line-height: 1.6;
            min-height: 80px;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🙏 વિદુષી ૨.૦</h1>
        <div class="developer">દેવેન્દ્ર રામાનુજ | 9276505035</div>
        <div class="status">🚀 સર્વર ચાલુ છે</div>
        
        <div class="input-group">
            <input type="text" id="question" placeholder="તમારો પ્રશ્ન લખો...">
            <button onclick="ask()">પૂછો</button>
        </div>
        
        <div class="response">
            <div class="response-title">વિદુષીનો જવાબ:</div>
            <div id="answer">અહીં જવાબ દેખાશે...</div>
        </div>
        
        <div class="footer">AI આસિસ્ટન્ટ તમારી સેવામાં છે</div>
    </div>

    <script>
        async function ask() {
            const question = document.getElementById('question').value;
            const answerDiv = document.getElementById('answer');
            
            if (!question) {
                answerDiv.innerHTML = '❓ કૃપા કરીને કંઈક લખો';
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
                answerDiv.innerHTML = '❌ ભૂલ આવી';
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
            return jsonify({"answer": "❓ કૃપા કરીને કંઈક લખો"})
        
        if not g4f_available:
            return jsonify({"answer": f"🤖 હું વિદુષી છું. તમે પૂછ્યું: '{question}'"})
        
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
            return jsonify({"answer": f"🤖 હું વિદુષી છું. તમે પૂછ્યું: '{question}'"})
            
    except Exception as e:
        return jsonify({"answer": "❌ ભૂલ આવી"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "g4f": g4f_available})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
