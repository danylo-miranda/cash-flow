import os
from django.apps import apps
from django.test import TestCase
from django.db import connections
from tenants.application.provisioning_service import ProvisioningService
from tenants.domain.context.tenant_context import TenantContext, TenantContextData
from tenants.infrastructure.database.connection import DynamicConnectionManager
from tenants.tests.helpers import DynamicTenantTestMixin, cleanup_tenant_connection


class CrossTenantDataIsolationTestCase(DynamicTenantTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.service = ProvisioningService()
        self.t1 = self.service.execute("tenant_alpha", "Empresa Alpha", "FREE")
        self.t2 = self.service.execute("tenant_beta", "Empresa Beta", "FREE")

    def tearDown(self):
        for tenant_res in [self.t1, self.t2]:
            path = tenant_res["db_config"].get("path") or tenant_res["db_config"].get("NAME")
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

        for alias in list(connections.databases.keys()):
            if alias != "default":
                cleanup_tenant_connection(alias)

        super().tearDown()

    def test_cross_tenant_data_isolation(self):
        OrgModel = apps.get_model("organizations", "Organization")

        # 1. Inserção no Tenant Alpha
        alias_a = DynamicConnectionManager.register_tenant_db("tenant_alpha", self.t1["db_config"])
        token_a = TenantContext.set(TenantContextData("tenant_alpha", "Empresa Alpha", "FREE", alias_a, "sqlite"))
        OrgModel.objects.using(alias_a).create(name="Organização Exclusiva Alpha")
        TenantContext.clear(token_a)

        # 2. Inserção no Tenant Beta
        alias_b = DynamicConnectionManager.register_tenant_db("tenant_beta", self.t2["db_config"])
        token_b = TenantContext.set(TenantContextData("tenant_beta", "Empresa Beta", "FREE", alias_b, "sqlite"))
        OrgModel.objects.using(alias_b).create(name="Organização Exclusiva Beta")
        TenantContext.clear(token_b)

        # 3. Validação de Contagem em cada banco tenant
        self.assertEqual(OrgModel.objects.using(alias_a).count(), 1)
        self.assertEqual(OrgModel.objects.using(alias_b).count(), 1)

        # 4. Validação de Isolamento (Tenant Beta não enxerga dados do Tenant Alpha)
        token_b = TenantContext.set(TenantContextData("tenant_beta", "Empresa Beta", "FREE", alias_b, "sqlite"))
        has_alpha_data_in_beta = OrgModel.objects.using(alias_b).filter(name="Organização Exclusiva Alpha").exists()
        TenantContext.clear(token_b)
        self.assertFalse(has_alpha_data_in_beta)

        # 5. Validação de Isolamento (Tenant Alpha não enxerga dados do Tenant Beta)
        token_a = TenantContext.set(TenantContextData("tenant_alpha", "Empresa Alpha", "FREE", alias_a, "sqlite"))
        has_beta_data_in_alpha = OrgModel.objects.using(alias_a).filter(name="Organização Exclusiva Beta").exists()
        TenantContext.clear(token_a)
        self.assertFalse(has_beta_data_in_alpha)