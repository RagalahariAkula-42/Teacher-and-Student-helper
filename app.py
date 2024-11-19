from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS, cross_origin
import subprocess

# Create a Flask object
app = Flask(__name__)
CORS(app)

@app.route("/", methods=['GET'])
@cross_origin()
def home():
    return render_template('index.html')

@app.route("/chatbot", methods=['GET'])
@cross_origin()
def chatbot():
    # Launch Streamlit app in a non-blocking way (only if it isn't running already)
    subprocess.Popen(["streamlit", "run", "./src/chatbot/qachat.py"])
    # Redirect to home page
    return render_template('index.html')

@app.route("/mcq_generation", methods=['GET'])
@cross_origin()
def mcq_generation():
    # Launch Streamlit app in a non-blocking way (only if it isn't running already)
    subprocess.Popen(["streamlit", "run", "./src/mcq's_generator/mcq_generator.py"])
    # Redirect to home page
    return render_template('index.html')

@app.route('/VirtualPainter',methods=['POST'])
def predict():
    # Launch Streamlit app in a non-blocking way (only if it isn't running already)
    subprocess.Popen(["python","./src/virtualpainter/VirtualPainter.py"])
    # Redirect to home page
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
