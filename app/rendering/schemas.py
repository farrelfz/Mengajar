"""
KIR AI Document Intelligence — Rendering Schemas.
"""
from enum import Enum
from pydantic import BaseModel, Field
from app.design.schemas import ComponentFamily

class RenderTarget(str, Enum):
    HTML = "html"
    REPORTLAB = "reportlab"
    PYTHON_VISUAL = "python_visual"
    AUTO = "auto"

class RenderPlanItem(BaseModel):
    source_block_id: str
    component_family: ComponentFamily
    target: RenderTarget
    page_number: int

class RenderPlan(BaseModel):
    composition_id: str
    items: list[RenderPlanItem] = Field(default_factory=list)

class AssetMetadata(BaseModel):
    asset_id: str
    asset_type: str
    source_component_id: str
    render_engine: RenderTarget
    format: str
    path: str
    width: int | None = None
    height: int | None = None

class RenderResult(BaseModel):
    success: bool
    pdf_path: str | None = None
    assets_generated: int = 0
    pages: int = 0
    errors: list[str] = Field(default_factory=list)
