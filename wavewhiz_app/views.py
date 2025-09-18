from rest_framework import viewsets
from .models import (
    Usuario,
    Produto,
    MetodoPagamento,
    Carrinho,
    ItemCarrinho,
    Loja,
    CategoriaLoja,
)
from .serializers import (
    UsuarioSerializer,
    ProdutoSerializer,
    MetodoPagamentoSerializer,
    CarrinhoSerializer,
    ItemCarrinhoSerializer
    , LojaSerializer,
    CategoriaLojaSerializer,
)

from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        loja_id = self.request.query_params.get('loja')
        if loja_id:
            queryset = queryset.filter(loja_id=loja_id)
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
        queryset = super().get_queryset()
        cliente_id = self.request.query_params.get('cliente')
        if cliente_id:
            if user.is_staff:
                queryset = queryset.filter(cliente__id=cliente_id)
            else:
                # Non-staff can only see their own, ignore the param
                queryset = queryset.filter(cliente=user)
        else:
            if user.is_staff:
                # Staff can see all carts if no filter
                pass  # no filter
            else:
                queryset = queryset.filter(cliente=user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)  


class ItemCarrinhoViewSet(viewsets.ModelViewSet):
    queryset = ItemCarrinho.objects.all()
    serializer_class = ItemCarrinhoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return super().get_queryset()
        # Non-staff see only items from their own carts
        return super().get_queryset().filter(carrinho__cliente=user)

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
        # usuários comuns só veem seu próprio perfil
        return Usuario.objects.filter(id=user.id)

    def update(self, request, *args, **kwargs):
        # permitir que usuários atualizem apenas seu próprio perfil
        user = request.user
        if not user.is_staff:
            # se não for staff, forçar o PK para o próprio usuário
            kwargs['pk'] = user.pk
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            kwargs['pk'] = user.pk
        return super().partial_update(request, *args, **kwargs)


class LojaViewSet(viewsets.ModelViewSet):
    queryset = Loja.objects.all()
    serializer_class = LojaSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_id = self.request.query_params.get('categoria')
        empreendedor_id = self.request.query_params.get('empreendedor')
        if categoria_id:
            queryset = queryset.filter(categorias__id=categoria_id)
        if empreendedor_id:
            queryset = queryset.filter(empreendedor__id=empreendedor_id)
        return queryset

    def perform_create(self, serializer):
        # atribui automaticamente o empreendedor como o usuário autenticado
        serializer.save(empreendedor=self.request.user)


class CategoriaLojaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CategoriaLoja.objects.all()
    serializer_class = CategoriaLojaSerializer
    permission_classes = [AllowAny]