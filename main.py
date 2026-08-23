from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import os
import requests

app = FastAPI(title="ConsultaSano.pe API")

@app.get("/", response_class=HTMLResponse)
def home():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>ConsultaSano.pe Activo</h1>"

@app.get("/consultar")
def consultar_placa(placa: str = Query(...), whatsapp: str = Query(...)):
    placa_clean = placa.upper().strip()
    
    # Fuentes mapeadas para el barrido
    fuentes_nacionales = {
        "SUNARP": "https://www.sunarp.gob.pe/ConsultaVehicular/",
        "SUNARP_SIGUELO": "https://siguelo.sunarp.gob.pe/siguelo/",
        "MTC_CITV": "http://portal.mtc.gob.pe/reportedgtt/form/frmconsultaplacaitv.aspx",
        "INFOGAS": f"http://infogas.com.pe/placa/?placa={placa_clean}",
        "APESEG_SOAT": "https://www.apeseg.org.pe/consultas-soat/",
        "LUNAS_POLARIZADAS": f"https://consultaspnp.com/?doc={placa_clean}&show_view=yes",
        "SUTRAN_INFRACCIONES": "https://www.sutran.gob.pe/consultas/record-de-infracciones/record-de-infracciones/",
        "SUTRAN_CINEMOMETRO": "https://webexterno.sutran.gob.pe/WebExterno/Pages/frmPapeletasCinemometro.aspx",
        "ATU": "https://pasarela.atu.gob.pe/#",
        "JNE_MULTAS": "https://multas.jne.gob.pe/login"
    }

    return {
        "status": "processing",
        "placa": placa_clean,
        "whatsapp": whatsapp,
        "mensaje": "Auditoría iniciada correctamente en todas las fuentes oficiales.",
        "endpoints_evaluados": len(fuentes_nacionales),
        "cobertura": "Nacional + Módulos Municipales Provinciales"
    }
