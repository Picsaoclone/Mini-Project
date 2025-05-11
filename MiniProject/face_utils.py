import cv2
import numpy as np
import base64
import hashlib

# Phát hiện và cắt khuôn mặt từ ảnh (dùng cascade)
def extract_face(image_path):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    if len(faces) == 0:
        return None

    x, y, w, h = faces[0]
    face_img = gray[y:y+h, x:x+w]
    resized_face = cv2.resize(face_img, (100, 100))  # Chuẩn hóa kích thước
    return resized_face

# Mã hóa ảnh bằng hash
def image_to_hash(image_array):
    _, buffer = cv2.imencode(".jpg", image_array)
    img_bytes = buffer.tobytes()
    return hashlib.sha256(img_bytes).hexdigest()

# So sánh hash
def compare_hash(hash1, hash2):
     return hash1 == hash2
