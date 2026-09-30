# Casa Aurora — Contrato da API v1

Este documento descreve a API REST do backend demonstrativo “Casa Aurora —
Presentes e Decoração” para implementação do site público e de um painel
administrativo em frontend separado.

**Estado de verificação:** este contrato foi confrontado com os arquivos
entregues nas Partes 02–09. Ele não constitui evidência de instalação,
migração, execução de testes ou funcionamento no ambiente do usuário.
Divergências observadas em execução devem ser investigadas e corrigidas
também neste documento.

## 1. Escopo e base

- Prefixo da API: `/api/v1/`.
- Respostas da API: JSON.
- Site público: leitura de loja, categorias, produtos e promoções.
- Painel personalizado: usa os endpoints `/api/v1/admin/`.
- Django Admin auxiliar: `/django-admin/`; não substitui a API do painel.
- Não existem endpoints de carrinho, checkout, pagamento, pedido ou cadastro
  público de administradores.

Em desenvolvimento, os exemplos assumem a API em
`http://localhost:8000` e, quando separado por porta, o frontend em
`http://localhost:5173`. Em uma demonstração publicada, use frontend e API
sob a mesma origem HTTPS. As imagens são expostas em URLs de mídia; a
publicação desses arquivos em produção depende de um serviço de mídia
configurado separadamente.

## 2. Endpoints

### Públicos

| Método | Caminho | Autenticação | Resposta principal |
|---|---|---|---|
| GET | `/api/v1/public/store/` | Não | Objeto da loja; `404` se ainda não configurada |
| GET | `/api/v1/public/categories/` | Não | Array de categorias ativas |
| GET | `/api/v1/public/products/` | Não | Objeto paginado de produtos publicáveis |
| GET | `/api/v1/public/products/<slug>/` | Não | Produto publicável; `404` se oculto, inexistente ou pertencente a categoria inativa |
| GET | `/api/v1/public/promotions/` | Não | Array de promoções publicamente elegíveis |

### Autenticação

| Método | Caminho | Autenticação anterior | Resultado |
|---|---|---|---|
| GET | `/api/v1/auth/csrf/` | Não | `200`, token CSRF e cookie CSRF |
| POST | `/api/v1/auth/login/` | Não; exige CSRF | `200`, usuário staff, sessão e novo token CSRF; credenciais inválidas ou usuário não staff: `403` |
| GET | `/api/v1/auth/me/` | Sessão de usuário staff | `200`, identidade; sem sessão staff: `403` |
| POST | `/api/v1/auth/logout/` | Sessão autenticada; exige CSRF | `204`, sem corpo de resposta; anônimo ou CSRF recusado: `403` |

`/auth/logout/` usa `IsAuthenticated`, não `IsStaffUser`: uma sessão já
autenticada pode ser encerrada por esse endpoint. O login da API, porém,
somente estabelece uma sessão quando a conta autenticada é staff.

### Administrativos

Todos os caminhos abaixo exigem uma sessão autenticada com
`is_staff=True`, inclusive métodos `GET`. Escritas com sessão exigem token
CSRF. Os detalhes usam ID numérico, não slug.

| Método | Caminho | Operação |
|---|---|---|
| GET | `/api/v1/admin/dashboard/` | Contagens do catálogo |
| GET, POST | `/api/v1/admin/categories/` | Listar, criar categorias |
| GET, PATCH, DELETE | `/api/v1/admin/categories/<id>/` | Consultar, editar parcialmente, excluir categoria |
| GET, POST | `/api/v1/admin/products/` | Listar, criar produtos |
| GET, PATCH, DELETE | `/api/v1/admin/products/<id>/` | Consultar, editar parcialmente, excluir produto |
| GET, PATCH | `/api/v1/admin/store/` | Consultar ou configurar a loja |
| GET, POST | `/api/v1/admin/promotions/` | Listar, criar promoções |
| GET, PATCH, DELETE | `/api/v1/admin/promotions/<id>/` | Consultar, editar parcialmente, excluir promoção |

As listagens administrativas de categorias, produtos e promoções são
paginadas. A lista pública de **produtos** é paginada; listas públicas de
categorias e promoções são arrays JSON, sem envelope de paginação.

Uma categoria com produtos vinculados não pode ser excluída: o backend
responde `409` com um objeto contendo `detail`, sem excluir a categoria nem
seus produtos. Produtos usam `category` obrigatória. Excluir um produto
vinculado a uma promoção aplica a relação `SET_NULL` do modelo à promoção;
o arquivo de imagem associado não é automaticamente removido.

## 3. Parâmetros de produtos

`GET /api/v1/public/products/` admite:

| Parâmetro | Uso |
|---|---|
| `search` | Busca sem diferenciar maiúsculas e minúsculas em `name` ou `short_description` |
| `category` | Slug da categoria |
| `featured` | Se presente, deve ser `true` — `false` não é um filtro suportado nesta implementação |
| `ordering` | Apenas `name`, `-name`, `price` ou `-price` |
| `page` | Número da página |
| `page_size` | Tamanho solicitado da página |

Sem `ordering`, a consulta usa `display_order`, `name`, `id`. Nas quatro
ordenações explícitas, `id` é desempate para estabilidade.

A paginação de produtos e das listagens administrativas usa tamanho padrão
12, máximo 50 e o seguinte envelope:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": []
}
```

`next` e `previous` podem ser URLs de página ou `null`. A URL depende da
requisição e conserva seus parâmetros. Página inexistente pode retornar
`404`. `page_size` superior a 50 é limitado pelo paginador, em vez de
aumentar indefinidamente a resposta. `ordering` fora da lista ou
`featured` presente com valor diferente de `true` produz erro de
validação com a chave do respectivo parâmetro.

O queryset público exclui:

- produtos com `status` diferente de `published`;
- produtos vinculados a categoria com `is_active=False`;
- detalhes por slug que não atendam às mesmas condições.

Uma promoção pública precisa ter `is_active=True`, início ausente ou não
posterior ao instante atual, fim ausente ou não anterior ao instante atual
e, se houver produto vinculado, esse produto precisa ser publicado e
pertencer a categoria ativa. Uma promoção sem produto vinculado pode ser
exibida se as demais regras forem atendidas.

## 4. Campos JSON

Os nomes abaixo são os nomes exatos dos serializers entregues. Campos
somente de leitura não devem ser enviados para tentar editar IDs ou datas.

### Categorias

Resposta pública de categoria:

| Campo | Tipo | Observação |
|---|---|---|
| `id` | inteiro | ID |
| `name` | string | Nome |
| `slug` | string | Slug único |
| `short_description` | string | Pode ser vazia |
| `display_order` | inteiro | Ordem |

Resposta administrativa acrescenta `is_active` (booleano),
`created_at` e `updated_at` (datas e horas serializadas). Na escrita
administrativa, `id`, `created_at` e `updated_at` são somente leitura.
Criar/alterar categoria usa os demais nomes de campo do serializer
`AdminCategorySerializer`.

### Produtos

Resposta pública de **listagem**:

| Campo | Tipo | Observação |
|---|---|---|
| `id` | inteiro | ID |
| `category` | objeto | Categoria pública aninhada; não um ID nesta resposta |
| `name` | string | Nome |
| `slug` | string | Slug único |
| `short_description` | string | Resumo |
| `price` | string decimal | Exemplo: `"89.90"`; não converter com `float` |
| `main_image` | URL ou `null` | Imagem principal |
| `alt_text` | string | Texto alternativo, possivelmente vazio |
| `is_featured` | booleano | Destaque |

O detalhe público inclui **todos** esses campos e acrescenta
`description` (string). Não inclua `description` na representação resumida
da listagem por suposição.

Resposta administrativa de produto contém:
`id`, `category`, `name`, `slug`, `short_description`, `description`,
`price`, `main_image`, `alt_text`, `is_featured`, `status`,
`display_order`, `created_at`, `updated_at`.

Na resposta e na escrita administrativa, `category` é **ID inteiro**;
na resposta pública, é um **objeto aninhado**. `status` admite
`"published"` e `"hidden"`. `price` é decimal não negativo, com duas
casas na representação prevista; não use ponto flutuante para cálculos
financeiros. `id` e datas são somente leitura. `main_image` aceita
arquivo na escrita e fornece URL ou `null` na leitura.

### Loja

Resposta pública:

`name`, `slogan`, `description`, `whatsapp_number`, `demo_address`,
`opening_hours`, `banner_image`, `banner_text`,
`primary_button_text`.

Resposta administrativa acrescenta `id`, `created_at` e `updated_at`.
Na escrita, esses três campos são somente leitura. `whatsapp_number`
é uma string internacional de 10 a 15 dígitos, sem `+`, espaço ou
pontuação, iniciando com dígito de 1 a 9.

Antes da criação do registro único, `GET /api/v1/public/store/` e
`GET /api/v1/admin/store/` respondem `404`. Se não houver loja,
`PATCH /api/v1/admin/store/` com todos os campos obrigatórios válidos
pode **criar** a configuração de ID `1` e retorna `201`; se ela já
existir, `PATCH` atualiza somente os campos informados e retorna `200`.
O comando `seed_demo` também cria a loja caso ainda não exista. O
primeiro PATCH não é uma atualização parcial de um registro inexistente.

### Promoções

Resposta pública:

`id`, `title`, `description`, `image`, `product`, `starts_at`,
`ends_at`, `display_order`.

Na resposta pública, `product` é um **produto público resumido
aninhado** ou `null`. Promoções públicas são previamente filtradas pela
view; o serializer, por si só, não decide a visibilidade.

Resposta administrativa acrescenta `is_active`, `created_at` e
`updated_at`. Na entrada administrativa, `product` é um **ID de produto
existente** ou `null`, e `image` é um arquivo opcional. Datas de
`starts_at` e `ends_at` podem ser omitidas ou informadas como data e
hora serializável; se ambas existirem, o início não pode ser posterior
ao fim. A validação de `PATCH` compara o valor recebido também com
a data já salva do outro campo. `id` e datas de criação/atualização são
somente leitura.

### Dashboard

`GET /api/v1/admin/dashboard/` retorna um objeto com:

```json
{
  "products_count": 9,
  "categories_count": 3,
  "active_promotions_count": 1
}
```

Os números acima são **apenas um exemplo compatível com a primeira
execução pretendida do seed**; o endpoint conta os registros atuais do
banco. `active_promotions_count` conta promoções com `is_active=True`,
não necessariamente promoções vigentes e visíveis no momento. A API
não fornece vendas, faturamento, pedidos ou acessos fictícios.

## 5. Sessão, cookies e CSRF

Autenticação administrativa usa a sessão Django e proteção CSRF. O
backend valida permissões: esconder botões no frontend **não** libera
acesso para anônimos ou usuários sem `is_staff`.

Sequência do frontend:

1. Faça `GET /api/v1/auth/csrf/` e aceite os cookies devolvidos.
2. Guarde o `csrfToken` da resposta **em memória**.
3. Faça `POST /api/v1/auth/login/` com JSON `{ "username": "...",
   "password": "..." }`, cookies incluídos e cabeçalho
   `X-CSRFToken` com o token do passo 1.
4. Em caso de login `200`, use o **novo** `csrfToken` retornado com
   `user`: o segredo CSRF é renovado no login.
5. Nas chamadas administrativas seguintes, inclua cookies; nas escritas
   (`POST`, `PATCH`, `DELETE`), envie `X-CSRFToken`.
6. Faça `GET /api/v1/auth/me/` para consultar a sessão e
   `POST /api/v1/auth/logout/` com CSRF para encerrá-la.
7. Depois do logout, descarte da memória o token e os dados de sessão
   do frontend.

Exemplo mínimo no navegador, supondo frontend e API na mesma origem:

```javascript
const csrfResponse = await fetch("/api/v1/auth/csrf/", {
  credentials: "include",
});
const { csrfToken } = await csrfResponse.json();

const loginResponse = await fetch("/api/v1/auth/login/", {
  method: "POST",
  credentials: "include",
  headers: {
    "Content-Type": "application/json",
    "X-CSRFToken": csrfToken,
  },
  body: JSON.stringify({
    username: userInput,
    password: passwordInput,
  }),
});

if (!loginResponse.ok) {
  throw new Error(`Login recusado: ${loginResponse.status}`);
}

const loginData = await loginResponse.json();
const authenticatedCsrfToken = loginData.csrfToken;
```

`userInput` e `passwordInput` representam entrada privada do usuário;
não há credenciais administrativas públicas neste projeto. **Não**
salve senha, cookie de sessão ou token em `localStorage`. O cookie de
sessão é `HttpOnly`; o navegador o envia conforme origem e política de
cookies. O token CSRF pode ser usado diretamente da resposta JSON.

Em desenvolvimento, se o frontend estiver em
`http://localhost:5173` e a API em `http://localhost:8000`, configure
a origem **exata** do frontend em `CORS_ALLOWED_ORIGINS` e
`CSRF_TRUSTED_ORIGINS`, mantenha credenciais habilitadas e use
`credentials: "include"` nas chamadas. Use `localhost` em ambos os
endereços de exemplo; trocar um deles por `127.0.0.1` pode mudar o
comportamento de cookies. CORS **não** substitui CSRF.

Em publicação, frontend e API devem estar na **mesma origem** HTTPS.
Cookies `Secure` dependem de HTTPS. Configuração de proxy, cabeçalhos,
mídia e cookies precisa ser verificada no ambiente implantado; este
contrato não certifica uma implantação real.

## 6. Upload e URLs de mídia

Para escrever **sem arquivo**, envie JSON. Para criar ou atualizar
**com arquivo**, envie `multipart/form-data` com campos **planos**:

| Recurso | Campo do arquivo |
|---|---|
| Produto | `main_image` |
| Loja | `banner_image` |
| Promoção | `image` |

Use os outros nomes de campos exatamente como os serializers
administrativos definem. Para produto, `category` é o ID da categoria,
enviado como campo simples do formulário; para promoção, `product` é o
ID, quando informado. **Não** envie JSON aninhado dentro de um campo
multipart para representar o produto inteiro. O navegador define o
`Content-Type` multipart com seu boundary; ao usar `FormData`, não
construa esse cabeçalho manualmente.

O backend aceita JPEG (`.jpg` ou `.jpeg`), PNG (`.png`) e WebP
(`.webp`), com limite `MAX_IMAGE_UPLOAD_MB`. O validador compara
extensão, formato detectado e conteúdo decodificável. O nome armazenado
é gerado pelo servidor com UUID em `products/`, `store/` ou
`promotions/`.

Nos serializers das views com `request` no contexto, imagem existente
é retornada como **URL absoluta** construída a partir da requisição;
imagem ausente é `null`. Em desenvolvimento local a URL pode apontar
para `/media/` servido pelo Django com `DEBUG=true`. Em produção,
o armazenamento e a entrega segura de mídia enviada pelos usuários
devem ser configurados à parte. URL no JSON **não prova** que o
arquivo exista ou possa ser obtido pelo navegador.

Para substituir uma imagem, envie novo arquivo sob o mesmo nome de
campo no formulário. Para limpeza de imagem, o serializer
administrativo admite `null` em JSON; como esse fluxo não recebeu
nesta documentação uma prova específica de comportamento em todas
as views e storages, confirme o efeito pretendido nos testes antes
de expor um botão de exclusão de imagem no painel. A substituição
ou exclusão de um registro não implica remoção automática do arquivo
antigo do armazenamento.

## 7. Exemplos de requisição e resposta

As respostas a seguir exemplificam os **formatos definidos pelo
código**. IDs, nomes de produtos e endereços de mídia são ilustrativos;
não são registros cuja criação ou execução tenha sido confirmada.
Campos de data variam conforme o instante real. Onde uma resposta
completa não é reproduzida, ela segue os campos da seção 4.

### 7.1 Obter CSRF

```http
GET /api/v1/auth/csrf/
```

Resposta pretendida, HTTP `200`:

```json
{
  "csrfToken": "TOKEN_CSRF_GERADO_PARA_ESTA_SESSAO"
}
```

O navegador também deve conservar o cookie CSRF da resposta.

### 7.2 Login administrativo

```http
POST /api/v1/auth/login/
Content-Type: application/json
X-CSRFToken: TOKEN_CSRF_OBTIDO_ANTES_DO_LOGIN
Cookie: csrftoken=COOKIE_RECEBIDO

{
  "username": "USUARIO_STAFF_CRIADO_MANUALMENTE",
  "password": "SENHA_PRIVADA_NAO_PUBLICADA"
}
```

Resposta pretendida, HTTP `200`:

```json
{
  "user": {
    "id": 1,
    "username": "USUARIO_STAFF_CRIADO_MANUALMENTE",
    "is_staff": true
  },
  "csrfToken": "NOVO_TOKEN_CSRF_APOS_LOGIN"
}
```

A sessão é mantida em cookie `HttpOnly` gerenciado pelo navegador;
não represente `sessionid` como campo JSON de login. O login sem
token CSRF válido é recusado. Login com credenciais inválidas ou de
conta sem `is_staff` retorna `403` com `detail`; se `username` ou
`password` não forem strings, a view retorna `400` com `detail`.

### 7.3 Listagem pública paginada

```http
GET /api/v1/public/products/?category=decoracao&featured=true&page=1&page_size=12
```

Resposta ilustrativa, HTTP `200`:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 7,
      "category": {
        "id": 2,
        "name": "Decoração",
        "slug": "decoracao",
        "short_description": "Peças demonstrativas.",
        "display_order": 1
      },
      "name": "Vaso Aurora",
      "slug": "vaso-aurora",
      "short_description": "Vaso decorativo demonstrativo.",
      "price": "89.90",
      "main_image": null,
      "alt_text": "",
      "is_featured": true
    }
  ]
}
```

`description` não aparece nesta listagem; o detalhe do produto a
inclui. O `count` e os itens dependerão do banco e dos filtros reais.

### 7.4 Criar produto com imagem

Considere que uma categoria de ID `2` já existe e que o usuário staff
está autenticado. Em `FormData`, `main_image` é um objeto `File` PNG
válido, e os demais valores são campos simples:

```javascript
const form = new FormData();
form.append("category", "2");
form.append("name", "Vaso Aurora");
form.append("slug", "vaso-aurora");
form.append("short_description", "Vaso demonstrativo.");
form.append("description", "Produto fictício para o catálogo.");
form.append("price", "89.90");
form.append("status", "published");
form.append("alt_text", "Vaso decorativo demonstrativo");
form.append("main_image", selectedPngFile);

const response = await fetch("/api/v1/admin/products/", {
  method: "POST",
  credentials: "include",
  headers: {
    "X-CSRFToken": authenticatedCsrfToken,
  },
  body: form,
});
```

Não defina manualmente `Content-Type` nesse `fetch`. O `File` precisa
ser JPEG, PNG ou WebP válido e respeitar o limite configurado.

Resposta ilustrativa de criação válida, HTTP `201`:

```json
{
  "id": 7,
  "category": 2,
  "name": "Vaso Aurora",
  "slug": "vaso-aurora",
  "short_description": "Vaso demonstrativo.",
  "description": "Produto fictício para o catálogo.",
  "price": "89.90",
  "main_image": "http://localhost:8000/media/products/NOME_GERADO.png",
  "alt_text": "Vaso decorativo demonstrativo",
  "is_featured": false,
  "status": "published",
  "display_order": 0,
  "created_at": "DATA_HORA_GERADA",
  "updated_at": "DATA_HORA_GERADA"
}
```

A URL e as datas acima indicam **posição e tipo dos campos**, não
valores literais garantidos. O nome do arquivo é gerado pelo servidor.
Com produto publicado em categoria ativa, uma consulta pública
subsequente deve torná-lo visível.

### 7.5 Erros e permissões

Preço negativo em criação de produto — resposta pretendida HTTP `400`;
o campo `price` contém mensagens de validação:

```json
{
  "price": [
    "O preço não pode ser negativo."
  ]
}
```

O texto exato pode refletir a ordem entre validação do campo de
modelo e `validate_price`; o ponto fixo do contrato para o frontend
é **HTTP 400 e a chave `price` com uma lista de mensagens**. Não
codifique o painel dependendo de uma frase única para esse caso.

Erro de período em promoção — HTTP `400`, com chave `ends_at`
e mensagem referente ao fim anterior ao início, inclusive em `PATCH`
parcial.

Categoria vinculada a produtos — `DELETE` devolve HTTP `409`:

```json
{
  "detail": "Não é possível excluir uma categoria que possui produtos vinculados."
}
```

Sem sessão em rota administrativa protegida por autenticação de
sessão DRF — resposta pretendida HTTP `403`. Conta autenticada
sem `is_staff=True` — HTTP `403`. Para essas recusas do DRF,
a resposta usa um objeto com `detail`; a mensagem exata pode
diferir entre ausência de autenticação e falta de permissão:

```json
{
  "detail": "Acesso restrito a administradores da loja."
}
```

O objeto acima ilustra a **forma** da falta de permissão; não
presuma que essa mesma frase seja a resposta do anônimo ou de
falha CSRF. **Não** apresente `401` como status garantido para
anônimos nesta configuração, cuja única autenticação DRF é
`SessionAuthentication`.

Depois de `POST /api/v1/auth/logout/` válido, a resposta é
HTTP `204` **sem corpo JSON**. O frontend deve conferir o status,
não chamar `response.json()` para essa resposta.

## 8. Regras para o frontend

- Consuma apenas a API para o painel personalizado; não dependa de
  páginas do Django Admin.
- Considere campos demonstrativos do seed como conteúdo fictício.
  Não ative um link de WhatsApp para o número fictício do seed.
- Respeite `null` para imagens e produto opcional de promoção.
- Use texto simples ao exibir campos editáveis; não insira seu
  conteúdo diretamente como HTML não sanitizado.
- Não exponha controles administrativos a visitantes, mas mantenha
  a autorização efetiva no backend.
- Não conclua que a API ou a implantação foram validadas porque
  este contrato foi entregue. Confira o projeto com instalação,
  migração, testes e requisições reais antes de publicar.