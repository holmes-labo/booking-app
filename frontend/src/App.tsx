import { useEffect, useState } from 'react'

type Service = {
  id: number
  business_id: number
  name: string
  duration_minutes: number
  price: number
  staff_assignment_mode: 'customer_choice' | 'automatic' | 'optional'
}

function App() {
  const [services, setServices] = useState<Service[]>([])

  useEffect(() => {
    fetch('http://localhost:8000/businesses/1/services')
      .then((response) => response.json())
      .then((data) => setServices(data))
  }, [])

  return (
    <main>
      <h1>Prendre rendez-vous</h1>

      {services.map((service) => (
        <div key={service.id}>
          <h2>{service.name}</h2>
          <p>{service.duration_minutes} minutes</p>
          <p>{service.price} €</p>
        </div>
      ))}
    </main>
  )
}

export default App