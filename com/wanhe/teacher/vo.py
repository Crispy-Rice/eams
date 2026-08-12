# 文件名：teacher/vo.py
"""
教师模块 - 请求 VO

职责：定义教师新增/修改请求体的字段与校验规则
依赖：pydantic（BaseModel / Field / computed_field）
"""
from pydantic import BaseModel, Field, computed_field


def _resolve_gangwei(score: float) -> str:
    """根据评教分数自动生成岗位：>=85 分为班主任，否则为任课教师"""
    return "班主任" if score >= 85 else "任课教师"


class TeacherCreate(BaseModel):
    """新增教师请求体"""
    name: str = Field(..., max_length=50, description="姓名")
    gender: str = Field('男', max_length=10, description="性别")
    age: int = Field(..., ge=20, le=70, description="年龄")
    subject: str = Field(..., max_length=50, description="教授科目")
    phone: str = Field('', max_length=20, description="联系电话")
    score: float = Field(0, ge=0, le=100, description="教师评教分数")

    @computed_field
    @property
    def gangwei(self) -> str:
        """岗位：根据评教分数自动生成（>=85 班主任，否则任课教师）"""
        return _resolve_gangwei(self.score)


class TeacherUpdate(BaseModel):
    """修改教师信息请求体（字段与新增一致）"""
    name: str = Field(..., max_length=50, description="姓名")
    gender: str = Field('男', max_length=10, description="性别")
    age: int = Field(..., ge=20, le=70, description="年龄")
    subject: str = Field(..., max_length=50, description="教授科目")
    phone: str = Field('', max_length=20, description="联系电话")
    score: float = Field(..., ge=0, le=100, description="教师评教分数")

    @computed_field
    @property
    def gangwei(self) -> str:
        """岗位：根据评教分数自动生成（>=85 班主任，否则任课教师）"""
        return _resolve_gangwei(self.score)
