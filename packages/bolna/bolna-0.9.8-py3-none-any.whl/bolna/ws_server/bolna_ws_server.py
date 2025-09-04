import asyncio
import traceback
import websockets
import os
import json
from dotenv import load_dotenv
from bolna.helpers.logger_config import configure_logger


logger = configure_logger(__name__)
load_dotenv()


class BolnaWebsocket():
    def __init__(self, **kwargs):
        super().__init__()
        self.run_id = kwargs['run_id']

    def get_bolna_ws_url(self):
        logger.info(f"GETTING BOLNA HANGUP WS")
        websocket_url = 'wss://6fc1-2406-7400-9a-49ce-b074-9dae-7686-7283.ngrok-free.app/hangup_chat/{}'.format(self.run_id)
        logger.info(f"Bolna hangup websocket url: {websocket_url}")
        return websocket_url

    async def receiver(self, ws):
        async for msg in ws:
            try:
                msg = json.loads(msg)
                if msg['type'] == "hangup":
                    logger.info(f"Got a hangup object {msg}")
                    yield 'YES'

            except Exception as e:
                traceback.print_exc()

    def bolna_connect(self):
        websocket_url = self.get_bolna_ws_url()
        extra_headers = {
            'Authorization': 'Token {}'.format(os.getenv('AUTH_TOKEN'))
        }
        bolna_ws = websockets.connect(websocket_url)
        return bolna_ws

    async def run(self):
        try:
            self.bolna_ws_task = asyncio.create_task(self.start_ws())
        except Exception as e:
            logger.error(f"not working {e}")

    async def start_ws(self):
        logger.info(f"STARTED BOLNA_WS")
        try:
            async with self.bolna_connect() as bolna_ws:
                async for message in self.receiver(bolna_ws):
                    logger.info('start_ws: {}'.format(message))
        except Exception as e:
            logger.info(f"Error in transcribe: {e}")
