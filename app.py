import os
import tempfile
import logging
from flask import Flask, request, jsonify, render_template_string, send_from_directory

# લોગિંગ સેટઅપ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# વિડિઓ ડિરેક્ટરી સેટઅપ
VIDEO_DIR = os.path.join(os.getcwd(), 'videos')
if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)
    logger.info(f"Created video directory: {VIDEO_DIR}")

@app.route('/videos/<path:filename>')
def serve_video(filename):
    """વિડિઓ ફાઇલો સર્વ કરો"""
    try:
        # પહેલા કરન્ટ ડિરેક્ટરીમાં ચેક કરો
        if os.path.exists(os.path.join(os.getcwd(), filename)):
            return send_from_directory(os.getcwd(), filename)
        # પછી વિડિઓ ડિરેક્ટરીમાં ચેક કરો
        elif os.path.exists(os.path.join(VIDEO_DIR, filename)):
            return send_from_directory(VIDEO_DIR, filename)
        else:
            logger.error(f"Video not found: {filename}")
            return "Video not found", 404
    except Exception as e:
        logger.error(f"Error serving video: {e}")
        return "Error loading video", 500

# બાકીનો HTML_PAGE અહીં જ રહેશે

@app.route('/get_response', methods=['POST'])
def chat_api():
    """AI રિસ્પોન્સ મેળવો"""
    try:
        data = request.json
        msg = data.get('message', '')
        img = data.get('image', '')
        
        # સરળ રિસ્પોન્સ (ટેસ્ટિંગ માટે)
        # વાસ્તવિક g4f ને બદલે ટેસ્ટ રિસ્પોન્સ
        test_response = f"વિદુષી અહીં છે. તમારો પ્રશ્ન: {msg[:50]}..."
        
        # અહીં તમે g4f ને બદલે કોઈ બીજી API વાપરી શકો છો
        # દા.ત. ઓપનAI, અથવા કોઈ ફ્રી API
        
        return jsonify({'reply': test_response})
        
    except Exception as e:
        logger.error(f"Error in chat_api: {e}")
        return jsonify({'reply': "ક્ષમા કરશો, ફરી પ્રયત્ન કરો."})

@app.route('/health')
def health_check():
    """રેન્ડર હેલ્થ ચેક માટે"""
    return jsonify({'status': 'healthy'}), 200

if __name__ != '__main__':
    # રેન્ડર માટે ગુનિકોર્ન સેટઅપ
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
