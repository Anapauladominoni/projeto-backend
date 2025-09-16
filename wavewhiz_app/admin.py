from django.contrib import admin
from .models import (
    Usuario,
    Produto,
    MetodoPagamento,
    Carrinho,
    ItemCarrinho,
    Loja
)
from .models import CategoriaLoja

# Registrando todos os models no admin
admin.site.register(Usuario)
admin.site.register(Produto)
admin.site.register(MetodoPagamento)
admin.site.register(Carrinho)
admin.site.register(ItemCarrinho)
class LojaAdmin(admin.ModelAdmin):
    filter_horizontal = ('categorias',)

admin.site.register(Loja, LojaAdmin)
admin.site.register(CategoriaLoja)
