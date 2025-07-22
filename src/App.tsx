import { Routes, Route } from "react-router-dom"
import Home from "./pages/Home"
import Play from "./pages/Play"
import Create from "./pages/Create"
import Layout from "./components/Layout"

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/play/:id" element={<Play />} />
        <Route path="/create" element={<Create />} />
      </Routes>
    </Layout>
  )
}