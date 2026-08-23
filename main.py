import io
import os
import datetime
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
    return "<h1>ConsultaSano - Servicio Activo</h1>"

@app.get("/descargar-pdf")
def descargar_pdf(placa: str = "AKI175"):
    try:
        # Consulta en tiempo real (evita repetir la placa anterior)
        datos = consultar_datos_vehiculo(placa)
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
        )
        styles = getSampleStyleSheet()
        story = []

        # Fecha y Hora actual
        ahora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # ==========================================
        # ENCABEZADO: LOGO CONSULTASANO (IZQ) Y FECHA/HORA/PLACA (DER)
        # ==========================================
        
        # Bloque Izquierdo: Logo
        logo_elem = Paragraph("<b>ConsultaSano.pe</b>", styles['Heading2'])
        if os.path.exists("logo_consultasano.png"):
            try:
                logo_elem = Image("logo_consultasano.png", width=140, height=40)
            except Exception:
                pass

        # Bloque Derecho: Reemplazo del logo por Metadatos de la Consulta
        info_cabecera_style = ParagraphStyle(
            'CabeceraDer',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            alignment=2,
            textColor=colors.HexColor("#2D3748")
        )
        info_cabecera_text = f"""
        <b>FECHA:</b> {ahora.split(' ')[0]}<br/>
        <b>HORA:</b> {ahora.split(' ')[1]}<br/>
        <b>VEHÍCULO A CONSULTAR:</b> {datos.get('placa', placa).upper()}
        """
        info_elem = Paragraph(info_cabecera_text, info_cabecera_style)

        header_table = Table([[logo_elem, info_elem]], colWidths=[270, 270])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))

        # ==========================================
        # TÍTULO PRINCIPAL (LETRAS MORADAS)
        # ==========================================
        titulo_morado_style = ParagraphStyle(
            'TituloMorado',
            parent=styles['Heading1'],
            fontSize=14, leading=17,
            textColor=colors.HexColor("#6B46C1"),  # Letras Moradas
            alignment=1
        )
        story.append(Paragraph(
            f"<b>REPORTE E INFORME VEHICULAR CONSOLIDADO - PLACA {datos.get('placa', placa).upper()}</b>", 
            titulo_morado_style
        ))
        story.append(Spacer(1, 10))

        # Texto Informativo Inicial
        intro_style = ParagraphStyle('IntroStyle', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor("#4A5568"))
        story.append(Paragraph(
            "<b>ESTADO DEL INFORME:</b> El presente documento consolida la información registral, técnica, tributaria y "
            "legal en tiempo real obtenida de las plataformas oficiales (SUNARP, SUTRAN, SAT, ATU, MTC y APESEG).",
            intro_style
        ))
        story.append(Spacer(1, 8))

        # ==========================================
        # 1. DATOS REGISTRALES (SUNARP)
        # ==========================================
        story.append(Paragraph("<b>1. DATOS REGISTRALES Y CARACTERÍSTICAS (SUNARP)</b>", styles['Heading2']))
        tabla_sunarp_data = [
            ["Oficina Registral", datos.get("oficina_registral", "-"), "Marca", datos.get("marca", "-")],
            ["Modelo", datos.get("modelo", "-"), "Año Fab.", datos.get("anio", "-")],
            ["Color", datos.get("color", "-"), "VIN / Serie", datos.get("vin", "-")],
            ["N° Motor", datos.get("motor", "-"), "Carrocería", datos.get("carroceria", "-")],
            ["Combustible", datos.get("combustible", "-"), "Estado", datos.get("estado", "EN CIRCULACION")]
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
        story.append(Spacer(1, 10))

        # ==========================================
        # 2. PROPIETARIOS, TRACTO Y ESTIMACIÓN DE TRANSFERENCIA
        # ==========================================
        story.append(Paragraph("<b>2. PROPIETARIOS Y ESTIMACIÓN DE COSTOS DE TRANSFERENCIA</b>", styles['Heading2']))
        tabla_transf_data = [
            ["Concepto / Evaluación", "Detalle / Monto Estimado", "Observación Legal / Referencia"],
            ["Propietario(s) Registral(es)", datos.get("propietarios", "Verificado en Partida"), "Titularidad en SUNARP"],
            ["Valor Comercial Referencial", datos.get("valor_referencial", "S/ 28,500.00"), "Estimado según año y modelo"],
            ["Derechos Registrales (SUNARP)", "S/ 90.00", "Tasa oficial de inscripción"],
            ["Gastos Notariales (Estimado)", "S/ 250.00 - S/ 350.00", "Varía según notaría elegida"],
            ["Impuesto Vehicular (SAT)", datos.get("impuesto_sat", "Aplica / Exento"), "Sujeto a antigüedad registral"]
        ]
        t_transf = Table(tabla_transf_data, colWidths=[160, 160, 220])
        t_transf.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#6B46C1")), # Cabecera Morada
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_transf)
        story.append(Spacer(1, 10))

        # ==========================================
        # 3. AUDITORÍA EN TIEMPO REAL
        # ==========================================
        story.append(Paragraph("<b>3. AUDITORÍA INTEGRAL DE PAPELETAS Y ALERTAS DE RIESGO</b>", styles['Heading2']))
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

        # Footer Página 1
        if os.path.exists("banner_footer.png"):
            try:
                story.append(Spacer(1, 6))
                story.append(Image("banner_footer.png", width=540, height=35))
            except Exception:
                pass

        # ==========================================
        # PÁGINA 2: INFOGRAFÍAS Y SERVICIOS
        # ==========================================
        story.append(PageBreak())

        if os.path.exists("banner_estudio_cordova.png"):
            try:
                story.append(Image("banner_estudio_cordova.png", width=540, height=180))
                story.append(Spacer(1, 10))
            except Exception as e:
                print(f"Error banner estudio: {e}")

        if os.path.exists("infografia_servicios.png"):
            try:
                story.append(Image("infografia_servicios.png", width=540, height=450))
            except Exception as e:
                print(f"Error infografía: {e}")

        doc.build(story)
        buffer.seek(0)
        return Response(content=buffer.getvalue(), media_type="application/pdf")

    except Exception as general_err:
        print("ERROR GENERANDO PDF:")
        traceback.print_exc()
        return Response(content=f"Error al generar el PDF: {str(general_err)}", status_code=500)
