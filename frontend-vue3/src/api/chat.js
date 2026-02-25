import request from '@/utils/request'

export function chat(data) {
  return request({
    url: '/api/chat',
    method: 'post',
    data,
  })
}

export function chatStream(data) {
  return request({
    url: '/api/chat',
    method: 'post',
    data: { ...data, stream: true },
    responseType: 'stream',
  })
}

export function ask(query, top_k = 5) {
  return request({
    url: '/api/ask',
    method: 'post',
    data: { query, top_k },
  })
}

export function healthCheck() {
  return request({
    url: '/api/health',
    method: 'get',
  })
}

export function getConfig() {
  return request({
    url: '/api/config',
    method: 'get',
  })
}
