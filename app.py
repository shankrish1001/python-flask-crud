from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from db import get_db

app = Flask(__name__)
CORS(app)

# Required parameters
REQUIRED_PARAMS = ['firstname', 'lastname', 'email']

# Common validation
def validate_input(data):
    if not data:
        return False, ['Invalid JSON body']

    missing_or_empty = [field for field in REQUIRED_PARAMS if
                        data.get(field) is None or str(data.get(field)).strip() == '']

    if missing_or_empty:
        return False, missing_or_empty

    # number validation
    age = data['age']
    if not isinstance(age, int) or age <= 0:
        return False, ['Age must be a positive integer']

    return True, []


@app.route("/")
def home():
    try:
        with get_db() as (cursor, conn):
            cursor.execute("SELECT id, firstname, lastname, age, email, mobile FROM students")
            rows = cursor.fetchall()
            return render_template('home.html', rows=rows)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/students', methods=['GET'])
def read_all_students():
    try:
        with get_db() as (cursor, conn):
            cursor.execute("SELECT id, firstname, lastname, age, email, mobile "+
                           "FROM students ORDER BY id DESC")
            rows = cursor.fetchall()
            cols = [desc[0] for desc in cursor.description]

            if not rows:
                return jsonify({"error": "Student list not found", "status": "error"}), 404

            return jsonify({
                "cols": cols,
                "rows": rows
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create student
@app.route('/students', methods=['POST'])
def create_student():
    try:
        with get_db() as (cursor, conn):
            data = request.json
            valid, issues = validate_input(data)
            if not valid:
                return jsonify({'error': 'Missing or empty fields', 'fields': issues}), 400

            cursor.execute("INSERT INTO students(firstname, lastname, age, email, mobile) "+
                           "VALUES(%s, %s, %s, %s, %s)",
                           (data['firstname'], data['lastname'], data['age'], data['email'], data['mobile']))
            conn.commit()
            new_id = cursor.lastrowid

            if new_id:
                return jsonify({
                    "id": new_id,
                    "message": "Student created successfully",
                    "status": "success"
                }), 201
            else:
                return jsonify({"error": "Failed to create student", "status": "error"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Read student
@app.route('/students/<id>', methods=['GET'])
def read_student(id):
    try:
        with get_db() as (cursor, conn):
            cursor.execute("SELECT * FROM students WHERE id = %s", (id,))
            rows = cursor.fetchone()
            cols = [desc[0] for desc in cursor.description]

            if not rows:
                return jsonify({"error": "Student not found", "status": "error"}), 404

            return jsonify({
                "cols": cols,
                "rows": rows
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update student
@app.route('/students/<id>', methods=['PUT'])
def update_student(id):
    try:
        with get_db() as (cursor, conn):
            data = request.json
            valid, issues = validate_input(data)
            if not valid:
                return jsonify({'error': 'Missing or empty fields', 'fields': issues}), 400

            query = "UPDATE students SET firstname=%s, lastname=%s, age=%s, email=%s, mobile=%s WHERE id=%s"
            cursor.execute(query, (data['firstname'], data['lastname'], data['age'], data['email'], data['mobile'], id))
            conn.commit()

            affected_rows = cursor.rowcount

            if affected_rows>0:
                return jsonify({
                    "message": "Student details updated successfully",
                    "status": "success"
                }), 201
            else:
                return jsonify({"error": "Failed to update student", "status": "error"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete student
@app.route('/students/<id>', methods=['DELETE'])
def delete_student(id):
    try:
        with get_db() as (cursor, conn):
            cursor.execute("DELETE FROM students WHERE id = %s", (id,))
            conn.commit()

            if cursor.rowcount > 0:
                return jsonify({"message": "Student deleted successfully", "status": "success"})
            else:
                return jsonify({"error": "Student not found or delete failed", "status": "error"}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found", "status": "error"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "status": "error"}), 500

if __name__ == "__main__":
    app.run(debug=True)

