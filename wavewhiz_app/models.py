from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

cpf_validator = RegexValidator(
    regex=r'^\d{11}$',
    message='CPF deve ter exatamente 11 dígitos numéricos.'
)

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

    def create_superuser(self, email, senha, role='empreendedor', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário precisa ter is_superuser=True.')
        return self.create_user(email, senha, role, **extra_fields)

ROLE_CHOICES = (
    ('cliente', 'Cliente'),
    ('empreendedor', 'Empreendedor'),
)

class Usuario(AbstractBaseUser):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=11, unique=True, validators=[cpf_validator])
    telefone = models.CharField(max_length=15, validators=[telefone_validator])
    data_nascimento = models.DateField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'cpf', 'role']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.nome} ({self.role})"

class Loja(models.Model):
    CATEGORIAS = [
        ('ALIMENTOS', 'Alimentos'),
        ('ARTESANATOS', 'Artesanatos'),
        ('ROUPAS', 'Roupas'),
        ('OUTROS', 'Outros'),
    ]
    empreendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='lojas')
    nome = models.CharField(max_length=150)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='OUTROS')
    descricao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to='lojas/', blank=True, null=True)

    class Meta:
        verbose_name = "Loja"
        verbose_name_plural = "Lojas"

    def __str__(self):
        return self.nome

    def clean(self):
        if self.empreendedor.role != 'empreendedor':
            raise ValidationError("O usuário deve ter role 'empreendedor' para criar uma loja.")

class Produto(models.Model):
    CATEGORIAS = [
        ('ALIMENTOS', 'Alimentos'),
        ('ARTESANATOS', 'Artesanatos'),
        ('ROUPAS', 'Roupas'),
        ('OUTROS', 'Outros'),
    ]
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=150)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='OUTROS')
    estoque = models.PositiveIntegerField(default=0)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return f"{self.nome} - {self.loja.nome} ({self.get_categoria_display()})"

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

    def total(self):                   ml´. ;º°
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
