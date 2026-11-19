import io
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def build_excel_report(result):
    output = io.BytesIO()
    wb = Workbook()
    executive = wb.active
    executive.title = "Executive Recommendations"
    executive.append(["Title", "Priority", "Description", "Expected Impact"])
    recs = result["outputs"]["Executive Decision"]["key_results"]["recommendations"]
    for rec in recs:
        executive.append([rec["title"], rec["priority"], rec["description"], rec["expected_impact"]])
    for agent, payload in result["outputs"].items():
        ws = wb.create_sheet(agent[:31])
        ws.append(["Status", "Key", "Value"])
        ws.append([payload["status"], "", ""])
        for key, value in payload["key_results"].items():
            if key not in ("clean_data", "order_ids"):
                ws.append(["", key, str(value)])
    wb.save(output)
    output.seek(0)
    return output


def build_pdf_report(result):
    output = io.BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    width, height = A4
    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, "Agent Gatekeeper - Management Report")
    y -= 24
    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, y, "SYNTHETIC DEMONSTRATION DATA - education only")
    y -= 24

    recs = result["outputs"]["Executive Decision"]["key_results"]["recommendations"]
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y, "Ranked recommendations")
    y -= 18
    pdf.setFont("Helvetica", 10)
    for rec in recs:
        lines = f"{rec['priority']} - {rec['title']}: {rec['description']}"
        pdf.drawString(40, y, lines[:110])
        y -= 18
        if y < 50:
            pdf.showPage()
            y = height - 50
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(40, y, "Assumptions")
    y -= 16
    pdf.setFont("Helvetica", 9)
    for assumption in result["outputs"]["Executive Decision"]["key_results"]["assumptions"]:
        pdf.drawString(40, y, "- " + assumption)
        y -= 14
    pdf.save()
    output.seek(0)
    return output
