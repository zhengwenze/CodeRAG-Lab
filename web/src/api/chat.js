import request from "@/utils/request";

export function chat(data) {
  return request({
    url: "/chat",
    method: "post",
    data,
  });
}

export function chatStream(data) {
  return request({
    url: "/chat",
    method: "post",
    data: { ...data, stream: true },
    responseType: "stream",
  });
}

// Load chat history by session_id
export function loadHistory(session_id) {
  return request({
    url: "/chat/history",
    method: "get",
    params: { session_id },
  });
}

// Save chat history for a session
export function saveHistory(session_id, messages) {
  return request({
    url: "/chat/history",
    method: "post",
    data: { session_id, messages },
  });
}

export function ask(query, top_k = 5) {
  return request({
    url: "/ask",
    method: "post",
    data: { query, top_k },
  });
}

export function healthCheck() {
  return request({
    url: "/health",
    method: "get",
  });
}

export function getConfig() {
  return request({
    url: "/config",
    method: "get",
  });
}
