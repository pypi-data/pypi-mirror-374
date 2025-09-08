"""Copyright 2024 Everlasting Systems and Solutions LLC (www.myeverlasting.net).
All Rights Reserved.

No part of this software or any of its contents may be reproduced, copied, modified or adapted, without the prior written consent of the author, unless otherwise indicated for stand-alone materials.

For permission requests, write to the publisher at the email address below:
office@myeverlasting.net

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
from reportlab.lib.pagesizes import letter,A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Circle,String
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO
async def make_pdf_socials(data: dict):
    title = data["title"]
    meta_description = data["meta_description"]
    google_search_desktop = data["google_search_desktop"]
    google_search_mobile = data["google_search_mobile"]
    social_media_tags = data["social_media_tags"]

    # Create a BytesIO object to store the PDF
    pdf_buffer = BytesIO()

    # Create a canvas object for the PDF
    pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)

    # Draw the title
    pdf_canvas.setFont("Helvetica-Bold", 16)
    pdf_canvas.drawString(50, 750, title)

    # Draw the meta description
    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.drawString(50, 700, "Meta Description:")
    pdf_canvas.drawString(50, 680, meta_description)

    # Draw the Google Search Results Preview
    pdf_canvas.setFont("Helvetica-Bold", 14)
    pdf_canvas.drawString(50, 630, "Google Search Results Preview:")
    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.drawString(50, 610, "Desktop version:")
    pdf_canvas.drawString(50, 590, google_search_desktop)
    pdf_canvas.drawString(50, 570, "Mobile version:")
    pdf_canvas.drawString(50, 550, google_search_mobile)

    # Draw the Social Media Meta Tags
    pdf_canvas.setFont("Helvetica-Bold", 14)
    pdf_canvas.drawString(50, 510, "Social Media Meta Tags:")
    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.drawString(50, 490, social_media_tags)

    # Save the PDF and move to the beginning of the buffer
    pdf_canvas.showPage()
    pdf_canvas.save()
    pdf_buffer.seek(0)
    return pdf_buffer