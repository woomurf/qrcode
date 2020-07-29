from flask import Flask, request, send_file, render_template, jsonify
from MyQR import myqr
from PIL import Image
import os
import time 
import threading
from queue import Queue, Empty

app = Flask(__name__, template_folder='./templates/')

requests_queue = Queue()
BATCH_SIZE = 1
CHECK_INTERVAL = 0.1

def handle_requests_by_batch():
    while True:
        requests_batch = []
        while not (len(requests_batch) >= BATCH_SIZE):
            try:
                requests_batch.append(requests_queue.get(timeout=CHECK_INTERVAL))
            except Empty:
                continue
            batch_outputs = []
            for request in requests_batch:
                batch_outputs.append(run(request['input'][0], request['input'][1], request['input'][2], request['input'][3]))
            
            for request, output in zip(requests_batch, batch_outputs):
                request['output'] = output

threading.Thread(target=handle_requests_by_batch).start()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/qr", methods=["POST"])
def generateQRcode():

    if requests_queue.qsize() > BATCH_SIZE: 
        return jsonify({'error': 'Too Many Requests'}), 429

    url = request.form['url']
    if 'contrast' in request.form: 
        contrast = request.form['contrast']
    else:
        contrast = 1.0
    
    if 'brightness' in request.form:
        brightness = request.form['brightness']
    else:
        brightness = 1.0

    if 'image' in request.files: 
        image = Image.open(request.files['image'].stream)
        format_ = image.format
    else:
        image = None
        format_ = "PNG"
    
    req = {
        'input': [url, image, contrast, brightness]
    }

    requests_queue.put(req)

    while 'output' not in req:
        time.sleep(CHECK_INTERVAL)
    
    qr = req['output']
    
    return send_file(qr, mimetype='image/'+format_)

@app.route("/healthz", methods=["GET"])
def healthCheck():
    return "ok", 200

def run(url, image, contrast, brightness):
    version, level, qr = myqr.run(
        url,
        version=1,
        level='H',
        picture=image,
        colorized=True,
        contrast=contrast,
        brightness=brightness,
        save_name= None,
        save_dir=os.getcwd()
        )

    qr.seek(0)
    
    return qr

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)