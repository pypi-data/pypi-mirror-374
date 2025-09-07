from datetime import datetime
from pydantic import BaseModel

class NocoDBConfig(BaseModel):
    nocodb_project_id: str
    nocodb_categories_table: str
    nocodb_products_table: str
    nocodb_orders_table: str
    nocodb_status_table: str
    nocodb_bot_commands_table: str
    nocodb_options_table: str | None
    nocodb_options_category_table: str | None

class ShopDetailsModel(BaseModel):
    shop_id: str
    shop_name: str
    friendly_name: str
    shop_language: str
    shop_api_url: str
    contact_phone: str | None
    contact_email: str
    orders_chat_id: int
    orders_history_chat_id: int | None
    search_enabled: bool | None
    warehouse_accounting: bool
    bot_url: str | None
    bot_token: str
    payment_token: str | None
    placeholder: str
    order_process: str
    nocodb_config: NocoDBConfig | None
    topic_chat_id: int | None
    premium_expiration_date: datetime | None
    web_app_url: str
