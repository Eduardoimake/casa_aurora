# Casa Aurora — Backend do catálogo demonstrativo

Backend em Django e Django REST Framework para o protótipo fictício
“Casa Aurora — Presentes e Decoração”.

O site público e o painel administrativo personalizado pertencem a um
frontend separado, que consome `/api/v1/`. O Django Admin, acessível em
`/django-admin/`, é uma ferramenta auxiliar; não substitui os endpoints
administrativos. Este projeto é um **catálogo com gestão**, não um
e-commerce: não implementa carrinho, checkout, pedidos ou pagamentos.

**Estado de verificação:** os arquivos e comandos foram entregues como
instruções reproduzíveis. A presença deste README não comprova que o
projeto tenha sido copiado, instalado, migrado, testado ou iniciado na
sua máquina. Registre os resultados reais antes de afirmar que ele está
pronto.

## 1. Requisitos

- Python 3.13, adotado no fluxo principal.
- Ambiente virtual Python e `pip`.
- Dependências diretas definidas em `requirements.txt`.
- SQLite para o desenvolvimento local.
- PostgreSQL opcional, configurado por variáveis de ambiente.
- Um diretório **novo** para evitar sobrescrever banco, mídia ou código
  de uma instalação existente.

As versões diretas especificadas são Django 6.0.8, Django REST
Framework 3.18.1, Pillow 12.3.0, `django-cors-headers` 4.9.0 e
`psycopg[binary]` 3.3.6. Elas foram selecionadas para a configuração
proposta; somente a instalação e a execução no seu ambiente confirmarão
o resultado local. `requirements.txt` não é um lockfile de todas as
dependências transitivas.

## 2. Árvore final de arquivos

```text
casa_aurora_backend/
├── .env.example
├── .gitignore
├── API_CONTRACT.md
├── README.md
├── manage.py
├── requirements.txt
├── casa_aurora/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── catalog/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── deployment_checks.py
    ├── media_audit.py
    ├── models.py
    ├── orphan_media_audit.py
    ├── pagination.py
    ├── permissions.py
    ├── prototype_readiness.py
    ├── serializers.py
    ├── urls.py
    ├── validators.py
    ├── views.py
    ├── management/
    │   ├── __init__.py
    │   └── commands/
    │       ├── __init__.py
    │       ├── audit_catalog.py
    │       ├── audit_media.py
    │       ├── audit_orphan_media.py
    │       ├── check_prototype.py
    │       └── seed_demo.py
    ├── migrations/
    │   ├── __init__.py
    │   └── 0001_initial.py
    └── tests/
        ├── __init__.py
        ├── test_admin_api.py
        ├── test_admin_validation_regression.py
        ├── test_audit_catalog.py
        ├── test_auth.py
        ├── test_catalog_query_regression.py
        ├── test_contract_regression.py
        ├── test_deployment_checks.py
        ├── test_e2e_journey.py
        ├── test_media_audit.py
        ├── test_orphan_media_audit.py
        ├── test_prototype_readiness.py
        ├── test_public_api.py
        ├── test_publication_transitions.py
        ├── test_seed.py
        └── test_uploads.py
```

A árvore lista os **arquivos canônicos entregues até a Parte 10**.
`.env`, `.venv/`, `db.sqlite3`, `media/` e `staticfiles/` são
configuração privada ou artefatos locais; não devem ser confundidos com
blocos de código já entregues nem versionados como arquivos do projeto.

A versão final de `catalog/apps.py` é a entregue na **Parte 09**,
que registra `deployment_checks.py` e substitui a da Parte 03.
`API_CONTRACT.md` é a versão única da Parte 10. A migração
`catalog/migrations/0001_initial.py` já é fornecida: não gere outra
migração inicial como passo adicional.

## 3. Instalação local do zero

Os blocos desta seção formam **uma única sequência**. O fluxo principal
usa bash em Linux, macOS ou ambiente Unix. Execute cada bloco somente
depois de concluir o anterior. Todos os comandos `python manage.py`
são executados na raiz `casa_aurora_backend/`.

### Passo 1 — Criar diretórios

**Terminal:** bash/Unix. **Diretório inicial:** pasta onde deseja criar
`casa_aurora_backend/`; esse nome **não pode já existir**.

```bash
python3.13 --version
mkdir casa_aurora_backend
cd casa_aurora_backend
mkdir casa_aurora catalog
mkdir catalog/management catalog/management/commands
mkdir catalog/migrations catalog/tests
```

Se `python3.13 --version` falhar, pare antes de criar a estrutura.
Se `mkdir casa_aurora_backend` disser que a pasta já existe, pare:
não sobrescreva uma instalação preexistente. Crie outra pasta de
trabalho ou faça backup e examine o conteúdo existente antes de
escolher um plano de migração de dados.

**Não** execute `django-admin startproject` nem
`python manage.py startapp catalog`: os arquivos correspondentes são
fornecidos para cópia e esses geradores seriam um fluxo **alternativo**,
não passos adicionais.

### Passo 2 — Criar os arquivos

Copie cada bloco integral das Partes 02–10 da conversa para seu caminho
na árvore acima. Copie a **última versão declarada canônica** quando
um arquivo tiver sido substituído: isso se aplica a `catalog/apps.py`
na Parte 09. Salve `README.md` e `API_CONTRACT.md` como Markdown;
código Python como arquivos `.py`, preservando a codificação UTF-8.

Antes de continuar, confira **no disco** se os caminhos existem.
Os anexos textuais e blocos da conversa **não** criam automaticamente
arquivos no computador. Não copie `PM, Partes ...` como se fossem
módulos do backend: são registros das entregas no Space.

### Passo 3 — Criar e ativar o ambiente virtual

**Terminal:** bash/Unix. **Diretório:** `casa_aurora_backend/`.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

Se você **já criou** `.venv` ao seguir a Parte 01, **não a crie de
novo**: apenas ative-a com `source .venv/bin/activate`.

**PowerShell no Windows, caso use esse terminal:** com Python 3.13
instalado, crie o ambiente somente se ele ainda não existir e ative-o
na raiz do projeto:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Não use os blocos bash e PowerShell cumulativamente na mesma `.venv`.

### Passo 4 — Instalar dependências

**Terminal:** bash/Unix ou PowerShell com `.venv` ativado.
**Diretório:** `casa_aurora_backend/`, depois de copiar
`requirements.txt`.

```bash
python -m pip install -r requirements.txt
```

Se a instalação falhar, guarde a saída e resolva essa falha antes
de tentar `manage.py`. Não declare compatibilidade efetiva a partir
da presença de versões no arquivo de dependências.

### Passo 5 — Configurar `.env` local

**Terminal:** bash/Unix. **Diretório:** `casa_aurora_backend/`.
Execute o primeiro comando **somente se `.env` ainda não existir**:

```bash
cp -n .env.example .env
```

O `.env.example` tem `DJANGO_SECRET_KEY=` vazio **de propósito**.
No `.env` privado, gere e defina uma chave aleatória própria. O bloco
abaixo substitui **uma única** linha vazia; ele recusa um `.env` já
modificado, em vez de sobrescrever uma chave configurada:

```bash
python - <<'PY'
from pathlib import Path
import secrets

path = Path(".env")
text = path.read_text(encoding="utf-8")
marker = "DJANGO_SECRET_KEY=\n"

if text.count(marker) != 1:
    raise SystemExit(
        "Confira .env: esperava uma única DJANGO_SECRET_KEY vazia."
    )

text = text.replace(
    marker,
    f"DJANGO_SECRET_KEY={secrets.token_urlsafe(64)}\n",
)
path.write_text(text, encoding="utf-8")
PY
```

Se `.env` já contiver uma chave sua, **não rode o bloco de geração
novamente**. O código em `settings.py` não aceita chave vazia nem usa
a antiga chave fixa de desenvolvimento. Não versionar `.env`;
`.gitignore` o ignora.

Para o fluxo local proposto, mantenha `DJANGO_DEBUG=true` e
`DB_ENGINE=sqlite`. Se o frontend rodar em `http://localhost:5173`
e a API em `http://localhost:8000`, mantenha essa origem exata
em `CORS_ALLOWED_ORIGINS` **e** `CSRF_TRUSTED_ORIGINS`. Use o mesmo
nome de host `localhost` nos dois serviços; não misture sem revisão
com `127.0.0.1`. CORS não substitui CSRF.

**PowerShell:** crie `.env` a partir de `.env.example` sem substituir
um arquivo já configurado, e edite a linha `DJANGO_SECRET_KEY=`
localmente com uma chave aleatória própria. Não publique essa chave
nem a copie para `.env.example`.

### Passo 6 — Verificar a configuração

**Terminal:** bash/Unix ou PowerShell, `.venv` ativado.
**Diretório:** `casa_aurora_backend/`. Só faça isso depois que
`manage.py`, `settings.py`, `casa_aurora/urls.py`,
`catalog/urls.py`, models, serializers, views e imports estiverem
todos copiados.

```bash
python manage.py check
```

Se ocorrer erro, pare e examine a saída. Um `check` sem erros não
significa que testes passaram ou que o banco foi migrado.

### Passo 7 — Conferir a migração fornecida

**Mesmo terminal e diretório.** A versão canônica de
`catalog/migrations/0001_initial.py` deve já estar copiada.

```bash
python manage.py makemigrations --check --dry-run
```

Se o comando mostrar diferenças ou falhar, **pare antes de `migrate`**.
Como a migração inicial foi entregue para um banco novo, não execute
`python manage.py makemigrations catalog` para gerar outra inicial
em paralelo. Guarde a saída e confronte `models.py` com a migração.
Se a migração já foi aplicada em outro banco, **não** reescreva seu
histórico sem plano de atualização seguro.

### Passo 8 — Aplicar e conferir migrações

**Mesmo terminal e diretório; somente depois dos passos 6 e 7 sem
erros.**

```bash
python manage.py migrate
```

Depois, em **etapa separada**:

```bash
python manage.py migrate --check
```

No fluxo SQLite local, o banco de desenvolvimento será criado conforme
a configuração em `settings.py`. Não apague banco existente para
“corrigir” migrações. Traga a mensagem de erro para investigação.

### Passo 9 — Executar testes

**Mesmo terminal e diretório.** Os testes usam **banco isolado de
testes**; você ainda **não** precisa executar `seed_demo` no banco de
desenvolvimento. Comece por módulos, se quiser localizar falhas:

```bash
python manage.py test catalog.tests.test_seed
python manage.py test catalog.tests.test_public_api
python manage.py test catalog.tests.test_admin_api
python manage.py test catalog.tests.test_auth
python manage.py test catalog.tests.test_uploads
python manage.py test catalog.tests.test_contract_regression
python manage.py test catalog.tests.test_e2e_journey
python manage.py test catalog.tests.test_publication_transitions
python manage.py test catalog.tests.test_admin_validation_regression
python manage.py test catalog.tests.test_catalog_query_regression
python manage.py test catalog.tests.test_audit_catalog
python manage.py test catalog.tests.test_media_audit
python manage.py test catalog.tests.test_orphan_media_audit
python manage.py test catalog.tests.test_deployment_checks
python manage.py test catalog.tests.test_prototype_readiness
```

Depois execute **toda a suíte**, para detectar interações e arquivos
esquecidos:

```bash
python manage.py test catalog.tests
```

Não interprete código de teste escrito como resultado de teste
executado. Se qualquer comando falhar, preserve a saída completa
para corrigir código, configuração ou expectativa errada — sem
enfraquecer testes apenas para obter resultado verde.

### Passo 10 — Popular dados demonstrativos

**Mesmo terminal e diretório; somente após `migrate` aplicado.**

```bash
python manage.py seed_demo
```

O comando pretende criar uma loja, três categorias, nove produtos e
uma promoção quando executado em banco novo. Reexecutá-lo não deve
duplicar os registros encontrados pelas chaves estáveis nem
sobrescrever edições administrativas nesses registros. Ele **não**
cria usuário staff.

Os textos, preços, banner sem imagem e o valor
`999999999999999` do campo WhatsApp são **demonstrativos**.
Não use esse número como contato público real nem ative um botão que
envie mensagens para ele. O frontend deve usar placeholder local
identificado até haver imagem autorizada.

### Passo 11 — Criar usuário staff manualmente

**Mesmo terminal e diretório; após `migrate`.** Crie uma conta própria
interativamente:

```bash
python manage.py createsuperuser
```

Escolha uma senha privada não previsível; não publique usuário e senha
no README nem acrescente conta de senha fixa ao seed. O comando
`createsuperuser` cria uma conta com permissões mais amplas que
`is_staff`; para uma instalação real, defina contas e privilégios
conforme sua política de acesso. O backend da API administrativa
confere sessão autenticada e `is_staff=True`.

### Passo 12 — Auditorias opcionais

**Mesmo terminal e diretório; banco já migrado.** Esses comandos
fazem diagnósticos e não são pré-requisitos para iniciar o núcleo.
Execute cada um separadamente para interpretar sua saída:

```bash
python manage.py audit_catalog
python manage.py audit_media
python manage.py audit_orphan_media
python manage.py check_prototype
```

- `audit_catalog` verifica loja e visibilidade; com o seed, deve
  apontar o WhatsApp fictício.
- `audit_media` consulta referências de imagens no banco e se o
  armazenamento informa que os arquivos existem.
- `audit_orphan_media` lista **candidatos** sem referência atual
  nas pastas gerenciadas; não os exclui.
- `check_prototype` verifica dados mínimos e faz leituras internas
  das rotas públicas por meio do cliente de testes do Django.

Nos comandos que aceitam `--strict`, avisos ou inspeção incompleta
podem fazer o comando retornar erro, **sem modificar dados**.
Não apague arquivos porque foram classificados como candidatos.
Auditorias sem avisos **não provam autorização** para publicar
telefone, endereço ou imagem. Se `check_prototype` reportar erro
HTTP `400` para o host `testserver`, confira `DJANGO_ALLOWED_HOSTS`
para o cliente de testes e a configuração efetivamente carregada;
não abra indiscriminadamente os hosts de produção para contornar
o diagnóstico.

### Passo 13 — Iniciar o servidor local

**Mesmo terminal e diretório.** Use isto somente no
**desenvolvimento local**:

```bash
python manage.py runserver
```

Com o servidor iniciado, confira as URLs em um navegador ou cliente
HTTP:

- `http://localhost:8000/api/v1/public/store/`
- `http://localhost:8000/api/v1/public/categories/`
- `http://localhost:8000/api/v1/public/products/`
- `http://localhost:8000/api/v1/public/promotions/`
- `http://localhost:8000/api/v1/auth/csrf/`

Antes do seed, `GET /api/v1/public/store/` pode devolver `404`.
Depois do seed, não habilite um link real de WhatsApp para o
número fictício. A existência de uma URL nesta lista não prova
que ela funcionou; confira o status e o corpo da resposta real.

Para conferir a jornada administrativa em um frontend, faça primeiro
`GET /api/v1/auth/csrf/`, depois `POST /api/v1/auth/login/` com
cookie e `X-CSRFToken`; use o **novo** token devolvido no login
para as operações de escrita, mantendo os cookies. O painel
personalizado consome `/api/v1/admin/`; o Django Admin é auxiliar.
Consulte `API_CONTRACT.md` antes de construir requisições ou
interpretar respostas.

## 4. Rotina local e publicação

O roteiro anterior é **local**. Não publique com `DEBUG=true`, não use
`runserver` como servidor de produção e não entregue o `.env` local
com o projeto. Para uma implantação, planeje separadamente:

1. Fornecer `DJANGO_SECRET_KEY` por mecanismo seguro de ambiente;
   configurar `DJANGO_DEBUG=false` e `DJANGO_ALLOWED_HOSTS` reais.
2. Colocar frontend e API sob a **mesma origem HTTPS**; configurar
   proxy reverso confiável, cookies seguros e cabeçalhos de HTTPS.
   Ativar `DJANGO_TRUST_PROXY_SSL_HEADER` apenas se o proxy impedir
   que clientes definam livremente o cabeçalho confiado.
3. Selecionar SQLite apenas onde for adequado ao ambiente ou
   configurar PostgreSQL com `DB_ENGINE=postgresql`, `DB_NAME`,
   `DB_USER`, `DB_PASSWORD`, `DB_HOST` e `DB_PORT`; verificar
   conectividade e backup antes de migrar dados.
4. Separar estáticos (`STATIC_ROOT`) de uploads de usuários
   (`MEDIA_ROOT`). Planejar `collectstatic` e um serviço de mídia
   adequado ao ambiente, sem depender de `static()` habilitado
   somente com `DEBUG=true`.
5. Confirmar titularidade e autorização de contatos, imagens,
   endereços e conteúdo publicado; substituir o seed demonstrativo
   conforme necessário **sem inventar dados reais**.
6. Executar os testes, auditorias pertinentes e as verificações
   estáticas de implantação em um ambiente configurado para isso:

```bash
python manage.py check --deploy
```

`check --deploy` não testa por si só navegador, frontend, HTTPS real,
proxy, permissões do armazenamento ou autorização de publicação.
Defina um servidor de aplicação e um plano operacional próprios
para produção; este README não recomenda `runserver` para ela.

## 5. Contrato para o frontend

`API_CONTRACT.md` é a fonte dos nomes de campos, paginação, filtros,
métodos e fluxo sessão–CSRF. No backend entregue:

- Preço usa `DecimalField` e é apresentado como string decimal no JSON.
- Listagem pública de produtos é paginada; categorias e promoções
  públicas são arrays.
- Entrada administrativa de `category` e `product` usa IDs;
  representações públicas associadas usam objetos aninhados.
- Upload usa campos planos em `multipart/form-data`:
  `main_image`, `banner_image` e `image`.
- A recusa de um anônimo nas rotas administrativas com a autenticação
  por sessão configurada está documentada como `403`, não como `401`
  presumido.
- O logout bem-sucedido é `204`, sem corpo JSON.
- O primeiro `PATCH /api/v1/admin/store/` com campos obrigatórios
  válidos pode criar o registro e retornar `201`; `PATCH` posterior
  retorna `200`.

Mantenha o frontend sem credenciais em `localStorage`, com CSRF
ativo e autorização verificada no backend. Se a execução real
identificar qualquer divergência entre este README, o contrato
e os arquivos Python, corrija a versão canônica correspondente
antes de declarar o protótipo concluído.