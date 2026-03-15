import { get, post, put, patch, del } from './client'

export function getPrompts({ collectionId, search } = {}) {
  const params = new URLSearchParams()
  if (collectionId) params.set('collection_id', collectionId)
  if (search) params.set('search', search)
  const query = params.toString()
  return get(`/prompts${query ? `?${query}` : ''}`)
}

export function getPrompt(id) {
  return get(`/prompts/${id}`)
}

export function createPrompt(data) {
  return post('/prompts', data)
}

export function updatePrompt(id, data) {
  return put(`/prompts/${id}`, data)
}

export function patchPrompt(id, data) {
  return patch(`/prompts/${id}`, data)
}

export function deletePrompt(id) {
  return del(`/prompts/${id}`)
}
