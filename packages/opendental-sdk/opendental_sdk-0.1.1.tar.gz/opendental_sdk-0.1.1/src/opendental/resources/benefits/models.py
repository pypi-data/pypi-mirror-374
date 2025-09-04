"""Benefits models for Open Dental SDK."""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from pydantic import Field

from ...base.models import BaseModel


class Benefit(BaseModel):
    """Benefit model with exact Open Dental API field mapping."""
    
    # Primary identifiers
    benefit_num: int = Field(..., alias="BenefitNum", description="Benefit number (primary key)")
    
    # Plan associations
    plan_num: int = Field(..., alias="PlanNum", description="Insurance plan number")
    pat_plan_num: Optional[int] = Field(None, alias="PatPlanNum", description="Patient plan number")
    
    # Benefit classification
    benefit_type: str = Field(..., alias="BenefitType", description="Benefit type (Limitations, Percentages, Deductible, etc.)")
    cov_cat_num: Optional[int] = Field(None, alias="CovCatNum", description="Coverage category number")
    
    # Financial limits
    monetary_amt: Optional[Decimal] = Field(None, alias="MonetaryAmt", description="Monetary amount for limitations or deductibles")
    percent: Optional[int] = Field(None, alias="Percent", description="Percentage coverage (0-100, -1 for N/A)")
    
    # Time period
    time_period: str = Field(..., alias="TimePeriod", description="Time period (CalendarYear, ServiceYear, Lifetime, etc.)")
    
    # Quantity limitations
    quantity_qualifier: Optional[str] = Field(None, alias="QuantityQualifier", description="Quantity qualifier (None, Years, Months, etc.)")
    quantity: Optional[int] = Field(None, alias="Quantity", description="Quantity limit")
    
    # Procedure code specificity
    code_num: Optional[int] = Field(None, alias="CodeNum", description="Procedure code number")
    proc_code: Optional[str] = Field(None, alias="procCode", description="Procedure code string")
    
    # Coverage level
    coverage_level: Optional[str] = Field(None, alias="CoverageLevel", description="Coverage level (Individual, Family)")
    
    # Timestamps
    date_timestamp: Optional[datetime] = Field(None, alias="DateTStamp", description="Last modified timestamp")
    
    # Timestamps
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None


class CreateBenefitRequest(BaseModel):
    """Request model for creating a new benefit with proper API field mapping."""
    
    # Required fields - matching API specification exactly
    plan_num: int
    benefit_type: str  # "Limitations", "Percentages", "Deductible", etc.
    time_period: str   # "CalendarYear", "ServiceYear", "Lifetime", etc.
    
    # Optional association fields
    pat_plan_num: Optional[int] = None
    cov_cat_num: Optional[int] = None
    
    # Financial amounts
    monetary_amt: Optional[Decimal] = None
    percent: Optional[int] = None  # -1 for N/A, 0-100 for percentages
    
    # Quantity limits
    quantity_qualifier: Optional[str] = None
    quantity: Optional[int] = None
    
    # Procedure code specificity
    code_num: Optional[int] = None
    proc_code: Optional[str] = None
    
    # Coverage level
    coverage_level: Optional[str] = None  # "Individual", "Family"


class UpdateBenefitRequest(BaseModel):
    """Request model for updating an existing benefit."""
    
    # All fields are optional for updates - matching API structure
    plan_num: Optional[int] = None
    benefit_type: Optional[str] = None
    time_period: Optional[str] = None
    pat_plan_num: Optional[int] = None
    cov_cat_num: Optional[int] = None
    monetary_amt: Optional[Decimal] = None
    percent: Optional[int] = None
    quantity_qualifier: Optional[str] = None
    quantity: Optional[int] = None
    code_num: Optional[int] = None
    proc_code: Optional[str] = None
    coverage_level: Optional[str] = None


class BenefitListResponse(BaseModel):
    """Response model for benefit list operations."""
    
    benefits: List[Benefit]
    total: int
    page: Optional[int] = None
    per_page: Optional[int] = None


class BenefitSearchRequest(BaseModel):
    """Request model for searching benefits."""
    
    plan_num: Optional[int] = None
    patient_num: Optional[int] = None
    procedure_code: Optional[str] = None
    coverage_level: Optional[str] = None
    benefit_type: Optional[str] = None
    benefit_year: Optional[int] = None
    
    # Pagination
    page: Optional[int] = 1
    per_page: Optional[int] = 50