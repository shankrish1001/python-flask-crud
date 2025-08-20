from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

con = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Shan@Data#1234",
    database = "student_db"
)

@app.route("/", methods=["GET"])
def get_tbl():
    cur = con.cursor()
    cur.execute("SHOW TABLES;")
    tbls = cur.fetchall()
    cur.close()
    con.close()

    tbl_names = [tbl[0] for tbl in tbls]
    return jsonify({"tables": tbl_names}), 200

if __name__ == "__main__":
    app.run(debug=True)

