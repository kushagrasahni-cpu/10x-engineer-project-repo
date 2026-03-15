const BASE_URL = '/api'

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  }

  const response = await fetch(url, config)

  if (response.status === 204) {
    return null
  }

  const data = await response.json()

  if (!response.ok) {
    const message = data.detail
      ? typeof data.detail === 'string'
        ? data.detail
        : 'Validation error'
      : `Request failed (${response.status})`
    throw new Error(message)
  }

  return data
}

export function get(path) {
  return request(path)
}

export function post(path, body) {
  return request(path, { method: 'POST', body: JSON.stringify(body) })
}

export function put(path, body) {
  return request(path, { method: 'PUT', body: JSON.stringify(body) })
}

export function patch(path, body) {
  return request(path, { method: 'PATCH', body: JSON.stringify(body) })
}

export function del(path) {
  return request(path, { method: 'DELETE' })
}
