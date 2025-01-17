# API

ArkID基于Django-ninja框架来开发API，完整继承了其所有能力。

## 自定义API

可以通过**Django-ninja**与 **Django原生** 两种方式来自定义API。

主要区别在于，Django-ninja方式定义会自动出现在openapi.json中,并依赖Schema，Django原生则不会或不需要。

### Django-ninja 的 API 定义方式

使用 [arkid.core.extension.Extension.register_api](../%20插件基类/#arkid.core.extension.Extension.register_api)


#### 创建Schema

使用 [arkid.core.extension.create_extension_schema](../%20插件基类/#arkid.core.extension.create_extension_schema)

注意！该函数的第二个参数，是指的插件的 \_\_init\_\_.py 文件所在的目录

```py title='示例'
from arkid.core import extension

class CaseExtension(extension.Extension): 
    def load(self): 
        super().load()
        
        self.register_api('/path/', 'GET', self.api_func)

    def api_func(self, request):
        pass
```
#### 权限
{todo}

#### 分页

arkid提供基础分页器功能，其使用方法如下：

``` py title="分页"
...
from ninja.pagination import paginate #引入分页装饰器
from arkid.core.pagenation import CustomPagination #引入分页器
...


# 声明返回列表项结构
class AppGroupListItemOut(Schema):
    id:str
    name:str
# 声明返回结构体
class AppGroupListOut(ResponseSchema):
    data: List[AppGroupListItemOut]

@api.get("/path/", response=List[AppGroupListItemOut]) #注意 此处因分页器会自动封装错误提示等数据  故而此处不需要填写封装错误信息后的Schema
@operation(AppGroupListOut)
@paginate(CustomPagination)
def get_app_groups(request,tenant_id: str):
    """ 应用分组列表
    """
    groups = AppGroup.expand_objects.filter(tenant__id=tenant_id)
    parent_id = query_data.dict().get("parent_id",None)
    groups = groups.filter(parent__id=parent_id)
    return groups.all()
```





### Django 的 API 定义方式

使用 [arkid.core.extension.Extension.register_routers](../%20插件基类/#arkid.core.extension.Extension.register_routers)

```py title='示例'
from arkid.core import extension
from django.urls import re_path
from django

class CaseExtension(extension.Extension): 
    def load(self): 
        super().load()
        
        class CaseView(View):
            def post(self,request):
                pass

        path_list = [
            re_path(rf'^/path/$',self.api_func),
            re_path(rf'^/path2/$',CaseView.as_view()),
        ]
        self.register_routers(path_list)

    def api_func(self,request):
        pass
```
## 修改内核API

必要的时候，我们需要更改原内核中的API。

### 修改request

修改request，就是修改API相关的Request Schema.

之后，我们希望获取该request，并执行自定义的逻辑.

在每个API响应之前，都会抛出一个事件，事件tag为: **operation_id + '_pre'**, 侦听该事件即可获取request对象

!!! 提示
    operation_id 可以在 openapi.json 中查找

使用 

* [arkid.core.extension.Extension.register_extend_api](../%20插件基类/#arkid.core.extension.Extension.register_extend_api)
* [arkid.core.extension.Extension.listen_event](../%20插件基类/#arkid.core.extension.Extension.listen_event)


```py title='示例'
from arkid.core import extension
from api.v1.views.app import AppConfigSchemaIn

class CaseExtension(extension.Extension): 
    def load(self): 
        super().load()
        
        self.register_extend_api(AppConfigSchemaIn, case1=str, case2=(str, Field(title='case2_name')))
        self.listen_event('api_v1_views_app_list_apps_pre',self.app_list_pre_handler)

    def app_list_pre_handler(self,event,**kwargs):
        print(event.request.case1)
        print(event.request.case2)
```

### 修改response

修改response，除了要修改Response Schema以外，还需要真的改变最终的返回值

在每个API响应完毕之后，也会抛出一个事件，事件的tag为 operation_id， 侦听该事件并修改事件中的reponse即可。

使用 

* [arkid.core.extension.Extension.register_extend_api](../%20插件基类/#arkid.core.extension.Extension.register_extend_api)
* [arkid.core.extension.Extension.listen_event](../%20插件基类/#arkid.core.extension.Extension.listen_event)

```py title='示例'
from arkid.core import extension
from api.v1.views.app import AppConfigSchemaOut

class CaseExtension(extension.Extension): 
    def load(self): 
        super().load()
        
        self.register_extend_api(AppConfigSchemaOut, case1=str, case2=(str, Field(title='case2_name')))
        self.listen_event('api_v1_views_app_list_apps',self.app_list_handler)

    def app_list_pre_handler(self,event,**kwargs):
        event.response['case1'] = 'case1'
        event.response['case2'] = 'case2'
```