from pydantic import BaseModel


class TagBase(BaseModel):
    tagging_difficulty: int | None = None  # TODO: 添加难度系数机制, 获取标注员反馈
