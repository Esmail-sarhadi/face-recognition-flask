import face_recognition
import cv2
import os
import numpy as np
from flask import Flask, render_template, request, Response, jsonify
from werkzeug.utils import secure_filename
import uuid 
import socket  

app = Flask(__name__)
 
# تنظیمات
UPLOAD_FOLDER = 'known_faces'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'} 
 
# اطمینان از وجود پوشه known_faces
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# بارگذاری چهره‌های شناخته‌شده
known_face_encodings = []
known_face_names = []

def load_known_faces():
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith(tuple(ALLOWED_EXTENSIONS)):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])
                name = os.path.splitext(filename)[0]
                known_face_names.append(name)

load_known_faces() 

# بررسی پسوند فایل مجاز
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# صفحه اصلی
@app.route('/')
def index():
    # پیدا کردن IP محلی برای نمایش به کاربر
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return render_template('index.html', ip_address=ip_address)

# آپلود تصویر و نام
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'name' not in request.form:
        return jsonify({'error': 'فایل یا نام وارد نشده است.'}), 400
    file = request.files['file']
    name = request.form['name'].strip()
    if file.filename == '' or not name:
        return jsonify({'error': 'فایل یا نام معتبر نیست.'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{name}_{uuid.uuid4().hex}.jpg")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        load_known_faces()  # به‌روزرسانی لیست چهره‌ها
        return jsonify({'success': 'چهره با موفقیت اضافه شد.'}), 200
    return jsonify({'error': 'فرمت فایل مجاز نیست.'}), 400

# پردازش فریم‌های ویدیویی 
def generate_frames():
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + b'Error: Cannot access webcam' + b'\r\n'
        return

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # تغییر اندازه فریم برای افزایش سرعت
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # شناسایی چهره‌ها
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_names = []
        if face_locations:
            try:
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
                    name = "ناشناس"
                    if known_face_encodings:
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        if face_distances.size > 0:
                            best_match_index = np.argmin(face_distances)
                            if matches[best_match_index]:
                                name = known_face_names[best_match_index]
                    face_names.append(name)
            except Exception:
                face_names = ["ناشناس" for _ in face_locations]

        # رسم کادرهای جذاب
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # رنگ کادر بر اساس شناخته‌شده یا ناشناس
            color = (0, 255, 0) if name != "ناشناس" else (0, 0, 255)
            thickness = 2

            # رسم کادر با گوشه‌های نرم (چند خط با شفافیت متغیر)
            for i in range(3):
                alpha = 1.0 - (i * 0.3)
                overlay = frame.copy()
                cv2.rectangle(overlay, (left - i, top - i), (right + i, bottom + i), color, thickness)
                cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

            # افزودن سایه به کادر
            shadow = frame.copy()
            cv2.rectangle(shadow, (left + 5, top + 5), (right + 5, bottom + 5), (0, 0, 0), thickness)
            cv2.addWeighted(shadow, 0.3, frame, 0.7, 0, frame)

            # پس‌زمینه نام با گرادیانت
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            for i in range(35):
                alpha = i / 35.0
                cv2.line(frame, (left, bottom - i), (right, bottom - i), (int(color[0] * alpha), int(color[1] * alpha), int(color[2] * alpha)), 1)

            # متن نام با فونت زیباتر
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, name, (left + 6, bottom - 10), font, 0.8, (255, 255, 255), 1, cv2.LINE_AA)

        # تبدیل فریم به JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    video_capture.release()

# استریم ویدیو
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4747)
