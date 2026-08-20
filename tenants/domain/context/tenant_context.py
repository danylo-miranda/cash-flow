from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass(frozen=True)
class TenantContextData:
    tenant_id: str
    company_name: str
    plan_type: str #FREE ou STARTER
    db_alias: str
    db_engine: str 
    features: List[str] = field(default_factory=list) #inicializar listas e dicionários vazios de forma segura em cada instância nova
    permissions: Dict[str, Any] = field(default_factory=dict)
    
_tenant_context: ContextVar[Optional[TenantContextData]] = ContextVar('tenant_context', default=None) #variável de escopo assíncrono/execução. Ela funciona como um "estado global seguro", onde cada requisição HTTP ou tarefa assíncrona enxerga apenas o seu próprio TenantContextData atual, evitando vazamento de dados entre requisições simultâneas

class TenantContext:
    @staticmethod
    def set(data: TenantContextData):
        return _tenant_context.set(data)
    
    @staticmethod
    def get() -> Optional[TenantContextData]:
        return _tenant_context.get()
    
    @staticmethod
    def clear(token=None):
        if token:
            _tenant_context.reset(token)
        else:
            _tenant_context.set(None)