from pydantic import BaseModel,Field

class TeacherCreate(BaseModel):
    '''
    新增教师请求体
    '''
    name:str=Field(max_length=50,min_length=0,description='姓名')
    gender:str=Field('女',max_length=5,description='性别')
    age:int=Field(...,ge=20,le=75,description='年龄')
    subject:str=Field(max_length=20,description='教授学科')
    phone:str=Field(...,max_length=50,min_length=0,description='电话号码')

class TeacherUpdate(BaseModel):
    '''
    修改教师请求体
    '''
    name: str = Field(max_length=50, min_length=0, description='姓名')
    gender: str = Field('女', max_length=5, description='性别')
    age: int = Field(..., ge=20, le=75, description='年龄')
    subject: str = Field(max_length=20, description='教授学科')
    phone: str = Field(..., max_length=50, min_length=0, description='电话号码')