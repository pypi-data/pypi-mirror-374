from functools import wraps
from typing import List, Optional

from django.db import models

from .constants import AuditLevel
from .middleware import get_current_user
from .services import AuditConfig, AuditService


def auditable(
    tracked_fields: Optional[List[str]] = None,
    excluded_fields: Optional[List[str]] = None,
    audit_creates: bool = True,
    audit_updates: bool = True,
    audit_deletes: bool = True,
    audit_reads: bool = False,
    level: str = AuditLevel.MEDIUM,
):
    """
    Decorator mejorado para auditoría de modelos

    Args:
        tracked_fields: Lista de campos específicos a trackear
        excluded_fields: Lista de campos a excluir del tracking
        audit_creates: Si auditar creaciones
        audit_updates: Si auditar actualizaciones
        audit_deletes: Si auditar eliminaciones
        audit_reads: Si auditar lecturas
        level: Nivel de auditoría
    """

    def decorator(cls):
        if not issubclass(cls, models.Model):
            raise ValueError(
                "El decorator auditable solo puede aplicarse a modelos Django"
            )

        # Configuración de auditoría
        audit_config = AuditConfig(
            tracked_fields=tracked_fields,
            excluded_fields=excluded_fields,
            audit_creates=audit_creates,
            audit_updates=audit_updates,
            audit_deletes=audit_deletes,
            audit_reads=audit_reads,
            level=level,
        )

        # Guardar configuración en el modelo
        cls._audit_config = audit_config

        # Interceptar save
        if audit_config.audit_creates or audit_config.audit_updates:
            original_save = cls.save

            @wraps(original_save)
            def new_save(self, *args, **kwargs):
                is_creation = self.pk is None
                old_instance = None

                if not is_creation and audit_config.audit_updates:
                    try:
                        old_instance = cls.objects.get(pk=self.pk)
                    except cls.DoesNotExist:
                        old_instance = None

                # Ejecutar save original
                result = original_save(self, *args, **kwargs)

                # Auditar después del save
                try:
                    if is_creation and audit_config.audit_creates:
                        AuditService.audit_create(
                            instance=self,
                            excluded_fields=audit_config.excluded_fields,
                            level=audit_config.level,
                        )
                    elif old_instance and audit_config.audit_updates:
                        AuditService.audit_update(
                            old_instance=old_instance,
                            new_instance=self,
                            tracked_fields=audit_config.tracked_fields,
                            excluded_fields=audit_config.excluded_fields,
                            level=audit_config.level,
                        )
                except Exception as e:
                    # Log error pero no fallar el save
                    import logging

                    logger = logging.getLogger("auditlog")
                    logger.error(f"Error en auditoría: {e}")

                return result

            cls.save = new_save

        # Interceptar delete
        if audit_config.audit_deletes:
            original_delete = cls.delete

            @wraps(original_delete)
            def new_delete(self, *args, **kwargs):
                # Auditar antes de eliminar
                try:
                    AuditService.audit_delete(instance=self, level=audit_config.level)
                except Exception as e:
                    import logging

                    logger = logging.getLogger("auditlog")
                    logger.error(f"Error en auditoría de eliminación: {e}")

                return original_delete(self, *args, **kwargs)

            cls.delete = new_delete

        return cls

    return decorator


# Decorator legacy para compatibilidad
def legacy_auditable(fields_to_track=None):
    """Decorator legacy mantenido para compatibilidad hacia atrás"""
    from .models import AttributeAudit

    def decorator(cls):
        original_save = cls.save

        @wraps(original_save)
        def new_save(self, *args, **kwargs):
            if self.pk:
                try:
                    old_obj = cls.objects.get(pk=self.pk)
                    campos = fields_to_track or [f.name for f in self._meta.fields]

                    for campo in campos:
                        old_value = getattr(old_obj, campo, None)
                        new_value = getattr(self, campo, None)

                        # Evitar ruido con campos de timestamp
                        if campo in ["created", "modified", "updated_at"]:
                            continue

                        if old_value != new_value:
                            AttributeAudit.objects.create(
                                model_name=self.__class__.__name__,
                                object_id=self.pk,
                                field_name=campo,
                                old_value=old_value,
                                new_value=new_value,
                                changed_by=get_current_user(),
                            )
                except Exception as e:
                    import logging

                    logger = logging.getLogger("auditlog")
                    logger.error(f"Error en auditoría legacy: {e}")

            return original_save(self, *args, **kwargs)

        cls.save = new_save
        return cls

    return decorator
