from typing import List, Optional
from pydantic import BaseModel, Field


class ClientOut(BaseModel):
    id: str
    client_name: str
    tickers: List[str] = []
    currencies: List[str] = []
    tenors_min: Optional[str] = None
    tenors_max: Optional[str] = None
    tenors_sweetspot: Optional[str] = None
    frn_buyer: bool = False
    callable_buyer: bool = False
    private_placement_buyer: Optional[str] = None
    esg_green: bool = False
    esg_social: bool = False
    esg_sustainable: bool = False
    target_spread_ois: Optional[str] = None
    target_g_spread: Optional[str] = None
    toms_code: Optional[str] = None
    client_notes: Optional[str] = None
    region: Optional[str] = None


class ClientListResponse(BaseModel):
    items: List[ClientOut]


class ClientUpdate(BaseModel):
    client_name: Optional[str] = None
    tickers: Optional[List[str]] = Field(default=None, description="List of ticker symbols")
    currencies: Optional[List[str]] = Field(default=None, description="List of currency codes")
    tenors_min: Optional[str] = None
    tenors_max: Optional[str] = None
    tenors_sweetspot: Optional[str] = None
    frn_buyer: Optional[bool] = None
    callable_buyer: Optional[bool] = None
    private_placement_buyer: Optional[str] = None
    esg_green: Optional[bool] = None
    esg_social: Optional[bool] = None
    esg_sustainable: Optional[bool] = None
    target_spread_ois: Optional[str] = None
    target_g_spread: Optional[str] = None
    toms_code: Optional[str] = None
    client_notes: Optional[str] = None
    region: Optional[str] = None


class ClientCreate(BaseModel):
    client_name: str
    tickers: Optional[List[str]] = Field(default=None, description="List of ticker symbols")
    currencies: Optional[List[str]] = Field(default=None, description="List of currency codes")
    tenors_min: Optional[str] = None
    tenors_max: Optional[str] = None
    tenors_sweetspot: Optional[str] = None
    frn_buyer: Optional[bool] = None
    callable_buyer: Optional[bool] = None
    private_placement_buyer: Optional[str] = None
    esg_green: Optional[bool] = None
    esg_social: Optional[bool] = None
    esg_sustainable: Optional[bool] = None
    target_spread_ois: Optional[str] = None
    target_g_spread: Optional[str] = None
    toms_code: Optional[str] = None
    client_notes: Optional[str] = None
    region: Optional[str] = None


class AuditItem(BaseModel):
    id: str
    client_id: str
    user_id: Optional[str] = None
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_at: str


class AuditListResponse(BaseModel):
    items: List[AuditItem]
