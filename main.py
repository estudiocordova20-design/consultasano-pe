from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, FileResponse
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>ConsultaSano.pe Activo</h1>"

@app.get("/consultar")
def consultar_placa(placa: str = Query(...), whatsapp: str = Query(...)):
    placa_clean = placa.upper().strip()
    return {
        "status": "success",
        "placa": placa_clean,
        "whatsapp": whatsapp,
        "mensaje": f"Consulta recibida exitosamente para la placa {placa_clean}. En breve procesaremos la auditoria completa.",
        "modulos_verificados": [
            "SUNARP (Partida y Propietarios)",
            "PNP / DIROVE (Alerta de Robo)",
            "APESEG (SOAT)",
            "MTC (CITV / Inspeccion Tecnica)",
            "Infogas (Certificacion GNV/GLP)",
            "SAT Lima / Callao, SUTRAN y Municipalidades"
        ]
    }