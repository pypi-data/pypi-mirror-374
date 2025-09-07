from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from shop_system_models.shared import ListResponseModel


class ScrappingPayload(BaseModel):
    website_url: str
    business_description: Optional[str] = None


class ScrappingJobStatus(str, Enum):
    started = 'started'
    completed = 'completed'
    failed = 'failed'

class ScrappingJob(ScrappingPayload):
    workflow_id: str
    research_url: Optional[str] = None
    status: ScrappingJobStatus
    created_at: datetime
    updated_at: datetime


class ScrappingJobResponse(ScrappingJob):
    id: str


class JobListResponseModel(ListResponseModel):
    jobs: List[ScrappingJobResponse]