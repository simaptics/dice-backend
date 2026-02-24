"""URL routes for the dice app (mounted under /api/ by the root urlconf)."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RollDiceView, DiceMacroViewSet

router = DefaultRouter()
router.register(r"macros", DiceMacroViewSet, basename="macros")

urlpatterns = [
    path("roll/", RollDiceView.as_view(), name="roll-dice"),  # POST /api/roll/
    path("", include(router.urls)),  # /api/macros/ CRUD + /api/macros/{id}/roll/
]
