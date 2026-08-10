"""
公共模块 统一响应

职责：
-统一的成功响应
-错误响应由 common/exception.py 全局异常处理器统一生成  无需在此处理

设计说明
-全系统接口统一 envelope 前端按code ==0 判定成功
-各业务的router 成功返回一律通过 success() 包装 保证格式一致
"""

def success(data=None,msg = "成功"):
    """
    统一的成功响应
    :param data: 响应数据 可为dict/list/None
    :param msg:  提示信息 默认成功
    :return:
    """
    return {"code":0,"msg":msg,"data":data}