from flask import Flask, request, jsonify, send_file, render_template
import os
import logging
import time
from werkzeug.utils import secure_filename
from PIL import Image
from sd_utils import generate_image, stylize_image
import torch

# Initialize Flask app
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = 'backend/uploads'
OUTPUT_FOLDER = '../static/outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/generate', methods=['POST'])
def generate():
    try:
        logger.info("🚀 Starting image generation from prompt...")
        start_time = time.time()

        data = request.get_json()
        prompt = data.get('prompt', '')
        if not prompt:
            return jsonify({'error': 'Prompt required'}), 400

        output_filename = secure_filename(f"generated_{int(time.time())}_{hash(prompt)}.png")
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        logger.info(f"📝 Generating image with prompt: '{prompt}'")
        result_path = generate_image(prompt, output_path=output_path)

        if result_path and os.path.exists(result_path):
            elapsed = time.time() - start_time
            logger.info(f"✅ Image generated successfully in {elapsed:.2f}s: {output_filename}")
            return jsonify({'image_url': f'/static/outputs/{output_filename}'})
        else:
            logger.error("❌ Failed to generate image")
            return jsonify({'error': 'Failed to generate image'}), 500
    except Exception as e:
        logger.error(f"❌ Error generating image: {e}", exc_info=True)
        return jsonify({'error': f'Failed to generate image: {str(e)}'}), 500

@app.route('/stylize', methods=['POST'])
def stylize():
    try:
        logger.info("🎭 Starting image stylization...")
        start_time = time.time()

        # Check for uploaded file
        if 'file' not in request.files or not request.files['file'].filename:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['file']
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif'}), 400

        style_preset = request.form.get('style', 'realistic')
        if style_preset not in ['anime', 'cartoon', 'painting', 'sketch', 'cyberpunk', 'realistic']:
            return jsonify({'error': 'Invalid style preset'}), 400

        # Save uploaded file
        content_filename = secure_filename(f"upload_{int(time.time())}_{file.filename}")
        content_path = os.path.join(UPLOAD_FOLDER, content_filename)
        file.save(content_path)
        logger.info(f"📁 Uploaded image: {content_filename}")

        output_filename = secure_filename(f"styled_{style_preset}_{int(time.time())}_{hash(content_filename)}.png")
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        logger.info(f"🎨 Applying {style_preset} style to image")
        result_path = stylize_image(content_path, style_preset, output_path=output_path)

        if result_path and os.path.exists(result_path):
            elapsed = time.time() - start_time
            logger.info(f"✅ Image stylized successfully in {elapsed:.2f}s: {output_filename}")
            return jsonify({'image_url': f'/static/outputs/{output_filename}'})
        else:
            logger.error("❌ Failed to stylize image")
            return jsonify({'error': 'Failed to stylize image'}), 500
    except Exception as e:
        logger.error(f"❌ Error in stylization: {e}", exc_info=True)
        return jsonify({'error': f'Failed to stylize image: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "AI Image Generator & Styler API is running"}), 200

@app.route('/gallery', methods=['GET'])
def get_gallery():
    """Get list of generated images for gallery display."""
    try:
        if not os.path.exists(OUTPUT_FOLDER):
            return jsonify({'images': []}), 200

        images = []
        for filename in os.listdir(OUTPUT_FOLDER):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # Get file stats for metadata
                filepath = os.path.join(OUTPUT_FOLDER, filename)
                stat = os.stat(filepath)
                images.append({
                    'filename': filename,
                    'url': f'/static/outputs/{filename}',
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                })

        # Sort by modification time (newest first)
        images.sort(key=lambda x: x['modified'], reverse=True)

        return jsonify({'images': images}), 200
    except Exception as e:
        logger.error(f"❌ Error getting gallery: {e}", exc_info=True)
        return jsonify({'error': 'Failed to load gallery'}), 500

if __name__ == '__main__':
    # Device detection is now handled in sd_utils.py
    app.run(debug=True, host='0.0.0.0', port=5000)
