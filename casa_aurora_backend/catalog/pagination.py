"""Paginação compartilhada pelas listagens da API Casa Aurora."""

from rest_framework.pagination import PageNumberPagination


class CatalogPagination(PageNumberPagination):
    """Paginação por número de página, com tamanho controlado pelo cliente."""

    page_size = 12
    page_query_param = "page"
    page_size_query_param = "page_size"
    max_page_size = 50
    invalid_page_message = "Página inválida."