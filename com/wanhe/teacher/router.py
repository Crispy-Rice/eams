from com.wanhe.teacher.model import TeacherModel
import logging
from fastapi import APIRouter
from com.wanhe.common.response import success
from com.wanhe.teacher.vo import *
from fastapi import HTTPException

logger = logging.getLogger(__name__)


router=APIRouter(prefix="/teachers",tags=["教师模块"])

@router.get('/all')
def teacher_all(keyword:str=''):
    '''
    查询所有教师
    '''
    return success(TeacherModel().get_all(keyword))

@router.get('/one/{teacher_id}')
def teacher_one(teacher_id:int):
    '''
    按id查询教师
    '''
    return success(TeacherModel().get_one(teacher_id))

@router.post('/add')
def teacher_add(data:TeacherCreate):
    '''
    新增教师
    '''
    te=TeacherModel()
    if te.exists_by_phone(data.phone):
        raise HTTPException(detatus_ccode=400,detail="该手机号已存在")
    new_id=TeacherModel().create(
        name=data.name,
        age=data.age,
        phone=data.phone,
        subject=data.subject,
        gender=data.gender,
    )
    logger.info(f"新增教师ID:{new_id},姓名:{data.name}")
    return success({"id":new_id},msg="新增成功！")

@router.put('/update/{teacher_id}')
def teacher_update(teacher_id:int,data:TeacherUpdate):
    '''
    修改教师信息
    '''
    if TeacherModel().update(teacher_id) is None:
        raise HTTPException(status_code=404,detail='教师不存在')
    TeacherModel().update(teacher_id,
                          name=data.name,
                          age=data.age,
                          phone=data.phone,
                          subject=data.subject,
                          gender=data.gender,)
    logger.info(f"修改教师ID:{teacher_id},姓名:{data.name}")
    return success(msg="修改成功！")

@router.delete('/delete/{teacher_id}')
def teacher_delete(teacher_id:int,confirm:bool):
    '''
    删除教师信息
    '''
    if not confirm:
        return success(msg="未确认删除操作,取消删除！")
    if TeacherModel().delete(teacher_id) is None:
        raise HTTPException(status_code=404,detail="教师不存在")
    TeacherModel().delete(teacher_id)
    logger.info(f"删除教师ID:{teacher_id}")
    return success(msg="删除教师成功！")

