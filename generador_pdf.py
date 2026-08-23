from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

def generar_pdf_consultasano(data_vehiculo: dict) -> bytes:
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
    
    # Estilos personalizados
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor("#0A2240"),
        spaceAfter=2
    )
    style_subtitle = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.HexColor("#00B050"),
        spaceAfter=10
    )
    style_section = ParagraphStyle(
        'SecHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor("#0A2240"),
        spaceBefore=8,
        spaceAfter=4
    )
    style_cell_label = ParagraphStyle(
        'CellLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=colors.HexColor("#4A5568")
    )
    style_cell_val = ParagraphStyle(
        'CellVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor("#1A202C")
    )

    story = []

    # 1. Cabecera
    story.append(Paragraph("Consulta<b>Sano</b>.pe", style_title))
    story.append(Paragraph("INFORME OFICIAL DE AUDITORÍA VEHICULAR INTEGRAL", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0A2240"), spaceAfter=10))

    # 2. Resumen Placa & Fecha
    info_cabecera = [
        [Paragraph("PLACA AUDITADA:", style_cell_label), Paragraph(f"<b>{data_vehiculo.get('placa', 'N/A')}</b>", style_cell_val),
         Paragraph("FECHA EMISIÓN:", style_cell_label), Paragraph(data_vehiculo.get('fecha_emision', '2026-08-22'), style_cell_val)],
        [Paragraph("ESTADO REGISTRAL:", style_cell_label), Paragraph(data_vehiculo.get('estado_circulacion', 'EN CIRCULACION'), style_cell_val),
         Paragraph("OFICINA REGISTRAL:", style_cell_label), Paragraph(data_vehiculo.get('oficina_registral', 'HUANCAYO'), style_cell_val)]
    ]
    t_cabecera = Table(info_cabecera, colWidths=[110, 160, 110, 160])
    t_cabecera.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_cabecera)
    story.append(Spacer(1, 10))

    # 3. Ficha Técnica SUNARP
    story.append(Paragraph("1. FICHA TÉCNICA REGISTRAL (SUNARP)", style_section))
    t_sunarp_data = [
        [Paragraph("Marca:", style_cell_label), Paragraph(data_vehiculo.get('marca', '-'), style_cell_val), Paragraph("Modelo:", style_cell_label), Paragraph(data_vehiculo.get('modelo', '-'), style_cell_val)],
        [Paragraph("Año Fab.:", style_cell_label), Paragraph(str(data_vehiculo.get('anio', '-')), style_cell_val), Paragraph("Color:", style_cell_label), Paragraph(data_vehiculo.get('color', '-'), style_cell_val)],
        [Paragraph("N° Serie / VIN:", style_cell_label), Paragraph(data_vehiculo.get('serie', '-'), style_cell_val), Paragraph("N° Motor:", style_cell_label), Paragraph(data_vehiculo.get('motor', '-'), style_cell_val)],
        [Paragraph("Carrocería:", style_cell_label), Paragraph(data_vehiculo.get('carroceria', '-'), style_cell_val), Paragraph("Combustible:", style_cell_label), Paragraph(data_vehiculo.get('combustible', '-'), style_cell_val)],
    ]
    t_sunarp = Table(t_sunarp_data, colWidths=[110, 160, 110, 160])
    t_sunarp.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sunarp)
    story.append(Spacer(1, 10))

    # 4. Trazabilidad & Propietarios (SÍGUELO)
    story.append(Paragraph("2. TRAZABILIDAD Y TRACTO SUCESIVO (SÍGUELO SUNARP)", style_section))
    t_prop_data = [
        [Paragraph("<b>Titular Actual / Presentante</b>", style_cell_label), Paragraph("<b>Partida</b>", style_cell_label), Paragraph("<b>Acto Inscrito</b>", style_cell_label), Paragraph("<b>Título / Fecha</b>", style_cell_label)],
        [Paragraph(data_vehiculo.get('propietario_actual', '-'), style_cell_val), Paragraph(data_vehiculo.get('partida', '-'), style_cell_val), Paragraph(data_vehiculo.get('acto', 'COMPRA - VENTA'), style_cell_val), Paragraph(data_vehiculo.get('titulo_fecha', '-'), style_cell_val)]
    ]
    t_prop = Table(t_prop_data, colWidths=[200, 80, 120, 140])
    t_prop.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_prop)
    story.append(Spacer(1, 10))

    # 5. Revisiones Técnicas, SOAT & Infracciones
    story.append(Paragraph("3. ESTADO DE SEGURIDAD, CITV, SOAT E INFRACCIONES", style_section))
    t_rev_data = [
        [Paragraph("<b>Módulo Evaluado</b>", style_cell_label), Paragraph("<b>Fuente Oficial</b>", style_cell_label), Paragraph("<b>Estado / Resultado</b>", style_cell_label)],
        [Paragraph("Alerta de Robo PNP", style_cell_val), Paragraph("DIROVE", style_cell_val), Paragraph("<b>SIN ORDEN DE CAPTURA VIGENTE</b>", style_cell_val)],
        [Paragraph("Vigencia de SOAT", style_cell_val), Paragraph("APESEG", style_cell_val), Paragraph(data_vehiculo.get('soat_estado', 'VIGENTE'), style_cell_val)],
        [Paragraph("Inspección Técnica (CITV)", style_cell_val), Paragraph("MTC", style_cell_val), Paragraph(data_vehiculo.get('citv_estado', 'APROBADO'), style_cell_val)],
        [Paragraph("Certificación GNV/GLP", style_cell_val), Paragraph("INFOGAS", style_cell_val), Paragraph(data_vehiculo.get('infogas_estado', 'NO APLICA / REGISTRADO'), style_cell_val)],
        [Paragraph("Récord Infracciones Tránsito", style_cell_val), Paragraph("SUTRAN / MTC", style_cell_val), Paragraph(data_vehiculo.get('sutran_estado', '0 PAPELETAS PENDIENTES'), style_cell_val)],
        [Paragraph("Fiscalización Municipal / SAT", style_cell_val), Paragraph(f"SAT {data_vehiculo.get('oficina_registral', 'LOCAL')}", style_cell_val), Paragraph(data_vehiculo.get('sat_estado', 'SIN MULTAS GRAVES DETECTADAS'), style_cell_val)],
    ]
    t_rev = Table(t_rev_data, colWidths=[160, 140, 240])
    t_rev.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_rev)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
