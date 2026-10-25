import { useState } from 'react'

// One form used by both the Login and Register pages
export default function AuthForm({ title, buttonText, onSubmit, footer }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault() // stop the browser from reloading the page
    setError('')
    try {
      await onSubmit(email, password)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm bg-white rounded-xl shadow p-6 space-y-4"
      >
        <h1 className="text-2xl font-bold text-slate-800">{title}</h1>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <input
          type="email"
          required
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full border border-slate-300 rounded px-3 py-2"
        />
        <input
          type="password"
          required
          minLength={6}
          placeholder="Password (at least 6 characters)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full border border-slate-300 rounded px-3 py-2"
        />
        <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded py-2">
          {buttonText}
        </button>
        <p className="text-sm text-slate-600">{footer}</p>
      </form>
    </div>
  )
}