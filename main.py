from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import io

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/descargar-pdf")
def descargar_pdf(placa: str = "W2G522"):
    placa_clean = placa.upper().strip()
    buffer = io.BytesIO()
    
    # Configuración de márgenes compactos
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=36, 
        leftMargin=36, 
        topMargin=36, 
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    style_title = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, leading=22, textColor=colors.HexColor("#0A2240"))
    style_subtitle = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor("#00B050"))
    style_sec_header = ParagraphStyle('SecHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.white)
    style_cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.HexColor("#0A2240"))
    style_cell_normal = ParagraphStyle('CellNormal', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=11, textColor=colors.HexColor("#333333"))
    style_status_ok = ParagraphStyle('StatusOk', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.HexColor("#008000"))
    style_footer_title = ParagraphStyle('FooterTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=colors.HexColor("#0A2240"))
    style_footer_text = ParagraphStyle('FooterText', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor("#444444"))

    elements = []

    # 1. ENCABEZADO PRINCIPAL (HEADER)
    header_data = [
        [
            Paragraph("<b>ConsultaSano<font color='#00B050'>.pe</font></b>", style_title),
            Paragraph(f"<b>FECHA EMISIÓN:</b> {datetime.now().strftime('%Y-%m-%d')}<br/><b>PLACA AUDITADA:</b> {placa_clean}", style_cell_bold)
        ],
        [
            Paragraph("AUDITORÍA VEHICULAR INTEGRAL Y LEGAL", style_subtitle),
            Paragraph("<b>OFICINA REGISTRAL:</b> HUANCAYO", style_cell_normal)
        ]
    ]
    header_table = Table(header_data, colWidths=[340, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0A2240"), spaceAfter=10))

    # 2. SECCIÓN SUNARP - FICHA TÉCNICA REGISTRAL
    elements.append(Table([[Paragraph("1. FICHA TÉCNICA REGISTRAL (SUNARP)", style_sec_header)]], colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0A2240")), ('BOTTOMPADDING', (0,0), (-1,-1), 4), ('TOPPADDING', (0,0), (-1,-1), 4)]))
    elements.append(Spacer(1, 4))
    
    sunarp_data = [
        [Paragraph("Marca:", style_cell_bold), Paragraph("CHERY", style_cell_normal), Paragraph("Modelo:", style_cell_bold), Paragraph("TIGGO", style_cell_normal)],
        [Paragraph("Año Fab.:", style_cell_bold), Paragraph("2013", style_cell_normal), Paragraph("Color:", style_cell_bold), Paragraph("NEGRO AZABACHE", style_cell_normal)],
        [Paragraph("N° Serie / VIN:", style_cell_bold), Paragraph("LVVDB11B9DD106355", style_cell_normal), Paragraph("N° Motor:", style_cell_bold), Paragraph("SQR481FFFC02315", style_cell_normal)],
        [Paragraph("Carrocería:", style_cell_bold), Paragraph("SUV", style_cell_normal), Paragraph("Combustible:", style_cell_bold), Paragraph("GASOLINA", style_cell_normal)],
    ]
    sunarp_table = Table(sunarp_data, colWidths=[90, 180, 90, 180])
    sunarp_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F8F9FA")),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor("#F8F9FA")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(sunarp_table)
    elements.append(Spacer(1, 10))

    # 3. SECCIÓN TRAZABILIDAD Y PROPIETARIOS
    elements.append(Table([[Paragraph("2. TRAZABILIDAD Y TRACTO SUCESIVO (SÍGUELO SUNARP)", style_sec_header)]], colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0A2240")), ('BOTTOMPADDING', (0,0), (-1,-1), 4), ('TOPPADDING', (0,0), (-1,-1), 4)]))
    elements.append(Spacer(1, 4))

    prop_data = [
        [Paragraph("Titular Actual / Presentante", style_cell_bold), Paragraph("Partida", style_cell_bold), Paragraph("Acto Inscrito", style_cell_bold), Paragraph("Título / Fecha", style_cell_bold)],
        [Paragraph("CORDOVA PALOMINO RICHARD SEBASTIAN", style_cell_normal), Paragraph("60548021", style_cell_normal), Paragraph("COMPRA - VENTA", style_cell_normal), Paragraph("03558353 - 2022", style_cell_normal)],
    ]
    prop_table = Table(prop_data, colWidths=[200, 80, 130, 130])
    prop_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F0F4F8")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(prop_table)
    elements.append(Spacer(1, 10))

    # 4. SECCIÓN EVALUACIÓN DE MULTAS, INSPECCIONES Y SOAT
    elements.append(Table([[Paragraph("3. EVALUACIÓN VISUAL DE SEGURIDAD, CITV, SOAT E INFRACCIONES", style_sec_header)]], colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0A2240")), ('BOTTOMPADDING', (0,0), (-1,-1), 4), ('TOPPADDING', (0,0), (-1,-1), 4)]))
    elements.append(Spacer(1, 4))

    sec_data = [
        [Paragraph("Módulo Evaluado", style_cell_bold), Paragraph("Entidad Fiscalizadora", style_cell_bold), Paragraph("Estado / Diagnóstico Visual", style_cell_bold)],
        [Paragraph("Alerta de Robo PNP", style_cell_normal), Paragraph("DIROVE / PNP", style_cell_bold), Paragraph("✔ SIN ORDEN DE CAPTURA VIGENTE", style_status_ok)],
        [Paragraph("Vigencia de SOAT", style_cell_normal), Paragraph("APESEG / MAPFRE", style_cell_bold), Paragraph("✔ VIGENTE (MAPFRE PERÚ)", style_status_ok)],
        [Paragraph("Inspección Técnica (CITV)", style_cell_normal), Paragraph("MTC / CITV PERÚ", style_cell_bold), Paragraph("✔ APROBADO Y VIGENTE", style_status_ok)],
        [Paragraph("Certificación GNV/GLP", style_cell_normal), Paragraph("INFOGAS", style_cell_bold), Paragraph("✔ SIN CONVERSIÓN / REGISTRADO", style_status_ok)],
        [Paragraph("Récord Infracciones Tránsito", style_cell_normal), Paragraph("SUTRAN / MTC", style_cell_bold), Paragraph("✔ 0 PAPELETAS PENDIENTES", style_status_ok)],
        [Paragraph("Fiscalización Municipal", style_cell_normal), Paragraph("SAT LIMA / SATH HUANCAYO", style_cell_bold), Paragraph("✔ SIN MULTAS GRAVES DETECTADAS", style_status_ok)],
    ]
    sec_table = Table(sec_data, colWidths=[150, 150, 240])
    sec_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F0F4F8")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(sec_table)
    elements.append(Spacer(1, 15))

    # 5. BLOQUE DE INFOGRAFÍA Y SERVICIOS LEGALES COMPLEMENTARIOS (ESTUDIO CÓRDOVA ABOGADOS)
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CCCCCC"), spaceAfter=8))
    
    footer_card_data = [
        [
            Paragraph("<b>ESTUDIO CÓRDOVA ABOGADOS</b><br/><font color='#00B050'><b>¿Necesitas Asesoría Legal o Contratos de Compraventa?</b></font>", style_footer_title),
            Paragraph("<b>CONTACTO DIRECTO:</b><br/>📞 921204578 - 990997973<br/>✉ estudiocordova20@gmail.com<br/>📍 Paseo la Breña 529 - Huancayo", style_footer_text)
        ]
    ]
    footer_table = Table(footer_card_data, colWidths=[320, 220])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F4F6F8")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#0A2240")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(footer_table)

    # Construir PDF
    doc.build(elements)
    
    pdf_value = buffer.getvalue()
    buffer.close()
    
    return Response(content=pdf_value, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=Informe_ConsultaSano_{placa_clean}.pdf"})
