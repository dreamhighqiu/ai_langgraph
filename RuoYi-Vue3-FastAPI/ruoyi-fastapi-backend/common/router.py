import importlib
import os
import sys
from collections.abc import Sequence
from enum import Enum
from typing import Annotated, Any, Callable, Literal, Optional, Union

from annotated_doc import Doc
from fastapi import FastAPI, params
from fastapi.datastructures import Default
from fastapi.routing import APIRoute, APIRouter
from fastapi.utils import generate_unique_id
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute
from starlette.types import ASGIApp, Lifespan
from typing_extensions import deprecated


class APIRouterPro(APIRouter):
    """
    `APIRouterPro` class, inherited from the `APIRouter` class, it has all the functions of `APIRouter` and provides some additional parameter settings.
    `APIRouter` class, used to group *path operations*, for example to structure
    an app in multiple files. It would then be included in the `FastAPI` app, or
    in another `APIRouter` (ultimately included in the app).

    Read more about it in the
    [FastAPI docs for Bigger Applications - Multiple Files](https://fastapi.tiangolo.com/tutorial/bigger-applications/).

    ## Example

    ```python
    from common.router import APIRouterPro, FastAPI

    app = FastAPI()
    router = APIRouterPro()


    @router.get('/users/', tags=['users'])
    async def read_users():
        return [{'username': 'Rick'}, {'username': 'Morty'}]


    app.include_router(router)
    ```
    """

    def __init__(  # noqa: PLR0913
        self,
        *,
        prefix: Annotated[str, Doc('An optional path prefix for the router.')] = '',
        order_num: Annotated[int, Doc('An optional order number for the router.')] = 100,
        auto_register: Annotated[bool, Doc('An optional auto register flag for the router.')] = True,
        tags: Annotated[
            Optional[list[Union[str, Enum]]],
            Doc(
                """
                A list of tags to be applied to all the *path operations* in this
                router.

                It will be added to the generated OpenAPI (e.g. visible at `/docs`).

                Read more about it in the
                [FastAPI docs for Path Operation Configuration](https://fastapi.tiangolo.com/tutorial/path-operation-configuration/).
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional[Sequence[params.Depends]],
            Doc(
                """
                A list of dependencies (using `Depends()`) to be applied to all the
                *path operations* in this router.

                Read more about it in the
                [FastAPI docs for Bigger Applications - Multiple Files](https://fastapi.tiangolo.com/tutorial/bigger-applications/#include-an-apirouter-with-a-custom-prefix-tags-responses-and-dependencies).
                """
            ),
        ] = None,
        default_response_class: Annotated[
            type[Response],
            Doc(
                """
                The default response class to be used.

                Read more in the
                [FastAPI docs for Custom Response - HTML, Stream, File, others](https://fastapi.tiangolo.com/advanced/custom-response/#default-response-class).
                """
            ),
        ] = Default(JSONResponse),
        responses: Annotated[
            Optional[dict[Union[int, str], dict[str, Any]]],
            Doc(
                """
                Additional responses to be shown in OpenAPI.

                It will be added to the generated OpenAPI (e.g. visible at `/docs`).

                Read more about it in the
                [FastAPI docs for Additional Responses in OpenAPI](https://fastapi.tiangolo.com/advanced/additional-responses/).

                And in the
                [FastAPI docs for Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/#include-an-apirouter-with-a-custom-prefix-tags-responses-and-dependencies).
                """
            ),
        ] = None,
        callbacks: Annotated[
            Optional[list[BaseRoute]],
            Doc(
                """
                OpenAPI callbacks that should apply to all *path operations* in this
                router.

                It will be added to the generated OpenAPI (e.g. visible at `/docs`).

                Read more about it in the
                [FastAPI docs for OpenAPI Callbacks](https://fastapi.tiangolo.com/advanced/openapi-callbacks/).
                """
            ),
        ] = None,
        routes: Annotated[
            Optional[list[BaseRoute]],
            Doc(
                """
                **Note**: you probably shouldn't use this parameter, it is inherited
                from Starlette and supported for compatibility.

                ---

                A list of routes to serve incoming HTTP and WebSocket requests.
                """
            ),
            deprecated(
                """
                You normally wouldn't use this parameter with FastAPI, it is inherited
                from Starlette and supported for compatibility.

                In FastAPI, you normally would use the *path operation methods*,
                like `router.get()`, `router.post()`, etc.
                """
            ),
        ] = None,
        redirect_slashes: Annotated[
            bool,
            Doc(
                """
                Whether to detect and redirect slashes in URLs when the client doesn't
                use the same format.
                """
            ),
        ] = True,
        default: Annotated[
            Optional[ASGIApp],
            Doc(
                """
                Default function handler for this router. Used to handle
                404 Not Found errors.
                """
            ),
        ] = None,
        dependency_overrides_provider: Annotated[
            Optional[Any],
            Doc(
                """
                Only used internally by FastAPI to handle dependency overrides.

                You shouldn't need to use it. It normally points to the `FastAPI` app
                object.
                """
            ),
        ] = None,
        route_class: Annotated[
            type[APIRoute],
            Doc(
                """
                Custom route (*path operation*) class to be used by this router.

                Read more about it in the
                [FastAPI docs for Custom Request and APIRoute class](https://fastapi.tiangolo.com/how-to/custom-request-and-route/#custom-apiroute-class-in-a-router).
                """
            ),
        ] = APIRoute,
        on_startup: Annotated[
            Optional[Sequence[Callable[[], Any]]],
            Doc(
                """
                A list of startup event handler functions.

                You should instead use the `lifespan` handlers.

                Read more in the [FastAPI docs for `lifespan`](https://fastapi.tiangolo.com/advanced/events/).
                """
            ),
        ] = None,
        on_shutdown: Annotated[
            Optional[Sequence[Callable[[], Any]]],
            Doc(
                """
                A list of shutdown event handler functions.

                You should instead use the `lifespan` handlers.

                Read more in the
                [FastAPI docs for `lifespan`](https://fastapi.tiangolo.com/advanced/events/).
                """
            ),
        ] = None,
        # the generic to Lifespan[AppType] is the type of the top level application
        # which the router cannot know statically, so we use typing.Any
        lifespan: Annotated[
            Optional[Lifespan[Any]],
            Doc(
                """
                A `Lifespan` context manager handler. This replaces `startup` and
                `shutdown` functions with a single context manager.

                Read more in the
                [FastAPI docs for `lifespan`](https://fastapi.tiangolo.com/advanced/events/).
                """
            ),
        ] = None,
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Mark all *path operations* in this router as deprecated.

                It will be added to the generated OpenAPI (e.g. visible at `/docs`).

                Read more about it in the
                [FastAPI docs for Path Operation Configuration](https://fastapi.tiangolo.com/tutorial/path-operation-configuration/).
                """
            ),
        ] = None,
        include_in_schema: Annotated[
            bool,
            Doc(
                """
                To include (or not) all the *path operations* in this router in the
                generated OpenAPI.

                This affects the generated OpenAPI (e.g. visible at `/docs`).

                Read more about it in the
                [FastAPI docs for Query Parameters and String Validations](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/#exclude-parameters-from-openapi).
                """
            ),
        ] = True,
        generate_unique_id_function: Annotated[
            Callable[[APIRoute], str],
            Doc(
                """
                Customize the function used to generate unique IDs for the *path
                operations* shown in the generated OpenAPI.

                This is particularly useful when automatically generating clients or
                SDKs for your API.

                Read more about it in the
                [FastAPI docs about how to Generate Clients](https://fastapi.tiangolo.com/advanced/generate-clients/#custom-generate-unique-id-function).
                """
            ),
        ] = Default(generate_unique_id),
    ) -> None:
        self.order_num = order_num
        self.auto_register = auto_register
        super().__init__(
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            dependency_overrides_provider=dependency_overrides_provider,
            route_class=route_class,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            lifespan=lifespan,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            generate_unique_id_function=generate_unique_id_function,
        )


class RouterRegister:
    """
    路由注册器，用于自动注册所有controller目录下的路由
    """

    def __init__(self, app: FastAPI) -> None:
        """
        初始化路由注册器

        :param app: FastAPI对象
        """
        self.app = app
        # 获取项目根目录
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        sys.path.insert(0, self.project_root)

    def _find_controller_files(self) -> list[str]:
        """
        查找所有controller目录下的py文件

        :return: py文件路径列表
        """
        controller_files = []
        # 遍历所有目录，查找controller目录
        for root, _dirs, files in os.walk(self.project_root):
            # 检查当前目录是否为controller目录
            if os.path.basename(root) == 'controller':
                # 遍历controller目录下的所有py文件
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        file_path = os.path.join(root, file)
                        controller_files.append(file_path)
                        print(f'   📄 Found controller file: {file_path}')
        return controller_files

    def _import_module_and_get_routers(self, controller_files: list[str]) -> list[tuple[str, APIRouter]]:
        """
        导入模块并获取路由实例

        :param controller_files: controller目录下的py文件路径列表
        :return: 路由实例列表
        """
        routers = []
        for file_path in controller_files:
            # 计算模块路径
            relative_path = os.path.relpath(file_path, self.project_root)
            module_name = relative_path.replace(os.sep, '.')[:-3]

            try:
                # 动态导入模块
                module = importlib.import_module(module_name)
                print(f'📦 Imported module: {module_name}')
                
                # 遍历模块属性，寻找APIRouter和APIRouterPro实例
                router_found = False
                for attr_name in dir(module):
                    # 跳过私有属性和特殊属性
                    if attr_name.startswith('_'):
                        continue
                    try:
                        attr = getattr(module, attr_name)
                        # 对于APIRouterPro实例，检查auto_register属性
                        if isinstance(attr, APIRouterPro):
                            auto_register = getattr(attr, 'auto_register', True)
                            if auto_register:
                                routers.append((attr_name, attr))
                                router_found = True
                                print(f'   ✓ Found APIRouterPro: {attr_name} (auto_register={auto_register})')
                            else:
                                print(f'   ⊘ Skipped APIRouterPro: {attr_name} (auto_register=False)')
                        # 对于APIRouter实例，直接添加
                        elif isinstance(attr, APIRouter):
                            routers.append((attr_name, attr))
                            router_found = True
                            print(f'   ✓ Found APIRouter: {attr_name}')
                    except Exception as e:
                        # 某些属性可能无法访问，记录但不中断
                        if 'router' in attr_name.lower() or 'controller' in attr_name.lower():
                            print(f'   ⚠️  Warning: Could not access attribute {attr_name}: {e}')
                
                if not router_found:
                    print(f'⚠️  Warning: No router found in module {module_name}')
            except ImportError as e:
                import traceback
                print(f'❌ ImportError importing module {module_name}: {e}')
                print(f'   File: {file_path}')
                print(f'   Traceback: {traceback.format_exc()}')
            except SyntaxError as e:
                import traceback
                print(f'❌ SyntaxError in module {module_name}: {e}')
                print(f'   File: {file_path}')
                print(f'   Traceback: {traceback.format_exc()}')
            except Exception as e:
                import traceback
                print(f'❌ Unexpected error importing module {module_name}: {e}')
                print(f'   File: {file_path}')
                print(f'   Error type: {type(e).__name__}')
                print(f'   Traceback: {traceback.format_exc()}')
        return routers

    def _sort_routers(self, routers: list[tuple[str, APIRouter]]) -> list[tuple[str, APIRouter]]:
        """
        按规则排序路由

        :param routers: 路由实例列表
        :return: 排序后的路由实例列表
        """

        # 按规则排序路由
        def sort_key(item: tuple[str, APIRouter]) -> Union[tuple[Literal[0], int, str], tuple[Literal[1], str]]:
            attr_name, router = item
            # APIRouterPro实例按order_num排序，序号越小越靠前
            if isinstance(router, APIRouterPro):
                return (0, router.order_num, attr_name)
            # APIRouter实例按变量名首字母排序
            return (1, attr_name)

        return sorted(routers, key=sort_key)

    def _register_routers_to_app(self, routers: list[tuple[str, APIRouter]]) -> None:
        """
        将路由注册到FastAPI应用

        :param routers: 排序后的路由实例列表
        :return: None
        """
        registered_count = 0
        for attr_name, router in routers:
            try:
                # 获取路由信息用于日志
                prefix = getattr(router, 'prefix', '')
                tags = getattr(router, 'tags', [])
                include_in_schema = getattr(router, 'include_in_schema', True)
                auto_register = getattr(router, 'auto_register', True)
                
                # 检查是否应该自动注册
                if isinstance(router, APIRouterPro) and not auto_register:
                    print(f'⏭️  Router {attr_name} (prefix: {prefix}) skipped (auto_register=False)')
                    continue
                
                # 检查是否应该包含在schema中
                if not include_in_schema:
                    print(f'⚠️  Router {attr_name} (prefix: {prefix}) is excluded from schema')
                
                # 获取路由数量
                route_count = len(router.routes) if hasattr(router, 'routes') else 0
                
                self.app.include_router(router=router)
                registered_count += 1
                print(f'✅ Registered router: {attr_name} (prefix: {prefix}, tags: {tags}, routes: {route_count})')
            except Exception as e:
                import traceback
                print(f'❌ Error registering router {attr_name}: {e}')
                print(f'   Traceback: {traceback.format_exc()}')
        
        print(f'📊 Successfully registered {registered_count}/{len(routers)} routers')

    def register_routers(self) -> None:
        """
        自动注册所有controller目录下的路由

        :return: None
        """
        print('🔍 Starting router registration...')
        print(f'📂 Project root: {self.project_root}')
        # 查找所有controller目录下的py文件
        controller_files = self._find_controller_files()
        print(f'📁 Found {len(controller_files)} controller files')
        if not controller_files:
            print('⚠️  WARNING: No controller files found!')
            print(f'   Searched in: {self.project_root}')
        # 导入模块并获取路由实例
        routers = self._import_module_and_get_routers(controller_files)
        print(f'🔌 Found {len(routers)} routers')
        if len(routers) < len(controller_files):
            print(f'⚠️  WARNING: Found {len(routers)} routers but {len(controller_files)} controller files!')
            print('   Some controllers may have failed to import or have no router defined.')
        # 按规则排序路由
        sorted_routers = self._sort_routers(routers)
        # 注册路由到FastAPI应用
        self._register_routers_to_app(sorted_routers)
        print(f'✨ Router registration completed! Total: {len(sorted_routers)} routers registered')
        
        # 验证：列出所有已注册的路由前缀
        print('\n📋 Summary of registered routes:')
        for attr_name, router in sorted_routers:
            prefix = getattr(router, 'prefix', '')
            tags = getattr(router, 'tags', [])
            route_count = len(router.routes) if hasattr(router, 'routes') else 0
            print(f'   - {attr_name}: {prefix} (tags: {tags}, {route_count} routes)')


def auto_register_routers(app: FastAPI) -> None:
    """
    自动注册所有controller目录下的路由

    :param app: FastAPI对象
    :return: None
    """
    # 使用路由注册器进行注册
    router_register = RouterRegister(app)
    router_register.register_routers()
