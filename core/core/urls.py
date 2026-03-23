"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import UserViewSet
from organizations.views import MembershipViewSet, OrganizationViewSet
from ledger.views import AccountViewSet, CategoryViewSet, TransactionViewSet
from cashflow.views import CashFlowSummaryViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'memberships', MembershipViewSet, basename='membership')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'cashflow', CashFlowSummaryViewSet, basename='cashflow')


def root_view(request):
    return JsonResponse(
        {
            "name": "cash-flow API",
            "status": "ok",
            "endpoints": {
                "admin": "/admin/",
                "api": "/api/",
                "token_obtain": "/api/auth/token/",
                "token_refresh": "/api/auth/token/refresh/",
            },
        }
    )

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
