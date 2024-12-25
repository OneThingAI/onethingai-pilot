from typing import Any, Dict, List, Optional, Union, TypeVar, Generic
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator
from pydantic.alias_generators import to_snake


class BillType(Enum):
    MONTHLY_SUBSCRIPTION = 1
    DAILY_SUBSCRIPTION = 2
    PAY_AS_YOU_GO = 3


class BusinessType(Enum):
    INSTANCE_USAGE = 1
    IMAGE_STORAGE = 2
    FILE_STORAGE = 3
    INSTANCE_EXPANSION = 4

class InstanceStatus(Enum):
    DEPLOYING = 100
    STARTING = 200
    RUNNING = 300
    STOPPING = 400
    RESETTING = 500
    CHANGING_IMAGE = 600
    RELEASING = 700
    STOPPED = 800

class PrivateImageStatus(Enum):
    SAVING = 1  # 私有镜像正在保存中
    SUCCESS = 4  # 私有镜像保存成功
    FAILED = 5  # 私有镜像保存失败

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


class QueryPrivateImage(CamelCaseModel):
    region_id: Optional[int] = None
    app_image_name: Optional[str] = None


class QueryPublishImage(CamelCaseModel):
    app_image_name: Optional[str] = None
    app_image_author: Optional[str] = None


class QueryResources(CamelCaseModel):
    app_image_id: str 
    gpu_type: Optional[str] = None
    region_id: Optional[int] = None


class CustomPort(CamelCaseModel):
    local_port: int
    type: str = "http" #http or tcp


class InstanceConfig(CamelCaseModel):
    app_image_id: str
    bill_type: Union[int, BillType] = BillType.PAY_AS_YOU_GO
    gpu_num: int
    region_id: int
    gpu_type: str
    duration: Optional[int] = None
    group_id: Optional[str] = None
    custom_port: Optional[list[CustomPort]] = []

    @validator('bill_type')
    def validate_bill_type(cls, v):
        if isinstance(v, BillType):
            return v.value
        return v

class QueryInstances(CamelCaseModel):
    page: int
    page_size: int
    app_id: Optional[str] = None
    group_id: Optional[str] = None


class QueryMetrics(CamelCaseModel):
    start_time: int
    end_time: int


class QueryBill(CamelCaseModel):
    """Model for consumption query parameters."""
    page: int = Field(..., gt=0, description="Page number")
    page_size: int = Field(..., gt=0, le=100, description="Items per page, must be between 1 and 100")
    app_id: Optional[str] = Field(None, description="Instance ID")
    business_type: Optional[Union[int, BusinessType]] = Field(None, description="Transaction type")

    @validator('page_size')
    def validate_page_size(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('page_size must be between 1 and 100')
        return v

    @validator('business_type')
    def validate_business_type(cls, v):
        if isinstance(v, BusinessType):
            return v.value
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


class Pagination(BaseModelWithConfig):
    """Model for pagination details."""
    page: int
    page_size: int = Field(..., alias="pageSize")
    total: int
    

class PrivateImageItem(BaseModelWithConfig):
    """Model for private image details."""
    app_image_id: str = Field(..., alias="appImageId")
    app_image_name: str = Field(..., alias="appImageName")
    app_image_description: str = Field("", alias="appImageDescription")
    app_image_status: PrivateImageStatus = Field(..., alias="appImageStatus")
    app_image_total_size: float = Field(..., alias="appImageTotalSize")
    region_id: int = Field(..., alias="regionId")
    updated_at: int = Field(..., alias="updatedAt")
    created_at: int = Field(..., alias="createdAt")

    @validator('app_image_status')
    def validate_app_image_status(cls, v):
        if isinstance(v, int):
            return PrivateImageStatus(v)
        return v

class PrivateImageList(BaseModelWithConfig):
    """Model for private image list response."""
    private_image_list: list[PrivateImageItem] = Field(..., alias="privateImageList")


class PublishImageItem(BaseModelWithConfig):
    """Model for published image details."""
    app_image_id: str = Field(..., alias="appImageId")
    app_image_name: str = Field(..., alias="appImageName")
    app_image_description: str = Field(..., alias="appImageDescription")
    app_image_author: str = Field(..., alias="appImageAuthor")
    app_image_version: str = Field(..., alias="appImageVersion")
    created_at: int = Field(..., alias="createdAt")
    updated_at: int = Field(..., alias="updatedAt")

class PublishImageList(BaseModelWithConfig):
    """Model for published image list response."""
    publish_image_list: list[PublishImageItem] = Field(..., alias="publishImageList") 


class ResourceItem(BaseModelWithConfig):
    """Model for resource details."""
    gpu_type: str = Field(..., alias="gpuType")
    region_id: int = Field(..., alias="regionId")
    max_gpu_num: int = Field(..., alias="maxGpuNum")


class ResourceList(BaseModelWithConfig):
    """Model for resource list response."""
    resource_list: list[ResourceItem] = Field(..., alias="resourceList")


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
    app_id: str = Field(..., alias="appId")
    app_image_id: str = Field(..., alias="appImageId")
    app_image_name: str = Field(..., alias="appImageName")
    app_image_author: str = Field(..., alias="appImageAuthor")
    app_image_version: str = Field(..., alias="appImageVersion")
    bill_type: BillType = Field(..., alias="billType")
    created_at: int = Field(..., alias="createdAt")
    custom_name: str = Field("", alias="customName")
    custom_port: list[CustomPortWithSubDomain] = Field(default_factory=list, alias="customPort")
    err_code: int = Field(..., alias="errCode")
    expired_at: int = Field(..., alias="expiredAt")
    gpu_type: str = Field(..., alias="gpuType")
    group_id: str = Field(..., alias="groupId")
    pre_price: float = Field(..., alias="prePrice")
    price: float = Field(..., alias="price")
    region_id: int = Field(..., alias="regionId")
    runtime: float = Field(..., alias="runtime")
    started_at: int = Field(..., alias="startedAt")
    status: InstanceStatus = Field(..., alias="status")
    stopped_at: int = Field(..., alias="stoppedAt")
    system_disk_size: int = Field(..., alias="systemDiskSize")
    system_disk_size_used: float = Field(..., alias="systemDiskSizeUsed")
    web_ui_address: str = Field(..., alias="webUIAddress")

    @validator('bill_type')
    def validate_bill_type(cls, v):
        if isinstance(v, int):
            return BillType(v)
        return v

    @validator('status', pre=True)
    def validate_status(cls, v):
        if isinstance(v, int):
            return InstanceStatus(v)
        return v


class InstanceList(BaseModelWithConfig):
    """Model for instance list response."""
    app_list: list[InstanceItem] = Field(..., alias="appList")
    pagination: Pagination = Field(..., alias="pagination")


class WalletDetail(BaseModelWithConfig):
    """Model for wallet/account balance details."""
    available_balance: float = Field(..., alias="availableBalance") # Available balance after deducting instance reservations
    available_voucher_cash: float = Field(..., alias="availableVoucherCash")  # Available voucher amount after deducting instance reservations  
    consume_cash_total: float = Field(..., alias="consumeCashTotal")  # Total consumption amount

class OrderItem(BaseModelWithConfig):
    """Model for individual bill/order record."""
    actual_pay_cash: float = Field(..., alias="actualPayCash")
    app_id: str = Field("", alias="appId")
    bill_type: BillType = Field(..., alias="billType")
    business_type: BusinessType = Field(..., alias="businessType")
    consume_cash: float = Field(..., alias="consumeCash")
    created_at: int = Field(..., alias="createdAt")
    event: str = Field("", alias="event")
    order_id: str = Field(..., alias="orderId")
    runtime: int = Field(..., alias="runtime")
    total_discount_price: float = Field(..., alias="totalDiscountPrice")
    voucher_deduct_cash: float = Field(..., alias="voucherDeductCash")

    @validator('bill_type')
    def validate_bill_type(cls, v):
        if isinstance(v, int):
            return BillType(v)
        return v

    @validator('business_type')
    def validate_business_type(cls, v):
        if isinstance(v, int):
            return BusinessType(v)
        return v


class OrderList(BaseModelWithConfig):
    """Model for bill/order list response."""
    order_list: list[OrderItem] = Field(..., alias="orderList")
    pagination: Pagination = Field(..., alias="pagination")
