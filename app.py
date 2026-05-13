from flask import Flask, render_template, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# 初始化 Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def index():
    return render_template('index.html')

# API: 獲取所有飲水機資料
@app.route('/get_fountains', methods=['GET'])
def get_fountains():
    fountains_ref = db.collection('water_fountains')
    docs = fountains_ref.stream()
    fountains_list = [doc.to_dict() for doc in docs]
    return jsonify(fountains_list)

# API: 新增飲水機定位
@app.route('/add_fountain', methods=['POST'])
def add_fountain():
    try:
        data = request.json
        new_doc = db.collection('water_fountains').document()
        new_doc.set({
            'location_name': data.get('name'),
            'lat': float(data.get('lat')),
            'lng': float(data.get('lng')),
            'last_filter_change': data.get('date'),
            'status': "正常"
        })
        return jsonify({"status": "success", "message": "定位已成功新增！"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)