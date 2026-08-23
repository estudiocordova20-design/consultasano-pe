from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response
import os
from generador_pdf import generar_pdf_consultasano

app = FastAPI(title="ConsultaSano.pe API")

@app.get("/", response_class=HTMLResponse)
def home():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>ConsultaSano.pe Activo</h1>"

@app.get("/descargar-pdf")
def descargar_pdf(placa: str = Query(...)):
    placa_clean = placa.upper().strip()
    
    # Datos de prueba para estructurar el reporte oficial
    datos_vehiculo = {
        "placa": placa_clean,
        "fecha_emision": "2026-08-22",
        "estado_circulacion": "EN CIRCULACION",
        "oficina_registral": "HUANCAYO",
        "marca": "CHERY",
        "modelo": "TIGGO",
        "anio": 2013,
        "color": "NEGRO AZABACHE",
        "serie": "LVVDB11B9DD106355",
        "motor": "SQR481FFFCL02315",
        "carroceria": "SUV",
        "combustible": "GASOLINA",
        "propietario_actual": "CORDOVA PALOMINO RICHARD SEBASTIAN",
        "partida": "60548021",
        "acto": "COMPRA - VENTA",
        "titulo_fecha": "03558353 - 2022",
        "soat_estado": "VIGENTE (APESEG)",
        "citv_estado": "APROBADO (MTC)",
        "infogas_estado": "SIN CONVERSIÓN / REGISTRADO",
        "sutran_estado": "0 PAPELETAS PENDIENTES",
        "sat_estado": "SIN MULTAS GRAVES DETECTADAS"
    }

    pdf_bytes = generar_pdf_consultasano(datos_vehiculo)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Reporte_ConsultaSano_{placa_clean}.pdf"}
    )
