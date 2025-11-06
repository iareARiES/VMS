import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Zones from './pages/Zones'
import Events from './pages/Events'
import Models from './pages/Models'
import Settings from './pages/Settings'
import Health from './pages/Health'
import Layout from './components/Layout'

function App() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/zones" element={<Zones />} />
          <Route path="/events" element={<Events />} />
          <Route path="/models" element={<Models />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/health" element={<Health />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App

