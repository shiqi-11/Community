from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import CreateView

from .models import User
from .forms import SignUpForm


# 来自 django.views.generic.edit 模块的 CreateView 类用于创建视图类
# 该类的父类有多层，最终继承自隔壁模块 base 中的 View 类
# 这些类中有很多方法，get 、post 、delete 等用于处理同名方式的请求
# 其中还有一个 as_view 类方法用于生成视图函数处理客户端发来的请求
# 此方法在当前应用的 urls.py 文件的 urlpatterns 列表中被调用
class UserSignupView(CreateView):
    """
    用户注册
    """
    model = User
    # CreateView 的一个父类是同模块中的 FormMixin
    # 后者有一个 get_form 方法用于创建表单类的实例，此方法的参数就是 form_class
    form_class = SignUpForm
    # 该属性用于提供模板文件，也是在父类的方法中被调用
    template_name = 'authentication/signup.html'

    # 如果客户端发来的是 post 请求，会调用从父类继承的 post 方法处理
    # 表单数据通过了全部验证后，会自动调用 form_valid 方法进行最后的处理
    # 参数 form 是用于用户注册的表单类 SignUpForm 的实例
    def form_valid(self, form):
        # save 方法是在当前应用的 forms.py 文件的 SignUpForm 表单类中定义的
        # 此方法的作用是创建映射类 User 的实例并添加属性
        # 调用实例的 save 方法保存用户信息到数据库，最后返回实例对象
        user = form.save()
        # 这是在 django/contrib/auth/__init__.py 文件中定义的函数
        # 它使得用户处于登录状态
        login(self.request, user)
        # 使用 redirect 方法重定向到主页，参数字符串有两种方式
        # 一种是来自 urlpatterns 列表的 path 函数的 name 参数值
        # 另一种是直接写 URL 路径，例如 http://haha.com/abc ，这里就写 '/abc'
        # 参数除了可以是字符串，还可以是映射类实例
        # 后一种需要在映射类中定义 get_asbolute_url 方法
        # 此 redirect 方法的返回值是 HttpResponseRedirect 类的实例
        # 此类在 django.http.response 模块中被定义
        # 执行完这行代码，视图类就把返回响应的工作交给参数字符串所在的 path
        return redirect('home')
