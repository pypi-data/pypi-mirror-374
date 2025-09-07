from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from shop_system_models.shared import ListResponseModel


class ScrappingPayload(BaseModel):
    website_url: str
    business_description: Optional[str] = None


class ScrappingJobStatus(str, Enum):
    parsing_started = 'parsing_started'
    parsing_completed = 'parsing_completed'
    parsing_failed = 'parsing_failed'

    import_started = 'import_started'
    import_completed = 'import_completed'
    import_failed = 'import_failed'

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