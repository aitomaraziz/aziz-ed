import os
import pandas as pd
from flask import Flask, render_template, request, jsonify

# إعداد المسارات لضمان عمل البرنامج في أي مكان
base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'))

EXCEL_DB = os.path.join(base_dir, "Database_Educational.xlsx")

# دالة إنشاء قاعدة البيانات بتنسيق مبسط
def init_db():
    if not os.path.exists(EXCEL_DB):
        with pd.ExcelWriter(EXCEL_DB, engine='openpyxl') as writer:
            # ورقة المديرين
            pd.DataFrame([['admin', '123456']], columns=['Username', 'Password']).to_excel(writer, sheet_name='Admins', index=False)
            # ورقة الأساتذة (مبسطة)
            pd.DataFrame(columns=['Username', 'Password']).to_excel(writer, sheet_name='Teachers', index=False)
            # ورقة التلاميذ
            pd.DataFrame(columns=['Username', 'Password', 'RoomID']).to_excel(writer, sheet_name='Students', index=False)
        print("✅ تم إنشاء ملف الإكسيل بنجاح بتنسيق مبسط")

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/classroom')
def classroom():
    return render_template('classroom.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    role = data.get('role')
    user_in = str(data.get('username')).strip()
    pass_in = str(data.get('password')).strip()

    sheet = 'Teachers' if role == 'teacher' else 'Students'
    
    try:
        df = pd.read_excel(EXCEL_DB, sheet_name=sheet)
        # تنظيف البيانات للمقارنة
        df['Username'] = df['Username'].astype(str).str.strip()
        df['Password'] = df['Password'].astype(str).str.strip()

        user = df[(df['Username'] == user_in) & (df['Password'] == pass_in)]
        
        if not user.empty:
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'بيانات الدخول غير صحيحة'})
    except:
        return jsonify({'success': False, 'message': 'خطأ في قراءة ملف البيانات'})

@app.route('/api/add-user', methods=['POST'])
def add_user():
    data = request.json
    sheet = data.pop('target_sheet')
    try:
        df = pd.read_excel(EXCEL_DB, sheet_name=sheet)
        new_row = pd.DataFrame([data])
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        with pd.ExcelWriter(EXCEL_DB, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            updated_df.to_excel(writer, sheet_name=sheet, index=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)