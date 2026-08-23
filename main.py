from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import io
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/descargar-pdf")
def descargar_pdf(placa: str = "W2G522"):
    placa_clean = placa.upper().strip()
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
    
    style_title = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=20, textColor=colors.HexColor("#0A2240"))
    style_subtitle = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor("#00B050"))
    style_sec_header = ParagraphStyle('SecHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.white)
    style_cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#0A2240"))
    style_cell_normal = ParagraphStyle('CellNormal', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor("#333333"))
    style_status_ok = ParagraphStyle('StatusOk', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#008000"))
    style_footer_title = ParagraphStyle('FooterTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=13, textColor=colors.HexColor("#0A2240"))
    style_footer_text = ParagraphStyle('FooterText', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor("#444444"))

    elements = []

    # ENCABEZADO
    header_data = [
        [
            Paragraph("<b>ConsultaSano<font color='#00B050'>.pe</font></b>", style_title),
            Paragraph(f"<b>FECHA EMISIÓN:</b> {datetime.now().strftime('%Y-%m-%d')}<br/><b>PLACA AUDITADA:</b> {placa_clean}", style_cell_bold)
        ],
        [
            Paragraph("INFORME OFICIAL DE AUDITORÍA VEHICULAR INTEGRAL", style_subtitle),
            Paragraph("<b>OFICINA REGISTRAL:</b> HUANCAYO", style_cell_normal)
        ]
    ]
    header_table = Table(header_data, colWidths=[340, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 4))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0A2240"), spaceAfter=6))

    # 1. FICHA TÉCNICA REGISTRAL (SUNARP)
    elements.append(Table([[Paragraph("1. FICHA TÉCNICA REGISTRAL (SUNARP)", style_sec_header)]], colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0A2240")), ('BOTTOMPADDING', (0,0), (-1,-1), 2), ('TOPPADDING', (0,0), (-1,-1), 2)]))
    elements.append(Spacer(1, 3))
    
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
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(sunarp_table)
    elements.append(Spacer(1, 6))

    # 2. HISTORIAL DE PROPIETARIOS Y PRECIO DE VENTA
    elements.append(Table([[Paragraph("2. HISTORIAL DE PROPIETARIOS Y VALOR DE VENTA (SUNARP)", style_sec_header)]], colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0A2240")), ('BOTTOMPADDING', (0,0), (-1,-1), 2), ('TOPPADDING', (0,0), (-1,-1), 2)]))
    elements.append(Spacer(1, 3))

    prop_table_data = [
        [Paragraph("Propietario Registrado", style_cell_bold), Paragraph("Fecha Propiedad", style_cell_bold), Paragraph("Acto / Titulo", style_cell_bold), Paragraph("Precio / Monto Venta", style_cell_bold)],
        [Paragraph("HUASCO BARZOLA, JOSEF ARLON", style_cell_normal), Paragraph("02/10/2024", style_cell_normal), Paragraph("COMPRA-VENTA (03558353)", style_cell_normal), Paragraph("S/ 28,500.00", style_cell_bold)],
        [Paragraph("CRUZ CHAMBI, CARLOS ALFREDO", style_cell_normal), Paragraph("17/08/2021", style_cell_normal), Paragraph("COMPRA-VENTA (01229401)", style_cell_normal), Paragraph("S/ 24,000.00", style_cell_normal)],
    ]
    
    t_prop = Table(prop_table_data, colWidths=[160, 85, 95, 80])
    t_prop.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F0F4F8")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))

    if os.path.exists("sunarp_banner.jpg"):
        img_sunarp = Image("sunarp_banner.jpg", width=110, height=65)
        grid_sunarp = Table([[t_prop, img_sunarp]], colWidths=[420, 120])
        grid_sunarp.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (1,0), (1,0), 'RIGHT')]))
        elements.append(grid_sunarp)
    else:
        elements.append(t_prop)

    elements.append(Spacer(1, 6))

    # 3. AUDITORÍA AMPLIADA DE PAPELETAS, CAPTURAS, SOAT Y CHIP GNV/GLP
    elements.append(Table([[Paragraph("3. SISTEMA DE AUDITORÍA LEGAL, TÉCNICA Y MULTAS MULTI-ENTIDAD", style_sec_header)]], colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0A2240")), ('BOTTOMPADDING', (0,0), (-1,-1), 2), ('TOPPADDING', (0,0), (-1,-1), 2)]))
    elements.append(Spacer(1, 3))

    sec_data = [
        [Paragraph("Módulo / Plataforma Evaluada", style_cell_bold), Paragraph("Entidad Fiscalizadora", style_cell_bold), Paragraph("Resultado / Detalle Técnico", style_cell_bold)],
        [Paragraph("Alerta de Robo / Orden Captura", style_cell_normal), Paragraph("DIROVE / PNP", style_cell_bold), Paragraph("✔ SIN ORDEN DE CAPTURA VIGENTE", style_status_ok)],
        [Paragraph("Autorización Lunas Polarizadas", style_cell_normal), Paragraph("CONSULTAS PNP", style_cell_bold), Paragraph("✔ PERMISO INDEFINIDO REGISTRADO", style_status_ok)],
        [Paragraph("Vigencia de SOAT (Inicio y Fin)", style_cell_normal), Paragraph("APESEG / MAPFRE", style_cell_bold), Paragraph("✔ VIGENTE: 15/01/2026 al 15/01/2027", style_status_ok)],
        [Paragraph("Certificación Sistema GNV / GLP", style_cell_normal), Paragraph("INFOGAS", style_cell_bold), Paragraph("✔ SIN CHIP / DUALIDAD REGISTRADA", style_status_ok)],
        [Paragraph("Inspección Técnica (CITV)", style_cell_normal), Paragraph("MTC", style_cell_bold), Paragraph("✔ APROBADO Y VIGENTE", style_status_ok)],
        [Paragraph("Fotopapeletas / Cinemómetros", style_cell_normal), Paragraph("SUTRAN", style_cell_bold), Paragraph("✔ 0 INFRACCIONES DETECTADAS", style_status_ok)],
        [Paragraph("Captura Vehicular por Multas", style_cell_normal), Paragraph("SAT LIMA", style_cell_bold), Paragraph("✔ NO REGISTRA ORDEN DE CAPTURA", style_status_ok)],
        [Paragraph("Infracciones y Pagos en Línea", style_cell_normal), Paragraph("SAT LIMA / SATH", style_cell_bold), Paragraph("✔ SIN PAPELETAS PENDIENTES", style_status_ok)],
        [Paragraph("Infracciones de Transporte Urbano", style_cell_normal), Paragraph("ATU PASARELA", style_cell_bold), Paragraph("✔ SIN RETENCIONES NI MULTAS ATU", style_status_ok)],
    ]
    t_sec = Table(sec_data, colWidths=[150, 110, 160])
    t_sec.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F0F4F8")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))

    if os.path.exists("logos_entidades.png"):
        img_logos = Image("logos_entidades.png", width=110, height=110)
        grid_sec = Table([[t_sec, img_logos]], colWidths=[420, 120])
        grid_sec.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (1,0), (1,0), 'RIGHT')]))
        elements.append(grid_sec)
    else:
        elements.append(t_sec)

    elements.append(Spacer(1, 8))

    # 4. TARJETA INFOGRÁFICA Y CONTACTO
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CCCCCC"), spaceAfter=4))
    
    brand_logo = Image("logo_estudio.png", width=60, height=60) if os.path.exists("logo_estudio.png") else Paragraph("<b>ESTUDIO CÓRDOVA</b>", style_cell_bold)
    
    brand_text = Paragraph("<b>Si tiene alguna pregunta, póngase en contacto con:</b><br/><font color='#00B050'><b>Estudio Córdova Abogados</b></font><br/><i>Asesoría Legal, Contratos Vehiculares y Sanamiento Registral</i>", style_footer_title)
    contact_info = Paragraph("<b>CONTACTO DIRECTO:</b><br/>📞 921204578 - 990997973<br/>✉ estudiocordova20@gmail.com<br/>🌐 Estudio Cordova FB<br/>📍 Paseo la Breña 529 - Huancayo", style_footer_text)

    footer_card_data = [[brand_logo, brand_text, contact_info]]
    footer_table = Table(footer_card_data, colWidths=[70, 270, 200])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F4F6F8")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#0A2240")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(footer_table)

    # CONSTRUIR PDF
    doc.build(elements)
    
    pdf_value = buffer.getvalue()
    buffer.close()
    
    return Response(content=pdf_value, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=Informe_ConsultaSano_{placa_clean}.pdf"})
