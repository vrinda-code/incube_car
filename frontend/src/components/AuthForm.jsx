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
    <div
      className="relative flex min-h-screen items-center justify-center bg-cover bg-center px-4 py-24"
      style={{
        backgroundImage:
          "linear-gradient(rgba(15, 23, 42, 0.35), rgba(15, 23, 42, 0.5)), url('/image.jpg')",
      }}
    >
      <h1 className="absolute left-6 top-6 text-3xl font-extrabold tracking-wide text-white drop-shadow-lg sm:left-10 sm:top-8 sm:text-5xl">
        CAR DELEARSHIP
      </h1>
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm space-y-4 rounded-xl border border-white/30 bg-white/40 p-6 shadow-2xl backdrop-blur-md"
      >
        <h2 className="text-2xl font-bold text-slate-800">{title}</h2>
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