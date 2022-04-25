from typing import Optional
from ninja.openapi.schema import OpenAPISchema
from ninja.openapi import get_schema
from arkid.core import routers, pages, translation, actions


def get_openapi_schema(self, path_prefix: Optional[str] = None) -> OpenAPISchema:
    if path_prefix is None:
        path_prefix = self.root_path
    schema = get_schema(api=self, path_prefix=path_prefix)
    schema["routers"] = routers.get_global_routers()
    schema["pages"] = pages.get_global_pages()
    schema["navs"] = actions.get_nav_actions()
    # permissions = get_permissions(self)
    # schema["permissions"] = permissions
    
    schema["translation"] = translation.lang_maps
    
    return schema