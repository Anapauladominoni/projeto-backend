from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import date

cpf_validator = RegexValidator(
    regex=r'^\d{11}$',
    message='CPF deve ter exatamente 11 dígitos numéricos.'
)

telefone_validator = RegexValidator(
    regex=r'^\d{8,15}$',
    message='Telefone deve conter apenas números, entre 8 e 15 dígitos.'
)

cep_validator = RegexValidator(
    regex=r'^\d{8}$',
    message='CEP deve conter exatamente 8 dígitos numéricos.'
)

cpf_cnpj_validator = RegexValidator(
    regex=r'^(\d{11}|\d{14})$',
    message='Informe CPF (11 dígitos) ou CNPJ (14 dígitos), somente números.'
)

class CategoriaLoja(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Categoria de Loja"
        verbose_name_plural = "Categorias de Loja"

    def __str__(self):
        return self.nome

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, role='cliente', **extra_fields):
        if not email:
            raise ValueError("Email obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        role = extra_fields.pop('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('nome', 'Administrador')
        extra_fields.setdefault('telefone', '0000000000') 
        extra_fields.setdefault('cpf', '00000000000')
        extra_fields.setdefault('data_nascimento', date(1970, 1, 1)) 
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário precisa ter is_superuser=True.')
        return self.create_user(email, password=password, role=role, **extra_fields)

ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('cliente', 'Cliente'),
    ('empreendedor', 'Empreendedor'),
)

class Usuario(AbstractBaseUser):
    def delete(self, *args, **kwargs):
        # Limpa relações ManyToMany e logs do admin antes de deletar
        if hasattr(self, 'groups'):
            self.groups.clear()
        if hasattr(self, 'user_permissions'):
            self.user_permissions.clear()
        if hasattr(self, 'logentry_set'):
            try:
                self.logentry_set.all().delete()
            except Exception:
                pass
        super().delete(*args, **kwargs)
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=11, unique=True, validators=[cpf_validator], null=True, blank=True)
    telefone = models.CharField(max_length=15, validators=[telefone_validator])
    data_nascimento = models.DateField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.nome} ({self.role})"

    def save(self, *args, **kwargs):
        # Exigir CPF apenas para usuários comuns (não superusers)
        if not self.is_superuser and not self.cpf:
            raise ValueError("CPF obrigatório para usuários comuns.")
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return True

    def has_perm(self, perm, obj=None):
        return bool(self.is_superuser)

    def has_module_perms(self, app_label):
        return bool(self.is_superuser)

class Loja(models.Model):
    empreendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='lojas')  # on_delete CASCADE garante deleção em cascata
    nome = models.CharField(max_length=150)
    categorias = models.ManyToManyField(CategoriaLoja, blank=True, related_name='lojas')
    descricao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to='lojas/', blank=True, null=True)
    cep = models.CharField(max_length=8, validators=[cep_validator], null=True, blank=True)
    rua = models.CharField(max_length=200, null=True, blank=True)
    numero = models.CharField(max_length=20, null=True, blank=True)
    complemento = models.CharField(max_length=150, null=True, blank=True)
    cpf_cnpj = models.CharField(max_length=14, validators=[cpf_cnpj_validator], null=True, blank=True)

    class Meta:
        verbose_name = "Loja"
        verbose_name_plural = "Lojas"

    def __str__(self):
        return self.nome

    def clean(self):
        if self.empreendedor.role != 'empreendedor':
            raise ValidationError("O usuário deve ter role 'empreendedor' para criar uma loja.")

class Produto(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=150)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return f"{self.nome} - {self.loja.nome}"

class MetodoPagamento(models.Model):
    nome = models.CharField(max_length=40)

    class Meta:
        verbose_name = "Método de Pagamento"
        verbose_name_plural = "Métodos de Pagamento"

    def __str__(self):
        return self.nome

class Carrinho(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='carrinhos')  # on_delete CASCADE garante deleção em cascata
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
        return self.quantidade * self.produto.preco
