import { useEffect, useState } from 'react'
import { getVehicles, purchaseVehicle } from '../api'
import { useAuth } from '../AuthContext'
import Navbar from '../components/Navbar'
import VehicleCard from '../components/VehicleCard'

export default function Dashboard() {
  const { token, logout } = useAuth()
  const [vehicles, setVehicles] = useState([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')

  // The login expires after 1 hour; the backend then answers 401, so go back to login
  function handleError(err) {
    if (err.status === 401) logout()
    else setMessage(err.message)
  }

  useEffect(() => {
    getVehicles(token)
      .then(setVehicles)
      .catch(handleError)
      .finally(() => setLoading(false))
  }, [])

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

  return (
    <div className="min-h-screen bg-slate-100">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-6">
        {message && <p className="mb-4 text-sm text-red-600">{message}</p>}
        {loading ? (
          <p className="text-slate-500">Loading cars...</p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {vehicles.map((car) => (
              <VehicleCard key={car.id} vehicle={car} onPurchase={handlePurchase} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}