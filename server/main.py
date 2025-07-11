import uvicorn
import asyncio
import logging
from logging.config import dictConfig
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Any, Optional
import os
import json

from .simulation.world import ProductionWorld
from .analysis.data_exporter import ScientificDataExporter
from .analysis.traffic_monitor import traffic_monitor, TrafficReport
from .validation.ws_schemas import BatchParamChangePayload
from pydantic import ValidationError

# --- Logging ---
dictConfig({
    "version": 1, "disable_existing_loggers": False,
    "formatters": {"default": {"()": "uvicorn.logging.DefaultFormatter", "fmt": "%(levelprefix)s %(asctime)s - %(message)s"}},
    "handlers": {"default": {"formatter": "default", "class": "logging.StreamHandler", "stream": "ext://sys.stderr"}},
    "loggers": {"uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False}},
})
logger = logging.getLogger(__name__)

# --- Custom JSON Response ---
class CustomJSONResponse(Response):
    media_type = "application/json"
    def render(self, content: Any) -> bytes:
        import numpy as np
        class CustomEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, (np.integer, np.floating, np.bool_)): return o.item()
                if isinstance(o, np.ndarray): return o.tolist()
                # CuPy'ı sadece gerektiğinde import et
                try:
                    import cupy as cp
                    if isinstance(o, cp.ndarray): return o.get().tolist()
                except ImportError:
                    pass
                return super().default(o)
        return json.dumps(content, cls=CustomEncoder).encode("utf-8")

app = FastAPI(title="NeoMag Simulation Server", default_response_class=CustomJSONResponse)

# --- App State & Globals ---
world: Optional[ProductionWorld] = None
data_exporter = ScientificDataExporter(output_dir="exports")

# --- Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.lock = asyncio.Lock()
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self.lock: self.active_connections.append(websocket)
    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            if websocket in self.active_connections: self.active_connections.remove(websocket)
    async def broadcast_json(self, data: dict):
        message = CustomJSONResponse(data).body
        traffic_monitor.record_sent(len(message))
        async with self.lock:
            connections = self.active_connections[:]
        for conn in connections:
            try: await conn.send_bytes(message)
            except (WebSocketDisconnect, RuntimeError): await self.disconnect(conn)

manager = ConnectionManager()

# --- CORS & Static Files ---
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(project_root, "static")), name="static")
app.mount("/src", StaticFiles(directory=os.path.join(project_root, "src")), name="src")
app.mount("/node_modules", StaticFiles(directory=os.path.join(project_root, "node_modules")), name="node_modules")

# --- Simulation Lifecycle ---
async def run_simulation():
    logger.info("Simülasyon döngüsü başlatıldı!")
    while True:
        if world and not world.clock.is_paused:
            world.update(delta_time=0.016)
            if world.clock.ticks % 2 == 0:
                state = world.get_state_for_client()
                if state: await manager.broadcast_json(state)
        await asyncio.sleep(0.016)

@app.on_event("startup")
async def startup_event():
    global world
    world = ProductionWorld(width=1000, height=800, initial_population=150)
    app.title = f"NeoMag v{world.version}"
    logger.info(f"{app.title} - Simülasyon yöneticileri başlatıldı.")
    asyncio.create_task(run_simulation())

# --- WebSocket Handlers ---
async def handle_set_pause(world, payload, **kwargs):
    is_paused = payload.get("paused", True)
    if isinstance(is_paused, bool): world.set_pause(is_paused)
async def handle_reset(world, **kwargs):
    world.reset()
async def handle_batch_param_change(world, payload, **kwargs):
    try:
        validated_params = BatchParamChangePayload.parse_obj(payload)
        world.update_parameters(validated_params.dict(exclude_unset=True))
    except ValidationError as e: logger.warning(f"Parametre doğrulama hatası: {e}")

MESSAGE_HANDLERS = {
    "set_pause": handle_set_pause, "reset": handle_reset, "batch_param_change": handle_batch_param_change,
}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            traffic_monitor.record_received(len(data.encode('utf-8')))
            try: message = json.loads(data)
            except json.JSONDecodeError: continue
            handler = MESSAGE_HANDLERS.get(message.get("type"))
            if handler and world: await handler(world=world, payload=message.get("payload", {}))
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

# --- API Endpoints ---
@app.get("/health")
async def health_check():
    if not world: raise HTTPException(status_code=503, detail="Simülasyon hazır değil.")
    return {
        "version": world.version, "session_id": world.state.session_id,
        "is_paused": world.clock.is_paused, "ticks": world.clock.ticks,
        "population": len(world.entities.agents),
    }

@app.get("/api/statistics")
async def get_statistics_endpoint():
    if not world: raise HTTPException(status_code=503, detail="Simülasyon hazır değil.")
    return world.get_statistics()

@app.get("/api/performance")
async def get_performance_metrics():
    if not world: raise HTTPException(status_code=503, detail="Simülasyon hazır değil.")
    return world.stats.perf_monitor.get_average_metrics()

@app.post("/api/save_snapshot")
async def save_snapshot_endpoint():
    if not world: raise HTTPException(status_code=503, detail="Simülasyon hazır değil.")
    world.state.save_snapshot(world.clock.ticks, world.clock.generation)
    return {"message": "Snapshot kaydı tetiklendi."}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_path = os.path.join(project_root, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f: return HTMLResponse(content=f.read())
    raise HTTPException(status_code=404, detail="index.html not found")

if __name__ == "__main__":
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=True) 