import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "વિદુષી ૨.૦ - સર્વર ચાલુ છે! 🚀"

@app.route('/health')
def health():
    return {"status": "healthy", "message": "સર્વર ઓનલાઇન છે"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
