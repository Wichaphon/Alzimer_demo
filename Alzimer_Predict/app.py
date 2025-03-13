from flask import Flask, request, render_template, jsonify
import os
import pandas as pd
import numpy as np
import pickle
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ✅ ใช้ /tmp/uploads/ แทน uploads/ (Render เขียนไฟล์ได้ที่นี่)
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ ตรวจสอบและสร้างโฟลเดอร์หากไม่มี
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ตรวจสอบนามสกุลไฟล์
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# โหลดโมเดล
def load_model(model_path):
    if not model_path.endswith('.pkl'):
        raise ValueError("Only .sav model format is supported")
    return pickle.load(open(model_path, 'rb'))

# ✅ โหลดโมเดลจากตำแหน่งเดิม (ไม่เปลี่ยนแปลง)
model = load_model("models/best_model_no_smote.pkl")

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

        # ✅ เช็คและสร้างโฟลเดอร์อีกครั้งกันพลาด
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # ✅ บันทึกไฟล์
        file.save(file_path)

        # ✅ Debug Log (ให้แน่ใจว่าเซฟได้)
        print(f"File saved at: {file_path}")

        try:
            df = pd.read_csv(file_path)
            X = df[['FunctionalAssessment', 'MMSE', 'ADL', 'MemoryComplaints', 'BehavioralProblems']]
            predictions = model.predict(X.values)

            # ✅ ลบไฟล์หลังใช้เสร็จ
            os.remove(file_path)

            return jsonify({
                'status': 'success',
                'predictions': predictions.tolist()
            })

        except Exception as e:
            return jsonify({'error': str(e)})

@app.route('/manual', methods=['POST'])
def manual_input():
    print(99)
    mmse = request.form.get('field1')
    functional = request.form.get('field2')
    memory = request.form.get('field3')
    behavior = request.form.get('field4')
    adl = request.form.get('field5')

    print(mmse)

    if None in [mmse, functional, memory, behavior, adl]:
        return jsonify({'error': 'Missing input values'})

    data = np.array([[functional, mmse, adl, memory, behavior]])
    predictions = model.predict(data)
    print("Raw predictions:", predictions)

    return jsonify({
        'status': 'success',
        'predictions': predictions.tolist()
    })

if __name__ == '__main__':
    # ✅ สร้างโฟลเดอร์อัปโหลดตอนรันเซิร์ฟเวอร์ (สำคัญ)
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
