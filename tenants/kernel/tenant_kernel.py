# Em registry_manager.py e tenant_manager.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tenants.kernel.tenant_kernel import TenantKernel

class RegistryManager:
    def initialize(self, kernel: "TenantKernel"):
        # Se precisar do objeto em tempo de execução dentro do método:
        # from tenants.kernel.tenant_kernel import TenantKernel
        pass