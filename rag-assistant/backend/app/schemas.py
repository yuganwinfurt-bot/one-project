from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    knowledge_base_ids: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("项目名称不能为空")
        return value


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=60)
    knowledge_base_ids: list[str] | None = None


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    description: str = Field(default="", max_length=240)

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("知识库名称不能为空")
        return value


class AgentRetrieveRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    knowledge_base_ids: list[Annotated[str, Field(min_length=1, max_length=64)]] = Field(
        min_length=1, max_length=20
    )
    top_k: int = Field(default=4, ge=1, le=20)
    product_ids: list[int] | None = Field(default=None, max_length=5000)
    doc_types: list[Annotated[str, Field(min_length=1, max_length=40)]] | None = Field(default=None, max_length=30)
    knowledge_base_name: str | None = Field(default=None, max_length=60)

    @field_validator("doc_types")
    @classmethod
    def validate_doc_types(cls, value):
        if value is not None and any(item not in ECOMMERCE_DOC_TYPES for item in value):
            raise ValueError("不支持的电商资料类型")
        return list(dict.fromkeys(value)) if value else None

    @field_validator("query")
    @classmethod
    def trim_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("检索问题不能为空")
        return value


ECOMMERCE_DOC_TYPES = {
    "product", "review", "order", "review_reply", "after_sale", "after_sale_message", "after_sale_risk",
    "diagnosis_report", "alert", "platform_log", "agent_run", "agent_step", "agent_feedback",
    "user_summary", "address_summary", "cart_item", "favorite", "direct_conversation", "direct_message",
    "customer_notice", "shipment_notice", "review_notice", "staff_notice", "platform_feature",
    "inventory_state", "restock_notice",
    "cart_variant", "brand", "catalog_category", "faq", "search_keyword", "advertisement", "topic", "coupon", "group_rule", "mall_notice", "role_definition", "mall_setting", "product_catalog", "customer_footprint", "customer_search", "mall_feedback", "coupon_claim", "coupon_stock", "order_promotion", "group_purchase", "group_member", "staff_permission", "region_reference", "storage_file", "statistics_summary",
}


class EcommerceRecord(BaseModel):
    record_id: str = Field(min_length=1, max_length=80)
    doc_type: str = Field(min_length=1, max_length=40)
    product_id: int | None = Field(default=None, ge=1)
    source_table: str = Field(default="", max_length=80)
    source_id: str = Field(default="", max_length=80)
    review_id: int | None = Field(default=None, ge=1)
    rating: int | None = Field(default=None, ge=1, le=5)
    name: str = Field(default="", max_length=200)
    category: str = Field(default="", max_length=100)
    has_image: bool = False
    content: str = Field(min_length=1, max_length=30000)

    @field_validator("doc_type")
    @classmethod
    def allowed_type(cls, value):
        if value not in ECOMMERCE_DOC_TYPES:
            raise ValueError("不支持的电商业务记录类型")
        return value


class EcommerceSyncRequest(BaseModel):
    records: list[EcommerceRecord] = Field(min_length=1, max_length=100000)


class SupportRecord(BaseModel):
    record_id: str = Field(min_length=1, max_length=80)
    doc_type: Literal["support_knowledge", "support_overview", "support_category", "support_keyword", "support_gap", "support_escalation", "support_rules"]
    source_table: str = Field(default="", max_length=80)
    source_id: str = Field(default="", max_length=80)
    name: str = Field(default="", max_length=200)
    category: str = Field(default="", max_length=100)
    content: str = Field(min_length=1, max_length=30000)


class SupportSyncRequest(BaseModel):
    records: list[SupportRecord] = Field(min_length=1, max_length=100000)


class ChatCreate(BaseModel):
    scope_mode: Literal["project", "custom"] = "project"
    knowledge_base_ids: list[str] | None = None


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=12000)
    knowledge_base_ids: list[str] | None = None

    @field_validator("content")
    @classmethod
    def trim_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("问题不能为空")
        return value


class ChatUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=80)
    scope_mode: Literal["project", "custom"] | None = None
    knowledge_base_ids: list[str] | None = None
