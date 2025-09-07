from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
# Validator para CPF
cpf_validator = RegexValidator(
    regex=r'^\d{11}$',
    message='CPF deve ter exatamente 11 dígitos numéricos.'
)

# Validator para telefone (opcional)
telefone_validator = RegexValidator(
    regex=r'^\d{8,15}$',
    message='Telefone deve conter apenas números, entre 8 e 15 dígitos.'
)

class CategoriaLoja(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Categoria de Loja"
        verbose_name_plural = "Categorias de Loja"

    def __str__(self):
        return self.nome

class UsuarioManager(BaseUserManager):
    def create_user(self, email, senha, role, **extra_fields):
        if not email:
            raise ValueError("Email obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(senha)
        user.save()
        return user

ROLE_CHOICES = (
    ('cliente', 'Cliente'),
    ('empreendedor', 'Empreendedor'),
)


class Usuario(AbstractBaseUser):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=11, unique=True)
    telefone = models.CharField(max_length=15)
    data_nascimento = models.DateField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'cpf', 'role']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.nome} ({self.role})"
    

class Loja(models.Model):
    empreendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='lojas')
    nome = models.CharField(max_length=150)
    categoria = models.ForeignKey(CategoriaLoja, on_delete=models.SET_NULL, null=True)
    descricao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to='lojas/', blank=True, null=True)

    class Meta:
        verbose_name = "Loja"
        verbose_name_plural = "Lojas"

    def __str__(self):
        return self.nome
    
    def clean(self):
        # Valida se o usuário é realmente um empreendedor
        if self.empreendedor.role != 'empreendedor':
            raise ValidationError("O usuário deve ter role 'empreendedor' para criar uma loja.")






class Produto(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=150)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=50)
    estoque = models.PositiveIntegerField(default=0)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return f"{self.nome} - {self.loja.nome}"

# ------------------- PAGAMENTO -------------------
class MetodoPagamento(models.Model):
    nome = models.CharField(max_length=40)

    class Meta:
        verbose_name = "Método de Pagamento"
        verbose_name_plural = "Métodos de Pagamento"

    def __str__(self):
        return self.nome

class Carrinho(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='carrinhos')
    metodo_pagamento = models.ForeignKey(MetodoPagamento, on_delete=models.SET_NULL, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    finalizado = models.BooleanField(default=False)

    def __str__(self):
        return f'Carrinho {self.pk} - {self.cliente.nome}'

    def total(self):
        return sum(item.subtotal() for item in self.itens.all())

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Item do Carrinho"
        verbose_name_plural = "Itens do Carrinho"

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"

    def subtotal(self):
        return self.quantidade * self.produto.preco