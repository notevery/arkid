from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'third_auth'
name = '第三方认证'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑第三方认证"))


pages.register_front_pages(page)
pages.register_front_pages(edit_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/third_auths/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/third_auths/',
        )
    },
    local_actions={
        "edit": actions.EditAction(
            page=edit_page,
        ),
        "delete":actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/third_auths/{id}/",
        )
    },
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/third_auths/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/third_auths/{id}/"
        ),
    }
)

