from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RollDiceView, DiceMacroViewSet

router = DefaultRouter()
router.register(r"macros", DiceMacroViewSet, basename="macros")

urlpatterns = [
    path("roll/", RollDiceView.as_view(), name="roll-dice"),
    path("", include(router.urls)),
]
