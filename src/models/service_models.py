"""
Pydantic models for request and response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ExtractedServiceData(BaseModel):
    """Model for extracted service variation data matching the expected format."""
    serviceId: str = Field(..., description="Unique identifier for the service")
    name: str = Field(..., description="Display name of the service")
    category: str = Field(..., description="Category of the service (e.g., 'Shaving', 'Facial')")
    categoryServiceId: str = Field(..., description="Service ID that this belongs to")
    duration: int = Field(..., description="Duration in minutes")
    gender: str = Field(..., description="Target gender: M, F, or U")
    personType: str = Field(..., description="Type of person (e.g., 'A' for adult)")
    price: float = Field(..., description="Price of the service")
    tagNameAndValues: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Tags like hair length, style type, etc."
    )
    variationId: str = Field(..., description="Unique identifier for this variation")

    # Additional fields that might be included
    originalPrice: Optional[float] = Field(None, description="Original price before discounts")
    bufferInMins: Optional[int] = Field(None, description="Buffer time between appointments")
    pricingType: Optional[str] = Field(None, description="How pricing works")
    fullName: Optional[str] = Field(None, description="Full display name")
    serviceName: Optional[str] = Field(None, description="Short service name")
    salonServiceName: Optional[str] = Field(None, description="Salon's custom service name")
    salonId: Optional[str] = Field(None, description="Salon identifier")
    genericService: Optional[str] = Field(None, description="Generic category name")
    isCombo: Optional[bool] = Field(None, description="Whether this is a combo service")
    vatCategory: Optional[str] = Field(None, description="VAT category for Europe")
    pricePerUnit: Optional[float] = Field(None, description="Price per unit for per-unit pricing")
    unitType: Optional[str] = Field(None, description="Unit type for per-unit pricing")
    basePriceCalculationType: Optional[str] = Field(None, description="Base price calculation type")

class ServiceExtractionResponse(BaseModel):
    """Response model for the service extraction endpoint."""
    success: bool = Field(..., description="Whether the extraction was successful")
    data: List[ExtractedServiceData] = Field(
        default_factory=list,
        description="List of extracted and matched service variations"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata about the extraction process"
    )
    error: Optional[str] = Field(None, description="Error message if success is false")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of the response"
    )

# Request models (if needed for additional parameters)
class ServiceExtractionRequest(BaseModel):
    """Request model for service extraction (if we need additional parameters beyond file upload)."""
    salon_id: Optional[str] = Field(None, description="Optional salon ID for filtering")
    include_metadata: bool = Field(True, description="Whether to include metadata in response")