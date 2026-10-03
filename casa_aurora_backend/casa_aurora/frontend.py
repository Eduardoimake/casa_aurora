"""Entrega o HTML compilado da aplicação frontend nas rotas públicas."""

from django.conf import settings
from django.http import Http404, HttpResponseNotAllowed
from django.views import View


class FrontendAppView(View):
    """Entrega a SPA apenas nas rotas de interface conhecidas."""

    def get(self, request, *args, **kwargs):
        index_path = settings.FRONTEND_DIST / "index.html"

        if not index_path.is_file():
            raise Http404("Frontend compilado não disponível.")

        return self._serve_index(index_path)

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    @staticmethod
    def _serve_index(index_path):
        from django.http import HttpResponse

        response = HttpResponse(
            index_path.read_bytes(),
            content_type="text/html; charset=utf-8",
        )
        response["Cache-Control"] = "no-store"
        return response

    def http_method_not_allowed(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["GET", "HEAD"])