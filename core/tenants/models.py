from django.db import models

class TenantModel(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=20)
    plan = models.CharField(max_length=20, default="FREE")
    db_engine = models.CharField(max_length=20, default="sqlite")
    db_config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "master_tenants"
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        
    def __str__(self):
        return f"{self.name} ({self.id})"