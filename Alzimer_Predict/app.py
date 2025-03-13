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

# ตรวจสอบนามสกุลไฟล์
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# โหลดโมเดล .sav
def load_model(model_path):
    if not model_path.endswith('.pkl'):
        raise ValueError("Only .sav model format is supported")
    return pickle.load(open(model_path, 'rb'))

# โหลดโมเดล (ปรับ path ตามตำแหน่งใหม่)
model = load_model(r"models\best_model_no_smote.pkl")
@app.route('/', methods=['GET'])
def home ():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':

        # ตรวจสอบว่ามีไฟล์ใน request หรือไม่
        if 'file' not in request.files:

            return jsonify({'error': 'No file part'})
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print(122)
            # อ่านไฟล์ CSV
            try:
                df = pd.read_csv(file_path)
                #sort
                X =df[['FunctionalAssessment','MMSE','ADL','MemoryComplaints','BehavioralProblems']]
                print(X.values)
                # ทำนายผล (อาจต้องปรับ preprocessing ตามโมเดล)
                predictions = model.predict(X.values)
                
                # print("Raw predictions:", predictions)

                # ลบไฟล์หลังใช้งาน
                os.remove(file_path)
                
                # ส่งผลลัพธ์กลับ
                return jsonify({
                    'status': 'success',
                    'predictions': predictions.tolist()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)})
    


@app.route('/manual', methods=['POST'])
def manual_input():
    print(99)
    # รับค่าจาก FormData
    mmse = request.form.get('field1')
    functional = request.form.get('field2')
    memory = request.form.get('field3')
    behavior = request.form.get('field4')
    adl = request.form.get('field5')
    print(mmse)
        # ตรวจสอบว่าค่าทั้งหมดไม่เป็นค่าว่าง
    if None in [mmse, functional, memory, behavior, adl]:
            return jsonify({'error': 'Missing input values'})
        
    data=np.array([[functional,mmse,adl, memory, behavior]])
        # print(data)
    predictions=0
    predictions = model.predict(data)
    print("Raw predictions:", predictions)
        
    return jsonify({
            'status': 'success',
            'predictions': predictions.tolist()
     })



if __name__ == '__main__':
    # สร้างโฟลเดอร์ uploads ถ้ายังไม่มี
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True) 