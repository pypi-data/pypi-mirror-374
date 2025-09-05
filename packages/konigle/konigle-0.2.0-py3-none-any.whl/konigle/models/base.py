"""
Base model classes and mixins for the Konigle SDK.

This module provides the foundation for all resource models,
including Active Record functionality, state tracking, and
common model patterns.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from pydantic import BaseModel, ConfigDict, PrivateAttr

from konigle.types.common import IDMixin, TimestampMixin

if TYPE_CHECKING:
    from konigle.managers.base import BaseAsyncManager, BaseSyncManager


class BaseResource(BaseModel):
    """
    Base class providing Active Record functionality to all resources.

    This class enables resources to have methods like save(), delete(),
    and reload() by maintaining a reference to their manager and tracking
    field modifications.
    """

    _manager: Optional["BaseSyncManager | BaseAsyncManager"] = None
    """Reference to the manager handling this resource."""

    _original_data: Optional[Dict[str, Any]] = None
    """Snapshot of the original data for change tracking."""

    _modified_fields: Set[str] = PrivateAttr(default_factory=set)
    """Set of field names that have been modified since last sync."""

    def __setattr__(self, name: str, value: Any) -> None:
        """Track field modifications for dirty checking."""
        # Only track changes to actual model fields, not private attributes
        if (
            hasattr(self, "_original_data")
            and name in self.__class__.model_fields
            and self._original_data is not None
        ):
            self._modified_fields = self._modified_fields or set()

            original_value = self._original_data.get(name)
            if original_value != value:
                self._modified_fields.add(name)

        super().__setattr__(name, value)

    def save(self) -> "BaseResource":
        """
        Save changes back to the API.

        Returns:
            Updated resource instance with fresh data from the server

        Raises:
            ValueError: If resource is not associated with a manager
            APIError: If the API request fails
        """
        if not self._manager:
            raise ValueError(
                f"Cannot save: {self.__class__.__name__} not associated with "
                "a manager"
            )

        # Check if manager is sync
        from konigle.managers.base import BaseAsyncManager

        if isinstance(self._manager, BaseAsyncManager):
            raise ValueError(
                f"Cannot use save(): {self.__class__.__name__} is "
                "associated with an async manager. Use asave() instead."
            )

        if not self._modified_fields:
            return self  # No changes to save

        # Create update data with only modified fields
        update_data = {
            field: getattr(self, field) for field in self._modified_fields
        }

        # Call manager's update method
        updated_resource = self._manager.update(self._get_id(), update_data)

        # Update self with fresh data from server
        for field, value in updated_resource.model_dump().items():
            if (
                field in self.__class__.model_fields
            ):  # Only update model fields
                setattr(self, field, value)

        # Reset tracking state
        if self._modified_fields:
            self._modified_fields.clear()
        self._original_data = self.model_dump()

        return self

    def delete(self) -> bool:
        """
        Delete this resource from the API.

        Returns:
            True if deletion was successful

        Raises:
            ValueError: If resource is not associated with a manager
            APIError: If the API request fails
        """
        if not self._manager:
            raise ValueError(
                f"Cannot delete: {self.__class__.__name__} not associated "
                "with a manager"
            )

        # Check if manager is sync
        from konigle.managers.base import BaseAsyncManager

        if isinstance(self._manager, BaseAsyncManager):
            raise ValueError(
                f"Cannot use delete(): {self.__class__.__name__} is "
                "associated with an async manager. Use adelete() instead."
            )

        return self._manager.delete(self._get_id())

    def reload(self) -> "BaseResource":
        """
        Reload fresh data from the API.

        Returns:
            Self with updated data from the server

        Raises:
            ValueError: If resource is not associated with a manager
            APIError: If the API request fails
        """
        if not self._manager:
            raise ValueError(
                f"Cannot reload: {self.__class__.__name__} not associated "
                "with a manager"
            )

        from konigle.managers.base import BaseAsyncManager

        if isinstance(self._manager, BaseAsyncManager):
            raise ValueError(
                f"Cannot use reload(): {self.__class__.__name__} is "
                "associated with an async manager. Use areload() instead."
            )

        fresh_resource = self._manager.get(self._get_id())

        # Update self with fresh data
        for field, value in fresh_resource.model_dump().items():
            if field in self.__class__.model_fields:
                setattr(self, field, value)

        # Reset tracking state
        if self._modified_fields:
            self._modified_fields.clear()
        self._original_data = self.model_dump()

        return self

    async def asave(self) -> "BaseResource":
        """
        Async version of save() - Save changes back to the API.

        Returns:
            Updated resource instance with fresh data from the server

        Raises:
            ValueError: If resource is not associated with an async manager
            APIError: If the API request fails
        """
        if not self._manager:
            raise ValueError(
                f"Cannot save: {self.__class__.__name__} not associated with "
                "a manager"
            )

        from konigle.managers.base import BaseAsyncManager

        if not isinstance(self._manager, BaseAsyncManager):
            raise ValueError(
                f"Cannot use asave(): {self.__class__.__name__} is "
                "associated with a sync manager. Use save() instead."
            )

        if not self._modified_fields:
            return self  # No changes to save

        # Create update data with only modified fields
        update_data = {
            field: getattr(self, field) for field in self._modified_fields
        }

        # Call manager's update method
        updated_resource = await self._manager.update(
            self._get_id(), update_data
        )

        # Update self with fresh data from server
        for field, value in updated_resource.model_dump().items():
            if (
                field in self.__class__.model_fields
            ):  # Only update model fields
                setattr(self, field, value)

        # Reset tracking state
        self._modified_fields.clear()
        self._original_data = self.model_dump()

        return self

    async def adelete(self) -> bool:
        """
        Async version of delete() - Delete this resource from the API.

        Returns:
            True if deletion was successful

        Raises:
            ValueError: If resource is not associated with an async manager
            APIError: If the API request fails
        """
        if not self._manager:
            raise ValueError(
                f"Cannot delete: {self.__class__.__name__} not associated "
                "with a manager"
            )

        # Check if manager is async
        from konigle.managers.base import BaseAsyncManager

        if not isinstance(self._manager, BaseAsyncManager):
            raise ValueError(
                f"Cannot use adelete(): {self.__class__.__name__} is "
                "associated with a sync manager. Use delete() instead."
            )

        return await self._manager.delete(self._get_id())

    async def areload(self) -> "BaseResource":
        """
        Async version of reload() - Reload fresh data from the API.

        Returns:
            Self with updated data from the server

        Raises:
            ValueError: If resource is not associated with an async manager
            APIError: If the API request fails
        """
        if not self._manager:
            raise ValueError(
                f"Cannot reload: {self.__class__.__name__} not associated "
                "with a manager"
            )

        # Check if manager is async
        from konigle.managers.base import BaseAsyncManager

        if not isinstance(self._manager, BaseAsyncManager):
            raise ValueError(
                f"Cannot use areload(): {self.__class__.__name__} is "
                "associated with a sync manager. Use reload() instead."
            )

        fresh_resource = await self._manager.get(self._get_id())

        # Update self with fresh data
        for field, value in fresh_resource.model_dump().items():
            if field in self.__class__.model_fields:
                setattr(self, field, value)

        # Reset tracking state
        if self._modified_fields:
            self._modified_fields.clear()
        self._original_data = self.model_dump()

        return self

    @property
    def is_dirty(self) -> bool:
        """Check if the object has unsaved changes."""
        return len(self._modified_fields or set()) > 0

    @property
    def dirty_fields(self) -> Set[str]:
        """Get the names of fields that have been modified."""
        return (self._modified_fields or set()).copy()

    def reset_changes(self) -> None:
        """Reset all changes to original values."""
        if self._original_data and self._modified_fields:
            for field in self._modified_fields:
                if field in self._original_data:
                    setattr(self, field, self._original_data[field])
        if self._modified_fields:
            self._modified_fields.clear()

    def _get_id(self) -> str:
        """Helper to get the ID field if it exists."""
        id_ = getattr(self, "id", None)
        if id_ is None:
            raise ValueError(
                f"Cannot get ID: {self.__class__.__name__} does not have an 'id' field."
            )
        return id_

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
        validate_assignment=True,
    )


class Resource(BaseResource, IDMixin):
    """
    Standard resource model for resources that have an ID but no timestamps.

    Combines BaseResource (Active Record) with IDMixin (id field).
    Use this for simple resources that don't have created_at/updated_at fields.
    """

    pass


class TimestampedResource(BaseResource, IDMixin, TimestampMixin):
    """
    Resource model for resources that have ID and timestamp fields.

    Combines BaseResource (Active Record), IDMixin (id field),
    and TimestampMixin (created_at, updated_at) for resources
    that include full timestamp tracking.
    """

    pass


class CreateModel(BaseModel):
    """
    Base class for creation models.

    Used for models that define fields required/allowed
    when creating new resources.
    """

    # Allow arbitrary types for file handling
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )


class UpdateModel(BaseModel):
    """
    Base class for update models.

    Used for models that define fields allowed when
    updating existing resources. All fields are optional.
    """

    # Allow arbitrary types for file handling
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )
