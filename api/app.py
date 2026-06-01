import os
import json
from flask import Flask, render_template, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__, template_folder='../templates')

# --- Firebase 初始化 (Vercel 環境變數版) ---
# 檢查是否已經初始化過，避免 Vercel 重複執行報錯
if not firebase_admin._apps:
    # 讀取你在 Vercel 設定的環境變數 FIREBASE_CONFIG_JSON
    firebase_json = os.environ.get('FIREBASE_CONFIG_JSON')
    
    if firebase_json:
        # 將字串轉回字典格式
        cred_dict = json.loads(firebase_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    else:
        # 本地開發測試備案 (如果環境變數不存在，嘗試讀取本地檔案)
        try:
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        except:
            print("警告：找不到 Firebase 設定資料")

db = firestore.client()
# --- 路由設定 ---


@app.route('/sdgs')
def sdgs_page():
    return render_template('sdg_info.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/map')
def map_page():
    # 這裡的變數名稱必須跟 Vercel 設定的一模一樣
    maps_key = os.environ.get('Maps_API_KEY') 
    return render_template('index.html', google_maps_api_key=maps_key)

@app.route('/get_fountains', methods=['GET'])
def get_fountains():
    try:
        fountains_ref = db.collection('water_fountains')
        docs = fountains_ref.stream()
        fountains_list = [doc.to_dict() for doc in docs]
        return jsonify(fountains_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add_fountain', methods=['POST'])
def add_fountain():
    try:
        data = request.json
        location_name = data.get('name') # 取得飲水機名稱
        
        # 使用名稱作為文件 ID (或是尋找座標相近的文件)
        # 這樣當使用者二輸入相同的名稱時，會直接更新該筆資料
        doc_ref = db.collection('water_fountains').document(location_name)
        
        doc_ref.set({
            'location_name': location_name,
            'lat': float(data.get('lat')),
            'lng': float(data.get('lng')),
            'last_filter_change': data.get('date'),
            'status': data.get('status') # 這裡會被使用者二更新為「故障」
        })
        return jsonify({"status": "success", "message": f"「{location_name}」資訊已更新！"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# Vercel 部署時不需要 app.run()，這行僅供本地測試使用
if __name__ == '__main__':
    app.run(debug=True)



