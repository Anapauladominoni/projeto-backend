from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Usuario, Produto, MetodoPagamento, Carrinho, ItemCarrinho

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class UsuarioLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    senha = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['senha'])
        if not user:
            raise serializers.ValidationError("Credenciais inválidas")
        data['user'] = user
        return data

# Produtos e carrinho
class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'

class MetodoPagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPagamento
        fields = '__all__'

class ItemCarrinhoSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)
    produto_id = serializers.PrimaryKeyRelatedField(
        queryset=Produto.objects.all(), write_only=True, source='produto'
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemCarrinho
        fields = ['id', 'produto', 'produto_id', 'quantidade', 'subtotal']

    def get_subtotal(self, obj):
        return obj.subtotal()

class CarrinhoSerializer(serializers.ModelSerializer):
    cliente = UsuarioSerializer(read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), write_only=True, source='cliente'
    )
    itens = ItemCarrinhoSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carrinho
        fields = ['id', 'cliente', 'cliente_id', 'metodo_pagamento', 'itens', 'total', 'finalizado']

    def get_total(self, obj):
        return obj.total()