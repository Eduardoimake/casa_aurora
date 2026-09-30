# Casa Aurora — Frontend

Frontend separado para o catálogo demonstrativo “Casa Aurora — Presentes e Decoração”.

A interface pública consulta a API Django REST Framework. O painel personalizado utiliza os endpoints `/api/v1/admin/` e exige conta autenticada com `is_staff=True`. O Django Admin do backend é apenas auxiliar.

O projeto não oferece carrinho, checkout, pagamento, pedidos, vendas fictícias ou cadastro público de administradores.

## 1. Pré-requisitos

- Node.js e npm compatíveis com a versão do Vite instalada.
- Backend Django da Casa Aurora disponível separadamente.
- Migrações do backend aplicadas.
- Conta staff criada manualmente no backend para usar o painel.
- Imagens e contatos autorizados antes de publicação.

O frontend não instala o backend nem cria credenciais.

## 2. Estrutura

```text
casa_aurora_frontend/
├── .env.example
├── .gitignore
├── MANUAL_CHECKLIST.md
├── README.md
├── index.html
├── package.json
├── public/
│   └── favicon.svg
├── scripts/
│   └── check-syntax.mjs
└── src/
    ├── main.js
    ├── router.js
    ├── api/
    │   ├── client.js
    │   ├── publicApi.js
    │   ├── authApi.js
    │   └── adminApi.js
    ├── state/
    │   ├── appStore.js
    │   └── sessionStore.js
    ├── utils/
    │   ├── a11y.js
    │   ├── dom.js
    │   ├── errors.js
    │   ├── formatters.js
    │   ├── media.js
    │   └── validation.js
    ├── components/
    │   ├── SiteHeader.js
    │   ├── SiteFooter.js
    │   ├── LoadingState.js
    │   ├── EmptyState.js
    │   ├── ErrorState.js
    │   ├── ProductCard.js
    │   ├── CategoryCard.js
    │   ├── PromotionCard.js
    │   ├── Pagination.js
    │   ├── Toast.js
    │   └── admin/
    │       ├── AdminSidebar.js
    │       ├── AdminTable.js
    │       ├── AdminForm.js
    │       ├── ImageField.js
    │       └── ConfirmDialog.js
    ├── pages/
    │   ├── PublicHomePage.js
    │   ├── ProductsPage.js
    │   ├── ProductDetailPage.js
    │   ├── AdminLoginPage.js
    │   ├── AdminDashboardPage.js
    │   ├── AdminCategoriesPage.js
    │   ├── AdminProductsPage.js
    │   ├── AdminStorePage.js
    │   ├── AdminPromotionsPage.js
    │   └── NotFoundPage.js
    └── styles/
        ├── tokens.css
        ├── base.css
        ├── layout.css
        ├── components.css
        └── pages.css
```

Cada caminho acima tem uma versão canônica: a última versão completa explicitamente declarada como substituta nas ETAPAS 02–08. Os blocos apresentados na conversa não criam automaticamente arquivos no disco.

## 3. Instalação do frontend

Partindo de uma pasta que ainda não contém `casa_aurora_frontend/`:

```bash
mkdir casa_aurora_frontend
cd casa_aurora_frontend
npm create vite@latest . -- --template vanilla
```

Copie para este diretório os conteúdos canônicos entregues nas etapas. Os arquivos padrão do gerador usados pelo projeto são substituídos pelas versões entregues; não execute `npm create vite` novamente.

Depois que `package.json` existir:

```bash
npm install
```

Configure a URL da API:

```bash
cp .env.example .env.local
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env.local
```

O valor de desenvolvimento previsto é `VITE_API_BASE_URL=http://localhost:8000`. A variável contém somente a origem; a camada de API acrescenta `/api/v1/`.

Para implantação em mesma origem HTTPS, avalie `VITE_API_BASE_URL=` e sirva a API também em `/api/v1/` nessa origem. Configure o servidor web para entregar `index.html` nas rotas do frontend e encaminhar `/api/v1/` ao backend. Configure entrega de mídia separadamente.

## 4. Execução local

Terminal 1, dentro de `casa_aurora_backend/`, depois da configuração e das migrações do backend:

```bash
python manage.py runserver localhost:8000
```

Terminal 2, dentro de `casa_aurora_frontend/`:

```bash
npm run dev
```

O frontend previsto é `http://localhost:5173/`. Rotas relevantes:

- `/`
- `/catalogo`
- `/produto/<slug>`
- `/painel/login`
- `/painel`
- `/painel/categorias`
- `/painel/produtos`
- `/painel/loja`
- `/painel/promocoes`

A apresentação “Sobre” fica na página inicial. A rota `/sobre` permanece informativa, não representa um endpoint separado do backend.

## 5. CORS, cookies e CSRF

Quando frontend e API usarem portas diferentes no desenvolvimento:

- Backend: permitir `http://localhost:5173` em `CORS_ALLOWED_ORIGINS`.
- Backend: confiar em `http://localhost:5173` em `CSRF_TRUSTED_ORIGINS`.
- Cliente: utilizar `credentials: "include"`.
- Usar `localhost` de forma consistente: não misturar com `127.0.0.1` sem revisar cookies, origens e configurações.
- Manter CSRF ativo.

Antes do login, a interface solicita `/api/v1/auth/csrf/`. Depois do login, substitui o token em memória pelo retornado em `/api/v1/auth/login/`. As escritas enviam `X-CSRFToken`. O cookie de sessão é administrado pelo navegador; senha e token não são salvos em `localStorage` ou `sessionStorage`.

A publicação prevista usa frontend e API sob a mesma origem HTTPS. Não use o servidor de desenvolvimento Vite ou `runserver` como solução de produção.

## 6. Comandos de verificação

Depois de copiar `package.json` e `scripts/check-syntax.mjs`:

```bash
npm run check:syntax
npm run build
```

Somente se o build passar:

```bash
npm run preview
```

Abra `http://localhost:4173/` para conferir o build.

O script `check:syntax` verifica sintaxe, não funcionalidades. O build verifica empacotamento, não autenticação, CSRF ou comportamento do backend. Para esses cenários, siga `MANUAL_CHECKLIST.md`.

## 7. API e conteúdo demonstrativo

O frontend usa exclusivamente os endpoints documentados em `casa_aurora_backend/API_CONTRACT.md`.

- Produtos usam preço como string decimal.
- Produto público usa categoria aninhada; produto administrativo usa ID de categoria.
- Promoção pública pode conter produto resumido ou `null`; promoção administrativa usa ID ou `null`.
- Produtos e listagens administrativas são paginados.
- Categorias e promoções públicas são arrays.
- Upload com arquivo utiliza `FormData`; o navegador define o boundary multipart.
- Logout válido retorna `204`, sem corpo JSON.

O seed do backend fornece dados demonstrativos. Seu número de WhatsApp e endereço não são contatos verificados. Não ative link de WhatsApp para o número demonstrativo nem publique imagens e contatos sem autorização.

## 8. Limitações e status

A existência destes arquivos em uma conversa não prova instalação ou funcionamento local.

Antes de considerar o frontend concluído, ainda é preciso:

1. Copiar todos os arquivos para os caminhos da árvore.
2. Executar verificação sintática.
3. Executar build.
4. Testar a interface no navegador.
5. Iniciar o backend real.
6. Conferir CORS, cookies, CSRF e sessão staff.
7. Exercitar CRUD, uploads e paginação.
8. Corrigir falhas encontradas com substituição integral dos arquivos afetados.
9. Testar acessibilidade e responsividade.
10. Confirmar autorização de publicação dos dados demonstrativos.

A confirmação do botão “Cancelar” existe. Navegação global com formulário alterado e a combinação de troca de imagem com limpeza de datas de promoção precisam ser verificadas e eventualmente corrigidas antes de classificar a experiência como concluída.

Registre cada item como `EXECUTADO E PASSOU`, `EXECUTADO E FALHOU`, `NÃO EXECUTADO` ou `NÃO VERIFICADO POR DEPENDÊNCIA DO BACKEND`, anexando a saída ou evidência adequada.