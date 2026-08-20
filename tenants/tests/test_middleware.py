import os
from django.http import HttpResponse
from django.test import TestCase, RequestFactory
from django.db import connections
from tenants.application.provisioning_service import ProvisioningService
from tenants.interfaces.middleware import TenantMiddleware
from tenants.tests.helpers import DynamicTenantTestMixin, cleanup_tenant_connection


class TenantMiddlewareTestCase(DynamicTenantTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.service = ProvisioningService()
        self.tenant_id = "test_mid_company"
        
        result = self.service.execute(
            tenant_id=self.tenant_id,
            company_name="Empresa Middleware Teste",
            plan_type="FREE"
        )
        self.db_path = result["db_config"].get("path") or result["db_config"].get("NAME")

        def dummy_view(request):
            return HttpResponse("Sucesso", status=200)

        self.middleware = TenantMiddleware(dummy_view)

    def tearDown(self):
        for alias in list(connections.databases.keys()):
            if alias != "default":
                cleanup_tenant_connection(alias)

        if self.db_path and os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass
        super().tearDown()

    def test_request_without_tenant_header_passes_through(self):
        request = self.factory.get("/public-endpoint/")
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_request_with_invalid_tenant_returns_403(self):
        request = self.factory.get("/api/data/", HTTP_X_TENANT_ID="inexistente")
        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)

    def test_request_with_valid_tenant_resolves_context_and_returns_200(self):
        request = self.factory.get("/api/data/", HTTP_X_TENANT_ID=self.tenant_id)
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)