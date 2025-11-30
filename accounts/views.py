from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib import messages

from bookings.models import Barbeiro


class RoleAwareLoginView(LoginView):
    """
    Login que redireciona barbeiros para a agenda
    e clientes para o dashboard.
    """
    template_name = "accounts/login.html"
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True  # se já estiver logado, evita relogar

    def get_success_url(self):
        # 1) Se houver ?next=/alguma-coisa/, respeita isso
        next_url = self.get_redirect_url()
        if next_url:
            return next_url

        user = self.request.user

        # 2) Se for barbeiro -> agenda do barbeiro
        if Barbeiro.objects.filter(user=user).exists():
            return reverse_lazy("bookings:agenda_barbeiro")

        # 3) Caso contrário -> dashboard de cliente
        return reverse_lazy("bookings:dashboard")


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Conta criada com sucesso!")
            return redirect("bookings:dashboard")
    else:
        form = UserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})
