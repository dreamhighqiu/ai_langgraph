/**
 * URL 状态同步 Composable
 * 
 * 类似于 ai-test-management 项目中的 nuqs (useQueryState)
 * 实现 URL 查询参数与 Vue 状态的双向同步
 * 
 * 功能：
 * 1. 从 URL 读取初始状态
 * 2. 状态变化自动同步到 URL
 * 3. 支持类型转换（string, number, boolean, json）
 * 4. 支持默认值
 * 5. 浏览器后退/前进同步
 */

import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

/**
 * 值解析器
 */
const parsers = {
  string: (value) => value,
  number: (value) => {
    const num = Number(value)
    return isNaN(num) ? null : num
  },
  boolean: (value) => value === 'true' || value === '1',
  json: (value) => {
    try {
      return JSON.parse(value)
    } catch {
      return null
    }
  }
}

/**
 * 值序列化器
 */
const serializers = {
  string: (value) => String(value),
  number: (value) => String(value),
  boolean: (value) => value ? 'true' : 'false',
  json: (value) => JSON.stringify(value)
}

/**
 * 单个 URL 查询参数状态
 * 
 * @param {string} key - URL 参数名
 * @param {Object} options - 配置选项
 * @param {any} options.defaultValue - 默认值
 * @param {string} options.type - 值类型 (string/number/boolean/json)
 * @param {boolean} options.history - 是否使用 pushState（否则使用 replaceState）
 * 
 * @example
 * const threadId = useQueryState('threadId', { defaultValue: '', type: 'string' })
 * const page = useQueryState('page', { defaultValue: 1, type: 'number' })
 */
export function useQueryState(key, options = {}) {
  const {
    defaultValue = null,
    type = 'string',
    history = false
  } = options

  const router = useRouter()
  const route = useRoute()
  
  const parse = parsers[type] || parsers.string
  const serialize = serializers[type] || serializers.string

  // 从 URL 读取初始值
  const getInitialValue = () => {
    const urlValue = route.query[key]
    if (urlValue !== undefined && urlValue !== null) {
      const parsed = parse(urlValue)
      return parsed !== null ? parsed : defaultValue
    }
    return defaultValue
  }

  const state = ref(getInitialValue())

  // 更新 URL
  const updateUrl = (newValue) => {
    const query = { ...route.query }
    
    if (newValue === null || newValue === undefined || newValue === defaultValue) {
      delete query[key]
    } else {
      query[key] = serialize(newValue)
    }

    const method = history ? router.push : router.replace
    method({ query }).catch(() => {})
  }

  // 监听状态变化，同步到 URL
  watch(state, (newValue) => {
    updateUrl(newValue)
  })

  // 监听路由变化，同步到状态
  watch(
    () => route.query[key],
    (newUrlValue) => {
      const parsed = newUrlValue !== undefined ? parse(newUrlValue) : defaultValue
      if (parsed !== state.value) {
        state.value = parsed !== null ? parsed : defaultValue
      }
    }
  )

  // 重置为默认值
  const reset = () => {
    state.value = defaultValue
  }

  return {
    value: state,
    reset,
    // 直接设置值的方法
    set: (newValue) => {
      state.value = newValue
    }
  }
}

/**
 * 多个 URL 查询参数状态
 * 
 * @param {Object} schema - 参数模式定义
 * 
 * @example
 * const { state, reset, updateQuery } = useQueryStates({
 *   threadId: { defaultValue: '', type: 'string' },
 *   page: { defaultValue: 1, type: 'number' },
 *   showSidebar: { defaultValue: true, type: 'boolean' }
 * })
 */
export function useQueryStates(schema) {
  const router = useRouter()
  const route = useRoute()
  
  const states = {}
  const defaults = {}

  // 为每个参数创建响应式状态
  for (const [key, options] of Object.entries(schema)) {
    const {
      defaultValue = null,
      type = 'string'
    } = options

    defaults[key] = defaultValue
    const parse = parsers[type] || parsers.string
    
    // 从 URL 读取初始值
    const urlValue = route.query[key]
    let initialValue = defaultValue
    if (urlValue !== undefined && urlValue !== null) {
      const parsed = parse(urlValue)
      initialValue = parsed !== null ? parsed : defaultValue
    }
    
    states[key] = ref(initialValue)
  }

  // 合并的状态对象
  const state = computed(() => {
    const result = {}
    for (const key of Object.keys(schema)) {
      result[key] = states[key].value
    }
    return result
  })

  // 更新 URL
  const updateUrl = () => {
    const query = { ...route.query }
    
    for (const [key, options] of Object.entries(schema)) {
      const { defaultValue = null, type = 'string' } = options
      const serialize = serializers[type] || serializers.string
      const value = states[key].value
      
      if (value === null || value === undefined || value === defaultValue) {
        delete query[key]
      } else {
        query[key] = serialize(value)
      }
    }

    router.replace({ query }).catch(() => {})
  }

  // 监听各个状态的变化
  for (const key of Object.keys(schema)) {
    watch(states[key], () => {
      updateUrl()
    })
  }

  // 监听路由变化
  watch(
    () => route.query,
    (newQuery) => {
      for (const [key, options] of Object.entries(schema)) {
        const { defaultValue = null, type = 'string' } = options
        const parse = parsers[type] || parsers.string
        
        const urlValue = newQuery[key]
        const parsed = urlValue !== undefined ? parse(urlValue) : defaultValue
        
        if (parsed !== states[key].value) {
          states[key].value = parsed !== null ? parsed : defaultValue
        }
      }
    },
    { deep: true }
  )

  // 重置所有参数
  const reset = () => {
    for (const [key, defaultValue] of Object.entries(defaults)) {
      states[key].value = defaultValue
    }
  }

  // 批量更新
  const updateQuery = (updates) => {
    for (const [key, value] of Object.entries(updates)) {
      if (states[key]) {
        states[key].value = value
      }
    }
  }

  // 获取单个状态的引用
  const getState = (key) => states[key]

  return {
    state,
    states,
    reset,
    updateQuery,
    getState
  }
}

/**
 * 分页状态
 * 
 * @param {Object} options - 配置选项
 * 
 * @example
 * const { page, pageSize, total, setPage, setPageSize } = usePaginationState({
 *   defaultPage: 1,
 *   defaultPageSize: 10
 * })
 */
export function usePaginationState(options = {}) {
  const {
    defaultPage = 1,
    defaultPageSize = 10,
    pageKey = 'page',
    pageSizeKey = 'pageSize'
  } = options

  const page = useQueryState(pageKey, { 
    defaultValue: defaultPage, 
    type: 'number' 
  })
  
  const pageSize = useQueryState(pageSizeKey, { 
    defaultValue: defaultPageSize, 
    type: 'number' 
  })

  const total = ref(0)

  // 计算总页数
  const totalPages = computed(() => {
    return Math.ceil(total.value / pageSize.value.value)
  })

  // 设置页码
  const setPage = (newPage) => {
    page.value.value = Math.max(1, Math.min(newPage, totalPages.value || 1))
  }

  // 设置每页条数
  const setPageSize = (newPageSize) => {
    pageSize.value.value = newPageSize
    // 重置到第一页
    page.value.value = 1
  }

  // 设置总数
  const setTotal = (newTotal) => {
    total.value = newTotal
  }

  return {
    page: page.value,
    pageSize: pageSize.value,
    total,
    totalPages,
    setPage,
    setPageSize,
    setTotal
  }
}

