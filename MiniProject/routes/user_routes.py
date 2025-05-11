from flask import Blueprint, request, jsonify
from db import get_connection
from face_utils import extract_face, image_to_hash

user_bp = Blueprint("user", __name__)

@user_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.form
        image = request.files["image"]
        image_path = "temp_register.jpg"
        image.save(image_path)

        # Tách khuôn mặt
        face = extract_face(image_path)
        if face is None:
            print("❌ Không phát hiện khuôn mặt trong ảnh đăng ký.")
            return jsonify({"status": "fail", "msg": "No face found"}), 400

        # Tạo mã hash
        face_hash = image_to_hash(face)
        print("🔐 HASH ĐĂNG KÝ:", face_hash)

        # Ghi vào DB
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO USERS (USER_ID, FULL_NAME, EMAIL, FACE_ENCODING)
            VALUES (USERS_SEQ.NEXTVAL, :name, :email, :encoding)
        """, {
            "name": data["name"],
            "email": data["email"],
            "encoding": face_hash
        })
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "success"}), 201

    except Exception as e:
        print("❌ Lỗi khi đăng ký:", str(e))
        return jsonify({"status": "fail", "msg": "Server error"}), 500

@user_bp.route("/update_user", methods=["POST"])
def update_user():
    try:
        data = request.form
        image = request.files.get("image", None)
        image_path = "temp_update.jpg"
        user_id = int(data["user_id"])
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()

        print("UPDATE REQUEST:", {"user_id": user_id, "name": name, "email": email})

        conn = get_connection()
        cur = conn.cursor()

        # Nếu có ảnh
        if image and image.filename != "":
            image.save(image_path)
            face = extract_face(image_path)
            if face is None:
                return jsonify({"status": "fail", "msg": "No face found"}), 400
            face_hash = image_to_hash(face)

            cur.execute("""
                UPDATE USERS
                SET FULL_NAME = :name, EMAIL = :email, FACE_ENCODING = :encoding
                WHERE USER_ID = :user_id
            """, {
                "name": name,
                "email": email,
                "encoding": face_hash,
                "user_id": user_id
            })
        else:
            # Không có ảnh
            cur.execute("""
                UPDATE USERS
                SET FULL_NAME = :name, EMAIL = :email
                WHERE USER_ID = :user_id
            """, {
                "name": name,
                "email": email,
                "user_id": user_id
            })

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("❌ UPDATE ERROR:", str(e))
        return jsonify({"status": "fail", "msg": "Server error"}), 500



@user_bp.route("/delete_user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM USERS WHERE USER_ID = :user_id", {"user_id": user_id})
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "success"}), 200

@user_bp.route("/get_users")
def get_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT USER_ID, FULL_NAME, EMAIL, FACE_ENCODING FROM USERS")

    users = []
    for row in cur.fetchall():
        users.append({
            "USER_ID": row[0],
            "FULL_NAME": row[1],
            "EMAIL": row[2],
            "FACE_ENCODING": str(row[3])[:64]  # Cắt ngắn lại nếu cần
        })

    cur.close()
    conn.close()
    return jsonify(users)
