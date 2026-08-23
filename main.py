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
def descargar_pdf(placa: str = "AKI175"):
    # 1. Traer datos en tiempo real de servicios_vehiculares.py
    datos = consultar_datos_vehiculo(placa)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()
    story = []

    # 2. Agregar Logos (Encabezado)
    try:
        logo_izq = Image("logo_consultasano.png", width=140, height=40)
        logo_der = Image("logo_estudio.png", width=120, height=40)
        tabla_encabezado = Table([[logo_izq, logo_der]], colWidths=[270, 270])
        tabla_encabezado.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(tabla_encabezado)
        story.append(Spacer(1, 15))
    except Exception as e:
        print(f"No se pudieron cargar los logos: {e}")

    # 3. Título del Reporte
    titulo_style = ParagraphStyle(
        'TituloReporte',
        parent=styles['Heading1'],
        fontSize=15, leading=18,
        textColor=colors.HexColor("#1A365D"),
        alignment=1
    )
    story.append(Paragraph(f"<b>REPORTE VEHICULAR CONSOLIDADO - PLACA {datos['placa']}</b>", titulo_style))
    story.append(Spacer(1, 12))

    # 4. Tabla 1: Datos Registrales SUNARP
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

    # 5. Tabla 2: Auditoría de Alertas
    story.append(Paragraph("<b>2. AUDITORÍA EN TIEMPO REAL Y ALERTAS</b>", styles['Heading2']))
    tabla_auditoria_data = [["Módulo / Verificación", "Entidad / Fuente", "Resultado / Estado", "Nivel Riesgo"]]
    for item in datos["auditoria"]:
        tabla_auditoria_data.append([item["modulo"], item["fuente"], item["resultado"], item["riesgo"]])

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

    # 6. Banner Footer
    try:
        story.append(Spacer(1, 15))
        banner = Image("banner_footer.png", width=540, height=50)
        story.append(banner)
    except Exception:
        pass

    doc.build(story)
    buffer.seek(0)
    return Response(content=buffer.getvalue(), media_type="application/pdf")
