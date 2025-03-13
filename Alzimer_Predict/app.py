from flask import Flask, request, render_template, jsonify
import os
import pandas as pd
import numpy as np
import pickle
from werkzeug.utils import secure_filename

app = Flask(__name__)

# กำหนดโฟลเดอร์สำหรับอัปโหลดไฟล์
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ตรวจสอบนามสกุลไฟล์
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# โหลดโมเดล .pkl (แก้ path ให้รองรับทุก OS)
def load_model(model_path):
    if not model_path.endswith('.pkl'):
        raise ValueError("Only .pkl model format is supported")  # แก้ error message
    with open(model_path, 'rb') as file:
        return pickle.load(file)

# โหลดโมเดล (ใช้ os.path.join() เพื่อให้รองรับทุกระบบ)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best_model_no_smote.pkl")

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

        # อ่านไฟล์ CSV
        try:
            df = pd.read_csv(file_path)

            # คัดเลือก feature
            X = df[['FunctionalAssessment', 'MMSE', 'ADL', 'MemoryComplaints', 'BehavioralProblems']]

            # ทำนายผล
            predictions = model.predict(X.values)

            # ลบไฟล์หลังใช้งาน
            os.remove(file_path)

            return jsonify({
                'status': 'success',
                'predictions': predictions.tolist()
            })
        except Exception as e:
            return jsonify({'error': str(e)})

@app.route('/manual', methods=['POST'])
def manual_input():
    mmse = request.form.get('field1')
    functional = request.form.get('field2')
    memory = request.form.get('field3')
    behavior = request.form.get('field4')
    adl = request.form.get('field5')

    if None in [mmse, functional, memory, behavior, adl]:
        return jsonify({'error': 'Missing input values'})

    try:
        data = np.array([[float(functional), float(mmse), float(adl), float(memory), float(behavior)]])
        predictions = model.predict(data)

        return jsonify({
            'status': 'success',
            'predictions': predictions.tolist()
        })
    except ValueError:
        return jsonify({'error': 'Invalid input type, please enter numeric values'})

if __name__ == '__main__':
    # สร้างโฟลเดอร์ uploads ถ้ายังไม่มี
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)
