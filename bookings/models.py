# bookings/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# --------------------------
# MODELO: SERVIÇO
# --------------------------
class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    duracao_min = models.PositiveIntegerField(help_text="Duração em minutos")
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to="servicos/", blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.preco}€)"


# --------------------------
# MODELO: BARBEIRO
# --------------------------
class Barbeiro(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    foto = models.ImageField(upload_to="barbeiros/", blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# --------------------------
# MODELO: MARCAÇÃO
# --------------------------
class Marcacao(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("confirmed", "Confirmada"),
        ("cancelled", "Cancelada"),
    ]

    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="marcacoes")
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE, related_name="marcacoes")
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    inicio = models.DateTimeField()
    criado_em = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # ---------- NOVAS PROPRIEDADES ----------
    @property
    def data(self):
        """Retorna apenas a data local da marcação."""
        return timezone.localtime(self.inicio).date()

    @property
    def hora(self):
        """Retorna apenas a hora local da marcação."""
        return timezone.localtime(self.inicio).strftime("%H:%M")

    # ---------- MÉTODOS DE CONTROLO ----------
    def confirm(self):
        self.status = "confirmed"
        self.save()

    def cancel(self):
        self.status = "cancelled"
        self.save()

    def __str__(self):
        return f"{self.servico.nome} - {self.data} {self.hora}"
