"""Base repository with generic CRUD operations."""

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.database import db_session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic repository for database operations."""

    def __init__(self, model_class: type[T], session: Session | None = None):
        """Initialize repository with model class.

        Args:
            model_class: The SQLAlchemy model class
            session: Optional database session (defaults to thread-local session)
        """
        self._model = model_class
        self._session = session or db_session

    def get_by_id(self, id: int) -> T | None:
        """Get a single record by ID."""
        return self._session.get(self._model, id)

    def get_all(self) -> list[T]:
        """Get all records."""
        return self._session.query(self._model).all()

    def create(self, data: dict) -> T:
        """Create a new record.

        Args:
            data: Dictionary of field values

        Returns:
            The created model instance
        """
        instance = self._model(**data)
        self._session.add(instance)
        self._session.commit()
        return instance

    def update(self, id: int, data: dict) -> T | None:
        """Update a record by ID.

        Args:
            id: The record ID
            data: Dictionary of fields to update

        Returns:
            The updated model instance or None if not found
        """
        instance = self.get_by_id(id)
        if instance:
            for key, value in data.items():
                setattr(instance, key, value)
            self._session.commit()
        return instance

    def delete(self, id: int) -> bool:
        """Delete a record by ID.

        Args:
            id: The record ID

        Returns:
            True if deleted, False if not found
        """
        instance = self.get_by_id(id)
        if instance:
            self._session.delete(instance)
            self._session.commit()
            return True
        return False

    def count(self) -> int:
        """Count total records."""
        return self._session.query(self._model).count()
