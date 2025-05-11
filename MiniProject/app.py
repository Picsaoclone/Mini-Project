from flask import Flask
from routes.user_routes import user_bp
from routes.login_routes import login_bp
from db import get_connection

app = Flask(__name__)
app.register_blueprint(user_bp)
app.register_blueprint(login_bp)

@app.route("/db-status")
def check_db():
    try:
        conn = get_connection()
        conn.close()
        return {"message": "✅ Đã kết nối OracleDB thành công"}
    except Exception as e:
        return {"message": f"❌ Lỗi kết nối: {str(e)}"}, 500

if __name__ == "__main__":
    app.run(debug=True)
