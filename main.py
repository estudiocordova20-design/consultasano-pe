from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import io
import os
from servicios_vehiculares import consultar_datos_vehiculo
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/descargar-pdf")
def descargar_pdf(placa: str = "W2G522"):
    # 1. Consultar datos en tiempo real (SUNARP, SUTRAN, SAT, MTC, APESEG)
    datos = consultar_datos_vehiculo(placa)
    
    # 2. Configurar buffer y documento PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    story = []

    # 3. Encabezado / Título
    titulo_style = ParagraphStyle(
        'TituloReporte',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1A365D"),
        alignment=1
    )
    story.append(Paragraph(f"<b>REPORTE VEHICULAR CONSOLIDADO - PLACA {datos['placa']}</b>", titulo_style))
    story.append(Spacer(1, 12))

    # 4. Tabla 1: Datos de SUNARP
    story.append(Paragraph("<b>1. DATOS REGISTRALES (SUNARP)</b>", styles['Heading2']))
    tabla_sunarp_data = [
        ["Oficina Registral", datos["oficina_registral"], "Marca", datos["marca"]],
        ["Modelo", datos["modelo"], "Año Fab.", datos["anio"]],
        ["Color", datos["color"], "VIN", datos["vin"]],
        ["N° Motor", datos["motor"], "Carrocería", datos["carroceria"]],
        ["Combustible", datos["combustible"], "", ""]
    ]
    t_sunarp = Table(tabla_sunarp_data, colWidths=[100, 160, 100, 160])
    t_sunarp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_sunarp)
    story.append(Spacer(1, 14))

    # 5. Tabla 2: Auditoría en Tiempo Real (SUTRAN, SAT, MTC, PNP, APESEG)
    story.append(Paragraph("<b>2. AUDITORÍA EN TIEMPO REAL Y ALERTAS</b>", styles['Heading2']))
    tabla_auditoria_data = [["Módulo / Verificación", "Entidad / Fuente", "Resultado / Estado", "Nivel Riesgo"]]
    
    for item in datos["auditoria"]:
        tabla_auditoria_data.append([
            item["modulo"],
            item["fuente"],
            item["resultado"],
            item["riesgo"]
        ])

    t_auditoria = Table(tabla_auditoria_data, colWidths=[140, 110, 170, 100])
    t_auditoria.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_auditoria)

    # 6. Construir PDF y retornar respuesta
    doc.build(story)
    buffer.seek(0)
    
    return Response(content=buffer.getvalue(), media_type="application/pdf")
