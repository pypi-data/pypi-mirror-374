import logging

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from cloe_metadata import base

logger = logging.getLogger(__name__)


class DataSourceInfo(BaseModel):
    """Class for advanced or shared DataSourceInfo functionality."""

    base_obj: base.DataSourceInfo
    sourcesystems: base.Sourcesystems = Field(..., exclude=True)
    tenants: base.Tenants = Field(..., exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("sourcesystems")
    @classmethod
    def sourcesystem_exists(cls, value: base.Sourcesystems, info: ValidationInfo):
        """
        Validates that the source system exists in the source systems.

        Args:
            value (base.Sourcesystems): The source systems object to validate.
            info (ValidationInfo): Information about the field being validated.

        Raises:
            ValueError: If the sourcesystem_id does not exist in the source systems.

        Returns:
            base.Sourcesystems: The validated source systems object.
        """
        base_obj: base.DataSourceInfo | None = info.data.get("base_obj")
        if (
            base_obj is not None
            and base_obj.sourcesystem_id not in value.get_sourcesystems()
        ):
            raise ValueError("sourcesystem does not exist")
        return value

    @field_validator("tenants")
    @classmethod
    def tenant_exists(cls, value: base.Tenants, info: ValidationInfo):
        """
        Validates that the tenant exists in the tenants.

        Args:
            value (base.Tenants): The tenants object to validate.
            info (ValidationInfo): Information about the field being validated.

        Raises:
            ValueError: If the tenant_id does not exist in the tenants.

        Returns:
            base.Tenants: The validated tenants object.
        """
        base_obj: base.DataSourceInfo | None = info.data.get("base_obj")
        if (
            base_obj is not None
            and base_obj.tenant_id is not None
            and base_obj.tenant_id not in value.get_tenants()
        ):
            raise ValueError("tenant does not exist")
        return value

    @property
    def tenant(self) -> base.Tenant | None:
        """
        Returns the tenant object.

        Returns:
            base.Tenant | None: The tenant object, or None if it does not exist.
        """
        if self.base_obj.tenant_id is not None:
            return self.tenants.get_tenants().get(self.base_obj.tenant_id)
        return None

    @property
    def sourcesystem(self) -> base.Sourcesystem:
        """
        Returns the source system object.

        Returns:
            base.Sourcesystem: The source system object.
        """
        return self.sourcesystems.get_sourcesystems()[self.base_obj.sourcesystem_id]
