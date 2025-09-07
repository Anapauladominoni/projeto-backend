from rest_framework import viewsets
from .models import (
    Usuario,
    Produto,
    MetodoPagamento,
    Carrinho,
    ItemCarrinho
)
from .serializers import (
    UsuarioSerializer,
    ProdutoSerializer,
    MetodoPagamentoSerializer,
    CarrinhoSerializer,
    ItemCarrinhoSerializer
)

from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        loja_id = self.request.query_params.get('loja')
        categoria = self.request.query_params.get('categoria')
        if loja_id:
            queryset = queryset.filter(loja_id=loja_id)
        if categoria:
            queryset = queryset.filter(categoria__iexact=categoria)
        return queryset


class MetodoPagamentoViewSet(viewsets.ModelViewSet):
    queryset = MetodoPagamento.objects.all()
    serializer_class = MetodoPagamentoSerializer


class CarrinhoViewSet(viewsets.ModelViewSet):
    queryset = Carrinho.objects.all()
    serializer_class = CarrinhoSerializer
    permission_classes = [IsAuthenticated]  

    def get_queryset(self):

        user = self.request.user
        return super().get_queryset().filter(cliente=user)  


class ItemCarrinhoViewSet(viewsets.ModelViewSet):
    queryset = ItemCarrinho.objects.all()
    serializer_class = ItemCarrinhoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        serializer.save()


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.action == 'create':  # Cadastro é público
            permission_classes = [AllowAny]
        elif self.action in ['list', 'destroy']:  # Listagem e deleção só admins
            permission_classes = [IsAdminUser]
        else:  # Atualização ou retrieve exige login
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff: 
            return Usuario.objects.all()
        return Usuario.objects.filter(id=user.id)