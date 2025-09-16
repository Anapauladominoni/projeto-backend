from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario, Produto, MetodoPagamento, Carrinho, ItemCarrinho, Loja, CategoriaLoja

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email') or attrs.get('username')
        password = attrs.get('password')
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Credenciais inválidas")

        if not user.check_password(password):
            raise serializers.ValidationError("Credenciais inválidas")
        if not getattr(user, 'is_active', True):
            raise serializers.ValidationError("Usuário inativo")

        refresh = self.get_token(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class UsuarioSerializer(serializers.ModelSerializer):
    # aceitar CPF com pontos/traços no input; normalizar antes da validação do campo do modelo
    cpf = serializers.CharField(required=False, allow_blank=True, max_length=18)
    data_nascimento = serializers.DateField(format='%d/%m/%Y', input_formats=['%d/%m/%Y', '%Y-%m-%d'])

    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'cpf', 'telefone', 'data_nascimento', 'password', 'role', 'is_staff', 'is_superuser']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_cpf(self, value):
        if not value:
            return value
        # normaliza removendo caracteres não numéricos
        digits = ''.join(ch for ch in value if ch.isdigit())
        if len(digits) != 11:
            raise serializers.ValidationError('CPF precisa conter 11 dígitos.')
        # valida unicidade (permitir atualizar o próprio registro)
        qs = Usuario.objects.filter(cpf=digits)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('CPF já cadastrado.')
        return digits

    def create(self, validated_data):
        # Usar create_user do manager para respeitar set_password e defaults
        # remover campos que create_user não espera
        password = validated_data.pop('password', None) if 'password' in validated_data else None
        return Usuario.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        # permitir atualização parcial e tratar password separadamente
        password = validated_data.pop('password', None) if 'password' in validated_data else None
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CategoriaLojaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaLoja
        fields = ['id', 'nome']


class LojaSerializer(serializers.ModelSerializer):
    categorias = serializers.PrimaryKeyRelatedField(queryset=CategoriaLoja.objects.all(), many=True, required=False)

    class Meta:
        model = Loja
        fields = ['id', 'nome', 'empreendedor', 'categorias', 'descricao', 'imagem', 'cep', 'rua', 'numero', 'complemento', 'cpf_cnpj']
        read_only_fields = ['empreendedor']

    def validate_cpf_cnpj(self, value):
        if not value:
            return value
        digits = ''.join(ch for ch in value if ch.isdigit())
        if len(digits) not in (11, 14):
            raise serializers.ValidationError('CPF/CNPJ precisa ter 11 (CPF) ou 14 (CNPJ) dígitos.')
        return digits

class UsuarioLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    senha = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(request=self.context.get('request'),
                            username=data['email'],
                            password=data['senha'])
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