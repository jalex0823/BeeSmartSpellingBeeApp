import React, { useState, useEffect } from 'react'
import './DeltaAnalyzer.css'

interface MeshData {
  name: string
  vertex_count: number
  face_count: number
  normal_count: number
  texture_coord_count: number
  min_bounds: [number, number, number]
  max_bounds: [number, number, number]
  materials_used: string[]
  has_normals: boolean
  has_texture_coords: boolean
  issues: string[]
}

interface TextureData {
  name: string
  path: string
  type: string
  exists: boolean
  size_bytes: number
  format: string
  issues: string[]
}

interface MaterialData {
  name: string
  ambient: [number, number, number]
  diffuse: [number, number, number]
  specular: [number, number, number]
  shininess: number
  opacity: number
  texture_count: number
  textures: TextureData[]
  issues: string[]
}

interface AvatarAnalysis {
  avatar_name: string
  file_path: string
  file_size: number
  file_modified: string
  obj_file: string
  mtl_file: string | null
  meshes: MeshData[]
  materials: MaterialData[]
  summary: {
    total_meshes: number
    total_materials: number
    total_textures: number
    total_issues: number
    critical_issues: string[]
    warnings: string[]
    info: string[]
  }
}

interface DeltaAnalysis {
  comparison: {
    working: string
    broken: string
  }
  summary: {
    working_issues: number
    broken_issues: number
    issue_delta: number
  }
  mesh_differences: {
    working: { vertices: number; faces: number }
    broken: { vertices: number; faces: number }
    delta: { vertex_delta: number; face_delta: number }
  }
  material_differences: {
    working_count: number
    broken_count: number
    delta: number
  }
  texture_differences: {
    working_count: number
    broken_count: number
    delta: number
    working_textures: number
    broken_textures: number
  }
  diagnostic_findings: string[]
  suggested_fixes: string[]
}

interface AvatarInfo {
  name: string
  status: 'working' | 'broken'
}

export const DeltaAnalyzer: React.FC = () => {
  const [avatars, setAvatars] = useState<{ working: AvatarInfo[]; broken: AvatarInfo[] }>({
    working: [],
    broken: []
  })
  const [selectedWorking, setSelectedWorking] = useState<string>('')
  const [selectedBroken, setSelectedBroken] = useState<string>('')
  const [workingAnalysis, setWorkingAnalysis] = useState<AvatarAnalysis | null>(null)
  const [brokenAnalysis, setBrokenAnalysis] = useState<AvatarAnalysis | null>(null)
  const [deltaAnalysis, setDeltaAnalysis] = useState<DeltaAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')

  // Fetch avatar list on mount
  useEffect(() => {
    const fetchAvatars = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/avatars')
        const data = await response.json()
        setAvatars(data)
        if (data.working.length > 0) setSelectedWorking(data.working[0].name)
        if (data.broken.length > 0) setSelectedBroken(data.broken[0].name)
      } catch (err) {
        setError('Failed to fetch avatars')
      }
    }
    fetchAvatars()
  }, [])

  // Perform comparison
  const handleCompare = async () => {
    if (!selectedWorking || !selectedBroken) {
      setError('Please select both avatars')
      return
    }

    setLoading(true)
    setError('')

    try {
      // Fetch working avatar analysis
      const workingRes = await fetch(
        `http://localhost:5000/api/analyze/file/${selectedWorking}`
      )
      if (!workingRes.ok) throw new Error('Failed to analyze working avatar')
      const working = await workingRes.json()
      setWorkingAnalysis(working)

      // Fetch broken avatar analysis
      const brokenRes = await fetch(
        `http://localhost:5000/api/analyze/file/${selectedBroken}`
      )
      if (!brokenRes.ok) throw new Error('Failed to analyze broken avatar')
      const broken = await brokenRes.json()
      setBrokenAnalysis(broken)

      // Fetch delta comparison
      const deltaRes = await fetch('http://localhost:5000/api/compare/delta', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          working: selectedWorking,
          broken: selectedBroken
        })
      })
      if (!deltaRes.ok) throw new Error('Failed to compare avatars')
      const delta = await deltaRes.json()
      setDeltaAnalysis(delta)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Comparison failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="delta-analyzer">
      <header className="analyzer-header">
        <h1>🔬 Deep Avatar Delta Analyzer</h1>
        <p>Forensic comparison of working vs broken avatars</p>
      </header>

      <section className="selector-panel">
        <div className="selector-group">
          <label>✅ Working Avatar</label>
          <select
            value={selectedWorking}
            onChange={(e) => setSelectedWorking(e.target.value)}
            disabled={loading}
          >
            {avatars.working.map((avatar) => (
              <option key={avatar.name} value={avatar.name}>
                {avatar.name}
              </option>
            ))}
          </select>
        </div>

        <div className="selector-group">
          <label>❌ Broken Avatar</label>
          <select
            value={selectedBroken}
            onChange={(e) => setSelectedBroken(e.target.value)}
            disabled={loading}
          >
            {avatars.broken.map((avatar) => (
              <option key={avatar.name} value={avatar.name}>
                {avatar.name}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleCompare}
          disabled={loading || !selectedWorking || !selectedBroken}
          className="compare-button"
        >
          {loading ? '⏳ Analyzing...' : '🔍 Analyze & Compare'}
        </button>
      </section>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {deltaAnalysis && (
        <section className="analysis-results">
          {/* Summary */}
          <div className="result-section summary-section">
            <h2>📊 Comparison Summary</h2>
            <div className="summary-grid">
              <div className="summary-card">
                <span className="label">Working Issues</span>
                <span className={`value ${deltaAnalysis.summary.working_issues > 0 ? 'warning' : 'good'}`}>
                  {deltaAnalysis.summary.working_issues}
                </span>
              </div>
              <div className="summary-card">
                <span className="label">Broken Issues</span>
                <span className={`value ${deltaAnalysis.summary.broken_issues > 0 ? 'critical' : 'good'}`}>
                  {deltaAnalysis.summary.broken_issues}
                </span>
              </div>
              <div className="summary-card">
                <span className="label">Issue Delta</span>
                <span className={`value ${deltaAnalysis.summary.issue_delta > 0 ? 'critical' : 'good'}`}>
                  {deltaAnalysis.summary.issue_delta > 0 ? '+' : ''}{deltaAnalysis.summary.issue_delta}
                </span>
              </div>
            </div>
          </div>

          {/* Mesh Comparison */}
          <div className="result-section mesh-section">
            <h2>🗂️ Mesh Structure</h2>
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>Metric</th>
                  <th className="working">{selectedWorking}</th>
                  <th className="broken">{selectedBroken}</th>
                  <th>Delta</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Vertices</td>
                  <td className="working">
                    {deltaAnalysis.mesh_differences.working.vertices.toLocaleString()}
                  </td>
                  <td className="broken">
                    {deltaAnalysis.mesh_differences.broken.vertices.toLocaleString()}
                  </td>
                  <td className={deltaAnalysis.mesh_differences.delta.vertex_delta !== 0 ? 'diff' : ''}>
                    {deltaAnalysis.mesh_differences.delta.vertex_delta > 0 ? '+' : ''}
                    {deltaAnalysis.mesh_differences.delta.vertex_delta.toLocaleString()}
                  </td>
                </tr>
                <tr>
                  <td>Faces</td>
                  <td className="working">
                    {deltaAnalysis.mesh_differences.working.faces.toLocaleString()}
                  </td>
                  <td className="broken">
                    {deltaAnalysis.mesh_differences.broken.faces.toLocaleString()}
                  </td>
                  <td className={deltaAnalysis.mesh_differences.delta.face_delta !== 0 ? 'diff' : ''}>
                    {deltaAnalysis.mesh_differences.delta.face_delta > 0 ? '+' : ''}
                    {deltaAnalysis.mesh_differences.delta.face_delta.toLocaleString()}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Materials Comparison */}
          <div className="result-section material-section">
            <h2>🎨 Materials</h2>
            <div className="comparison-cards">
              <div className="card working">
                <span className="label">{selectedWorking}</span>
                <span className="value">{deltaAnalysis.material_differences.working_count}</span>
                <span className="unit">materials</span>
              </div>
              <div className="card broken">
                <span className="label">{selectedBroken}</span>
                <span className="value">{deltaAnalysis.material_differences.broken_count}</span>
                <span className="unit">materials</span>
              </div>
            </div>
          </div>

          {/* Textures Comparison */}
          <div className="result-section texture-section">
            <h2>🖼️ Textures</h2>
            <div className="comparison-cards">
              <div className="card working">
                <span className="label">{selectedWorking}</span>
                <span className="value">{deltaAnalysis.texture_differences.working_textures}</span>
                <span className="unit">found of {deltaAnalysis.texture_differences.working_count}</span>
              </div>
              <div className="card broken">
                <span className="label">{selectedBroken}</span>
                <span className="value">{deltaAnalysis.texture_differences.broken_textures}</span>
                <span className="unit">found of {deltaAnalysis.texture_differences.broken_count}</span>
              </div>
            </div>
          </div>

          {/* Diagnostic Findings */}
          {deltaAnalysis.diagnostic_findings.length > 0 && (
            <div className="result-section findings-section">
              <h2>🔍 Diagnostic Findings</h2>
              <ul className="findings-list">
                {deltaAnalysis.diagnostic_findings.map((finding, idx) => (
                  <li key={idx} className="finding">
                    {finding}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Suggested Fixes */}
          {deltaAnalysis.suggested_fixes.length > 0 && (
            <div className="result-section fixes-section">
              <h2>💡 Suggested Fixes</h2>
              <ul className="fixes-list">
                {deltaAnalysis.suggested_fixes.map((fix, idx) => (
                  <li key={idx} className="fix">
                    ✓ {fix}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Detailed Analysis */}
          {workingAnalysis && brokenAnalysis && (
            <div className="result-section details-section">
              <h2>📋 Detailed Analysis</h2>
              <div className="details-grid">
                <CollapsiblePanel
                  title={`${selectedWorking} - File Details`}
                  analysis={workingAnalysis}
                  status="working"
                />
                <CollapsiblePanel
                  title={`${selectedBroken} - File Details`}
                  analysis={brokenAnalysis}
                  status="broken"
                />
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  )
}

interface CollapsiblePanelProps {
  title: string
  analysis: AvatarAnalysis
  status: 'working' | 'broken'
}

const CollapsiblePanel: React.FC<CollapsiblePanelProps> = ({
  title,
  analysis,
  status
}) => {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className={`collapsible-panel ${status}`}>
      <button
        className="panel-header"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="toggle">{expanded ? '▼' : '▶'}</span>
        {title}
        <span className="issue-badge">
          {analysis.summary.total_issues > 0 && (
            <span className="badge critical">{analysis.summary.total_issues}</span>
          )}
        </span>
      </button>

      {expanded && (
        <div className="panel-content">
          {/* Mesh Details */}
          <div className="detail-group">
            <h4>🗂️ Mesh Data</h4>
            {analysis.meshes.map((mesh, idx) => (
              <div key={idx} className="detail-item">
                <div className="detail-row">
                  <span className="key">Vertices:</span>
                  <span className="value">{mesh.vertex_count.toLocaleString()}</span>
                </div>
                <div className="detail-row">
                  <span className="key">Faces:</span>
                  <span className="value">{mesh.face_count.toLocaleString()}</span>
                </div>
                <div className="detail-row">
                  <span className="key">Has Normals:</span>
                  <span className={`value ${mesh.has_normals ? 'good' : 'warning'}`}>
                    {mesh.has_normals ? '✓' : '✗'} {mesh.has_normals ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="key">Texture Coords:</span>
                  <span className={`value ${mesh.has_texture_coords ? 'good' : 'warning'}`}>
                    {mesh.has_texture_coords ? '✓' : '✗'} {mesh.has_texture_coords ? 'Yes' : 'No'}
                  </span>
                </div>
                {mesh.issues.length > 0 && (
                  <div className="issues">
                    {mesh.issues.map((issue, i) => (
                      <div key={i} className="issue critical">
                        🔴 {issue}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Material Details */}
          {analysis.materials.length > 0 && (
            <div className="detail-group">
              <h4>🎨 Materials</h4>
              {analysis.materials.map((material, idx) => (
                <div key={idx} className="detail-item">
                  <div className="detail-row">
                    <span className="key">Name:</span>
                    <span className="value">{material.name}</span>
                  </div>
                  <div className="detail-row">
                    <span className="key">Opacity:</span>
                    <span className="value">{material.opacity}</span>
                  </div>
                  <div className="detail-row">
                    <span className="key">Textures:</span>
                    <span className="value">{material.texture_count}</span>
                  </div>
                  {material.issues.length > 0 && (
                    <div className="issues">
                      {material.issues.map((issue, i) => (
                        <div key={i} className="issue warning">
                          ⚠️ {issue}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Summary */}
          <div className="detail-group">
            <h4>📊 Summary</h4>
            {analysis.summary.critical_issues.length > 0 && (
              <div className="issues">
                <strong>Critical Issues:</strong>
                {analysis.summary.critical_issues.map((issue, i) => (
                  <div key={i} className="issue critical">
                    🔴 {issue}
                  </div>
                ))}
              </div>
            )}
            {analysis.summary.warnings.length > 0 && (
              <div className="issues">
                <strong>Warnings:</strong>
                {analysis.summary.warnings.map((warning, i) => (
                  <div key={i} className="issue warning">
                    ⚠️ {warning}
                  </div>
                ))}
              </div>
            )}
            {analysis.summary.info.length > 0 && (
              <div className="issues">
                <strong>Info:</strong>
                {analysis.summary.info.map((info, i) => (
                  <div key={i} className="issue info">
                    ℹ️ {info}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
