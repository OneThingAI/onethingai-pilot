from typing import Any, Dict, List, Optional, Union, TypeVar, Generic
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator
from pydantic.alias_generators import to_snake

# API Parameters
class CamelCaseModel(BaseModel):
    def dict(self, *args, **kwargs) -> dict:
        # Get the original dict with by_alias=True to handle nested models
        kwargs['by_alias'] = True
        original_dict = super().dict(*args, **kwargs)
        
        # Convert snake_case to camelCase for all keys
        def convert_dict(d: dict) -> dict:
            new_dict = {}
            for k, v in d.items():
                new_key = ''.join(word.title() if i > 0 else word 
                                for i, word in enumerate(k.split('_')))
                if isinstance(v, dict):
                    new_dict[new_key] = convert_dict(v)
                elif isinstance(v, list):
                    new_dict[new_key] = [convert_dict(item) if isinstance(item, dict) else item for item in v]
                else:
                    new_dict[new_key] = v
            return new_dict
            
        return convert_dict(original_dict)

class ResourceQuery(CamelCaseModel):
    app_image_id: int 
    gpu_type: str

class CustomPort(CamelCaseModel):
    local_port: int
    type: str  # 1, tcp, 2, http

class InstanceConfigQuery(CamelCaseModel):
    app_image_id: str
    bill_type: int
    gpu_num: int
    region_id: int
    gpu_type: str
    duration: int
    group_id: str 
    custom_port: list[CustomPort]

class InstanceQuery(CamelCaseModel):
    page: int
    page_size: int
    app_id: Optional[str] = None
    group_id: Optional[str] = None

class ConsumeQuery(CamelCaseModel):
    """Model for consumption query parameters."""
    page: int = Field(..., gt=0, description="Page number")
    page_size: int = Field(..., gt=0, le=100, description="Items per page, must be between 1 and 100")
    app_id: Optional[str] = Field(None, description="Instance ID")
    business_type: Optional[int] = Field(None, description="Transaction type: 1=Instance usage, 2=Image storage, 3=File storage, 4=Instance expansion")

    @validator('page_size')
    def validate_page_size(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('page_size must be between 1 and 100')
        return v


# API Responses
class BaseModelWithConfig(BaseModel):
    class Config:
        alias_generator = to_snake
        populate_by_name = True


T = TypeVar('T')

class APIResponse(BaseModelWithConfig, Generic[T]):
    """Standard API response structure"""
    code: int = 0  # 0 for success, 1 for failure
    msg: str = "success"
    data: Optional[T] = None


class ResourceItem(BaseModelWithConfig):
    """Model for resource details."""
    gpu_type: str = Field(..., alias="gpuType")
    region_id: int = Field(..., alias="regionId")
    max_gpu_num: int = Field(..., alias="maxGpuNum")

class ResourceResponse(BaseModelWithConfig):
    """Model for resource details."""
    resource: list[ResourceItem]

class InstanceCreateResponse(BaseModelWithConfig):
    """Model for instance record details."""
    app_id: str = Field(..., alias="appId") # instance id in OnethinaAI platform
    group_id: str = Field(..., alias="groupId")

class CustomPortWithSubDomain(BaseModelWithConfig):
    local_port: int = Field(..., alias="localPort")
    type: str  # http or tcp
    sub_domain: str = Field(..., alias="subDomain")
    
class InstanceItem(BaseModelWithConfig):
    """Model for instance details."""
    app_image_id: int = Field(..., alias="appImageId")
    app_image_name: str = Field(..., alias="appImageName")
    app_image_author: str = Field(..., alias="appImageAuthor")
    app_image_version: str = Field(..., alias="appImageVersion")
    bill_type: int = Field(..., alias="billType")
    err_code: int = Field(..., alias="errCode")
    system_disk_size: int = Field(..., alias="systemDiskSize")
    system_disk_size_used: float = Field(..., alias="systemDiskSizeUsed")
    gpu_type: str = Field(..., alias="gpuType")
    app_id: str = Field(..., alias="appId")
    pre_price: float = Field(..., alias="prePrice")
    price: float = Field(..., alias="price")
    region_id: int = Field(..., alias="regionId")
    status: int = Field(..., alias="status")
    web_ui_address: str = Field(..., alias="webUIAddress")
    created_at: int = Field(..., alias="createdAt")
    stopped_at: int = Field(..., alias="stoppedAt")
    expired_at: int = Field(..., alias="expiredAt")
    started_at: int = Field(..., alias="startedAt")
    runtime: float = Field(..., alias="runtime")
    custom_port: list[CustomPortWithSubDomain] = Field(..., alias="customPort")

class InstanceResponse(BaseModelWithConfig):
    """Model for instance list response."""
    list: list[InstanceItem]


class WalletDetailResponse(BaseModelWithConfig):
    """Model for wallet/account balance details."""
    available_balance: float = Field(..., alias="availableBalance") # Available balance after deducting instance reservations
    available_voucher_cash: float = Field(..., alias="availableVoucherCash")  # Available voucher amount after deducting instance reservations  
    consume_cash_total: float = Field(..., alias="consumeCashTotal")  # Total consumption amount

class WalletConsume(BaseModelWithConfig):
    """Model for individual wallet consumption record."""
    order_id: str = Field(..., alias="orderId")
    date: datetime = Field(..., alias="date")
    app_id: str = Field(..., alias="appId")
    consum_cash: float = Field(..., alias="consumCash")
    voucher_deduct_cash: float = Field(..., alias="voucherDeductCash")
    actual_pay_cash: float = Field(..., alias="actualPayCash")
    business_type: int = Field(..., alias="businessType")
    bill_type: int = Field(..., alias="billType")
    runtime: int = Field(..., alias="runtime")
    event: str = Field(..., alias="event")
    total_discount_price: float = Field(..., alias="totalDiscountPrice")

class WalletConsumeResponse(BaseModelWithConfig):
    """Model for wallet consumption query response."""
    order_list: list[WalletConsume] = Field(..., alias="orderList") 

class PrivateImageItem(BaseModelWithConfig):
    """Model for private image details."""
    app_image_id: str = Field(..., alias="appImageId")
    image_description: str = Field(..., alias="imageDescription")
    image_name: str = Field(..., alias="imageName")
    image_status: int = Field(..., alias="imageStatus")
    image_total_size: int = Field(..., alias="imageTotalSize")
    region_id: int = Field(..., alias="regionId")
    updated_at: str = Field(..., alias="updatedAt")
    created_at: str = Field(..., alias="createdAt")
    

class PrivateImageResponse(BaseModelWithConfig):
    """Model for private image list response."""
    data: list[PrivateImageItem]
    
