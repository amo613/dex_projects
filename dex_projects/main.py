# main.py
import asyncio
import logging
from nicegui import ui, app
from viewmodels.dex_vm import DexcelerateViewModel
from views.web_view import DexWebView
import requests
logger = logging.getLogger("Main")
logger.setLevel(logging.INFO)

def init_ui():
    vm = DexcelerateViewModel()
    DexWebView(vm)
    
    @app.middleware
    async def log_connections(request: requests, call_next):
        logger.info(f"Neue Verbindung von {request.client.host}")
        response = await call_next(request)
        return response

    app.on_startup(lambda: asyncio.create_task(run_background_tasks(vm)))

async def run_background_tasks(vm):
    await vm.start()
    logger.info("Service gestartet")
    while vm.service.running:
        await asyncio.sleep(1)

if __name__ in {"__main__", "__mp_main__"}:
    init_ui()
    
    ui.run(
        title="Dex Dashboard",
        host="0.0.0.0",
        port=8080,
        show=True,
        favicon="🚀",
        dark=True,
        show_welcome_message=False,
        uvicorn_logging_level="info" 
    )