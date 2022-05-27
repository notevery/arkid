# 审批管理
from arkid.core.translation import gettext_default as _
from arkid.core import pages, routers, actions

tag = "mine_approve_request"
name = _("审批请求")


page = pages.TabsPage(name=name, tag=tag)
waiting_page = pages.TablePage(name='未审核')
approved_page = pages.TablePage(name='已审核')

pages.register_front_pages(page)
pages.register_front_pages(waiting_page)
pages.register_front_pages(approved_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    icon='app',
    page=page,
)

page.add_pages(
    [
        waiting_page,
        approved_page,
    ]
)

waiting_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/mine/tenant/{tenant_id}/approve_requests/?is_approved=false',
        method=actions.FrontActionMethod.GET,
    ),
)

approved_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/mine/tenant/{tenant_id}/approve_requests/?is_approved=true',
        method=actions.FrontActionMethod.GET,
    ),
)
