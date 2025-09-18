# Wavewhiz API

Documentação básica da API do Wavewhiz (backend Django REST Framework).

## Autenticação
- Usamos JWT com `rest_framework_simplejwt`.
- Endpoints:
  - `POST /api/token/` - obter `access` e `refresh` (envie `email` e `password`).
  - `POST /api/token/refresh/` - renovar `access` com `refresh`.

## Endpoints principais
Registrados pelo router em `wavewhiz_app/urls.py`:

- `GET/POST /usuarios/` - listar/registrar usuários. Criação (`POST`) é pública.
- `GET/PUT/PATCH /usuarios/{id}/` - ver/atualizar usuário. Usuários normais só podem ver/editar o próprio perfil; admins podem editar qualquer.
- `GET/DELETE /usuarios/{id}/` - listagem e deleção restritas a admins.

- `GET/POST /lojas/` - listar/registrar lojas. Criação exige autenticação (o usuário autenticado será definido como empreendedor automaticamente).
- `GET/PUT/PATCH /lojas/{id}/` - ver/editar loja (autenticação requerida para editar).

- `GET/POST /produtos/` - CRUD de produtos
- `GET/POST /metodos-pagamento/` - CRUD de métodos de pagamento
- `GET/POST /carrinhos/` - Carrinho do cliente (apenas carrinhos do próprio cliente são visíveis; admins podem filtrar com `?cliente=<id>`)
- `GET/POST /itens-carrinho/` - Itens do carrinho
- `GET /categorias/` - Listar categorias de loja (público)

## Modelos / Campos relevantes
### Usuario
Campos principais (JSON):
- `id` (int)
- `nome` (string)
- `email` (email)
- `cpf` (string, 11 dígitos; pode enviar com máscara `123.456.789-01` — será normalizado)
- `telefone` (string)
- `data_nascimento` (string, formato `dd/mm/aaaa` ou `YYYY-MM-DD`)
- `role` (string: `admin`, `cliente`, `empreendedor`)

Exemplo de criação (POST /usuarios/):

```
{
  "nome": "João Cliente",
  "email": "joao@ex.com",
  "cpf": "123.456.789-01",
  "telefone": "999888777",
  "data_nascimento": "15/09/1990",
  "role": "cliente"
}
```

### Loja
- `id`, `nome`, `empreendedor` (ID), `categorias` (lista de IDs de `CategoriaLoja`), `descricao`, `imagem`, `cep`, `rua`, `numero`, `complemento`, `cpf_cnpj` (11 ou 14 dígitos)

Exemplo de criação (autenticado como empreendedor):

```
POST /lojas/
{
  "nome": "Minha Loja",
  "categorias": [1, 2],
  "descricao": "Produtos locais",
  "cep": "12345678",
  "rua": "Rua A",
  "numero": "10",
  "complemento": "Sala 2",
  "cpf_cnpj": "11222333000181"
}
```

### CategoriaLoja
- `id`, `nome` (string único)

Exemplo de listagem (GET /categorias/):

```
[
  {"id": 1, "nome": "Alimentos"},
  {"id": 2, "nome": "Artesanatos"}
]
```

### Produto
- `id`, `loja` (ID), `nome`, `preco` (decimal), `estoque` (int), `imagem`, `descricao`

Exemplo de criação (autenticado como empreendedor):

```
POST /produtos/
{
  "loja": 1,
  "nome": "Produto Exemplo",
  "preco": 29.99,
  "estoque": 100,
  "descricao": "Descrição do produto"
}
```

### Carrinho
- `id`, `cliente` (ID, readonly), `metodo_pagamento` (ID), `itens` (lista readonly), `total` (calculado readonly), `finalizado` (bool)

Exemplo de criação (cliente cria seu carrinho automaticamente):

```
POST /carrinhos/
{
  "metodo_pagamento": 1
}
```

- O `cliente` é definido automaticamente como o usuário autenticado.

### ItemCarrinho
- `id`, `carrinho_id` (write-only), `produto` (readonly), `produto_id` (write-only), `quantidade` (int), `subtotal` (calculado readonly)

Exemplo de adição de item ao carrinho:

```
POST /itens-carrinho/
{
  "carrinho_id": 1,
  "produto_id": 2,
  "quantidade": 3
}
```

### MetodoPagamento
- `id`, `nome` (string)

## Funcionalidades do Carrinho
### Adicionar Itens ao Carrinho
1. Crie ou use um carrinho existente (GET /carrinhos/ para listar os seus).
2. Adicione itens com POST /itens-carrinho/, especificando `carrinho` (ID do carrinho), `produto_id` (ID do produto) e `quantidade`.
3. O subtotal é calculado automaticamente (preço × quantidade).

### Concluir (Finalizar) um Carrinho
Para finalizar uma compra:
1. Atualize o carrinho com PATCH /carrinhos/{id}/, definindo `"finalizado": true`.
2. Exemplo:

```
PATCH /carrinhos/1/
{
  "finalizado": true
}
```

- Uma vez finalizado, o carrinho não pode ser editado (lógica pode ser adicionada no futuro para validar estoque, etc.).
- O `total` é a soma dos subtotais de todos os itens.

### Filtros Disponíveis
- **Lojas**: `GET /lojas/?categoria=<id>` ou `GET /lojas/?empreendedor=<id>`
- **Produtos**: `GET /produtos/?loja=<id>`
- **Carrinhos** (admins): `GET /carrinhos/?cliente=<id>`

## Permissões e Funcionalidades por Role
Cada usuário tem um `role` (`admin`, `cliente`, `empreendedor`) que define o que pode fazer. Abaixo, as funcionalidades principais por role.

### Cliente
- **Cadastro e Autenticação**: Pode se cadastrar (POST /usuarios/) e fazer login (POST /api/token/).
- **Perfil**: Ver/editar apenas o próprio perfil (GET/PUT/PATCH /usuarios/{id}/).
- **Navegação**: Listar lojas (GET /lojas/), produtos (GET /produtos/), categorias (GET /categorias/) — tudo público.
- **Carrinho**: Criar/ver carrinho próprio (GET/POST /carrinhos/), adicionar/remover itens (GET/POST /itens-carrinho/), escolher método de pagamento.
- **Restrições**: Não pode criar lojas, produtos ou gerenciar outros usuários.

### Empreendedor
- **Tudo do Cliente**: Pode fazer tudo que um cliente faz.
- **Lojas**: Criar/editar suas próprias lojas (POST/PUT/PATCH /lojas/), listar todas as lojas.
- **Produtos**: CRUD completo de produtos (GET/POST/PUT/PATCH /produtos/), mas associado às suas lojas.
- **Restrições**: Não pode gerenciar usuários ou deletar perfis.

### Admin
- **Tudo do Empreendedor**: Pode fazer tudo que empreendedores fazem.
- **Usuários**: Listar/deletar qualquer usuário (GET/DELETE /usuarios/), editar qualquer perfil (PUT/PATCH /usuarios/{id}/).
- **Gerenciamento Geral**: Acesso total a todos os endpoints, incluindo métodos de pagamento, carrinhos de qualquer um, etc.
- **Admin Django**: Acesso ao painel /admin/ para gerenciamento avançado.

## Observações
- CPF/CNPJ e CEP são validados para conter apenas dígitos e tamanho correto; entradas com máscara serão normalizadas.
- `Loja.categorias` é ManyToMany com `CategoriaLoja`.
- Endereços ficam na Loja, não no Usuario (um empreendedor pode ter várias lojas).
- Faça backup do banco (`db.sqlite3`) antes de alterações de esquema em produção.

## Como testar localmente
```bash
pdm install
pdm run python manage.py migrate
pdm run python manage.py runserver
```

## Restaurar usuários a partir do backup
Se você tiver `users_backup.json` gerado com `dumpdata`, pode restaurar com:

```bash
pdm run python manage.py loaddata users_backup.json
```
