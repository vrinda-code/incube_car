import { createContext, useCallback, useContext, useState } from 'react'
import { loginUser } from './api'

const AuthContext = createContext(null)

function readRole(token) {
  try {
    return JSON.parse(atob(token.split('.')[1])).role
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('token'))

  async function login(email, password) {
    const data = await loginUser(email, password)
    localStorage.setItem('token', data.access_token)
    setToken(data.access_token)
  }

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    setToken(null)
  }, [])

  const role = token ? readRole(token) : null

  return (
    <AuthContext.Provider value={{ token, role, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)