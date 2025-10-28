import { useState, useEffect } from 'react'
import './App.css'
import { DeltaAnalyzer } from './DeltaAnalyzer'

interface Avatar {
  name: string
  path: string
  size: number
  status: 'working' | 'broken'
  type: string
}

interface AvatarResponse {
  working: Avatar[]
  broken: Avatar[]
  total: number
  working_count: number
  broken_count: number
}

function App() {
  const [avatars, setAvatars] = useState<AvatarResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAvatars()
  }, [])

  const fetchAvatars = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:5000/api/avatars')
      if (!response.ok) throw new Error('Failed to fetch avatars')
      const data = await response.json()
      setAvatars(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="container" style={{ padding: '2rem' }}>Loading avatars...</div>
  if (error) return <div className="container" style={{ padding: '2rem', color: '#ff6b6b' }}>Error: {error}</div>
  if (!avatars) return <div className="container" style={{ padding: '2rem' }}>No data</div>

  return (
    <div className="app">
      <DeltaAnalyzer />
    </div>
  )
}

export default App
