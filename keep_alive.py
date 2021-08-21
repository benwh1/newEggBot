from flask import Flask, render_template
from threading import Thread
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
@app.route('/')
def index():
  return render_template("index.html")
  
def run():
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()
