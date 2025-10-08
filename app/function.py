from app import mysql
from werkzeug.security import generate_password_hash
from flask import jsonify

# ---------------------
# CREATE
# ---------------------
def create_user(data):
    nama = data['nama']
    email = data['email']
    password = generate_password_hash(data['password'])
    peran = data.get('peran', 'pelanggan')

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO users (nama, email, password_hash, peran)
        VALUES (%s, %s, %s, %s)
    """, (nama, email, password, peran))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "✅ User created successfully"}), 201


# ---------------------
# READ ALL
# ---------------------
def get_all_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nama, email, peran FROM users")
    users = cur.fetchall()
    cur.close()

    result = [{"id": u[0], "nama": u[1], "email": u[2], "peran": u[3]} for u in users]
    return jsonify(result)


# ---------------------
# READ ONE
# ---------------------
def get_user_by_id(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nama, email, peran FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()

    if user:
        return jsonify({"id": user[0], "nama": user[1], "email": user[2], "peran": user[3]})
    else:
        return jsonify({"message": "❌ User not found"}), 404


# ---------------------
# UPDATE
# ---------------------
def update_user(user_id, data):
    nama = data['nama']
    email = data['email']
    peran = data.get('peran', 'pelanggan')

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE users
        SET nama = %s, email = %s, peran = %s
        WHERE id = %s
    """, (nama, email, peran, user_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "✅ User updated successfully"})


# ---------------------
# DELETE
# ---------------------
def delete_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "🗑️ User deleted successfully"})
