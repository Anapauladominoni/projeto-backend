from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet,
    ProdutoViewSet,
    MetodoPagamentoViewSet,
    CarrinhoViewSet,
    ItemCarrinhoViewSet,
    LojaViewSet,
    CategoriaLojaViewSet,
)
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'produtos', ProdutoViewSet)
router.register(r'metodos-pagamento', MetodoPagamentoViewSet)
router.register(r'carrinhos', CarrinhoViewSet)
router.register(r'itens-carrinho', ItemCarrinhoViewSet)
router.register(r'lojas', LojaViewSet)
router.register(r'categorias', CategoriaLojaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
