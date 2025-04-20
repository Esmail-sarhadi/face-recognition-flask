📸 Face Recognition with Flask and OpenCV
This project demonstrates a face recognition system using a Flask web server, OpenCV, and the face_recognition library. It allows users to upload known faces, stream webcam video, and identify faces in real-time with a user-friendly web interface.
📑 Table of Contents

⚙️ Installation
🚀 Usage
📂 Project Structure
🔧 Code Explanation
🐞 Troubleshooting
🤝 Contributing
📄 License

⚙️ Installation
To set up this project, you need Python 3.7+ and the required dependencies. It's recommended to use a virtual environment.

Clone the repository:git clone https://github.com/Esmail-sarhadi/face_recognition.git


Navigate to the project directory:cd face-recognition-flask


Create and activate a virtual environment:python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:pip install flask opencv-python face-recognition numpy werkzeug


Ensure you have a webcam connected to your system.

🚀 Usage

Run the Flask application:python app.py


Open a web browser and navigate to http://localhost:4747 (or the IP address displayed in the console for network access).
Use the web interface to:
Upload a new face with a name and image (JPG, JPEG, or PNG).
View the live webcam feed with real-time face recognition.


To access the application from another device on the same network, use the IP address shown in the web interface (e.g., http://<your-ip>:4747).

📂 Project Structure

app.py: Main Flask application script handling face recognition, webcam streaming, and file uploads.
templates/index.html: HTML template for the web interface.
known_faces/: Directory to store uploaded face images.

🔧 Code Explanation
The project is divided into several key components:

Flask Setup and File Upload:
app = Flask(__name__)
UPLOAD_FOLDER = 'known_faces'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

Configures the Flask app and sets up a folder for storing known face images.

Loading Known Faces:
def load_known_faces():
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith(tuple(ALLOWED_EXTENSIONS)):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])
                name = os.path.splitext(filename)[0]
                known_face_names.append(name)

Loads face encodings from images in the known_faces directory for recognition.

Webcam Streaming and Face Recognition:
def generate_frames():
    video_capture = cv2.VideoCapture(0)
    while True:
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        # ... (face matching and drawing rectangles)
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

Streams webcam frames, detects faces, matches them against known faces, and draws labeled rectangles.

Web Interface:The index.html template uses Tailwind CSS for styling and JavaScript for handling file uploads via AJAX. It displays the webcam feed and provides a form for uploading new faces.


🐞 Troubleshooting

Webcam Issues: Ensure your webcam is connected and accessible. Check if other applications are using the webcam.
Face Recognition Fails: Verify that uploaded images are clear and contain visible faces. Ensure sufficient lighting for webcam detection.
Network Access Issues: If accessing from another device, ensure both devices are on the same network and the firewall allows traffic on port 4747.
Dependency Errors: Confirm all required libraries are installed correctly. Use pip list to verify.

🤝 Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
📝 Description
This project provides a robust face recognition system using Flask, OpenCV, and face_recognition. It features a sleek web interface for uploading known faces and streaming live webcam footage with real-time face identification, making it ideal for applications like security or attendance systems.
