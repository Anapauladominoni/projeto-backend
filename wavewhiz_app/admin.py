from django.contrib import admin
from .models import (
    Usuario,
    Produto,
    MetodoPagamento,
    Carrinho,
    ItemCarrinho,
    Loja
)

# Registrando todos os models no admin
admin.site.register(Usuario)
admin.site.register(Produto)
admin.site.register(MetodoPagamento)
admin.site.register(Carrinho)
admin.site.register(ItemCarrinho)
admin.site.register(Loja)