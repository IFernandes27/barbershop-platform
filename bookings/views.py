from datetime import datetime, date, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _

from .models import Barbeiro, Marcacao, Servico

from .forms import BookingForm



# ----------------------------
# HOME (index) + alias landing
# ----------------------------
def index(request):
    servicos = Servico.objects.all()[:6]
    servicos_precos = Servico.objects.order_by("preco")[:5]
    return render(
        request,
        "index.html",   # <- agora é só "index.html"
        {"servicos": servicos, "servicos_precos": servicos_precos},
    )


# compatibilidade com URLs antigas
landing = index


# ----------------------------
# LISTA DE SERVIÇOS
# ----------------------------
@login_required
def services_list(request):
    servicos = Servico.objects.all().order_by("preco", "nome")
    return render(request, "booking_wizard/services_list.html", {"servicos": servicos})


# ----------------------------
# ESCOLHER BARBEIRO
# ----------------------------
@login_required
def choose_barber(request, servico_id: int):
    servico = get_object_or_404(Servico, pk=servico_id)
    barbeiros = Barbeiro.objects.all().order_by(
        "user__first_name", "user__last_name", "user__username"
    )
    ctx = {"servico": servico, "barbeiros": barbeiros}
    return render(request, "booking_wizard/choose_barber.html", ctx)


# ----------------------------
# GERA SLOTS (ajudante)
# ----------------------------
def _generate_slots(day: date, duration_min: int, barbeiro: Barbeiro):
    """
    Gera horários disponíveis entre 09:00 e 18:00, removendo conflitos com marcações
    (exceto canceladas). Usa make_aware para lidar com timezone corretamente.
    """
    tz = timezone.get_current_timezone()
    WORK_START = time(9, 0)
    WORK_END = time(18, 0)

    start_dt = timezone.make_aware(datetime.combine(day, WORK_START), tz)
    end_dt = timezone.make_aware(datetime.combine(day, WORK_END), tz)
    step = timedelta(minutes=duration_min)

    # Marcações do barbeiro neste dia (ativas)
    ocupadas = Marcacao.objects.filter(
        barbeiro=barbeiro, inicio__date=day
    ).exclude(status="cancelled")

    slots = []
    current = start_dt
    while current + step <= end_dt:
        # conflito simples: existe marcação a começar dentro da janela [current, current+step)
        conflito = ocupadas.filter(inicio__gte=current, inicio__lt=current + step).exists()
        if not conflito:
            slots.append(current)
        current += step

    return slots


# ----------------------------
# ESCOLHER DATA/HORA
# ----------------------------
@login_required
def choose_datetime(request, servico_id: int, barbeiro_id: int):
    servico = get_object_or_404(Servico, pk=servico_id)
    barbeiro = get_object_or_404(Barbeiro, pk=barbeiro_id)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            marcacao = form.save(commit=False)
            marcacao.servico = servico
            marcacao.barbeiro = barbeiro
            marcacao.cliente = request.user
            marcacao.status = "pending"
            marcacao.save()

            messages.success(request, _("Marcação criada com sucesso!"))
            return redirect("bookings:dashboard")
    else:
        form = BookingForm()

    ctx = {
        "servico": servico,
        "barbeiro": barbeiro,
        "form": form,
    }
    return render(request, "booking_wizard/choose_datetime.html", ctx)

# ----------------------------
# CONFIRMAR (resumo)
# ----------------------------
@login_required
def booking_confirm(request):
    if request.method != "POST":
        return redirect("bookings:services_list")

    servico = get_object_or_404(Servico, pk=request.POST.get("servico_id"))
    barbeiro = get_object_or_404(Barbeiro, pk=request.POST.get("barbeiro_id"))

    slot_str = request.POST.get("slot")
    try:
        slot_dt = datetime.fromisoformat(slot_str)
    except Exception:
        messages.error(request, _("Horário inválido."))
        return redirect("bookings:choose_datetime", servico.id, barbeiro.id)

    if timezone.is_naive(slot_dt):
        slot_dt = timezone.make_aware(slot_dt, timezone.get_current_timezone())

    return render(
        request,
        "booking_wizard/booking_confirm.html",
        {"servico": servico, "barbeiro": barbeiro, "slot": slot_dt},
    )


# ----------------------------
# CRIAR MARCAÇÃO (grava)
# ----------------------------
@login_required
def create_booking(request):
    if request.method != "POST":
        return redirect("bookings:services_list")

    servico = get_object_or_404(Servico, pk=request.POST.get("servico_id"))
    barbeiro = get_object_or_404(Barbeiro, pk=request.POST.get("barbeiro_id"))

    slot_str = request.POST.get("slot")
    try:
        inicio = datetime.fromisoformat(slot_str)
    except Exception:
        messages.error(request, _("Horário inválido."))
        return redirect("bookings:choose_datetime", servico.id, barbeiro.id)

    if timezone.is_naive(inicio):
        inicio = timezone.make_aware(inicio, timezone.get_current_timezone())

    Marcacao.objects.create(
        cliente=request.user,
        servico=servico,
        barbeiro=barbeiro,
        inicio=inicio,
        status="pending",
    )
    messages.success(request, _("Marcação criada com sucesso!"))
    return redirect("bookings:dashboard")


# ----------------------------
# DASHBOARD CLIENTE / AGENDA BARBEIRO
# (mantidos aqui para não quebrar rotas existentes)
# ----------------------------
@login_required
def dashboard(request):
    marcacoes = (
        Marcacao.objects.filter(cliente=request.user)
        .select_related("barbeiro__user", "servico")
        .order_by("-inicio", "-criado_em")
    )
    return render(request, "bookings/dashboard.html", {"marcacoes": marcacoes})


@login_required
def agenda_barbeiro(request):
    try:
        barbeiro = Barbeiro.objects.get(user=request.user)
    except Barbeiro.DoesNotExist:
        messages.error(request, _("A tua conta não está registada como barbeiro."))
        return redirect("bookings:dashboard")

    marcacoes = (
        Marcacao.objects.filter(barbeiro=barbeiro)
        .select_related("cliente", "servico")
        .order_by("-inicio", "-criado_em")
    )
    return render(
        request,
        "bookings/agenda_barbeiro.html",
        {"marcacoes": marcacoes, "barbeiro": barbeiro},
    )


# (opcionais se já existirem com outros nomes)
@login_required
def confirmar_marcacao(request, pk):
    try:
        barbeiro = Barbeiro.objects.get(user=request.user)
    except Barbeiro.DoesNotExist:
        messages.error(request, _("A tua conta não está registada como barbeiro."))
        return redirect("bookings:dashboard")

    m = get_object_or_404(Marcacao, pk=pk, barbeiro=barbeiro)
    if m.status != "confirmed":
        m.confirm()
        messages.success(request, _("Marcação confirmada com sucesso."))
    else:
        messages.info(request, _("Esta marcação já está confirmada."))
    return redirect("bookings:agenda_barbeiro")


@login_required
def cancelar_marcacao_barbeiro(request, pk):
    try:
        barbeiro = Barbeiro.objects.get(user=request.user)
    except Barbeiro.DoesNotExist:
        messages.error(request, _("A tua conta não está registada como barbeiro."))
        return redirect("bookings:dashboard")

    m = get_object_or_404(Marcacao, pk=pk, barbeiro=barbeiro)
    if m.status != "cancelled":
        m.cancel()
        messages.success(request, _("Marcação cancelada."))
    else:
        messages.info(request, _("Esta marcação já está cancelada."))
    return redirect("bookings:agenda_barbeiro")


@login_required
def cancelar_marcacao(request, pk):
    m = get_object_or_404(Marcacao, pk=pk, cliente=request.user)
    if m.status != "cancelled":
        m.cancel()
        messages.success(request, _("Marcação cancelada."))
    else:
        messages.info(request, _("Esta marcação já está cancelada."))
    return redirect("bookings:dashboard")


# --- Alias compatível para o URL name=cancel_booking -------------------------
@login_required
def cancel_booking(request, marcacao_id: int):
    """
    Cancela uma marcação. Permite o cancelamento pelo próprio cliente
    ou pelo barbeiro da marcação. Redireciona para o dashboard certo.
    """
    m = get_object_or_404(Marcacao, pk=marcacao_id)

    is_owner = (m.cliente_id == request.user.id)
    is_barber = (getattr(m.barbeiro, "user_id", None) == request.user.id)

    if not (is_owner or is_barber):
        messages.error(request, _("Não tens permissões para cancelar esta marcação."))
        return redirect("bookings:dashboard")

    if m.status == "cancelled":
        messages.info(request, _("Esta marcação já estava cancelada."))
    else:
        # usa o método do modelo, se existir; caso não, define status diretamente
        if hasattr(m, "cancel"):
            m.cancel()
        else:
            m.status = "cancelled"
            m.save(update_fields=["status"])
        messages.success(request, _("Marcação cancelada com sucesso."))

    # Redireciona consoante o papel
    if is_barber:
        return redirect("bookings:agenda_barbeiro")
    return redirect("bookings:dashboard")
