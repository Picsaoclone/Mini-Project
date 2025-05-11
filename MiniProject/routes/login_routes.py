from flask import Blueprint, request, jsonify
from db import get_connection
from face_utils import extract_face, image_to_hash, compare_hash

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["POST"])
def login_face():
    image = request.files["image"]
    image_path = "temp_login.jpg"
    image.save(image_path)

    # Tách khuôn mặt
    face = extract_face(image_path)
    if face is None:
        print("❌ Không phát hiện khuôn mặt trong ảnh đăng nhập.")
        return jsonify({"status": "fail", "msg": "No face detected"}), 400

    # Tạo hash từ ảnh
    login_hash = image_to_hash(face)
    print("🔑 HASH ĐĂNG NHẬP:", login_hash)

    # Lấy dữ liệu từ DB
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT USER_ID, FACE_ENCODING FROM USERS")
    users = cur.fetchall()

    # So sánh với từng user
    for user_id, face_hash in users:
        print(f"👤 So với USER_ID={user_id} → HASH={face_hash}")
        face_hash = str(face_hash).strip()
        if login_hash == face_hash:
            print("✅ MATCHED!")
            cur.execute("""
                INSERT INTO LOGIN_HISTORY (HISTORY_ID, USER_ID, STATUS)
                VALUES (LOGIN_HISTORY_SEQ.NEXTVAL, :user_id, 'Success')
            """, {"user_id": user_id})
            conn.commit()
            return jsonify({"status": "success", "user_id": user_id}), 200

    # Không match
    print("❌ Không tìm thấy người dùng phù hợp.")
    cur.execute("""
        INSERT INTO LOGIN_HISTORY (HISTORY_ID, USER_ID, STATUS)
        VALUES (LOGIN_HISTORY_SEQ.NEXTVAL, NULL, 'Failed')
    """)
    conn.commit()
    return jsonify({"status": "fail"}), 401
