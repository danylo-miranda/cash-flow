# Sistema de Gestão Financeira - Backend API

Sistema backend desenvolvido em Django REST Framework para gestão financeira empresarial, com suporte a múltiplas organizações, hierarquia de usuários e fluxo de caixa.

## 🚀 Tecnologias Utilizadas

- **Python 3.x** - Linguagem de programação
- **Django 5.2.8** - Framework web principal
- **Django REST Framework (DRF) 3.16.1** - APIs REST
- **SimpleJWT 5.5.1** - Autenticação JWT
- **Django Filter 25.2** - Filtragem avançada de dados
- **SQLite** - Banco de dados (desenvolvimento)
- **MySQL** - Banco de dados (produção)

## 📋 Funcionalidades Principais

### 🔐 Autenticação e Autorização
- Sistema de usuários customizado com papéis hierárquicos
- Autenticação via JWT (Access + Refresh tokens)
- Controle de acesso baseado em organizações
- Permissões granulares por funcionalidade

### 🏢 Gestão Organizacional
- Múltiplas organizações por usuário
- Sistema de membros com papéis específicos
- Controle de acesso por organização

### 💰 Gestão Financeira
- Cadastro de receitas, despesas, custos, investimentos e impostos
- Sistema hierárquico de contas e categorias
- Controle de competência vs. pagamento
- Status de transações (previsto/confirmado)

### 📊 Fluxo de Caixa
- Projeções automáticas baseadas em transações
- Consolidação por período (diário/semanal/mensal)
- Cálculo de saldos acumulados
- Relatórios de entrada, saída e saldo líquido

## 🏗️ Arquitetura do Sistema

### Estrutura de Apps

```
core/
├── accounts/          # Usuários e autenticação
├── organizations/     # Organizações e membros
├── ledger/           # Transações financeiras
├── cashflow/         # Fluxo de caixa e projeções
└── core/             # Configurações principais
```

### Modelos de Dados

#### 👤 Accounts (Usuários)
```python
User (AbstractUser)
├── role: ADMIN | FINANCEIRO | CONSULTOR | ANALISTA
├── username, email, first_name, last_name
└── Relacionamentos via Membership
```

#### 🏢 Organizations (Organizações)
```python
Organization
├── name: Nome da empresa
├── cnpj: CNPJ (opcional)
├── default_currency: Moeda padrão
└── timezone: Fuso horário

Membership (Relacionamento User ↔ Organization)
├── user: Usuário
├── organization: Organização
├── role: Papel específico na organização
├── is_active: Status do membro
└── joined_at: Data de entrada
```

#### 💳 Ledger (Livro Razão)
```python
Account (Contas Hierárquicas)
├── name: Nome da conta
├── account_type: RECEITA | DESPESA | INVESTIMENTO | IMPOSTO
├── parent: Conta pai (hierarquia)
├── depth: Nível hierárquico
└── organization: Organização proprietária

Category (Categorias)
├── name: Nome da categoria
├── parent: Categoria pai
├── depth: Nível hierárquico
└── organization: Organização

Transaction (Transações)
├── organization: Organização
├── account: Conta de origem/destino
├── category: Categoria de classificação
├── kind: RECEITA | DESPESA | CUSTO | INVESTIMENTO | IMPOSTO
├── amount: Valor (Decimal)
├── competence_date: Data de competência
├── payment_date: Data de pagamento
├── status: PREVISTO | CONFIRMADO
├── description: Descrição
└── notes: Observações
```

#### 📈 Cashflow (Fluxo de Caixa)
```python
CashFlowProjection
├── organization: Organização
├── date: Data da projeção
├── inflow: Entradas previstas
├── outflow: Saídas previstas
├── net_flow: Fluxo líquido
└── accumulated_balance: Saldo acumulado
```

## 🔄 Fluxos de Informação

### 1. Autenticação e Acesso
```
Cliente → POST /auth/login → JWT Token → Headers Authorization
       ↓
Middleware JWT → Validação → User Context → Permissions
       ↓
ViewSet → Organization Check → Data Access
```

### 2. Cadastro de Transações
```
Frontend → POST /api/transactions/
       ↓
Serializer Validation → Transaction.save()
       ↓
Auto-update CashFlow → Recalcular Projeções
```

### 3. Geração de Fluxo de Caixa
```
Request → GET /api/cashflow/summary/?organization=X&start=Y&end=Z
       ↓
generate_cashflow_summary() → Query Transactions
       ↓
Aggregate por Data → Calcular Entradas/Saídas
       ↓
Série Temporal → JSON Response
```

## 🛠️ Configuração e Instalação

### Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes)
- MySQL 8.0+ (produção)

### Instalação

1. **Clone e prepare o ambiente:**
```bash
cd saas/
# Ativar ambiente virtual existente
.\env\Scripts\activate  # Windows
# source env/bin/activate  # Linux/Mac
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure o banco de dados:**

**Desenvolvimento (SQLite):**
```bash
cd core/
python manage.py migrate
python manage.py createsuperuser
```

**Produção (MySQL):**
```bash
# Instalar driver MySQL
pip install mysqlclient

# Configurar variáveis de ambiente
export DB_ENGINE=mysql
export MYSQL_DATABASE=saas
export MYSQL_USER=saas_user
export MYSQL_PASSWORD=senha_forte
export MYSQL_HOST=localhost
export MYSQL_PORT=3306

# Executar migrações
python manage.py migrate
python manage.py createsuperuser
```

4. **Inicie o servidor:**
```bash
python manage.py runserver
```

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Django
DJANGO_SECRET_KEY=sua_chave_secreta_aqui
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=api.seudominio.com,localhost

# Banco de Dados
DB_ENGINE=mysql  # ou sqlite para desenvolvimento
MYSQL_DATABASE=saas
MYSQL_USER=saas_user
MYSQL_PASSWORD=senha_forte
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

## 📡 Endpoints da API

### Autenticação
```
POST /auth/login/          # Login (username/password → JWT)
POST /auth/refresh/        # Renovar token
POST /auth/logout/         # Logout
```

### Organizações
```
GET    /api/organizations/           # Listar organizações do usuário
POST   /api/organizations/           # Criar organização
GET    /api/organizations/{id}/      # Detalhes da organização
PUT    /api/organizations/{id}/      # Atualizar organização
DELETE /api/organizations/{id}/      # Excluir organização
```

### Contas e Categorias
```
GET    /api/accounts/               # Listar contas
POST   /api/accounts/               # Criar conta
GET    /api/categories/             # Listar categorias
POST   /api/categories/             # Criar categoria
```

### Transações
```
GET    /api/transactions/           # Listar transações
POST   /api/transactions/           # Criar transação
GET    /api/transactions/{id}/      # Detalhes da transação
PUT    /api/transactions/{id}/      # Atualizar transação
DELETE /api/transactions/{id}/      # Excluir transação

# Filtros disponíveis:
# ?organization=1&kind=RECEITA&status=CONFIRMADO
# ?competence_date__gte=2024-01-01&competence_date__lte=2024-12-31
```

### Fluxo de Caixa
```
GET /api/cashflow/summary/          # Resumo do fluxo de caixa
# Parâmetros obrigatórios:
# ?organization=1&start=2024-01-01&end=2024-12-31
```

## 🧪 Testes

Execute a suíte de testes:

```bash
cd core/
python manage.py test
```

### Cobertura de Testes
- ✅ Modelos (User, Organization, Transaction, etc.)
- ✅ Serializers e validações
- ✅ Permissions e autenticação
- ✅ APIs principais (CRUD + fluxo de caixa)
- ✅ Serviços de negócio

## 🔒 Segurança

### Autenticação
- JWT com tokens de curta duração (30min) + refresh (7 dias)
- Headers `Authorization: Bearer <token>`
- Logout via blacklist de tokens

### Autorização
- Permissões baseadas em organização
- Validação de membership ativo
- Controle de acesso por papel do usuário

### Validações
- Sanitização de entrada via serializers
- Validação de datas e valores monetários
- Prevenção de acesso cross-organization

## 📊 Exemplo de Uso

### 1. Autenticação
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "senha123"}'

# Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 2. Criar Transação
```bash
curl -X POST http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "organization": 1,
    "account": 1,
    "category": 1,
    "kind": "RECEITA",
    "amount": "1500.00",
    "competence_date": "2024-01-15",
    "payment_date": "2024-01-15",
    "status": "CONFIRMADO",
    "description": "Venda de produto"
  }'
```

### 3. Consultar Fluxo de Caixa
```bash
curl -X GET "http://localhost:8000/api/cashflow/summary/?organization=1&start=2024-01-01&end=2024-01-31" \
  -H "Authorization: Bearer <token>"

# Response:
[
  {
    "date": "2024-01-01",
    "inflow": "0.00",
    "outflow": "0.00",
    "net": "0.00",
    "balance": "0.00"
  },
  {
    "date": "2024-01-15",
    "inflow": "1500.00",
    "outflow": "0.00",
    "net": "1500.00",
    "balance": "1500.00"
  }
]
```

## 🚀 Deploy e Produção

### Checklist de Deploy
- [ ] Configurar variáveis de ambiente de produção
- [ ] Configurar servidor MySQL
- [ ] Instalar `mysqlclient` ou driver MySQL
- [ ] Executar `python manage.py migrate`
- [ ] Configurar servidor web (nginx + gunicorn)
- [ ] Configurar SSL/HTTPS
- [ ] Configurar backup automático do banco

### Comandos de Produção
```bash
# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Executar com Gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000

# Verificar configuração
python manage.py check --deploy
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Consulte a documentação da API
- Verifique os logs de erro em `DEBUG=True`

---

**Desenvolvido com ❤️ usando Django REST Framework**
