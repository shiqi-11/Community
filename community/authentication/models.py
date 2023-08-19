from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin
)

from .manager import UserManager


# 创建普通映射类只需继承 django.db.models 模块中的 Model 类
# AbstractBaseUser 和 PermissionsMixin 是 Model 的子类
# 创建管理型用户的映射类就需要继承这两个父类
# 前者提供了一些处理用户名、邮箱和密码的相关方法
# 并且定义了 password 和 last_login 等很多字段属性
# 后者提供了创建组和权限管理所需的一些属性和方法
class User(AbstractBaseUser, PermissionsMixin):
    """
    Model to create users.
    """

    # 这里没有 password 字段，因为父类 AbstractBaseUser 中已经定义了
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    is_admin = models.BooleanField(default=False)   # 默认不是超级权限管理员
    is_staff = models.BooleanField(default=False)   # 默认不是协管员
    is_active = models.BooleanField(default=True)   # 默认是活动用户

    # 同目录下的 manager.py 文件中定义的类在这里用上了
    # UserManager 是管理器类，将其实例赋值给当前类 User 的 objects 属性
    # 映射类本身的 objects 属性就被覆盖了
    # UserManager 的实例赋值给任意变量，映射类本身的 objects 属性都会被覆盖
    objects = UserManager()

    # 该属性将作为用户的唯一标识，用户登录后
    # 在前端模板文件中可以使用 {{ user.get_username }} 来获取当前类中的属性
    # 因为在父类 AbstractBaseUser 中定义了 get_username 方法
    # 该方法的返回值就是 self.USERNAME_FIELD
    USERNAME_FIELD = 'username'
    # 在终端执行 python manage.py createsuperuser 命令创建超级用户时
    # 需要填写一些信息，首先肯定是唯一标识那个属性值
    # 除此之外，还需要填写哪些信息呢？就将属性名写到下面的列表里
    REQUIRED_FIELDS = ['email']

    # 该类的类名是固定的，用于定义模型的元数据，即除了字段之外的所有内容
    # 包括数据表名、排序方式、单数复数等，该类所有代码都是非必须的
    # 但这些代码很有用，在实际项目中肯定要用到
    class Meta:
        # 下面这俩属性用于设置前端显示的类名的单复数
        # 其实映射类每个字段也都可以添加这俩属性
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_userid(self):
        return User.objects.get(username=self.username).user_id
