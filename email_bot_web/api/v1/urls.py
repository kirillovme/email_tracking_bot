from django.urls import path
from email_service.api import service_router
from ninja import NinjaAPI
from user.api import user_router

api = NinjaAPI(title='Email Bot API', description='API for Email Bot')

api.add_router('/services', service_router)
api.add_router('/users', user_router)

urlpatterns = [
    path('', api.urls),
]
