import { Navigate, Route, Routes } from 'react-router-dom'

import { AdminLayout } from '@/layouts/admin-layout'
import { DashboardPage } from '@/pages/dashboard-page'
import { AgendaPage } from '@/pages/agenda-page'

function App() {
  return (
    <Routes>
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="agenda" element={<AgendaPage />} />
      </Route>

      {/* Pour l'instant, l'entrée de l'application mène au back-office. */}
      <Route path="/" element={<Navigate to="/admin" replace />} />
    </Routes>
  )
}

export default App