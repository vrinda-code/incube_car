// One helper for every call to the backend
async function request(path, { method = 'GET', body, token } = {}) {
  const response = await fetch(path, {
    method,
    headers: {
      ...(body && { 'Content-Type': 'application/json' }),
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: body ? JSON.stringify(body) : undefined,
  })

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const detail = data?.detail
    const error = new Error(typeof detail === 'string' ? detail : 'Please check what you entered')
    error.status = response.status
    throw error
  }
  return data
}

export const registerUser = (email, password) =>
  request('/api/auth/register', { method: 'POST', body: { email, password } })

export const loginUser = (email, password) =>
  request('/api/auth/login', { method: 'POST', body: { email, password } })

export const getVehicles = (token) => request('/api/vehicles', { token })

export const searchVehicles = (token, filters) => {
  const params = new URLSearchParams()

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== '') params.set(key, value)
  })

  return request(`/api/vehicles/search?${params.toString()}`, { token })
}

export const purchaseVehicle = (token, id) =>
  request(`/api/vehicles/${id}/purchase`, { method: 'POST', token })