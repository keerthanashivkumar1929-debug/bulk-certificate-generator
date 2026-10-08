from flask import Flask, request, jsonify, send_file
from database import create_tables, get_db_connection
from certificate_generator import generate_certificate
import os

app = Flask(__name__)


create_tables()


CERTIFICATE_FOLDER = "certificates"
os.makedirs(CERTIFICATE_FOLDER, exist_ok=True)



@app.route("/")
def home():
    return {
        "message": "Bulk Certificate Generator API is running!"
    }



@app.route("/jobs", methods=["POST"])
def create_job():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    event_name = data.get("event_name")
    date = data.get("date")
    recipients = data.get("recipients")

   
    if not event_name or not date:
        return jsonify({
            "error": "event_name and date are required"
        }), 400

    
    if not isinstance(recipients, list) or len(recipients) == 0:
        return jsonify({
            "error": "recipients must be a non-empty list"
        }), 400

    connection = get_db_connection()

    
    cursor = connection.execute(
        """
        INSERT INTO jobs
        (event_name, date, status, total, successful, failed)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (event_name, date, "processing", len(recipients), 0, 0)
    )

    job_id = cursor.lastrowid
    connection.commit()

    successful = 0
    failed = 0

 
    for recipient in recipients:

        name = recipient.get("name")
        email = recipient.get("email")

        
        if not name or not email:

            connection.execute(
                """
                INSERT INTO certificates
                (job_id, recipient_name, recipient_email,
                 status, error_message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    name or "Unknown",
                    email or "Unknown",
                    "failed",
                    "Name and email are required"
                )
            )

            failed += 1
            continue

        try:

            filename = (
                f"certificate_{job_id}_{successful + failed + 1}.pdf"
            )

            file_path = os.path.join(
                CERTIFICATE_FOLDER,
                filename
            )

            
            generate_certificate(
                name,
                event_name,
                date,
                file_path
            )

          
            connection.execute(
                """
                INSERT INTO certificates
                (job_id, recipient_name, recipient_email,
                 status, file_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    name,
                    email,
                    "completed",
                    file_path
                )
            )

            successful += 1

        except Exception as error:

          
            connection.execute(
                """
                INSERT INTO certificates
                (job_id, recipient_name, recipient_email,
                 status, error_message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    name,
                    email,
                    "failed",
                    str(error)
                )
            )

            failed += 1

    
    if failed == 0:
        status = "completed"
    else:
        status = "completed_with_errors"

    connection.execute(
        """
        UPDATE jobs
        SET status = ?, successful = ?, failed = ?
        WHERE id = ?
        """,
        (status, successful, failed, job_id)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "job_id": job_id,
        "status": status,
        "total": len(recipients),
        "successful": successful,
        "failed": failed
    }), 201



@app.route("/jobs/<int:job_id>", methods=["GET"])
def get_job_status(job_id):

    connection = get_db_connection()

    job = connection.execute(
        "SELECT * FROM jobs WHERE id = ?",
        (job_id,)
    ).fetchone()

    connection.close()

    if not job:
        return jsonify({
            "error": "Job not found"
        }), 404

    return jsonify(dict(job))



@app.route("/jobs/<int:job_id>/certificates", methods=["GET"])
def get_certificates(job_id):

    connection = get_db_connection()

    certificates = connection.execute(
        """
        SELECT * FROM certificates
        WHERE job_id = ?
        """,
        (job_id,)
    ).fetchall()

    connection.close()

    return jsonify({
        "job_id": job_id,
        "certificates": [
            dict(certificate)
            for certificate in certificates
        ]
    })



@app.route("/certificates/<int:certificate_id>", methods=["GET"])
def download_certificate(certificate_id):

    connection = get_db_connection()

    certificate = connection.execute(
        """
        SELECT * FROM certificates
        WHERE id = ?
        """,
        (certificate_id,)
    ).fetchone()

    connection.close()

    if not certificate:
        return jsonify({
            "error": "Certificate not found"
        }), 404

    if certificate["status"] != "completed":
        return jsonify({
            "error": "Certificate was not generated successfully"
        }), 400

    return send_file(
        certificate["file_path"],
        as_attachment=True
    )



if __name__ == "__main__":
    app.run(debug=True)