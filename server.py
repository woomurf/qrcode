from flask import Flask, request, send_file, render_template
from MyQR import myqr
from PIL import Image
import os

app = Flask(__name__, template_folder='./templates/')

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/qr", methods=["POST"])
def generateQRcode():
    url = request.form['url']
    if 'image' in request.files: 
        image = Image.open(request.files['image'].stream)
        format_ = image.format
    else:
        image = None
        format_ = "PNG"


    version, level, qr = myqr.run(
        url,
        version=1,
        level='H',
        picture=image,
        colorized=True,
        contrast=1.0,
        brightness=1.0,
        save_name= None,
        save_dir=os.getcwd()
        )

    qr.seek(0)
    
    return send_file(qr, mimetype='image/'+format_)

@app.route("/healthz", methods=["GET"])
def healthCheck():
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=False)