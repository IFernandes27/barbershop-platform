# bookings/urls.py
from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    # Homepage / landing
    path("", views.index, name="index"),

    # Serviços e wizard de marcação
    path("services/", views.services_list, name="services_list"),
    path("choose-barber/<int:servico_id>/", views.choose_barber, name="choose_barber"),
    path(
        "choose-datetime/<int:servico_id>/<int:barbeiro_id>/",
        views.choose_datetime,
        name="choose_datetime",
    ),
    path("booking/confirm/", views.booking_confirm, name="booking_confirm"),
    path("booking/create/", views.create_booking, name="create_booking"),

    # Dashboard do cliente
    path("dashboard/", views.dashboard, name="dashboard"),

    # Agenda do barbeiro
    path("agenda/", views.agenda_barbeiro, name="agenda_barbeiro"),

    # Ações do barbeiro sobre marcações
    path(
        "agenda/confirm/<int:pk>/",
        views.confirmar_marcacao,
        name="confirm_booking",            # <--- ESTE NOME é o que o template usa
    ),
    path(
        "agenda/cancel/<int:pk>/",
        views.cancelar_marcacao_barbeiro,
        name="cancel_booking_barber",      # <--- usado no template também
    ),

    # Cancelamento genérico (cliente ou barbeiro)
    path(
        "booking/cancel/<int:marcacao_id>/",
        views.cancel_booking,
        name="cancel_booking",
    ),
]
