from flask import Flask, request, render_template, jsonify
import os
import pandas as pd
import numpy as np
import pickle
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 📂 กำหนดโฟลเดอร์สำหรับอัปโหลดไฟล์
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ ตรวจสอบและสร้างโฟลเดอร์อัปโหลดถ้ายังไม่มี
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ✅ ตรวจสอบนามสกุลไฟล์ที่อัปโหลดได้
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 📍 ระบุ PATH ของโมเดลให้ชัดเจน (แก้ปัญหาที่ Render หาไฟล์ไม่เจอ)
MODEL_PATH = os.path.join(os.getcwd(), "Alzimer_Predict", "models", "best_model_no_smote.pkl")

# ✅ ฟังก์ชันโหลดโมเดล
def load_model(model_path):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    return pickle.load(open(model_path, 'rb'))

# โหลดโมเดล
model = load_model(MODEL_PATH)

# ✅ Route หน้าแรก
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# ✅ Route สำหรับอัปโหลด CSV และพยากรณ์ผล
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

        try:
            df = pd.read_csv(file_path)
            X = df[['FunctionalAssessment', 'MMSE', 'ADL', 'MemoryComplaints', 'BehavioralProblems']]
            predictions = model.predict(X.values)

            os.remove(file_path)  # ลบไฟล์หลังใช้งาน

            return jsonify({'status': 'success', 'predictions': predictions.tolist()})
        except Exception as e:
            return jsonify({'error': str(e)})

# ✅ Route สำหรับการพยากรณ์แบบ Manual Input
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

        return jsonify({'status': 'success', 'predictions': predictions.tolist()})
    
    except Exception as e:
        return jsonify({'error': str(e)})

# ✅ รัน Flask App
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=10000)  # ✅ เปลี่ยนเป็น port 10000 เพื่อให้ตรงกับ Render
