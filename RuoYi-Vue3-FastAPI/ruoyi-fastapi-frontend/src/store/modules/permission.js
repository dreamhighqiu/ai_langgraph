import auth from '@/plugins/auth'
import router, { constantRoutes, dynamicRoutes } from '@/router'
import { getRouters } from '@/api/menu'
import Layout from '@/layout/index'
import ParentView from '@/components/ParentView'
import InnerLink from '@/layout/components/InnerLink'

// 匹配views里面所有的.vue文件
const modules = import.meta.glob('./../../views/**/*.vue')

const usePermissionStore = defineStore(
  'permission',
  {
    state: () => ({
      routes: [],
      addRoutes: [],
      defaultRoutes: [],
      topbarRouters: [],
      sidebarRouters: []
    }),
    actions: {
      setRoutes(routes) {
        this.addRoutes = routes
        this.routes = constantRoutes.concat(routes)
      },
      setDefaultRoutes(routes) {
        this.defaultRoutes = constantRoutes.concat(routes)
      },
      setTopbarRoutes(routes) {
        this.topbarRouters = routes
      },
      setSidebarRouters(routes) {
        this.sidebarRouters = routes
      },
      // 兜底：若后端未正确挂载，补充测试三大模块路由，避免 404
      ensureTestingRoutes() {
        const existing = router.getRoutes().map(r => r.path)
        const toAdd = []

        // 项目管理路由
        const makeProject = () => ({
          path: '/testing',
          component: Layout,
          alwaysShow: true,
          meta: { title: '测试管理', icon: 'test-tube' },
          children: [
            {
              path: 'project',
              component: loadView('testing/project/index'),
              name: 'TestingProject',
              meta: { title: '项目管理', icon: 'folder-opened' }
            }
          ]
        })

        const makePerf = () => ({
          path: '/performance',
          component: Layout,
          alwaysShow: true,
          meta: { title: '性能测试', icon: 'dashboard' },
          children: [
            { path: 'index', component: loadView('testing/performance/index'), name: 'PerformanceTesting', meta: { title: '性能测试', icon: 'odometer' } },
            { path: 'requirement', component: loadView('testing/performance/requirement'), name: 'PerformanceRequirement', meta: { title: '需求管理', icon: 'list' } },
            { path: 'script', component: loadView('testing/performance/script'), name: 'PerformanceScript', meta: { title: '脚本管理', icon: 'edit' } },
            { path: 'execution', component: loadView('testing/performance/execution'), name: 'PerformanceExecution', meta: { title: '脚本执行', icon: 'play' } },
            { path: 'report', component: loadView('testing/performance/report'), name: 'PerformanceReport', meta: { title: '报告管理', icon: 'document' } }
          ]
        })
        const makeUI = () => ({
          path: '/ui-automation',
          component: Layout,
          alwaysShow: true,
          meta: { title: 'UI自动化', icon: 'monitor' },
          children: [
            { path: 'index', component: loadView('testing/ui-automation/index'), name: 'UIAutomation', meta: { title: 'UI自动化', icon: 'monitor' } },
            { path: 'requirement', component: loadView('testing/ui-automation/requirement'), name: 'UIRequirement', meta: { title: '需求管理', icon: 'list' } },
            { path: 'generate', component: loadView('testing/ui-automation/generate'), name: 'UIGenerate', meta: { title: '脚本生成', icon: 'magic-stick' } },
            { path: 'script', component: loadView('testing/ui-automation/script'), name: 'UIScript', meta: { title: '脚本管理', icon: 'edit' } },
            { path: 'execution', component: loadView('testing/ui-automation/execution'), name: 'UIExecution', meta: { title: '脚本执行', icon: 'play' } },
            { path: 'report', component: loadView('testing/ui-automation/report'), name: 'UIReport', meta: { title: '报告管理', icon: 'document' } }
          ]
        })
        const makeAPI = () => ({
          path: '/api-automation',
          component: Layout,
          alwaysShow: true,
          meta: { title: 'API自动化', icon: 'api' },
          children: [
            { path: 'index', component: loadView('testing/api-automation/index'), name: 'APIAutomation', meta: { title: 'API自动化', icon: 'connection' } },
            { path: 'requirement', component: loadView('testing/api-automation/requirement'), name: 'APIRequirement', meta: { title: '需求管理', icon: 'list' } },
            { path: 'script', component: loadView('testing/api-automation/script'), name: 'APIScript', meta: { title: '脚本管理', icon: 'edit' } },
            { path: 'execution', component: loadView('testing/api-automation/execution'), name: 'APIExecution', meta: { title: '脚本执行', icon: 'play' } },
            { path: 'report', component: loadView('testing/api-automation/report'), name: 'APIReport', meta: { title: '报告管理', icon: 'document' } }
          ]
        })

        if (!existing.includes('/testing')) toAdd.push(makeProject())
        if (!existing.includes('/performance')) toAdd.push(makePerf())
        if (!existing.includes('/ui-automation')) toAdd.push(makeUI())
        if (!existing.includes('/api-automation')) toAdd.push(makeAPI())
        toAdd.forEach(r => router.addRoute(r))
      },
      generateRoutes(roles) {
        return new Promise(resolve => {
          // 向后端请求路由数据
          getRouters().then(res => {
            const sdata = JSON.parse(JSON.stringify(res.data))
            const rdata = JSON.parse(JSON.stringify(res.data))
            const defaultData = JSON.parse(JSON.stringify(res.data))
            const sidebarRoutes = filterAsyncRouter(sdata)
            const rewriteRoutes = filterAsyncRouter(rdata, false, true)
            const defaultRoutes = filterAsyncRouter(defaultData)
            const asyncRoutes = filterDynamicRoutes(dynamicRoutes)
            asyncRoutes.forEach(route => { router.addRoute(route) })
            // 兜底补充三大测试模块，防止路由未挂载导致 404
            this.ensureTestingRoutes()
            this.setRoutes(rewriteRoutes)
            this.setSidebarRouters(constantRoutes.concat(sidebarRoutes))
            this.setDefaultRoutes(sidebarRoutes)
            this.setTopbarRoutes(defaultRoutes)
            resolve(rewriteRoutes)
          })
        })
      }
    }
  })

// 遍历后台传来的路由字符串，转换为组件对象
function filterAsyncRouter(asyncRouterMap, lastRouter = false, type = false) {
  return asyncRouterMap.filter(route => {
    if (type && route.children) {
      route.children = filterChildren(route.children)
    }
    if (route.component) {
      // Layout ParentView 组件特殊处理
      if (route.component === 'Layout') {
        route.component = Layout
      } else if (route.component === 'ParentView') {
        route.component = ParentView
      } else if (route.component === 'InnerLink') {
        route.component = InnerLink
      } else {
        route.component = loadView(route.component)
      }
    }
    if (route.children != null && route.children && route.children.length) {
      route.children = filterAsyncRouter(route.children, route, type)
    } else {
      delete route['children']
      delete route['redirect']
    }
    return true
  })
}

function filterChildren(childrenMap, lastRouter = false) {
  var children = []
  childrenMap.forEach(el => {
    el.path = lastRouter ? lastRouter.path + '/' + el.path : el.path
    if (el.children && el.children.length && el.component === 'ParentView') {
      children = children.concat(filterChildren(el.children, el))
    } else {
      children.push(el)
    }
  })
  return children
}

// 动态路由遍历，验证是否具备权限
export function filterDynamicRoutes(routes) {
  const res = []
  routes.forEach(route => {
    if (route.permissions) {
      if (auth.hasPermiOr(route.permissions)) {
        res.push(route)
      }
    } else if (route.roles) {
      if (auth.hasRoleOr(route.roles)) {
        res.push(route)
      }
    }
  })
  return res
}

export const loadView = (view) => {
  let res;
  for (const path in modules) {
    const dir = path.split('views/')[1].split('.vue')[0];
    if (dir === view) {
      res = () => modules[path]();
    }
  }
  return res
}

export default usePermissionStore
