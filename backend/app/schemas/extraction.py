from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """
    Normalized 2D bounding box representing spatial location on a document page.
    Coordinates are expressed as percentages (0.0 to 100.0) of page width/height.
    """
    id: Optional[str] = Field(None, description="Unique identifier for the bounding box element")
    label: str = Field(..., description="Entity label (e.g. 'GSTIN Number', 'PAN Number', 'Validity Date')")
    x: float = Field(..., description="Top-left X coordinate percentage (0 - 100)")
    y: float = Field(..., description="Top-left Y coordinate percentage (0 - 100)")
    width: float = Field(..., description="Width percentage (0 - 100)")
    height: float = Field(..., description="Height percentage (0 - 100)")
    status: str = Field("valid", description="Verification state: 'valid' | 'invalid' | 'warning'")
    text: Optional[str] = Field(None, description="Recognized text inside this bounding box")


class ExtractedEntity(BaseModel):
    """
    Normalized extraction schema representing a single verified document entity.
    """
    field_name: str = Field(..., description="Canonical field identifier (e.g., 'gstin', 'panNumber')")
    extracted_value: str = Field(..., description="Verbatim raw text string extracted from the document")
    normalized_value: Optional[str] = Field(None, description="Cleaned, standardized format (e.g. uppercase, ISO date)")
    page_number: int = Field(1, description="1-indexed document page where the entity was detected")
    bounding_box: Optional[BoundingBox] = Field(None, description="Spatial coordinates of the entity on the source page")
    evidence_reference: Optional[str] = Field(None, description="Human-readable evidence reference (e.g. 'Page 1 [X: 28.0%, Y: 15.5%]')")
    confidence: float = Field(1.0, description="Extraction confidence score from 0.0 to 1.0")


class DocumentExtractionResult(BaseModel):
    """
    Container for all extracted entities and spatial geometries of a single document.
    """
    document_id: str = Field(..., description="Internal or server-controlled document ID")
    document_type: str = Field(..., description="Document type: 'GST_CERTIFICATE' | 'PAN_CARD' | 'UDYAM_MSME' | 'STARTUP_INDIA' | 'OEM_MAF' | 'OTHER'")
    title: str = Field(..., description="User-facing title of the document")
    form_type: Optional[str] = Field(None, description="Official government form designation (e.g. 'Form REG-06')")
    raw_text: str = Field("", description="Full text parsed from all document pages")
    page_count: int = Field(1, description="Total number of pages in the document")
    fields: Dict[str, ExtractedEntity] = Field(default_factory=dict, description="Map of field_name -> ExtractedEntity")
    bounding_boxes: List[BoundingBox] = Field(default_factory=list, description="All highlightable bounding boxes on the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Supplementary document metadata")


class VendorDossier(BaseModel):
    """
    Complete vendor filing bundle comprising all submitted statutory documents.
    """
    vendor_id: str
    vendor_name: str
    tender_id: Optional[str] = None
    documents: List[DocumentExtractionResult] = Field(default_factory=list)
