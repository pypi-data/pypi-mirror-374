from pydantic import BaseModel, Field
from .resource.config import ConfigMixin as ResourceConfigMixin


class Config(ResourceConfigMixin):
    pass


class ConfigMixin(BaseModel):
    infra: Config = Field(..., description="Infra config")
