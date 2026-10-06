import axios from 'axios'
import { ElLoading, ElMessage } from 'element-plus'
import { router } from '@/router'

let csrfTokenPromise

const getCsrfToken = () => {
  if (!csrfTokenPromise) {
    csrfTokenPromise = axios.get(`${import.meta.env.VITE_APP_URL}/api/csrf`, {
      withCredentials: true,
      timeout: 30000
    }).then(res => res.data.token).catch(error => {
      csrfTokenPromise = undefined
      throw error
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
  return axios.request(query)
    .then(res => {
      if (loadtip) {
        loading.close()
      }
      if (res.data.code === 401) {
        router.push({ path: '/login' })
        return Promise.reject(res.data)
      } else if (res.data.code === 500) {
        return Promise.reject(res.data)
      } else if (res.data.code === 501) {
        return Promise.reject(res.data)
      } else if (res.data.code === 502) {
        router.push({ path: '/login' })
        return Promise.reject(res.data)
      } else {
        return Promise.resolve(res.data)
      }
    })
    .catch(e => {
      if (loadtip) {
        loading.close()
      }
      ElMessage.error(e.message)
      return Promise.reject(e.message)
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
