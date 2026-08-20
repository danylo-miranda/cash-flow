import os
from django.test import TestCase
from django.db import connections
from tenants.application.provisioning_service import ProvisioningService
from tenants.models import TenantModel
from tenants.tests.helpers import DynamicTenantTestMixin, cleanup_tenant_connection


class ProvisioningServiceTestCase(DynamicTenantTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.service = ProvisioningService()
        self.tenant_id = "test_prov_company"
        self.company_name = "Empresa Teste Provisionamento"
        self.db_path = None

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

    def test_provisioning_creates_master_record_and_db_file(self):
        result = self.service.execute(
            tenant_id=self.tenant_id,
            company_name=self.company_name,
            plan_type="FREE"
        )
        self.db_path = result["db_config"].get("path") or result["db_config"].get("NAME")

        # 1. Valida gravação no Banco Mestre
        master_tenant = TenantModel.objects.using("default").get(id=self.tenant_id)
        self.assertEqual(master_tenant.name, self.company_name)
        self.assertEqual(master_tenant.plan, "FREE")
        self.assertTrue(master_tenant.is_active)

        # 2. Valida existência física do arquivo SQLite
        self.assertTrue(os.path.exists(self.db_path))