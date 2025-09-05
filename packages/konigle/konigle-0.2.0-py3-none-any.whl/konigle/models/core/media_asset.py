"""
Media asset models for the Konigle SDK.

This module defines models for Image, Video, and Document assets.
All three types map to the same backend StorefrontAsset table but are
differentiated by mime_type for user-friendly separate interfaces.
"""

import io
from enum import Enum
from typing import BinaryIO, List, Optional, Tuple, Union

from pydantic import ConfigDict, Field, field_validator, model_validator

from konigle.models.base import CreateModel, TimestampedResource, UpdateModel
from konigle.utils import FileInput


class AssetType(str, Enum):
    """Asset type enumeration."""

    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"


class BaseAsset(TimestampedResource):
    """Base class for all media assets with common fields."""

    name: str = Field(..., max_length=255)
    """User-friendly name for searching"""

    mime_type: str = Field(..., max_length=100)
    """MIME type of the file"""

    alt_text: str = Field(default="")
    """Alt text for accessibility"""

    size: int = Field(default=0, ge=0)
    """Total size in bytes"""

    asset_url: Optional[str] = Field(None)
    """URL to access the asset"""

    tags: List[str] = Field(default_factory=list)
    """Tags for categorization"""


class BaseAssetCreate(CreateModel):
    """Base create model for assets."""

    name: str = Field(..., max_length=255)
    """User-friendly name"""

    alt_text: str = Field(default="")
    """Alt text for accessibility"""

    tags: str = Field(default="")
    """Tags for categorization. Comma-separated string."""


class BaseAssetUpdate(UpdateModel):
    """Base update model for assets - only mutable fields."""

    name: Optional[str] = Field(None, max_length=255)
    """User-friendly name"""

    alt_text: Optional[str] = Field(None)
    """Alt text for accessibility"""

    tags: Optional[List[str]] = Field(None)
    """Tags for categorization"""

    model_config = ConfigDict(arbitrary_types_allowed=True)


# Image-specific models
class Image(BaseAsset):
    """Image asset model."""

    image_width: Optional[int] = Field(None, ge=0)
    """Image width in pixels"""

    image_height: Optional[int] = Field(None, ge=0)
    """Image height in pixels"""


class ImageCreate(BaseAssetCreate):
    """Create model for image assets."""

    image: Union[
        str,
        bytes,
        io.BytesIO,
        BinaryIO,
        Tuple[Union[bytes, io.BytesIO, BinaryIO], str],
    ] = Field(...)
    """Image file to upload. Can be file path, bytes, BytesIO, BinaryIO, or
    tuple of (file_data, filename)"""

    @field_validator("image")
    @classmethod
    def validate_image_file(cls, v):
        """Ensure we're uploading an image file."""
        allowed_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
        ]
        # Handle tuple input
        if isinstance(v, tuple) and len(v) == 2:
            _, filename = v
            if not any(
                filename.lower().endswith(ext) for ext in allowed_extensions
            ):
                raise ValueError(
                    f"File must be an image {', '.join(allowed_extensions)}"
                )
        elif (
            isinstance(v, str)
            and not v.startswith("https://")
            and not any(v.lower().endswith(ext) for ext in allowed_extensions)
        ):
            raise ValueError(
                f"File must be an image ({', '.join(allowed_extensions)})"
            )
        return v

    @model_validator(mode="after")
    def normalize_file(self):
        """Convert file paths or bytes to FileInput."""
        self.image = FileInput.normalize(self.image)
        return self


class ImageUpdate(BaseAssetUpdate):
    """Update model for image assets - file cannot be updated."""


# Video-specific models
class Video(BaseAsset):
    """Video asset model."""


class VideoCreate(BaseAssetCreate):
    """Create model for video assets."""

    file: Union[
        str,
        bytes,
        io.BytesIO,
        BinaryIO,
        Tuple[Union[bytes, io.BytesIO, BinaryIO], str],
    ] = Field(...)
    """Video file to upload. Can be file path, bytes, BytesIO, BinaryIO,
    or tuple of (file_data, filename)"""

    @field_validator("file")
    @classmethod
    def validate_video_file(cls, v):
        """Ensure we're uploading a video file."""
        supported_formats = [".mp4", ".webm"]
        # Handle tuple input
        if isinstance(v, tuple) and len(v) == 2:
            _, filename = v
            if not any(
                filename.lower().endswith(ext) for ext in supported_formats
            ):
                raise ValueError(
                    f"File must be a video {', '.join(supported_formats)}"
                )
        elif (
            isinstance(v, str)
            and not v.startswith("https://")
            and not any(v.lower().endswith(ext) for ext in supported_formats)
        ):
            raise ValueError(
                f"File must be a video ({', '.join(supported_formats)})"
            )
        return v

    @model_validator(mode="after")
    def normalize_file(self):
        """Convert file paths or bytes to FileInput."""
        self.file = FileInput.normalize(self.file)
        return self


class VideoUpdate(BaseAssetUpdate):
    """Update model for video assets - file cannot be updated."""


# Document-specific models
class Document(BaseAsset):
    """Document asset model."""


class DocumentCreate(BaseAssetCreate):
    """Create model for document assets."""

    file: Union[
        str,
        bytes,
        io.BytesIO,
        BinaryIO,
        Tuple[Union[bytes, io.BytesIO, BinaryIO], str],
    ] = Field(...)
    """Document file to upload. Can be file path, bytes, BytesIO, BinaryIO, or tuple of (file_data, filename)"""

    @field_validator("file")
    @classmethod
    def validate_document_file(cls, v):
        """Ensure we're uploading a supported document file."""
        supported_extensions = [
            ".pdf",
            ".csv",
            ".txt",
            ".docx",
            ".xlsx",
            ".doc",
            ".xls",
        ]

        # Handle tuple input
        if isinstance(v, tuple) and len(v) == 2:
            _, filename = v
            if not any(
                filename.lower().endswith(ext) for ext in supported_extensions
            ):
                raise ValueError(
                    f"File must be a supported document: "
                    f"{', '.join(supported_extensions)}"
                )
        elif isinstance(v, str) and not v.startswith("https://"):
            if not any(
                v.lower().endswith(ext) for ext in supported_extensions
            ):
                raise ValueError(
                    f"File must be a supported document: "
                    f"{', '.join(supported_extensions)}"
                )
        return v

    @model_validator(mode="after")
    def normalize_file(self):
        """Convert file paths or bytes to FileInput."""
        self.file = FileInput.normalize(self.file)
        return self


class DocumentUpdate(BaseAssetUpdate):
    """Update model for document assets - file cannot be updated."""
