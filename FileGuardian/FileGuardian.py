import os
import re
import requests
from urllib.parse import urlparse
from flask import Flask, request, jsonify
import concurrent.futures
import logging
import hashlib
import magic
import gzip
import zlib
from datetime import datetime
from threat_intelligence import ThreatIntelFeed
from cloud_storage import CloudStorageClient
from siem_integration import SIEMClient

app = Flask(__name__)

# Directory to save intercepted files
INTERCEPTED_DIR = "intercepted_files"

# Create directory if it doesn't exist
if not os.path.exists(INTERCEPTED_DIR):
    os.makedirs(INTERCEPTED_DIR)

# Configure logging
logging.basicConfig(filename='file_interceptor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Maximum file size limit for interception (in bytes)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

# Initialize threat intelligence feed client
threat_intel = ThreatIntelFeed()

# Initialize cloud storage client
cloud_storage = CloudStorageClient()

# Initialize SIEM client
siem_client = SIEMClient()

def intercept_file(url):
    try:
        # Send a GET request to the specified URL
        response = requests.get(url, stream=True)

        # Extract filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)

        # Validate file size
        if 'content-length' in response.headers:
            content_length = int(response.headers['content-length'])
            if content_length > MAX_FILE_SIZE:
                logging.warning(f"File size exceeds maximum limit: {content_length} bytes")
                return

        # Detect content type
        content_type = response.headers.get('content-type', '')
        if not content_type:
            content_type = magic.Magic(mime=True).from_buffer(response.content)

        # Generate file hash
        file_hash = hashlib.sha256(response.content).hexdigest()

        # Save the intercepted file to the local directory
        file_path = os.path.join(INTERCEPTED_DIR, filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logging.info(f"File intercepted and saved: {filename}, Content-Type: {content_type}, Hash: {file_hash}")

        # Send file metadata to SIEM
        siem_client.send_event({
            'timestamp': datetime.now(),
            'event_type': 'file_interception',
            'file_name': filename,
            'file_type': content_type,
            'file_hash': file_hash,
            'source_url': url
        })

        # Upload intercepted file to cloud storage
        cloud_storage.upload_file(file_path)

        # Check file against threat intelligence feed
        threat_intel.check_file(file_path)

    except Exception as e:
        logging.error(f"Failed to intercept file from {url}: {str(e)}")

@app.route('/intercept', methods=['GET'])
def intercept():
    url = request.args.get('url')

    if url:
        # Validate URL format
        if re.match(r'^https?://', url):
            # Intercept file asynchronously
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(intercept_file, url)
            
            return "File interception request received and processing asynchronously.", 200
        else:
            return "Invalid URL format. Please provide a valid HTTP/HTTPS URL.", 400
    else:
        return "URL parameter is missing. Please provide a URL to intercept.", 400

@app.route('/status', methods=['GET'])
def status():
    # Check status of file interceptor components
    status_info = {
        'threat_intel_feed': threat_intel.check_status(),
        'cloud_storage': cloud_storage.check_status(),
        'siem_integration': siem_client.check_status()
    }
    return jsonify(status_info), 200

if __name__ == '__main__':
    app.run(debug=True)
