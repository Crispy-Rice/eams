
import logging

from fastapi import APIRouter, HTTPException

from com.wanhe.teacher.model import TeacherModel
from com.wanhe.teacher.vo import TeacherCreate, TeacherUpdate
from com.wanhe.common.response import success

logger = logging.getLogger(__name__)

# 创建子路由
router = APIRouter(prefix="/teachers", tags=["教师模块"])


@router.get("/all")  # 路由装饰器：注册 GET 查询接口
def list_teachers(keyword: str = ""):
    """查：获取所有教师，可按姓名模糊查询"""
    return success(TeacherModel().get_all(keyword))


@router.get("/one/{teacher_id}")  # 路由装饰器：注册 GET 查询接口
def get_teacher(teacher_id: int):
    """查：按 ID 获取单个教师"""
    teacher = TeacherModel().get_by_id(teacher_id)
    if teacher is None:
        raise HTTPException(status_code=404, detail="教师不存在")
    return success(teacher)


@router.post("/add")  # 路由装饰器：注册 POST 新增接口
def add_teacher(data: TeacherCreate):
    """增：新增教师"""
    te = TeacherModel()
    if te.exists_by_phone(data.phone):
        raise HTTPException(status_code=400, detail="该手机号已存在")
    if data.score >= 85:
        gangwei = "班主任"
    else:
        gangwei = "任课教师"
    new_id = TeacherModel().create(
        name=data.name,
        gender=data.gender,
        age=data.age,
        subject=data.subject,
        phone=data.phone,#顺序可变
        score=data.score,
        gangwei=gangwei,


    )
    logger.info("新增教师 id:%s 姓名:%s", new_id, data.name)
    return success({"id": new_id}, msg="新增成功")


@router.put("/update/{teacher_id}")  # 路由装饰器：注册 PUT 修改接口
def update_teacher(teacher_id: int, data: TeacherUpdate):
    """改：修改教师信息"""
    if TeacherModel().get_by_id(teacher_id) is None:
        raise HTTPException(status_code=404, detail="教师不存在")
    if data.score >= 85:
        gangwei = "班主任"
    else:
        gangwei = "任课教师"
    TeacherModel().update(
        teacher_id, data.name, data.gender, data.age, data.subject, data.phone,data.score,gangwei#顺序不能变
    )
    logger.info("修改教师 id:%s", teacher_id)
    return success(msg="修改成功")


@router.delete("/del/{teacher_id}")  # 路由装饰器：注册 DELETE 删除接口
def delete_teacher(teacher_id: int):
    """删：删除教师"""
    if TeacherModel().get_by_id(teacher_id) is None:
        raise HTTPException(status_code=404, detail="教师不存在")
    TeacherModel().delete(teacher_id)
    logger.info("删除教师 id:%s", teacher_id)
    return success(msg="删除成功")
