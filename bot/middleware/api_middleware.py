from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from config.config import API_URL
from utils.api_client import APIClient


class ApiMiddleware(LifetimeControllerMiddleware):
    """Middleware, который контролирует сессии взаимодействия с API."""

    def __init__(self):
        super().__init__()

    async def pre_process(self, obj, data, *args):
        self.api_session = APIClient(API_URL)
        data['api'] = self.api_session

    async def post_process(self, obj, data, *args):
        api_session = data.get('api')
        if api_session:
            await self.api_session.close()
