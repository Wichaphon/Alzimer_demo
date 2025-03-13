import pickle
import numpy as np
import pandas as pd 
# โหลดโมเดล .sav
def load_model(model_path):
    if not model_path.endswith('.sav'):
        raise ValueError("Only .sav model format is supported")
    return pickle.load(open(model_path, 'rb'))
model = load_model(r"models\best_model_no_smote.pkl")
data=np.array([[7.39606098,25.82073187,0.756231808,0,1]])
df=pd.read_csv('test.csv')
X =df[['FunctionalAssessment','MMSE','ADL','MemoryComplaints','BehavioralProblems']]
print(X.values)
print(model.predict(X.values))
# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         # ตรวจสอบว่ามีไฟล์ใน request หรือไม่
#         if 'file' not in request.files:
#             return jsonify({'error': 'No file part'})
        
#         file = request.files['file']
        
#         if file.filename == '':
#             return jsonify({'error': 'No selected file'})
        
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
            
#             # อ่านไฟล์ CSV
#             try:
#                 df = pd.read_csv(file_path)
#                 #sort
#                 X =df[['FunctionalAssessment','MMSE','ADL','MemoryComplaints','BehavioralProblems']]
#                 print(X.values)
#                 # ทำนายผล (อาจต้องปรับ preprocessing ตามโมเดล)
#                 predictions = model.predict(X.values)
                
#                 print("Raw predictions:", predictions)
                
#                 # ลบไฟล์หลังใช้งาน
#                 os.remove(file_path)
                
#                 # ส่งผลลัพธ์กลับ
#                 return jsonify({
#                     'status': 'success',
#                     'predictions': predictions.tolist()
#                 })
                
#             except Exception as e:
#                 return jsonify({'error': str(e)})