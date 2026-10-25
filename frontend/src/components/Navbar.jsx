import { useAuth } from '../AuthContext'

export default function Navbar() {
  const { role, logout } = useAuth()

  return (
    <header className="bg-white shadow">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <h1 className="text-xl font-bold text-indigo-600">Car Dealership</h1>
        <div className="flex items-center gap-3">
          <span className="text-xs uppercase tracking-wide bg-slate-100 text-slate-600 rounded px-2 py-1">
            {role}
          </span>
          <button onClick={logout} className="text-sm text-slate-600 hover:text-slate-900">
            Log out
          </button>
        </div>
      </div>
    </header>
  )
}