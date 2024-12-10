from typing import Any, Dict, List, Optional, Union, TypeVar, Generic
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator

# API Parameters
class CamelCaseModel(BaseModel):
    def dict(self, *args, **kwargs) -> dict:
        # Get the original dict with by_alias=True to handle nested models
        kwargs['by_alias'] = True
        original_dict = super().dict(*args, **kwargs)
        print(original_dict)
        
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
    app_image_id: int
    bill_type: int
    gpu_num: int
    region_id: int
    gpu_type: str
    duration: int
    group_id: int
    custom_port: CustomPort

class InstanceQuery(CamelCaseModel):
    page: int
    page_size: int
    app_id: str 
    group_id: str

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
        alias_generator = lambda string: ''.join(
            word.capitalize() if i else word.lower()
            for i, word in enumerate(string.split('_'))
        )
        populate_by_name = True

T = TypeVar('T')

class APIResponse(BaseModelWithConfig, Generic[T]):
    """Standard API response structure"""
    code: int = 0  # 0 for success, 1 for failure
    msg: str = "success"
    data: Optional[T] = None


class ResourceItem(BaseModelWithConfig):
    """Model for resource details."""
    gpuType: str
    regionId: int
    maxGpuNum: int

class ResourceResponse(BaseModelWithConfig):
    """Model for resource details."""
    resource: list[ResourceItem]

class InstanceCreateResponse(BaseModelWithConfig):
    """Model for instance record details."""
    appId: str # instance id in OnethinaAI platform
    groupId: str

class CustomPortWithSubDomain(BaseModelWithConfig):
    localPort: int
    type: str  # http or tcp
    subDomain: str
    
class InstanceItem(BaseModelWithConfig):
    """Model for instance details."""
    appImageId: int
    appImageName: str
    appImageAuthor: str
    appImageVersion: str
    billType: int
    errCode: int
    systemDiskSize: int
    systemDiskSizeUsed: int
    gpuType: str
    appId: str
    prePrice: float
    price: float
    regionId: int
    status: int
    webUIAddress: str
    createdAt: int
    stoppedAt: int
    expiredAt: int
    startedAt: int
    runtime: int
    customPort: list[CustomPortWithSubDomain]

class InstanceResponse(BaseModelWithConfig):
    """Model for instance list response."""
    list: list[InstanceItem]


class WalletDetailResponse(BaseModelWithConfig):
    """Model for wallet/account balance details."""
    availableBalance: float  # Available balance after deducting instance reservations
    availableVoucherCash: float  # Available voucher amount after deducting instance reservations  
    consumeCashTotal: float  # Total consumption amount

class WalletConsume(BaseModelWithConfig):
    """Model for individual wallet consumption record."""
    orderId: str
    date: datetime
    appId: str
    consumCash: float
    voucherDeductCash: float
    actualPayCash: float
    businessType: int
    billType: int
    runtime: int
    event: str
    totalDiscountPrice: float

class WalletConsumeResponse(BaseModelWithConfig):
    """Model for wallet consumption query response."""
    orderList: list[WalletConsume]

class PrivateImageItem(BaseModelWithConfig):
    """Model for private image details."""
    appImageId: str
    imageDescription: str
    imageName: str
    imageStatus: int 
    imageTotalSize: int 
    regionId: int 
    updatedAt: str 
    createdAt: str 
    
    class Config:
        alias_generator = lambda string: ''.join(
            word.capitalize() if i else word.lower()
            for i, word in enumerate(string.split('_'))
        )
        allow_population_by_field_name = True

class PrivateImageResponse(BaseModelWithConfig):
    """Model for private image list response."""
    data: list[PrivateImageItem]
    
