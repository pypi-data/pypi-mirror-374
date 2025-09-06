from pydantic import BaseModel

from workspace_services.tag_models.tag_base import TagBase


class DetectionObject(BaseModel):
    object_type_id: int
    relative_points: list[tuple[float, float]]


class DetectionTag(TagBase):
    objects: list[DetectionObject] = []
