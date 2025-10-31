from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
from ipaddress import ip_network

# Example list of subnets, separate by comma
cidrs_input = """
10.66.149.0/24, 10.66.148.0/24, 10.66.147.0/24, 10.66.144.128/27, 10.66.144.32/27,
10.32.234.0/23, 10.32.232.0/23, 10.32.230.0/23, 10.32.228.0/23, 10.32.226.0/23,
10.32.224.0/23, 10.32.212.0/22, 10.32.208.0/22, 10.32.204.0/22, 10.32.200.0/22,
10.32.196.0/22, 10.32.192.0/22, 10.32.224.128/25, 10.66.144.32/28
"""

networks = [ip_network(x.strip(), strict=False) for x in cidrs_input.split(",") if x.strip()]

records = []
for i, a in enumerate(networks):
    for j, b in enumerate(networks):
        if i >= j:
            continue
        overlap = a.overlaps(b)
        records.append({
            "A": str(a),
            "B": str(b),
            "Overlap": overlap,
            "A_in_B": a.subnet_of(b),
            "B_in_A": b.subnet_of(a),
            "A_range": f"{a.network_address} - {a.broadcast_address}",
            "B_range": f"{b.network_address} - {b.broadcast_address}",
            "Intersection": f"{max(a.network_address, b.network_address)} - {min(a.broadcast_address, b.broadcast_address)}" if overlap else ""
        })

df = pd.DataFrame(records)
df_overlap = df[df["Overlap"] == True]

# Generate PDF
pdf_file = "subnet_overlaps_report.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=A4)
styles = getSampleStyleSheet()
elements = []

elements.append(Paragraph("=== Overlapping Pairs ===", styles["Heading2"]))
if df_overlap.empty:
    elements.append(Paragraph("No overlaps found.", styles["Normal"]))
else:
    data_overlap = [df_overlap.columns.tolist()] + df_overlap.values.tolist()
    table_overlap = Table(data_overlap, repeatRows=1)
    table_overlap.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 7),
        ("BOX", (0,0), (-1,-1), 0.25, colors.black),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    elements.append(table_overlap)

elements.append(Spacer(1, 12))
elements.append(Paragraph("=== All Pairwise Checks ===", styles["Heading2"]))

data_all = [df.columns.tolist()] + df.values.tolist()
table_all = Table(data_all, repeatRows=1)
table_all.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.grey),
    ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
    ("ALIGN", (0,0), (-1,-1), "LEFT"),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 7),
    ("BOX", (0,0), (-1,-1), 0.25, colors.black),
    ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
]))
elements.append(table_all)

doc.build(elements)
pdf_file