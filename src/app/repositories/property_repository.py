"""Property repository."""

from app.models.property import Property
from app.repositories.base_repository import BaseRepository


class PropertyRepository(BaseRepository[Property]):
    """Repository for Property operations."""

    def __init__(self, session=None):
        """Initialize with Property model."""
        super().__init__(Property, session)

    def get_active(self) -> list[Property]:
        """Get all active properties."""
        return self._session.query(Property).filter(Property.is_active == True).all()

    def get_with_tenant_count(self) -> list[tuple[Property, int]]:
        """Get properties with tenant counts.

        Returns:
            List of tuples (Property, tenant_count)
        """
        from sqlalchemy import func

        from app.models.tenant import Tenant

        return (
            self._session.query(Property, func.count(Tenant.id).label("tenant_count"))
            .outerjoin(Tenant, Tenant.property_id == Property.id)
            .group_by(Property.id)
            .all()
        )

    def get_by_city(self, city: str) -> list[Property]:
        """Get properties by city."""
        return (
            self._session.query(Property)
            .filter(Property.city.ilike(f"%{city}%"))
            .all()
        )
