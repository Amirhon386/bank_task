from django.urls import path
from . import views

urlpatterns = [
    path("rpc/", views.rpc_endpoint, name="rpc_endpoint"),
]