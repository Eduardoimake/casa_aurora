"""Views públicas, autenticação e gestão administrativa da Casa Aurora."""

from django.contrib.auth import (
    authenticate,
    login as django_login,
    logout as django_logout,
)
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product, Promotion, StoreSettings
from .pagination import CatalogPagination
from .permissions import IsStaffUser
from .serializers import (
    AdminCategorySerializer,
    AdminProductSerializer,
    AdminPromotionSerializer,
    AdminStoreSerializer,
    PublicCategorySerializer,
    PublicProductDetailSerializer,
    PublicProductListSerializer,
    PublicPromotionSerializer,
    PublicStoreSerializer,
)


def eligible_promotions():
    """Seleciona promoções ativas, vigentes e publicamente apresentáveis."""
    now = timezone.now()

    return (
        Promotion.objects.filter(is_active=True)
        .filter(Q(starts_at__isnull=True) | Q(starts_at__lte=now))
        .filter(Q(ends_at__isnull=True) | Q(ends_at__gte=now))
        .filter(
            Q(product__isnull=True)
            | Q(
                product__status=Product.Status.PUBLISHED,
                product__category__is_active=True,
            )
        )
    )


class PublicStoreView(APIView):
    """Retorna os dados públicos da loja e do banner."""

    permission_classes = [AllowAny]

    def get(self, request):
        store = StoreSettings.objects.filter(pk=1).first()

        if store is None:
            return Response(
                {
                    "detail": (
                        "As informações da loja ainda não foram configuradas."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PublicStoreSerializer(
            store,
            context={"request": request},
        )
        return Response(serializer.data)


class PublicCategoryListView(generics.ListAPIView):
    """Lista categorias ativas na ordem definida pelo modelo."""

    permission_classes = [AllowAny]
    serializer_class = PublicCategorySerializer
    pagination_class = None

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class PublicProductListView(generics.ListAPIView):
    """Lista produtos visíveis com busca, filtros e ordenação limitada."""

    permission_classes = [AllowAny]
    serializer_class = PublicProductListSerializer
    pagination_class = CatalogPagination

    ORDERING_FIELDS = {
        "name": ("name", "id"),
        "-name": ("-name", "id"),
        "price": ("price", "id"),
        "-price": ("-price", "id"),
    }

    def get_queryset(self):
        params = self.request.query_params

        queryset = Product.objects.filter(
            status=Product.Status.PUBLISHED,
            category__is_active=True,
        ).select_related("category")

        search = params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(short_description__icontains=search)
            )

        category_slug = params.get("category", "").strip()
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        featured = params.get("featured")
        if featured is not None:
            if featured.lower() != "true":
                raise ValidationError(
                    {"featured": "Use featured=true ou omita o parâmetro."}
                )
            queryset = queryset.filter(is_featured=True)

        ordering = params.get("ordering")
        if ordering is None:
            return queryset.order_by("display_order", "name", "id")

        if ordering not in self.ORDERING_FIELDS:
            raise ValidationError(
                {"ordering": "Use name, -name, price ou -price."}
            )

        return queryset.order_by(*self.ORDERING_FIELDS[ordering])


class PublicProductDetailView(generics.RetrieveAPIView):
    """Exibe apenas produto publicado em categoria ativa."""

    permission_classes = [AllowAny]
    serializer_class = PublicProductDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Product.objects.filter(
            status=Product.Status.PUBLISHED,
            category__is_active=True,
        ).select_related("category")


class PublicPromotionListView(generics.ListAPIView):
    """Lista promoções elegíveis para exibição."""

    permission_classes = [AllowAny]
    serializer_class = PublicPromotionSerializer
    pagination_class = None

    def get_queryset(self):
        return eligible_promotions().select_related(
            "product",
            "product__category",
        )


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfTokenView(APIView):
    """Inicializa o cookie CSRF e entrega o token ao frontend."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    """Autentica usuário staff por sessão, exigindo CSRF no POST."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not isinstance(username, str) or not isinstance(password, str):
            return Response(
                {"detail": "Informe username e password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None or not user.is_staff:
            return Response(
                {"detail": "Credenciais inválidas ou acesso não autorizado."},
                status=status.HTTP_403_FORBIDDEN,
            )

        django_login(request, user)

        return Response(
            {
                "user": {
                    "id": user.pk,
                    "username": user.get_username(),
                    "is_staff": user.is_staff,
                },
                "csrfToken": get_token(request),
            },
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """Informa a identidade da sessão administrativa atual."""

    permission_classes = [IsStaffUser]

    def get(self, request):
        user = request.user

        return Response(
            {
                "id": user.pk,
                "username": user.get_username(),
                "is_staff": user.is_staff,
            }
        )


class LogoutView(APIView):
    """Encerra a sessão administrativa, preservando proteção CSRF."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        django_logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminDashboardView(APIView):
    """Fornece contagens reais do catálogo, sem métricas de vendas."""

    permission_classes = [IsStaffUser]

    def get(self, request):
        return Response(
            {
                "products_count": Product.objects.count(),
                "categories_count": Category.objects.count(),
                "active_promotions_count": Promotion.objects.filter(
                    is_active=True
                ).count(),
            }
        )


class AdminCategoryListCreateView(generics.ListCreateAPIView):
    """Lista e cria categorias para a equipe."""

    permission_classes = [IsStaffUser]
    serializer_class = AdminCategorySerializer
    queryset = Category.objects.all()
    pagination_class = CatalogPagination


class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Consulta, altera parcialmente ou remove uma categoria."""

    permission_classes = [IsStaffUser]
    serializer_class = AdminCategorySerializer
    queryset = Category.objects.all()
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "Não é possível excluir uma categoria que possui "
                        "produtos vinculados."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminProductListCreateView(generics.ListCreateAPIView):
    """Lista e cria produtos para a equipe."""

    permission_classes = [IsStaffUser]
    serializer_class = AdminProductSerializer
    queryset = Product.objects.select_related("category").all()
    pagination_class = CatalogPagination


class AdminProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Consulta, altera parcialmente ou remove um produto."""

    permission_classes = [IsStaffUser]
    serializer_class = AdminProductSerializer
    queryset = Product.objects.select_related("category").all()
    http_method_names = ["get", "patch", "delete", "head", "options"]


class AdminStoreView(APIView):
    """Consulta ou altera a configuração única da loja."""

    permission_classes = [IsStaffUser]

    def get(self, request):
        store = StoreSettings.objects.filter(pk=1).first()

        if store is None:
            return Response(
                {
                    "detail": (
                        "As informações da loja ainda não foram configuradas."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminStoreSerializer(
            store,
            context={"request": request},
        )
        return Response(serializer.data)

    def patch(self, request):
        store = StoreSettings.objects.filter(pk=1).first()

        if store is None:
            serializer = AdminStoreSerializer(
                data=request.data,
                context={"request": request},
            )
        else:
            serializer = AdminStoreSerializer(
                store,
                data=request.data,
                partial=True,
                context={"request": request},
            )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_status = (
            status.HTTP_201_CREATED
            if store is None
            else status.HTTP_200_OK
        )
        return Response(serializer.data, status=response_status)


class AdminPromotionListCreateView(generics.ListCreateAPIView):
    """Lista e cria promoções para a equipe."""

    permission_classes = [IsStaffUser]
    serializer_class = AdminPromotionSerializer
    queryset = Promotion.objects.select_related("product").all()
    pagination_class = CatalogPagination


class AdminPromotionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Consulta, altera parcialmente ou remove uma promoção."""

    permission_classes = [IsStaffUser]
    serializer_class = AdminPromotionSerializer
    queryset = Promotion.objects.select_related("product").all()
    http_method_names = ["get", "patch", "delete", "head", "options"]