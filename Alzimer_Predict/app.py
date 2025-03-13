from flask import Flask, request, render_template, jsonify
import os
import pandas as pd
import numpy as np
import pickle
from werkzeug.utils import secure_filename

app = Flask(__name__)

# กำหนดโฟลเดอร์สำหรับอัปโหลดไฟล์
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# สร้าง Path ให้ถูกต้อง เพื่อให้ Render หาไฟล์ `.pkl` เจอ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # หาตำแหน่งโฟลเดอร์ที่ `app.py` อยู่
MODEL_PATH = os.path.join(BASE_DIR, "models", "best_model_no_smote.pkl")  # รวม Path ไปยังไฟล์โมเดล

# ตรวจสอบนามสกุลไฟล์
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# โหลดโมเดล
def load_model(model_path):
    if not model_path.endswith('.pkl'):
        raise ValueError("Only .pkl model format is supported")
    with open(model_path, "rb") as file:
        return pickle.load(file)

# โหลดโมเดลจาก Path ที่แก้ไขให้ถูกต้อง
model = load_model(MODEL_PATH)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print("File uploaded successfully:", file_path)

        try:
            df = pd.read_csv(file_path)
            X = df[['FunctionalAssessment', 'MMSE', 'ADL', 'MemoryComplaints', 'BehavioralProblems']]
            print("Input values:", X.values)

            predictions = model.predict(X.values)

            os.remove(file_path)  # ลบไฟล์หลังใช้งาน

            return jsonify({'status': 'success', 'predictions': predictions.tolist()})

        except Exception as e:
            return jsonify({'error': str(e)})

@app.route('/manual', methods=['POST'])
def manual_input():
    try:
        mmse = request.form.get('field1')
        functional = request.form.get('field2')
        memory = request.form.get('field3')
        behavior = request.form.get('field4')
        adl = request.form.get('field5')

        if None in [mmse, functional, memory, behavior, adl]:
            return jsonify({'error': 'Missing input values'})

        data = np.array([[functional, mmse, adl, memory, behavior]])
        predictions = model.predict(data)
        print("Raw predictions:", predictions)

        return jsonify({'status': 'success', 'predictions': predictions.tolist()})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
