"""
公共模块 应用配置

职责 从环境变量 /项目根 .env 读取数据库连接配置
使用pydantic-settings 字段名与环境变量同名 大小不敏感 环境变量优先于 .env
"""

from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    """
    全局配置 字段名与环境变量同名 大小不敏感
    """

    #----数据库----
    db_host: str = "localhost" #数据库地址 本地部署
    db_port: int = 3306        #端口
    db_user: str = "root"      #用户名
    db_password: str = "123456" #密码 并发默认
    db_name: str = "school_db" #数据库名
    db_charset: str = "utf8mb4" #字符编码

    #读取配置 优先环境变量 其次项目根 ,env 文件
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra='ignore',
    )

#模块级单例 各模块 import settings
settings = Settings()