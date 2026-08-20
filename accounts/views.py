import os
import uuid
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
from django.shortcuts import render

from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

# Google OAuth
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Modelos do App de Organizações
from organizations.models import Membership, Organization

from .serializers import UserSerializer

User = get_user_model()
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID


def get_jwt_tokens(user):
    """Gera o par de tokens JWT (access e refresh) para o usuário."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def setup_initial_organization(user, org_name=None):
    """Cria uma organização inicial (Tenant) e vincula o usuário como membro ativo."""
    if not org_name:
        base_name = user.first_name or user.email.split('@')[0]
        org_name = f'Empresa de {base_name}'

    # Verifica se já existe um slug igual no banco para evitar duplicação
    base_slug = slugify(org_name)
    if Organization.objects.filter(slug=base_slug).exists():
        # Adiciona um sufixo único (ex: Empresa de Danylo-A1B2)
        org_name = f'{org_name}-{uuid.uuid4().hex[:4].upper()}'

    org = Organization.objects.create(name=org_name)
    Membership.objects.create(user=user, organization=org, is_active=True)
    return org

# =======================================================
# 1. VIEWSET DE USUÁRIOS (Importado no core/urls.py)
# =======================================================
class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Endpoints de leitura de usuários. Operações administrativas ficam no Django Admin.
    Permite listar usuários das mesmas organizações ativas e consultar o perfil atual ('me').
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()

        organization_ids = Membership.objects.filter(
            user=user,
            is_active=True,
        ).values_list("organization_id", flat=True)

        queryset = User.objects.filter(
            is_active=True,
            memberships__organization_id__in=organization_ids,
            memberships__is_active=True,
        ).distinct()

        org_param = self.request.query_params.get("organization") or self.request.query_params.get("organization_id")
        if org_param:
            queryset = queryset.filter(memberships__organization_id=org_param)

        return queryset

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """
        Retorna os dados do usuário autenticado no momento.
        Endpoint consumido pelo frontend para exibir o perfil logado.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# =======================================================
# 2. CADASTRO MANUAL (Email + Senha)
# =======================================================
class RegisterManualView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password')
        name = request.data.get('name', '').strip()

        if not email or not password:
            return Response(
                {'error': 'Email e senha são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Este email já está cadastrado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            setup_initial_organization(user)

        tokens = get_jwt_tokens(user)

        return Response({
            'message': 'Usuário cadastrado com sucesso!',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.first_name,
            },
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)


# =======================================================
# 3. LOGIN / CADASTRO VIA GOOGLE (SSO)
# =======================================================
class GoogleAuthView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        google_jwt_token = request.data.get('id_token')

        if not google_jwt_token:
            return Response(
                {'error': 'O parâmetro id_token é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            id_info = id_token.verify_oauth2_token(
                google_jwt_token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )

            email = id_info['email'].lower()
            first_name = id_info.get('given_name', '')
            last_name = id_info.get('family_name', '')

            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': email,
                        'first_name': first_name,
                        'last_name': last_name,
                    }
                )

                if created:
                    user.set_unusable_password()
                    user.save()
                    setup_initial_organization(user)

            tokens = get_jwt_tokens(user)

            return Response({
                'is_new_user': created,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.first_name,
                },
                'tokens': tokens
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except ValueError:
            return Response(
                {'error': 'Token do Google inválido ou expirado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

# =======================================================
# 4. VIEW DA PÁGINA DE LOGIN (HTML)
# =======================================================
def login_page(request):
    """Renderiza a página de login injetando o Client ID do Google."""
    return render(
        request, 'web/login.html', {'google_client_id': settings.GOOGLE_CLIENT_ID}
    )
