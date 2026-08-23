import io
import os
import traceback
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

from servicios_vehiculares import consultar_datos_vehiculo

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def index():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Servicio activo</h1>"

@app.get("/descargar-pdf")
def descargar_pdf(placa: str = "AKI175"):
    try:
        # Consulta de datos dinámicos
        datos = consultar_datos_vehiculo(placa)
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
        )
        styles = getSampleStyleSheet()
        story = []

        # ==========================================
        # PÁGINA 1: DATOS, TRANSFERENCIA Y AUDITORÍA
        # ==========================================

        # Logos
        if os.path.exists("logo_consultasano.png") and os.path.exists("logo_estudio.png"):
            try:
                logo_izq = Image("logo_consultasano.png", width=140, height=40)
                logo_der = Image("logo_estudio.png", width=120, height=40)
                header_table = Table([[logo_izq, logo_der]], colWidths=[270, 270])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(header_table)
                story.append(Spacer(1, 8))
            except Exception as e:
                print(f"Error logos: {e}")

        # Título
        titulo_style = ParagraphStyle(
            'TituloReporte',
            parent=styles['Heading1'],
            fontSize=14, leading=16,
            textColor=colors.HexColor("#1A365D"),
            alignment=1
        )
        story.append(Paragraph(f"<b>REPORTE VEHICULAR CONSOLIDADO - PLACA {datos.get('placa', placa)}</b>", titulo_style))
        story.append(Spacer(1, 8))

        # 1. DATOS SUNARP
        story.append(Paragraph("<b>1. DATOS REGISTRALES (SUNARP)</b>", styles['Heading2']))
        tabla_sunarp_data = [
            ["Oficina Registral", datos.get("oficina_registral", "-"), "Marca", datos.get("marca", "-")],
            ["Modelo", datos.get("modelo", "-"), "Año Fab.", datos.get("anio", "-")],
            ["Color", datos.get("color", "-"), "VIN", datos.get("vin", "-")],
            ["N° Motor", datos.get("motor", "-"), "Carrocería", datos.get("carroceria", "-")],
            ["Combustible", datos.get("combustible", "-"), "", ""]
        ]
        t_sunarp = Table(tabla_sunarp_data, colWidths=[100, 160, 100, 160])
        t_sunarp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_sunarp)
        story.append(Spacer(1, 8))

        # 2. COSTOS DE TRANSFERENCIA VEHICULAR
        story.append(Paragraph("<b>2. ESTIMACIÓN DE VALOR Y COSTOS DE TRANSFERENCIA</b>", styles['Heading2']))
        tabla_transf_data = [
            ["Concepto / Gastos", "Monto Estimado (S/)", "Observación / Referencia"],
            ["Valor Comercial Referencial", datos.get("valor_referencial", "S/ 28,500.00"), "Según marca, modelo y año"],
            ["Derechos Registrales (SUNARP)", "S/ 90.00", "Tasa oficial de inscripción"],
            ["Gastos Notariales (Estimado)", "S/ 250.00 - S/ 350.00", "Varía según notaría seleccionada"],
            ["Impuesto Vehicular (SAT)", datos.get("impuesto_sat", "Aplica / Exento"), "Verificación según antigüedad"]
        ]
        t_transf = Table(tabla_transf_data, colWidths=[180, 140, 200])
        t_transf.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_transf)
        story.append(Spacer(1, 8))

        # 3. AUDITORÍA
        story.append(Paragraph("<b>3. AUDITORÍA EN TIEMPO REAL Y ALERTAS</b>", styles['Heading2']))
        tabla_auditoria_data = [["Módulo / Verificación", "Entidad / Fuente", "Resultado / Estado", "Nivel Riesgo"]]
        for item in datos.get("auditoria", []):
            tabla_auditoria_data.append([item["modulo"], item["fuente"], item["resultado"], item["riesgo"]])

        t_auditoria = Table(tabla_auditoria_data, colWidths=[140, 110, 170, 100])
        t_auditoria.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_auditoria)

        # Banner Footer Página 1
        if os.path.exists("banner_footer.png"):
            try:
                story.append(Spacer(1, 6))
                story.append(Image("banner_footer.png", width=540, height=35))
            except Exception:
                pass

        # ==========================================
        # PÁGINA 2: INFOGRAFÍA Y SERVICIOS
        # ==========================================
        story.append(PageBreak())

        # Banner Estudio Córdova
        if os.path.exists("banner_estudio_cordova.png"):
            try:
                story.append(Image("banner_estudio_cordova.png", width=540, height=180))
                story.append(Spacer(1, 10))
            except Exception as e:
                print(f"Error banner estudio: {e}")

        # Infografía Principal de Servicios Vehiculares
        if os.path.exists("infografia_servicios.png"):
            try:
                story.append(Image("infografia_servicios.png", width=540, height=450))
            except Exception as e:
                print(f"Error infografía: {e}")

        doc.build(story)
        buffer.seek(0)
        return Response(content=buffer.getvalue(), media_type="application/pdf")

    except Exception as general_err:
        print("ERROR AL GENERAR PDF:")
        traceback.print_exc()
        return Response(content=f"Error al generar el PDF: {str(general_err)}", status_code=500)
