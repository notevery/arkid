from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'user_grant'
name = '所有用户'


page = pages.TreePage(tag=tag,name=name)
user_permission_page = pages.TablePage(name=_("该用户权限"))
update_user_permission_page = pages.TablePage(name=_("更新用户权限"),select=True)

pages.register_front_pages(page)
pages.register_front_pages(user_permission_page)
pages.register_front_pages(update_user_permission_page)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/user_no_super/',
        method=actions.FrontActionMethod.GET,
    ),
    node_actions=[
        actions.CascadeAction(
            page=user_permission_page
        )
    ],
)

user_permission_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permissions?select_user_id={select_user_id}',
        method=actions.FrontActionMethod.GET
    ),
    local_actions={
        "delete": actions.DeleteAction(
            path='/api/v1/tenant/{tenant_id}/permission/user/{select_user_id}/{permission_id}/remove_permission'
        )
    },
    global_actions={
        'open': actions.OpenAction(
            name=("添加用户权限"),
            page=update_user_permission_page
        )
    }
)

update_user_permission_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permissions?select_user_id={select_user_id}',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
        'confirm':actions.ConfirmAction(
            path='/api/v1/tenant/{tenant_id}/permission/user/{select_user_id}/add_permission',
        ),
    }
)