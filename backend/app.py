from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)   # allows frontend to connect

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="anupama@900",
    database="pothole_db"
)

cursor = db.cursor(dictionary=True)

@app.route('/')
def home():
    return "Backend is running successfully!"


@app.route('/report', methods=['POST'])
def report_pothole():
    data = request.json

    query = """
    INSERT INTO potholes (latitude, longitude, severity)
    VALUES (%s, %s, %s)
    """

    cursor.execute(query, (
        data['latitude'],
        data['longitude'],
        data['severity']
    ))

    db.commit()

    return jsonify({"status": "success"})


# ✅ FIXED: single decorator + strict aggregation
@app.route('/get-potholes', methods=['GET'])
def get_potholes():

    cursor.execute("SELECT latitude, longitude, severity FROM potholes")
    potholes = cursor.fetchall()

    grouped = {}

    # Severity priority mapping
    priority = {"High": 3, "Medium": 2, "Low": 1}

    for p in potholes:

        lat = round(float(p['latitude']), 3)
        lon = round(float(p['longitude']), 3)

        key = (lat, lon)
        severity = p['severity']

        if key not in grouped:
            grouped[key] = severity
        else:
            # keep highest severity only
            if priority[severity] > priority[grouped[key]]:
                grouped[key] = severity

    result = []

    for (lat, lon), severity in grouped.items():
        result.append({
            "latitude": lat,
            "longitude": lon,
            "severity": severity
        })

    return jsonify(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)