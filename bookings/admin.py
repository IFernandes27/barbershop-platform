from django.contrib import admin
from .models import Servico, Barbeiro, Marcacao


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco", "duracao_min", "has_image")
    search_fields = ("nome",)
    list_filter = ("duracao_min",)

    @admin.display(boolean=True, description="Imagem")
    def has_image(self, obj):
        return bool(obj.image)


@admin.register(Barbeiro)
class BarbeiroAdmin(admin.ModelAdmin):
    list_display = ("nome", "username", "ativo", "marcacoes_total")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    list_filter = ("ativo",)

    @admin.display(description="Nome")
    def nome(self, obj):
        # Mostra nome completo se houver, senão username
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description="Username")
    def username(self, obj):
        return obj.user.username

    @admin.display(description="Marcações")
    def marcacoes_total(self, obj):
        return obj.marcacoes.count()


@admin.register(Marcacao)
class MarcacaoAdmin(admin.ModelAdmin):
    list_display = ("cliente", "barbeiro", "servico", "inicio", "status")
    list_filter = ("status", "barbeiro", "servico")
    search_fields = (
        "cliente__username",
        "cliente__first_name",
        "cliente__last_name",
        "barbeiro__user__username",
        "servico__nome",
    )
    date_hierarchy = "inicio"
    ordering = ("-inicio",)
