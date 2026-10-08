from database import db


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default="pending")
    total = db.Column(db.Integer, default=0)
    successful = db.Column(db.Integer, default=0)
    failed = db.Column(db.Integer, default=0)


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, nullable=False)
    recipient_name = db.Column(db.String(200), nullable=False)
    recipient_email = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default="pending")
    file_path = db.Column(db.String(500), nullable=True)
    error_message = db.Column(db.String(500), nullable=True)