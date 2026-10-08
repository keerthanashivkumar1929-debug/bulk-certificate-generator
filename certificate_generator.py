from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
import os


def generate_certificate(name, event_name, date, output_path):
    """
    Generate one certificate PDF for a recipient.
    """

    width, height = landscape(A4)

    
    pdf = canvas.Canvas(output_path, pagesize=(width, height))

    
    pdf.setFont("Helvetica-Bold", 32)
    pdf.drawCentredString(
        width / 2,
        height - 120,
        "CERTIFICATE OF PARTICIPATION"
    )

    
    pdf.setFont("Helvetica", 18)
    pdf.drawCentredString(
        width / 2,
        height - 200,
        "This certificate is proudly presented to"
    )


    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(
        width / 2,
        height - 250,
        name
    )

    
    pdf.setFont("Helvetica", 18)
    pdf.drawCentredString(
        width / 2,
        height - 310,
        f"for participating in {event_name}"
    )

    pdf.drawCentredString(
        width / 2,
        height - 350,
        f"Date: {date}"
    )

    
    pdf.line(
        width / 2 - 80,
        100,
        width / 2 + 80,
        100
    )

    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(
        width / 2,
        80,
        "Authorized Signature"
    )

    pdf.save()