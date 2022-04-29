from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'permission_sync'
name = '权限同步'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑权限同步配置"))


pages.register_front_pages(page)
pages.register_front_pages(edit_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permission_syncs/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions=[
        actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/permission_syncs/',
        )
    ],
    local_actions=[
        actions.DirectAction(
            name=_("同步"),
            method=actions.FrontActionMethod.GET,
            path="/api/v1/tenant/{tenant_id}/permission_syncs/{id}/sync/",
        ),
        actions.EditAction(
            page=edit_page,
        ),
        actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/permission_syncs/{id}/",
        )
    ],
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permission_syncs/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions=[
        actions.ConfirmAction(path="/api/v1/tenant/{tenant_id}/permission_syncs/{id}/"),

    ]
)


