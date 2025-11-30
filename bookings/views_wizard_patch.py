from datetime import datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Barbeiro, Marcacao, Servico

WORK_START = time(9, 0)
WORK_END = time(18, 0)
SLOT_STEP_MIN = 15


def _overlap(a_start, a_end, b_start, b_end):
    return (a_start < b_end) and (a_end > b_start)


def _generate_slots(day_dt, duration_min, existing_starts_ends):
    tz = timezone.get_current_timezone()

    naive_start = datetime.combine(day_dt, WORK_START)
    naive_end = datetime.combine(day_dt, WORK_END)

    start_dt = timezone.make_aware(naive_start, tz) if timezone.is_naive(naive_start) else naive_start
    end_dt = timezone.make_aware(naive_end, tz) if timezone.is_naive(naive_end) else naive_end

    slots = []
    cursor = start_dt
    dur = timedelta(minutes=duration_min)

    while cursor + dur <= end_dt:
        s, e = cursor, cursor + dur
        conflict = any(_overlap(s, e, xs, xe) for xs, xe in existing_starts_ends)
        if not conflict and s >= timezone.now():
            slots.append(s)
        cursor += timedelta(minutes=SLOT_STEP_MIN)

    return slots


def services_list(request):
    servicos = Servico.objects.all().order_by("nome")
    return render(request, "booking_wizard/services_list.html", {"servicos": servicos})


def choose_barber(request, service_id):
    servico = get_object_or_404(Servico, pk=service_id)
    barbeiros = Barbeiro.objects.all().order_by("nome")

    req = request.session.get("booking_wizard", {})
    req["service_id"] = servico.id
    request.session["booking_wizard"] = req

    return render(
        request,
        "booking_wizard/choose_barber.html",
        {"servico": servico, "barbeiros": barbeiros},
    )


def choose_datetime(request, service_id, barber_id):
    servico = get_object_or_404(Servico, pk=service_id)
    barbeiro = get_object_or_404(Barbeiro, pk=barber_id)

    try:
        picked = request.GET.get("date")
        day = datetime.strptime(picked, "%Y-%m-%d").date() if picked else timezone.localdate()
    except ValueError:
        day = timezone.localdate()

    day_start = timezone.make_aware(datetime.combine(day, time.min))
    day_end = timezone.make_aware(datetime.combine(day, time.max))

    marcacoes = Marcacao.objects.filter(barbeiro=barbeiro, inicio__range=(day_start, day_end))
    existing = [(m.inicio, m.inicio + timedelta(minutes=m.servico.duracao_min)) for m in marcacoes]

    slots = _generate_slots(day, servico.duracao_min, existing)

    req = request.session.get("booking_wizard", {})
    req.update({"service_id": servico.id, "barber_id": barbeiro.id, "date": day.isoformat()})
    request.session["booking_wizard"] = req

    return render(
        request,
        "booking_wizard/choose_datetime.html",
        {"servico": servico, "barbeiro": barbeiro, "day": day, "slots": slots},
    )


@login_required
def booking_confirm(request):
    # Se veio do clique num slot, guardamos o ISO na sessão
    if request.method == "POST":
        start_iso = request.POST.get("start_iso")
        if start_iso:
            req = request.session.get("booking_wizard", {})
            req["start_iso"] = start_iso
            request.session["booking_wizard"] = req

    data = request.session.get("booking_wizard", {})
    if not data or not all(k in data for k in ["service_id", "barber_id", "start_iso"]):
        messages.error(request, "Selecione serviço, profissional e horário.")
        return redirect("services_list")

    servico = get_object_or_404(Servico, pk=data["service_id"])
    barbeiro = get_object_or_404(Barbeiro, pk=data["barber_id"])

    # start_iso pode vir aware (ex.: '2025-11-06T15:15:00+00:00') ou naive.
    start_dt = datetime.fromisoformat(data["start_iso"])
    if timezone.is_naive(start_dt):
        start = timezone.make_aware(start_dt)
    else:
        # garante conversão para o fuso configurado no projeto
        start = start_dt.astimezone(timezone.get_current_timezone())

    return render(
        request,
        "booking_wizard/confirm.html",
        {"servico": servico, "barbeiro": barbeiro, "start": start},
    )


@login_required
def create_booking(request):
    data = request.session.get("booking_wizard", {})
    if request.method != "POST" or not data:
        return redirect("services_list")

    servico = get_object_or_404(Servico, pk=data.get("service_id"))
    barbeiro = get_object_or_404(Barbeiro, pk=data.get("barber_id"))

    start_dt = datetime.fromisoformat(data.get("start_iso"))
    if timezone.is_naive(start_dt):
        start = timezone.make_aware(start_dt)
    else:
        start = start_dt.astimezone(timezone.get_current_timezone())

    marc = Marcacao(cliente=request.user, barbeiro=barbeiro, servico=servico, inicio=start)
    marc.full_clean()
    marc.save()

    request.session.pop("booking_wizard", None)
    messages.success(request, "Marcação criada! Em breve será confirmada.")
    return redirect("dashboard")
