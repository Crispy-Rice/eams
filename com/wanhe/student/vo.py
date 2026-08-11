# 数据校验 + 类型转换
# BaseModel 定义请求参数结构、自动校验数据格式
# Field 给字段设置必填、范围、默认值
from pydantic import BaseModel, Field

class StudentCreate(BaseModel):
    '''
    创建学生信息时的参数结构和字段设置
    '''
    name: str = Field(...,max_length=50,description='姓名')
    gender: str = Field('男', max_length=10, description="性别")
    age: int = Field(..., ge=10, le=100, description="年龄")
    grade: str = Field('高一', max_length=20, description="年级")
    class_id: int = Field(None, description="班级ID（可空，稍后分班）")
    teacher_id: int = Field(None, description="教师ID（可空，稍后选老师）")
    enrollment_date: str = Field('2025-09-01', description="入学日期 YYYY-MM-DD")

class StudentUpdate(BaseModel):
    '''
    修改学生信息时的参数结构和字段设置
    '''
    name: str = Field(..., max_length=50, description="姓名")
    gender: str = Field('男', max_length=10, description="性别")
    age: int = Field(..., ge=10, le=100, description="年龄")
    grade: str = Field('高一', max_length=20, description="年级")

class ClassAssign(BaseModel):
    '''
    选择班级时的参数结构和字段设置
    '''
    class_id: int = Field(..., description="目标班级ID")

class TeacherAssign(BaseModel):
    '''
    选择老师时的参数结构和字段设置
    '''
    teacher_id: int = Field(..., description="目标教师ID")

class GardeChoose(BaseModel):
    '''
    通过年级筛选学生
    '''
    garde: str | None = None

class StudentStatus(BaseModel):
    '''
    学籍状态管理
    '''
    status: str = Field(..., description="在读，休学，复学，退学")