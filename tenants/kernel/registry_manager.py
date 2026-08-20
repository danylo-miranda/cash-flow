from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tenants.kernel.tenant_kernel import TenantKernel


class RegistryManager:
    def __init__(self, kernel: "TenantKernel" = None):
        self.kernel = kernel