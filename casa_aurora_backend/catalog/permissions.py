"""Permissões de acesso aos endpoints administrativos da Casa Aurora."""

from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    """Permite acesso somente a usuários autenticados da equipe."""

    message = "Acesso restrito a administradores da loja."

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and user.is_staff
        )