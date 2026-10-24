import axios from 'axios'
import { ElLoading, ElMessage } from 'element-plus'
import { router } from '@/router'

let csrfTokenPromise

const getCsrfToken = () => {
  if (!csrfTokenPromise) {
    // 显式相对路径：不能拼接 VITE_APP_URL——生产构建无 .env 时它是 undefined，
    // 会变成 "undefined/api/csrf" 导致令牌预取永远失败（曾被旧 ErrorController 的 HTTP 200 掩盖）
    csrfTokenPromise = axios.get('/api/csrf', {
      withCredentials: true,
      timeout: 30000
    }).then(res => {
      const token = res.data && res.data.token
      if (!token) {
        // 拿不到令牌视为失败：不得带着空令牌发业务请求
        throw new Error('CSRF 令牌为空')
      }
      return token
    }).catch(e => {
      // 预取失败必须可见：提示一次、清缓存允许下次重试；否则业务请求会被静默吞掉
      ElMessage.error('安全令牌获取失败，请重试')
      throw e
    }).finally(() => {
      csrfTokenPromise = undefined
    })
  }
  return csrfTokenPromise
}

const withCsrfToken = async query => {
  const token = await getCsrfToken()
  query.headers = { ...query.headers, 'X-XSRF-TOKEN': token }
  return query
}

const request = function (loadtip, query) {
  let loading
  if (loadtip) {
    loading = ElLoading.service({
      lock: false,
      text: '正在加载中…',
      spinner: 'el-icon-loading',
      background: 'rgba(0, 0, 0, 0.5)'
    })
  }
  // 业务码统一分发（HTTP 200 时）：401/业务502 回登录页，500/501 原样 reject 交给调用方
  const dispatch = body => {
    if (body && body.code === 401) {
      router.push({ path: '/login' })
      return Promise.reject(body)
    } else if (body && body.code === 502) {
      router.push({ path: '/login' })
      return Promise.reject(body)
    } else if (body && (body.code === 500 || body.code === 501)) {
      return Promise.reject(body)
    }
    return Promise.resolve(body)
  }
  return axios.request(query)
    .then(res => dispatch(res.data))
    .catch(e => {
      // HTTP 层异常（非 2xx）与成功走同一套 response.data 解析：
      // 仅 HTTP 401 回登录页；403 等展示服务端可读消息；不把业务 502 误当 HTTP 处理
      const body = e && e.response && e.response.data
      const status = e && e.response ? e.response.status : undefined
      if (status === 401) {
        router.push({ path: '/login' })
      } else if (body && body.message) {
        ElMessage.error(body.message)
      } else if (!body) {
        ElMessage.error(e.message || '请求失败')
      }
      return Promise.reject(body || e)
    })
    .finally(() => {
      if (loadtip) {
        loading.close()
      }
    })
}

const post = function (url, params) {
  const query = {
    baseURL: import.meta.env.VITE_APP_URL,
    url: url,
    method: 'post',
    withCredentials: true,
    timeout: 30000,
    data: params,
    headers: { 'Content-Type': 'application/json', 'request-ajax': true }
  }
  return withCsrfToken(query).then(securedQuery => request(false, securedQuery))
}

const postWithLoadTip = function (url, params) {
  const query = {
    baseURL: import.meta.env.VITE_APP_URL,
    url: url,
    method: 'post',
    withCredentials: true,
    timeout: 30000,
    data: params,
    headers: { 'Content-Type': 'application/json', 'request-ajax': true }
  }
  return withCsrfToken(query).then(securedQuery => request(true, securedQuery))
}

const postWithOutLoadTip = function (url, params) {
  const query = {
    baseURL: import.meta.env.VITE_APP_URL,
    url: url,
    method: 'post',
    withCredentials: true,
    timeout: 30000,
    data: params,
    headers: { 'Content-Type': 'application/json', 'request-ajax': true }
  }
  return withCsrfToken(query).then(securedQuery => request(false, securedQuery))
}

const get = function (url, params) {
  const query = {
    baseURL: import.meta.env.VITE_APP_URL,
    url: url,
    method: 'get',
    withCredentials: true,
    timeout: 30000,
    params: params,
    headers: { 'request-ajax': true }
  }
  return request(false, query)
}

const form = function (url, params) {
  const query = {
    baseURL: import.meta.env.VITE_APP_URL,
    url: url,
    method: 'post',
    withCredentials: true,
    timeout: 30000,
    data: params,
    headers: { 'Content-Type': 'multipart/form-data', 'request-ajax': true }
  }
  return withCsrfToken(query).then(securedQuery => request(false, securedQuery))
}

export {
  post,
  postWithLoadTip,
  postWithOutLoadTip,
  get,
  form
}
