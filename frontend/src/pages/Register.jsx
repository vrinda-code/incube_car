import { Link, useNavigate } from 'react-router-dom'
import { registerUser } from '../api'
import { useAuth } from '../AuthContext'
import AuthForm from '../components/AuthForm'

export default function Register() {
  const { login } = useAuth()
  const navigate = useNavigate()

  async function handleRegister(email, password) {
    await registerUser(email, password)
    await login(email, password) // log the new user in straight away
    navigate('/')
  }

  return (
    <AuthForm
      title="Create account"
      buttonText="Register"
      onSubmit={handleRegister}
      footer={<>Already have an account? <Link to="/login" className="text-indigo-600">Log in</Link></>}
    />
  )
}