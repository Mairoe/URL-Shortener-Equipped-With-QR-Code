from flask import Flask, request, render_template, redirect, url_for, jsonify
import random, string
import qrcode
import os
import hashlib
import json
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 🔹 Allow cross-origin requests

# Dictionary to store short URLs
db = {}

# Ensure 'static' directory exists for QR code images
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
if not os.path.exists(static_folder):
    os.makedirs(static_folder)

# Function to generate short URL
def generate_short_url():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form.get('url', '').strip()
    alias = request.form.get('alias', '').strip()

    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    # Ensure alias is unique
    if alias:
        if alias in db:
            return jsonify({"error": "Alias already taken"}), 400
        short_url = alias
    else:
        short_url = generate_short_url()
        while short_url in db:
            short_url = generate_short_url()

    db[short_url] = original_url
    return jsonify({"short_url": request.host_url + short_url})

@app.route('/<short_url>')
def redirect_url(short_url):
    if short_url in db:
        return redirect(db[short_url])
    return "URL not found", 404

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    try:
        data = request.get_json(force=True)  
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    url = data.get('url') or data.get('short_url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    url = url.strip()

    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url  # Add http:// if missing

    url_hash = hashlib.md5(url.encode()).hexdigest()[:10]  # Short hash
    qr_filename = f"{url_hash}.png"
    qr_path = os.path.join(static_folder, qr_filename)

    # Check if QR code already exists
    if not os.path.exists(qr_path):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save(qr_path)

    # Generate the correct URL for the QR code image
    qr_url = url_for('static', filename=qr_filename)
    print("Generated QR Code:", qr_url)  # Debugging
    return jsonify({"qr_code": qr_url})

if __name__ == '__main__':
    app.run(debug=True)
