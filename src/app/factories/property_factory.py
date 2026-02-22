"""Property factory for creating Property objects."""

from datetime import date

from app.models.property import Property
from app.repositories.property_repository import PropertyRepository


class PropertyFactory:
    """Factory for creating Property objects with validation."""

    def __init__(self, repository: PropertyRepository | None = None):
        """Initialize factory with optional repository."""
        self._repository = repository or PropertyRepository()

    def create(
        self,
        address: str,
        city: str,
        postal_code: str,
        monthly_rent: float,
    ) -> Property:
        """Create a new Property with validation.

        Args:
            address: Street address
            city: City name
            postal_code: Postal/ZIP code
            monthly_rent: Monthly rent amount

        Returns:
            Created Property instance

        Raises:
            ValueError: If validation fails
        """
        # Validation
        if not address or not address.strip():
            raise ValueError("Address is required")

        if not city or not city.strip():
            raise ValueError("City is required")

        if not postal_code or not postal_code.strip():
            raise ValueError("Postal code is required")

        monthly_rent = float(monthly_rent)
        if monthly_rent <= 0:
            raise ValueError("Monthly rent must be positive")

        # Create property
        data = {
            "address": address.strip(),
            "city": city.strip(),
            "postal_code": postal_code.strip(),
            "monthly_rent": monthly_rent,
            "is_active": True,
        }

        return self._repository.create(data)

    def create_with_defaults(
        self,
        address: str,
        city: str,
        postal_code: str,
        monthly_rent: float = 1000.00,
    ) -> Property:
        """Create property with default values.

        Args:
            address: Street address
            city: City name
            postal_code: Postal/ZIP code
            monthly_rent: Monthly rent amount (defaults to 1000.00)

        Returns:
            Created Property instance
        """
        return self.create(address, city, postal_code, monthly_rent)
