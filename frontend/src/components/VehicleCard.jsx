import { useState } from 'react'

// "Tata" + "Nexon" -> "/cars/tata-nexon.jpg"
function photoUrl(vehicle) {
  const name = `${vehicle.make} ${vehicle.model}`.toLowerCase().replace(/[^a-z0-9]+/g, '-')
  return `/cars/${name}.jpg`
}

const formatPrice = (amount) => '₹' + amount.toLocaleString('en-IN')

export default function VehicleCard({ vehicle, onPurchase }) {
  const [photoFailed, setPhotoFailed] = useState(false)
  const outOfStock = vehicle.quantity === 0

  return (
    <div className="bg-white rounded-xl shadow p-4 flex gap-4">
      {photoFailed ? (
        <div className="w-32 h-24 shrink-0 rounded bg-slate-200 text-slate-500 text-xs flex items-center justify-center">
          No photo
        </div>
      ) : (
        <img
          src={photoUrl(vehicle)}
          alt={`${vehicle.make} ${vehicle.model}`}
          onError={() => setPhotoFailed(true)}
          className="w-32 h-24 shrink-0 rounded object-cover"
        />
      )}

      <div className="flex flex-col flex-1 min-w-0">
        <h2 className="font-semibold text-slate-800 truncate">
          {vehicle.make} {vehicle.model}
        </h2>
        <p className="text-sm text-slate-500">
          {vehicle.year} · {vehicle.color}
        </p>
        <div className="flex gap-2 mt-1 text-xs">
          <span className="bg-indigo-50 text-indigo-700 rounded px-2 py-0.5 capitalize">
            {vehicle.category}
          </span>
          <span className="bg-emerald-50 text-emerald-700 rounded px-2 py-0.5 capitalize">
            {vehicle.fuel_type}
          </span>
        </div>
        <p className="mt-2 font-bold text-slate-800">{formatPrice(vehicle.price)}</p>

        <div className="mt-auto pt-2 flex items-center justify-between">
          <span className={`text-xs ${outOfStock ? 'text-red-600 font-medium' : 'text-slate-500'}`}>
            {outOfStock ? 'Out of stock' : `${vehicle.quantity} in stock`}
          </span>
          <button
            disabled={outOfStock}
            onClick={() => onPurchase(vehicle.id)}
            className="text-sm rounded px-3 py-1 text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed"
          >
            Purchase
          </button>
        </div>
      </div>
    </div>
  )
}