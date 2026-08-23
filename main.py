import io
import os
import traceback
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# Importación de la función multihilo
try:
    from servicios_vehiculares import consultar_datos_vehiculo
except Exception as e:
    print(f"Error al importar servicios_vehiculares: {e}")

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
        # 1. Traer datos dinámicos en vivo
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
        # PÁGINA 1: LOGOS, DATOS SUNARP Y AUDITORÍA
        # ==========================================

        # Encabezado: Logos
        logo_izq_path = "logo_consultasano.png"
        logo_der_path = "logo_estudio.png"
        
        if os.path.exists(logo_izq_path) and os.path.exists(logo_der_path):
            try:
                logo_izq = Image(logo_izq_path, width=140, height=40)
                logo_der = Image(logo_der_path, width=120, height=40)
                header_table = Table([[logo_izq, logo_der]], colWidths=[270, 270])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(header_table)
                story.append(Spacer(1, 10))
            except Exception as img_err:
                print(f"Aviso al procesar logos: {img_err}")

        # Título principal
        titulo_style = ParagraphStyle(
            'TituloReporte',
            parent=styles['Heading1'],
            fontSize=15, leading=18,
            textColor=colors.HexColor("#1A365D"),
            alignment=1
        )
        story.append(Paragraph(f"<b>REPORTE VEHICULAR CONSOLIDADO - PLACA {datos['placa']}</b>", titulo_style))
        story.append(Spacer(1, 10))

        # Tabla 1: Datos Registrales SUNARP (Traídos dinámicamente)
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
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_sunarp)
        story.append(Spacer(1, 12))

        # Tabla 2: Auditoría en Tiempo Real
        story.append(Paragraph("<b>2. AUDITORÍA EN TIEMPO REAL Y ALERTAS</b>", styles['Heading2']))
        tabla_auditoria_data = [["Módulo / Verificación", "Entidad / Fuente", "Resultado / Estado", "Nivel Riesgo"]]
        for item in datos.get("auditoria", []):
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

        # Banner Footer Página 1
        banner_footer_path = "banner_footer.png"
        if os.path.exists(banner_footer_path):
            try:
                story.append(Spacer(1, 10))
                story.append(Image(banner_footer_path, width=540, height=45))
            except Exception:
                pass

        # ==========================================
        # PÁGINA 2: SALTO DE PÁGINA E INFOGRAFÍAS
        # ==========================================
        story.append(PageBreak())

        # Banner Estudio Córdova (Proporción 1/3)
        banner_estudio_path = "banner_estudio_cordova.png"
        if os.path.exists(banner_estudio_path):
            try:
                story.append(Image(banner_estudio_path, width=540, height=210))
                story.append(Spacer(1, 10))
            except Exception as e:
                print(f"Aviso al cargar banner estudio: {e}")

        # Infografía de Servicios Vehiculares y Legales (Proporción 2/3)
        infografia_path = "infografia_servicios.png"
        if os.path.exists(infografia_path):
            try:
                story.append(Image(infografia_path, width=540, height=430))
            except Exception as e:
                print(f"Aviso al cargar infografía servicios: {e}")

        # Construcción y entrega
        doc.build(story)
        buffer.seek(0)
        return Response(content=buffer.getvalue(), media_type="application/pdf")

    except Exception as general_err:
        # En caso de fallo crítico, imprime la traza completa en la consola de Render
        print("ERROR CRÍTICO GENERANDO PDF:")
        traceback.print_exc()
        return Response(content=f"Error al generar el PDF: {str(general_err)}", status_code=500)
