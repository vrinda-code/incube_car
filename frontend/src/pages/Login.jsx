import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import AuthForm from '../components/AuthForm'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()

  async function handleLogin(email, password) {
    await login(email, password)
    navigate('/')
  }

  return (
    <AuthForm
      title="Log in"
      buttonText="Log in"
      onSubmit={handleLogin}
      footer={<>No account? <Link to="/register" className="text-indigo-600">Register</Link></>}
    />
  )
}