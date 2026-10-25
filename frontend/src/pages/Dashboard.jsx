import { useCallback, useEffect, useState } from 'react'
import { getVehicles, purchaseVehicle, searchVehicles } from '../api'
import { useAuth } from '../AuthContext'
import Navbar from '../components/Navbar'
import VehicleCard from '../components/VehicleCard'

const emptyFilters = {
  make: '',
  model: '',
  category: '',
  min_price: '',
  max_price: '',
}

export default function Dashboard() {
  const { token, logout } = useAuth()
  const [vehicles, setVehicles] = useState([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [filters, setFilters] = useState(emptyFilters)

  // The login expires after 1 hour; the backend then answers 401, so go back to login
  const handleError = useCallback((err) => {
    if (err.status === 401) logout()
    else setMessage(err.message)
  }, [logout])

  useEffect(() => {
    getVehicles(token)
      .then(setVehicles)
      .catch(handleError)
      .finally(() => setLoading(false))
  }, [handleError, token])

  async function handlePurchase(id) {
    setMessage('')
    try {
      const result = await purchaseVehicle(token, id)
      // update just this car's quantity, no need to reload the whole list
      setVehicles((list) =>
        list.map((car) => (car.id === id ? { ...car, quantity: result.quantity } : car))
      )
    } catch (err) {
      handleError(err)
    }
  }

  async function handleSearch(event) {
    event.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      setVehicles(await searchVehicles(token, filters))
    } catch (err) {
      handleError(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleClearFilters() {
    setFilters(emptyFilters)
    setMessage('')
    setLoading(true)

    try {
      setVehicles(await getVehicles(token))
    } catch (err) {
      handleError(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-100">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-6">
        {message && <p className="mb-4 text-sm text-red-600">{message}</p>}
        <form onSubmit={handleSearch} className="mb-6 rounded-xl bg-white p-4 shadow">
          <h2 className="mb-4 text-lg font-semibold text-slate-800">Search and filter cars</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            <label className="text-sm text-slate-600">
              Make
              <input
                value={filters.make}
                onChange={(event) => setFilters({ ...filters, make: event.target.value })}
                placeholder="e.g. Toyota"
                className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-slate-900"
              />
            </label>
            <label className="text-sm text-slate-600">
              Model
              <input
                value={filters.model}
                onChange={(event) => setFilters({ ...filters, model: event.target.value })}
                placeholder="e.g. Camry"
                className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-slate-900"
              />
            </label>
            <label className="text-sm text-slate-600">
              Category
              <select
                value={filters.category}
                onChange={(event) => setFilters({ ...filters, category: event.target.value })}
                className="mt-1 w-full rounded border border-slate-300 bg-white px-3 py-2 text-slate-900"
              >
                <option value="">All categories</option>
                <option value="sedan">Sedan</option>
                <option value="hatchback">Hatchback</option>
                <option value="suv">SUV</option>
                <option value="sports">Sports</option>
              </select>
            </label>
            <label className="text-sm text-slate-600">
              Minimum price (₹)
              <input
                type="number"
                min="0"
                value={filters.min_price}
                onChange={(event) => setFilters({ ...filters, min_price: event.target.value })}
                className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-slate-900"
              />
            </label>
            <label className="text-sm text-slate-600">
              Maximum price (₹)
              <input
                type="number"
                min="0"
                value={filters.max_price}
                onChange={(event) => setFilters({ ...filters, max_price: event.target.value })}
                className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-slate-900"
              />
            </label>
          </div>
          <div className="mt-4 flex gap-3">
            <button
              type="submit"
              disabled={loading}
              className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-wait disabled:opacity-60"
            >
              Apply filters
            </button>
            <button
              type="button"
              onClick={handleClearFilters}
              disabled={loading}
              className="rounded border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 disabled:cursor-wait disabled:opacity-60"
            >
              Clear
            </button>
          </div>
        </form>
        {loading ? (
          <p className="text-slate-500">Loading cars...</p>
        ) : (
          vehicles.length === 0 ? (
            <p className="rounded-xl bg-white p-6 text-center text-slate-500 shadow">
              No cars match your search. Try adjusting or clearing your filters.
            </p>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {vehicles.map((car) => (
                <VehicleCard key={car.id} vehicle={car} onPurchase={handlePurchase} />
              ))}
            </div>
          )
        )}
      </main>
      <footer
        id="contact-us"
        className="scroll-mt-4 w-full border-t border-slate-200 bg-white px-4 py-8 shadow-inner"
      >
        <div className="flex w-full flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-800">Contact Us</h2>
            <p className="mt-1 text-sm text-slate-500">
              Questions about a car? Get in touch with our dealership.
            </p>
          </div>
          <div className="flex flex-col gap-2 text-sm sm:items-end">
            <a
              href="mailto:cardelearship@gmail.com"
              className="font-medium text-indigo-600 hover:text-indigo-800"
            >
              cardelearship@gmail.com
            </a>
            <a href="tel:8484848484" className="font-medium text-indigo-600 hover:text-indigo-800">
              8484848484
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}