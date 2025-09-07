from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from shop_system_models.shared import ListResponseModel as ListResponseModel

class ScrappingPayload(BaseModel):
    website_url: str
    business_description: str | None

class ScrappingJobStatus(str, Enum):
    started = 'started'
    completed = 'completed'
    failed = 'failed'

class ScrappingJob(ScrappingPayload):
    workflow_id: str
    research_url: str | None
    status: ScrappingJobStatus
    created_at: datetime
    updated_at: datetime

class ScrappingJobResponse(ScrappingJob):
    id: str

class JobListResponseModel(ListResponseModel):
    jobs: list[ScrappingJobResponse]
