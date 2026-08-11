import logging

# APIRouter 导入路由管理器
# HTTPException 异常抛出工具
from fastapi import APIRouter, HTTPException

from com.wanhe.student.model import StudentModel
from com.wanhe.student.vo import StudentCreate, StudentUpdate, ClassAssign, TeacherAssign
from com.wanhe.classes.model import ClassModel
from com.wanhe.teacher.model import TeacherModel
from com.wanhe.common.response import success

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/students", tags=["学生模块"])


@router.get("/all")
def list_students(keyword: str = ""):
    return success(StudentModel().get_all(keyword))


@router.get("/page")
def list_students_page(keyword: str = "", page: int = 1, page_size: int = 10):
    return success(StudentModel().get_page(keyword, page, page_size))


@router.get("/one/{student_id}")
def get_student(student_id: int):
    if StudentModel().get_by_id(student_id) is None:
        # raise 主动抛出异常
        raise HTTPException(status_code=404, detail="学生不存在")
    return success(StudentModel().get_by_id(student_id))


@router.post("/add")
def add_student(data: StudentCreate):
    if data.class_id and ClassModel().get_by_id(data.class_id) is None:
        raise HTTPException(status_code=404, detail="班级不存在")
    if data.teacher_id and TeacherModel().get_by_id(data.teacher_id) is None:
        raise HTTPException(status_code=404, detail="教师不存在")

    new_id = StudentModel().create(
        name=data.name,
        gender=data.gender,
        age=data.age,
        grade=data.grade,
        class_id=data.class_id,
        teacher_id=data.teacher_id,
        enrollment_date=data.enrollment_date,
    )
    logger.info("新增学生 id:%s 姓名:%s", new_id, data.name)
    return success({"id": new_id}, msg="新增成功")


@router.put("/update/{student_id}")
def update_student(student_id: int, data: StudentUpdate):
    if StudentModel().get_by_id(student_id) is None:
        raise HTTPException(status_code=404, detail="学生不存在")
    StudentModel().update(student_id, data.name, data.gender, data.age, data.grade)
    logger.info("修改学生 id:%s", student_id)
    return success(msg="修改成功")


@router.put("/assign-class/{student_id}")
def assign_class(student_id: int, data: ClassAssign):
    if StudentModel().get_by_id(student_id) is None:
        raise HTTPException(status_code=404, detail="学生不存在")
    if ClassModel().get_by_id(data.class_id) is None:
        raise HTTPException(status_code=404, detail="班级不存在")
    StudentModel().change_class(student_id, data.class_id)
    logger.info("学生分班 id:%s → 班级%s", student_id, data.class_id)
    return success(msg="分班成功")


@router.put("/assign-teacher/{student_id}")
def assign_teacher(student_id: int, data: TeacherAssign):
    if StudentModel().get_by_id(student_id) is None:
        raise HTTPException(status_code=404, detail="学生不存在")
    if TeacherModel().get_by_id(data.teacher_id) is None:
        raise HTTPException(status_code=404, detail="教师不存在")
    StudentModel().change_teacher(student_id, data.teacher_id)
    logger.info("学生选老师 id:%s → 教师%s", student_id, data.teacher_id)
    return success(msg="选老师成功")


@router.delete("/del/{student_id}")
def delete_student(student_id: int):
    if StudentModel().get_by_id(student_id) is None:
        raise HTTPException(status_code=404, detail="学生不存在")
    StudentModel().delete(student_id)
    logger.info("删除学生 id:%s", student_id)
    return success(msg="删除成功")

# @router.get("/list")
# def get_student_list(filter):
