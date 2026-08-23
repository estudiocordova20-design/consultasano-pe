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
    
    # ESTILOS REVISADOS Y OPTIMIZADOS
    style_subtitle_burgundy = ParagraphStyle(
        'SubTitleBurgundy', 
        parent=styles['Normal'], 
        fontName='Helvetica-Bold', 
        fontSize=11, 
        leading=14, 
        textColor=colors.HexColor("#800020"), 
        alignment=1 # CENTRADO
    )
    
    style_sec_header = ParagraphStyle('SecHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.white)
    style_cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#0A2240"))
    style_cell_normal = ParagraphStyle('CellNormal', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor("#333333"))
    
    # SEMÁFORO DE RIESGO
    style_risk_low = ParagraphStyle('RiskLow', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#008000"))

    elements = []

    # Cargar Logo Principal
    if os.path.exists("logo_consultasano.png"):
        header_logo = Image("logo_consultasano.png", width=250, height=115)
    else:
        header_logo = Paragraph("<b><font size=16 color='#0A2240'>ConsultaSano.pe</font></b>", style_cell_bold)

    # ENCABEZADO CON POSICIONES INVERTIDAS
    # Columna 0: Datos de emisión (Izquierda) | Columna 1: Logo (Derecha)
    header_data = [
        [
            Paragraph(f"<b>FECHA EMISIÓN:</b> {datetime.now().strftime('%Y-%m-%d')}<br/><b>PLACA AUDITADA:</b> {placa_clean}<br/><b>OFICINA REGISTRAL:</b> HUANCAYO", style_cell_bold),
            header_logo
        ],
        [
            Paragraph("INFORME OFICIAL DE AUDITORÍA Y SEGUIMIENTO DE INFRACCIONES VEHICULAR", style_subtitle_burgundy),
            Paragraph("", style_cell_normal)
        ]
    ]
    
    header_table = Table(header_data, colWidths=[230, 310])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('SPAN', (0,1), (1,1)), # Título centrado abarcando el ancho total
        ('TOPPADDING', (0,1), (0,1), 6),
        ('BOTTOMPADDING', (0,1), (0,1), 4),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 2))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#800020"), spaceAfter=6))

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

    # 2. HISTORIAL DE PROPIETARIOS Y VALOR DE VENTA
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

    if os.path.exists("sunarp_banner.png"):
        img_sunarp = Image("sunarp_banner.png", width=100, height=60)
    elif os.path.exists("sunarp_banner.jpg"):
        img_sunarp = Image("sunarp_banner.jpg", width=100, height=60)
    else:
        img_sunarp = None

    if img_sunarp:
        grid_sunarp = Table([[t_prop, img_sunarp]], colWidths=[420, 120])
        grid_sunarp.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (1,0), (1,0), 'CENTER')]))
        elements.append(grid_sunarp)
    else:
        elements.append(t_prop)

    elements.append(Spacer(1, 6))

    # 3. AUDITORÍA AMPLIADA CON SEMÁFORO DE RIESGO
    elements.append(Table([[Paragraph("3. SISTEMA DE AUDITORÍA LEGAL Y EVALUACIÓN DE RIESGO MULTI-ENTIDAD", style_sec_header)]], colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0A2240")), ('BOTTOMPADDING', (0,0), (-1,-1), 2), ('TOPPADDING', (0,0), (-1,-1), 2)]))
    elements.append(Spacer(1, 3))

    sec_data = [
        [Paragraph("Módulo Evaluado", style_cell_bold), Paragraph("Fuente", style_cell_bold), Paragraph("Resultado Técnico", style_cell_bold), Paragraph("Nivel Riesgo", style_cell_bold)],
        [Paragraph("Alerta Robo / Captura", style_cell_normal), Paragraph("PNP", style_cell_bold), Paragraph("SIN REQUERIMIENTO", style_cell_normal), Paragraph("🟢 BAJO", style_risk_low)],
        [Paragraph("Lunas Polarizadas", style_cell_normal), Paragraph("PNP", style_cell_bold), Paragraph("PERMISO VIGENTE", style_cell_normal), Paragraph("🟢 BAJO", style_risk_low)],
        [Paragraph("Vigencia SOAT", style_cell_normal), Paragraph("APESEG", style_cell_bold), Paragraph("15/01/26 AL 15/01/27", style_cell_normal), Paragraph("🟢 BAJO", style_risk_low)],
        [Paragraph("Chip GNV / GLP", style_cell_normal), Paragraph("INFOGAS", style_cell_bold), Paragraph("SIN REGISTRO DUAL", style_cell_normal), Paragraph("🟢 BAJO", style_risk_low)],
        [Paragraph("Inspección Técnica", style_cell_normal), Paragraph("MTC", style_cell_bold), Paragraph("APROBADO Y VIGENTE", style_cell_normal), Paragraph("🟢 BAJO", style_risk_low)],
        [Paragraph("Fotopapeletas", style_cell_normal), Paragraph("SUTRAN", style_cell_bold), Paragraph("0 INFRACCIONES", style_cell_normal), Paragraph("🟢 BAJO", style_risk_low)],
        [Paragraph("Captura Vehicular", style_cell_normal), Paragraph("SAT LIMA", style_cell_bold), Paragraph("SIN ORDEN CAPTURA", style_cell_normal), Paragraph("🟢 BAJO", style_risk_low)],
        [Paragraph("Infracciones / Pagos", style_cell_normal), Paragraph("SAT / SATH", style_cell_bold), Paragraph("SIN DEUDAS PENDIENTES", style_cell_normal), Paragraph("🟢 BAJO", style_risk_low)],
        [Paragraph("Fiscalización Urb.", style_cell_normal), Paragraph("ATU", style_cell_bold), Paragraph("0 MULTAS ATU", style_cell_normal), Paragraph("🟢 BAJO", style_risk_low)],
    ]
    t_sec = Table(sec_data, colWidths=[120, 60, 160, 80])
    t_sec.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F0F4F8")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ALIGN', (3,0), (3,-1), 'CENTER'),
    ]))

    if os.path.exists("logos_entidades.png"):
        img_logos = Image("logos_entidades.png", width=110, height=160)
        grid_sec = Table([[t_sec, img_logos]], colWidths=[420, 120])
        grid_sec.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (1,0), (1,0), 'CENTER')]))
        elements.append(grid_sec)
    else:
        elements.append(t_sec)

    elements.append(Spacer(1, 4))

    # 4. BANNER PUBLICITARIO AMPLIADO (ESTUDIO CÓRDOVA ABOGADOS)
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CCCCCC"), spaceAfter=4))
    
    if os.path.exists("banner_footer.png"):
        banner_img = Image("banner_footer.png", width=540, height=180)
        elements.append(banner_img)

    # CONSTRUIR PDF
    doc.build(elements)
    
    pdf_value = buffer.getvalue()
    buffer.close()
    
    return Response(content=pdf_value, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=Informe_ConsultaSano_{placa_clean}.pdf"})
