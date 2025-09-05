from typing import Dict, List, Optional

from django.db import models

from .constants import DEFAULT_EXCLUDED_FIELDS, AuditAction, AuditLevel
from .models import AuditLog
from .utils import AuditDataSerializer, AuditUserExtractor


class AuditService:
    """Servicio principal para manejo de auditoría"""

    @staticmethod
    def audit_create(
        instance: models.Model,
        excluded_fields: Optional[List[str]] = None,
        level: str = AuditLevel.MEDIUM,
        metadata: Optional[Dict] = None,
    ):
        """Audita la creación de un objeto"""
        user_info = AuditUserExtractor.get_user_info()

        # Obtener valores iniciales
        excluded = excluded_fields or DEFAULT_EXCLUDED_FIELDS
        initial_data = {}

        for field in instance._meta.fields:
            if field.name not in excluded:
                value = getattr(instance, field.name, None)
                if value is not None:
                    initial_data[field.name] = {
                        "old_value": None,
                        "new_value": AuditDataSerializer.mask_sensitive_data(
                            field.name, AuditDataSerializer.serialize_value(value)
                        ),
                    }

        return AuditLog.objects.create_audit(
            instance=instance,
            action=AuditAction.CREATE,
            changes=initial_data,
            level=level,
            metadata=metadata or {},
        )

    @staticmethod
    def audit_update(
        old_instance: models.Model,
        new_instance: models.Model,
        tracked_fields: Optional[List[str]] = None,
        excluded_fields: Optional[List[str]] = None,
        level: str = AuditLevel.MEDIUM,
        metadata: Optional[Dict] = None,
    ):
        """Audita la actualización de un objeto"""
        excluded = excluded_fields or DEFAULT_EXCLUDED_FIELDS

        if tracked_fields:
            # Filtrar campos excluidos de los campos trackeados
            tracked_fields = [f for f in tracked_fields if f not in excluded]
        else:
            # Usar todos los campos excepto los excluidos
            tracked_fields = [
                f.name for f in new_instance._meta.fields if f.name not in excluded
            ]

        changes = AuditDataSerializer.get_field_changes(
            old_instance, new_instance, tracked_fields
        )

        if changes:  # Solo crear log si hay cambios
            return AuditLog.objects.create_audit(
                instance=new_instance,
                action=AuditAction.UPDATE,
                changes=changes,
                level=level,
                metadata=metadata or {},
            )

        return None

    @staticmethod
    def audit_delete(
        instance: models.Model,
        level: str = AuditLevel.HIGH,
        metadata: Optional[Dict] = None,
    ):
        """Audita la eliminación de un objeto"""
        # Capturar estado final antes de eliminar
        final_state = {}
        for field in instance._meta.fields:
            if field.name not in DEFAULT_EXCLUDED_FIELDS:
                value = getattr(instance, field.name, None)
                if value is not None:
                    final_state[field.name] = {
                        "old_value": AuditDataSerializer.mask_sensitive_data(
                            field.name, AuditDataSerializer.serialize_value(value)
                        ),
                        "new_value": None,
                    }

        return AuditLog.objects.create_audit(
            instance=instance,
            action=AuditAction.DELETE,
            changes=final_state,
            level=level,
            metadata=metadata or {},
        )

    @staticmethod
    def audit_read(
        instance: models.Model,
        level: str = AuditLevel.LOW,
        metadata: Optional[Dict] = None,
    ):
        """Audita la lectura/consulta de un objeto"""
        return AuditLog.objects.create_audit(
            instance=instance,
            action=AuditAction.READ,
            changes={},
            level=level,
            metadata=metadata or {},
        )


class AuditConfig:
    """Configuración de auditoría para modelos"""

    def __init__(
        self,
        tracked_fields: Optional[List[str]] = None,
        excluded_fields: Optional[List[str]] = None,
        audit_creates: bool = True,
        audit_updates: bool = True,
        audit_deletes: bool = True,
        audit_reads: bool = False,
        level: str = AuditLevel.MEDIUM,
    ):
        self.tracked_fields = tracked_fields
        self.excluded_fields = excluded_fields or []
        self.audit_creates = audit_creates
        self.audit_updates = audit_updates
        self.audit_deletes = audit_deletes
        self.audit_reads = audit_reads
        self.level = level
