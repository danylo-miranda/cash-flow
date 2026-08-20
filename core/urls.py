from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Views da aplicação
from accounts.views import GoogleAuthView, RegisterManualView, UserViewSet
from cashflow.views import CashFlowSummaryViewSet
from core.web_views import app_page, login_page
from ledger.views import AccountViewSet, CategoryViewSet, TransactionViewSet
from organizations.views import MembershipViewSet, OrganizationViewSet

# Configuração do Router REST
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'memberships', MembershipViewSet, basename='membership')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'cashflow', CashFlowSummaryViewSet, basename='cashflow')

urlpatterns = [
    # 🌐 Páginas Web (HTML)
    path('', login_page, name='root'),
    path('login/', login_page, name='login'),
    # Captura /app, /app/ e qualquer sub-rota interna (ex: /app/dashboard, /app/config)
    re_path(r'^app(?:/.*)?$', app_page, name='app'),

    # 🔑 Autenticação JWT e Registro
    path('api/auth/register/', RegisterManualView.as_view(), name='auth_register'),
    path('api/auth/google/', GoogleAuthView.as_view(), name='auth_google'),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 📊 Endpoints REST de Dados
    path('api/', include(router.urls)),

    # 🛠️ Django Admin
    path('admin/', admin.site.urls),
]

# Servir arquivos de mídia e estáticos em desenvolvimento (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )
    if hasattr(settings, 'MEDIA_URL') and hasattr(settings, 'MEDIA_ROOT'):
        urlpatterns += static(
            settings.MEDIA_URL,
            document_root=settings.MEDIA_ROOT,
        )
