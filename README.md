# Casa Aurora — catálogo demonstrativo

Casa Aurora é um projeto demonstrativo de catálogo de presentes e decoração, desenvolvido para apresentar a estrutura de um site público integrado a uma API e a um painel de gestão. Não representa uma loja ou cliente real.

O projeto não implementa carrinho, checkout, pedidos, pagamentos nem métricas de vendas. Textos, preços e dados do catálogo usados na demonstração não devem ser interpretados como ofertas comerciais reais.

## Estrutura e tecnologias

```text
casa_aurora_frontend/   Interface pública e painel administrativo em Vite e JavaScript
casa_aurora_backend/    API e gestão em Django e Django REST Framework
```

O frontend contém páginas de catálogo, detalhe de produto e painel administrativo. O backend disponibiliza a API sob `/api/v1/`, autenticação administrativa por sessão com proteção CSRF e recursos de gestão do catálogo. O Django Admin é auxiliar; o painel personalizado consome a API administrativa.

Para detalhes de cada parte, consulte:

- `casa_aurora_frontend/README.md`
- `casa_aurora_frontend/MANUAL_CHECKLIST.md`
- `casa_aurora_backend/README.md`
- `casa_aurora_backend/API_CONTRACT.md`

## Funcionalidades e limites

- Consulta pública de informações da loja, categorias, produtos e promoções.
- Listagem de produtos, página de produto e seção de produtos em destaque.
- Login e sessão para usuários administrativos autorizados.
- Painel para gestão de categorias, produtos, configurações da loja e promoções.
- Upload de imagens por meio da API, sujeito às validações do backend.

A existência dessas funcionalidades no código não substitui a verificação da integração no navegador. Este repositório não contém dados de produção, conta administrativa pública nem credenciais de demonstração.

## Execução local no Windows

Pré-requisitos: instalações de Python e Node.js/npm compatíveis com as dependências declaradas em `casa_aurora_backend/requirements.txt` e `casa_aurora_frontend/package.json`. Os comandos abaixo usam PowerShell. Não recrie os projetos com `startproject`, `startapp` ou `npm create vite`: use os arquivos existentes.

No primeiro terminal, prepare o backend. Execute os comandos dentro de `C:\prototipo_profissional\casa_aurora_backend`:

```powershell
Set-Location C:\prototipo_profissional\casa_aurora_backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Crie um `.env` privado a partir de `.env.example` **somente se ainda não existir**:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Antes de iniciar o backend, edite o `.env` privado e defina uma `DJANGO_SECRET_KEY` gerada por você. Não copie o valor para documentação, mensagens ou Git. Confira também os hosts e as origens CORS/CSRF de desenvolvimento, de acordo com `casa_aurora_backend/README.md`.

Ainda no diretório do backend:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py migrate --check
python manage.py test catalog.tests
```

Se qualquer verificação falhar, pare e investigue antes de continuar. Para carregar dados fictícios no banco local e criar uma conta administrativa própria:

```powershell
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver localhost:8000
```

O `seed_demo` não cria uma conta administrativa. Dados demonstrativos de endereço ou contato não são autorização para apresentá-los como dados reais.

No segundo terminal, execute os comandos dentro de `C:\prototipo_profissional\casa_aurora_frontend`:

```powershell
Set-Location C:\prototipo_profissional\casa_aurora_frontend
npm ci
if (-not (Test-Path .env.local)) { Copy-Item .env.example .env.local }
npm run check:syntax
npm run build
npm run dev
```

Com os servidores locais iniciados, abra o frontend em `http://localhost:5173/`. O exemplo de `.env.local` aponta para a API em `http://localhost:8000`. Mantenha o hostname coerente nas duas aplicações e consulte o contrato da API se alterar as origens.

Um build concluído não comprova login, sessão, CSRF, CRUD, uploads nem funcionamento visual. Confira esses fluxos no navegador seguindo `casa_aurora_frontend/MANUAL_CHECKLIST.md`.

## Variáveis de ambiente

Use `casa_aurora_backend/.env.example` e `casa_aurora_frontend/.env.example` apenas como modelos. O backend exige uma chave privada própria e dispõe de configurações para modo de depuração, hosts, origens CORS/CSRF, banco de dados e limite de upload. O frontend usa `VITE_API_BASE_URL` para indicar a origem da API.

Não versione `.env`, `.env.local`, senhas, tokens, cookies, banco SQLite ou arquivos enviados por usuários. A presença de uma regra no `.gitignore` não comprova que um arquivo nunca tenha sido rastreado: confira o índice e o histórico Git antes de publicar.

## Conteúdo e publicação

A Casa Aurora é fictícia. Antes de tornar uma demonstração acessível ao público, revise as informações exibidas pela API e pelo frontend: contatos, endereço, imagens, descrições e quaisquer dados inseridos localmente. Não apresente informações demonstrativas como pertencentes a um cliente real. Não inclua capturas de tela até confirmar que seu conteúdo e suas imagens podem ser publicados.

A publicação do código no GitHub e a implantação da aplicação são etapas diferentes. Uma implantação requer configuração própria de HTTPS, banco, arquivos estáticos, mídia, variáveis privadas e servidor de aplicação; os servidores locais de desenvolvimento não são uma solução de produção.

**Capturas de tela:** pendentes de autorização e seleção.

**Link da demonstração:** pendente.

**Status das verificações:** não documentado neste README. Registre resultados executados e evidências antes de anunciar que a aplicação foi testada ou publicada.