# Casa Aurora — Checklist manual do frontend

Este checklist não substitui testes automatizados nem comprova integração antes da execução real.

## Preparação

- [ ] O backend está rodando em `http://localhost:8000`.
- [ ] O frontend está rodando em `http://localhost:5173`.
- [ ] O backend foi configurado com `CORS_ALLOWED_ORIGINS=http://localhost:5173`.
- [ ] O backend foi configurado com `CSRF_TRUSTED_ORIGINS=http://localhost:5173`.
- [ ] Frontend e backend usam `localhost`, sem misturar automaticamente com `127.0.0.1`.
- [ ] Existe uma conta staff criada manualmente no backend.
- [ ] Nenhuma senha foi adicionada ao frontend.
- [ ] Nenhum token aparece em `localStorage` ou `sessionStorage`.

## Site público

- [ ] `/` abre sem erro fatal quando a API está disponível.
- [ ] Nome e slogan da loja vêm da API.
- [ ] Banner usa a URL retornada pela API ou o placeholder.
- [ ] Categorias vêm de `/api/v1/public/categories/`.
- [ ] Produtos em destaque usam `featured=true`.
- [ ] Promoções vêm da API.
- [ ] Produto sem imagem mostra placeholder acessível.
- [ ] Imagem com URL inválida é substituída por placeholder.
- [ ] Loja inexistente (`404`) não derruba a página inteira.
- [ ] `/catalogo` carrega os produtos públicos.
- [ ] Busca usa `search`.
- [ ] Filtro usa slug em `category`.
- [ ] Destaque usa somente `featured=true`.
- [ ] Ordenação aceita somente `name`, `-name`, `price` e `-price`.
- [ ] Paginação mantém os demais filtros na URL.
- [ ] Lista vazia mostra estado vazio.
- [ ] Falha de API mostra mensagem e nova tentativa.
- [ ] Detalhe público exibe `description`.
- [ ] Produto oculto retorna tela de produto não encontrado.
- [ ] Produto em categoria inativa não aparece publicamente.
- [ ] Nenhum preço é calculado com `float`.
- [ ] Nenhum campo da API é inserido como HTML não sanitizado.
- [ ] O número demonstrativo de WhatsApp não vira link funcional.

## Login e sessão

- [ ] `/painel/login` solicita CSRF antes do login.
- [ ] Login inválido mostra erro compreensível.
- [ ] Usuário comum não entra no painel.
- [ ] Login staff válido retorna para `/painel`.
- [ ] O token CSRF é substituído pelo token retornado no login.
- [ ] O cookie de sessão é enviado automaticamente pelo navegador.
- [ ] A sessão não é copiada para `localStorage`.
- [ ] A sessão não é copiada para `sessionStorage`.
- [ ] Acesso direto a `/painel` sem sessão leva ao login.
- [ ] Sessão expirada durante consulta administrativa leva ao login.
- [ ] Erro de rede não é tratado automaticamente como logout.
- [ ] Logout válido aceita resposta `204`.
- [ ] Depois do logout, `/api/v1/auth/me/` não mantém acesso staff.

## Categorias

- [ ] Lista categorias administrativas paginadas.
- [ ] Cria uma categoria válida.
- [ ] Mostra erros por campo.
- [ ] Edita uma categoria com `PATCH`.
- [ ] Alterna `is_active`.
- [ ] Exige confirmação antes de excluir.
- [ ] Exibe erro compreensível para `409`.
- [ ] Não exclui categoria vinculada a produto.
- [ ] Atualiza a listagem depois de criar, editar ou excluir.

## Produtos

- [ ] Lista produtos publicados e ocultos no painel.
- [ ] Carrega categorias administrativas para o formulário.
- [ ] Cria produto sem imagem em JSON.
- [ ] Cria produto com JPEG, PNG ou WebP em `FormData`.
- [ ] Não define manualmente `Content-Type` em multipart.
- [ ] Mostra pré-visualização local da imagem.
- [ ] Distingue pré-visualização de imagem persistida.
- [ ] Envia `category` como ID.
- [ ] Preserva preço como string decimal.
- [ ] Publica produto.
- [ ] Produto publicado aparece no catálogo público.
- [ ] Oculta produto.
- [ ] Produto oculto deixa de aparecer publicamente.
- [ ] Edita preço e texto.
- [ ] Exige confirmação antes de excluir.
- [ ] Atualiza a lista depois das operações.

## Loja

- [ ] Exibe `404` como configuração ausente, sem erro fatal.
- [ ] Permite preencher nome e WhatsApp na primeira configuração.
- [ ] O primeiro `PATCH` pode retornar `201`.
- [ ] Atualiza loja existente com `PATCH`.
- [ ] Faz upload do banner com `banner_image`.
- [ ] Mostra pré-visualização local.
- [ ] Não oferece remoção definitiva não comprovada.
- [ ] Não cria link público para número demonstrativo.
- [ ] Atualiza a página inicial depois de salvar.

## Promoções

- [ ] Lista promoções paginadas.
- [ ] Cria promoção sem produto.
- [ ] Cria promoção vinculada por ID.
- [ ] Permite datas vazias.
- [ ] Valida fim anterior ao início.
- [ ] Exibe erro retornado pelo backend em `ends_at`.
- [ ] Cria promoção com imagem `image`.
- [ ] Edita promoção parcialmente.
- [ ] Alterna `is_active`.
- [ ] Exige confirmação antes de excluir.
- [ ] Atualiza a listagem após as operações.

## Responsividade

- [ ] Testar largura aproximada de 320 px.
- [ ] Testar largura de celular.
- [ ] Testar largura de tablet.
- [ ] Testar largura de desktop.
- [ ] Menu móvel abre e fecha.
- [ ] `aria-expanded` muda corretamente no menu.
- [ ] Tabelas administrativas continuam utilizáveis em telas estreitas.
- [ ] Botões não ficam sobrepostos.
- [ ] Texto não sai horizontalmente da tela.

## Teclado e acessibilidade

- [ ] Skip link aparece ao receber foco.
- [ ] Todos os links podem receber foco.
- [ ] Todos os botões podem receber foco.
- [ ] Foco visível permanece em controles.
- [ ] Labels estão associadas aos campos.
- [ ] Erros têm `role="alert"` ou `aria-live`.
- [ ] Carregamentos usam `role="status"`.
- [ ] Imagens têm texto alternativo.
- [ ] Placeholder de imagem comunica a ausência.
- [ ] Testar com `prefers-reduced-motion`.
- [ ] Navegar pelas telas sem usar mouse.