from django.urls import include, path
from django.contrib.auth import views as auth_views

from .views import UserSignupView

# 这个变量用于增加路由的命名空间，当前端使用 {% url %} 设置路由时
# 可以写成这样：{% url 'authentication:signup' %}
# 意为 authentication 命名空间下 name 为 signup 的 path 来处理
app_name = 'authentication'


urlpatterns = [
    # 这里使用了 django.contrib.auth.views 模块中定义的
    # 视图类提供的登录、登出功能
    path('login/', auth_views.LoginView.as_view(template_name='authentication/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', UserSignupView.as_view(), name='signup'),
]
