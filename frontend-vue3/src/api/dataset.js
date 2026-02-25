import request from '@/utils/request'

export function getDatasets() {
  return request({
    url: '/api/datasets',
    method: 'get',
  })
}

export function createDataset(data) {
  return request({
    url: '/api/datasets',
    method: 'post',
    data,
  })
}

export function getDataset(id) {
  return request({
    url: `/api/datasets/${id}`,
    method: 'get',
  })
}

export function updateDataset(id, data) {
  return request({
    url: `/api/datasets/${id}`,
    method: 'put',
    data,
  })
}

export function deleteDataset(id) {
  return request({
    url: `/api/datasets/${id}`,
    method: 'delete',
  })
}

export function uploadDocument(datasetId, formData) {
  return request({
    url: `/api/datasets/${datasetId}/documents`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

export function getDocuments(datasetId) {
  return request({
    url: `/api/datasets/${datasetId}/documents`,
    method: 'get',
  })
}

export function deleteDocument(datasetId, documentId) {
  return request({
    url: `/api/datasets/${datasetId}/documents/${documentId}`,
    method: 'delete',
  })
}

export function getChunks(datasetId, documentId) {
  return request({
    url: `/api/datasets/${datasetId}/documents/${documentId}/chunks`,
    method: 'get',
  })
}

export function reindexDocument(datasetId, documentId) {
  return request({
    url: `/api/datasets/${datasetId}/documents/${documentId}/reindex`,
    method: 'post',
  })
}
