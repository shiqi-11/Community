from django import forms
from django.core.exceptions import ValidationError
# 使用 raise 抛出异常时，需要提供异常类的实例
# 创建异常类的实例需要提供字符串作为异常提示信息
# ugettext_lazy 就是对异常信息进行翻译处理的函数
from django.utils.translation import ugettext_lazy as _

from .models import User


def forbidden_username_validator(value):
    """检查用户名是否属于禁用词集合
    """

    forbidden_usernames = {
        'admin', 'settings', 'news', 'about', 'help', 'signin', 'signup',
        'signout', 'terms', 'privacy', 'cookie', 'new', 'login', 'logout',
        'administrator', 'join', 'account', 'username', 'root', 'blog',
        'authentication', 'users', 'billing', 'subscribe', 'reviews', 'review',
        'blogs', 'edit', 'mail', 'email', 'home', 'job', 'jobs', 'contribute',
        'newsletter', 'shop', 'profile', 'register', 'authentication',
        'campaign', '.env', 'delete', 'remove', 'forum', 'forums',
        'download', 'downloads', 'contact', 'blogs', 'feed', 'feeds', 'faq',
        'intranet', 'log', 'registration', 'search', 'explore', 'rss',
        'support', 'status', 'static', 'media', 'setting', 'css', 'js',
        'follow', 'activity', 'questions', 'articles', 'network',
    }

    if value.lower() in forbidden_usernames:
        raise ValidationError('This is a reserved word.')

def invalid_username_validator(value):
    """检查用户名是否包含非法字符
    """

    if '@' in value or '+' in value or '-' in value:
        msg = _('Enter a valid username.')
        raise ValidationError(msg)


def unique_email_validator(value):
    '''验证邮箱是否已经被注册
    '''

    # 映射类的 objects 属性有很多过滤方法，俗称过滤器，filter 是常用的一个
    # 在过滤器中可以提供由属性和条件运算符用双下划线连接生成的变量作为参数名
    # 运算符 exact 为严格匹配之意，它没啥用，等同于不写
    # iexact 为不区分大小写的严格匹配
    if User.objects.filter(email__iexact=value).exists():
        msg = _('User with this Email already exists.')
        raise ValidationError(msg)

def unique_username_ignore_case_validator(value):
    """
    用户名唯一性
    """
    if User.objects.filter(username__iexact=value).exists():
        msg = _('User with this Username already exists.')
        raise ValidationError(msg)

# ModelForm 来自 django.forms.models 模块，是创建表单类的专用父类
class SignUpForm(forms.ModelForm):
    """
    A form for creating new users.
    """
    username = forms.CharField(
        # 各个字段中的 TextInput 、EmailInput 等都是 Widget 类的子类
        # Widget 定义在 django.forms.widgets 模块中
        # 每个 Widget 类的子类对应一种前端 <input type=''> 标签的 type 属性
        # 例如 TextInput 对应的是 <input type='text'>
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=30,required=True,label=_('Username'),
        help_text=_("Username may contain alphanumeric, '_' and '.' characters.")
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=_('Password'),required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=_('Confirm your password'),required=True,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True,max_length=75,label=_('Email')
    )

    # 元数据类
    class Meta:
        # 表单对应的映射类
        model = User
        # 排除以下几个属性
        exclude = ['last_login', 'date_joined', '哈哈']
        # 包括以下几个属性
        fields = ['username', 'email', 'password', 'confirm_password']

    def __init__(self, *args, **kwargs):
        """
        验证表单数据合法性
        """
        super(SignUpForm, self).__init__(*args, **kwargs)
        # self.fields 是一个有序字典对象
        # 它的 key 值就是元数据类的 fields 列表里那几个字符串
        # value 值就是对应的各种字段的值，CharField 、EmailField 等类的实例
        # 这些 value 都有 validators 属性，属性值为列表，里面是各种验证器
        self.fields['username'].validators += [
            forbidden_username_validator, invalid_username_validator,
            unique_username_ignore_case_validator,
        ]
        self.fields['email'].validators += [
            unique_email_validator,
        ]


    def clean_password(self):
        '''
        验证两次输入密码是否一致
        '''
        # self.cleaned_data 属性是字典对象，key 是 self.fields 的 key
        # value 是 self.fields 的 value 经过表单验证器验证和格式转换的值
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            msg = _('Passwords don\'t match.')
            self.add_error('confirm_password', msg)

        return password

    def clean(self):
        self.clean_password()
        # 调用父类的 clean 方法，返回值是 self.cleaned_data 字典
        super(SignUpForm, self).clean()

    def save(self, commit=True):
        """
        保存前的操作
        """
        # 此处调用的是 django.forms.models 模块中 BaseModelForm 类的 save 方法
        # 该类为当前表单类的父类，而且该类有个 instance 属性
        # 此 instance 属性值为当前类的元数据类 Meta 中的 model 属性值的调用
        # 也就是 User 映射类的实例
        # 该 save 方法会调用 self.instance.save() 方法将映射类实例保存至数据库
        # 这里有个 commit 参数，其值为布尔值，用来决定要不要把实例保存到数据库
        # 如果还有一些非空字段没添加数据或者有需要额外处理的字段
        # 就设置该参数为 False ，后面再处理一下，最后再 save 一次
        # 该 commit 参数的默认值为 True
        user = super().save(commit=False)
        # 这个 set_password 方法来自 user 所属类 User 的父类 AbstractBaseUser
        # 此方法的作用是为密码字符串创建哈希值，并保存原密码至 _password 属性上
        user.set_password(self.cleaned_data['password'])
        # 这个 save 是 AbstractBaseUser 类中的方法
        # 调用此方法时，如果保存数据成功，会将 _password 属性赋值为 None
        user.save()
        return user
