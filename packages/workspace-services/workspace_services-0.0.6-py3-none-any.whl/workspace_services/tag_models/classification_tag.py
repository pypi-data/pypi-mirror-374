from workspace_services.tag_models.tag_base import TagBase


class ClassificationTag(TagBase):
    classification: int | list[int] | None = None
