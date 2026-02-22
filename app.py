import os
from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>વિદુષી ૨.૦</title>
    <style>
        body { 
            background: linear-gradient(135deg, #000, #1a1a1a);
            color: white;
            font-family: 'Arial', sans-serif;
            text-align: center;
            padding: 50px;
        }
        h1 { color: #e67e22; font-size: 48px; }
        p { font-size: 20px; color: #ccc; }
    </style>
</head>
<body>
    <h1>🙏 વિદુષી ૨.૦</h1>
    <p>Developed by Devendra Ramanuj | 9276505035</p>
    <p>🚀 સર્વર ચાલુ છે!</p>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
