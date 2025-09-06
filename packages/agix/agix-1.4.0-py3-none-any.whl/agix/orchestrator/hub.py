from __future__ import annotations
from typing import Any, Dict, Sequence, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from agix.qualia.qualia_engine import QualiaEngine
from agix.memory.experiential import GestorDeMemoria
import uvicorn


class QualiaHub:
    """Orquestador central de módulos AGIX."""

    def __init__(self) -> None:
        self.modules: Dict[str, Dict[str, Any]] = {}
        self.app = FastAPI(title="Qualia Hub")
        try:
            self.engine = QualiaEngine(GestorDeMemoria())
        except Exception:
            self.engine = QualiaEngine(GestorDeMemoria(), backend="jax")
        self.current_state: Any | None = None
        self.clients: Set[WebSocket] = set()
        self._setup_routes()

    # ------------------------------------------------------------------
    def _setup_routes(self) -> None:
        @self.app.post("/register")
        def _register(payload: Dict[str, Any]):
            name = str(payload.get("name"))
            metadata = payload.get("metadata", {})
            if name:
                self.register_module(name, metadata)
            return JSONResponse({"status": "ok"})

        @self.app.get("/modules")
        def _modules():
            return JSONResponse({"modules": self.modules})

        @self.app.post("/event")
        def _event(payload: Dict[str, Any]):
            event = payload.get("event", "")
            self.broadcast_event(event)
            return JSONResponse({"status": "ok"})

        @self.app.post("/qualia")
        async def _process(payload: Dict[str, Any]):
            data = payload.get("input", [])
            state = payload.get("internal", [])
            qualia = self.process_input(data, state)
            for client in list(self.clients):
                await client.send_json({"qualia": self._as_list(qualia)})
            return JSONResponse({"qualia": self._as_list(qualia)})

        @self.app.get("/qualia")
        def _get_state():
            return JSONResponse({"qualia": self._as_list(self.current_state)})

        @self.app.websocket("/ws/qualia")
        async def _ws(ws: WebSocket):
            await ws.accept()
            self.clients.add(ws)
            if self.current_state is not None:
                await ws.send_json({"qualia": self._as_list(self.current_state)})
            try:
                while True:
                    await ws.receive_text()
            except WebSocketDisconnect:
                self.clients.remove(ws)

    # ------------------------------------------------------------------
    def register_module(self, name: str, metadata: Dict[str, Any]) -> None:
        """Registra un módulo junto a sus metadatos."""
        self.modules[name] = metadata

    def get_modules(self) -> Dict[str, Dict[str, Any]]:
        """Devuelve la tabla de módulos registrados."""
        return self.modules

    def broadcast_event(self, event: str) -> None:
        """Difunde un evento a los módulos registrados (solo log)."""
        print(f"Evento difundido: {event}")

    def process_input(
        self, input_data: Sequence[float], internal_state: Sequence[float]
    ) -> Any:
        """Genera y almacena un estado de cualia a partir de los datos."""
        self.current_state = self.engine.generate_state(input_data, internal_state)
        return self.current_state

    def apply_to_behavior(self, agix_agent: Any) -> None:
        """Ajusta el comportamiento del agente según el estado de cualia."""
        if self.current_state is None:
            return
        try:
            mean_val = float(self.engine._lib.mean(self.current_state))
        except Exception:
            mean_val = 0.0
        agix_agent.internal_state["qualia_intensity"] = mean_val
        if hasattr(agix_agent, "feel"):
            try:
                agix_agent.feel("qualia", abs(mean_val), "curiosidad")
            except Exception:
                pass

    # ------------------------------------------------------------------
    def _as_list(self, tensor: Any | None) -> list[float]:
        """Convierte el tensor a lista para ser serializado."""
        if tensor is None:
            return []
        try:
            data = tensor.tolist()  # type: ignore[assignment]
        except Exception:
            data = tensor
        if isinstance(data, list):
            return [float(x) for x in data]
        try:
            return [float(data)]  # type: ignore[arg-type]
        except Exception:
            return []

    def run(self, host: str = "127.0.0.1", port: int = 9000, emotion: bool = False) -> None:
        """Arranca el servidor HTTP de QualiaHub o del EmotionHub."""
        if emotion:
            from .emotion_hub import EmotionHub

            EmotionHub().run(host=host, port=port)
            return
        uvicorn.run(self.app, host=host, port=port)
