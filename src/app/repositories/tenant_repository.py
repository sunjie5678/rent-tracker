"""Tenant repository."""

from app.models.tenant import Tenant
from app.repositories.base_repository import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    """Repository for Tenant operations."""

    def __init__(self, session=None):
        """Initialize with Tenant model."""
        super().__init__(Tenant, session)

    def get_by_property(self, property_id: int) -> list[Tenant]:
        """Get all tenants for a property."""
        return (
            self._session.query(Tenant)
            .filter(Tenant.property_id == property_id)
            .order_by(Tenant.move_in_date.desc())
            .all()
        )

    def get_active_by_property(self, property_id: int) -> list[Tenant]:
        """Get active tenants (not moved out) for a property."""
        return (
            self._session.query(Tenant)
            .filter(
                Tenant.property_id == property_id,
                Tenant.move_out_date.is_(None),
            )
            .order_by(Tenant.move_in_date.desc())
            .all()
        )

    def get_current(self) -> list[Tenant]:
        """Get all current tenants (not moved out)."""
        return (
            self._session.query(Tenant)
            .filter(Tenant.move_out_date.is_(None))
            .order_by(Tenant.name)
            .all()
        )

    def search_by_name(self, name: str) -> list[Tenant]:
        """Search tenants by name."""
        return (
            self._session.query(Tenant)
            .filter(Tenant.name.ilike(f"%{name}%"))
            .order_by(Tenant.name)
            .all()
        )
