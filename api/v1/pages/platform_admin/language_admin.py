from arkid.core.translation import gettext_default as _
from arkid.core import routers, pages, actions

tag = 'language_admin'
name = '语言包管理'

page = pages.TablePage(tag = tag, name = name)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='language',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/languages/',
        method=actions.FrontActionMethod.GET,
    ),
)