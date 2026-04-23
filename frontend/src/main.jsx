import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import ErrorBoundary from './components/shared/ErrorBoundary.jsx'
import './styles/theme.css'
import './index.css'
import './App.css'

console.log('[MAIN] Starting app...')
console.log('[MAIN] Root element:', document.getElementById('root'))

try {
  const root = ReactDOM.createRoot(document.getElementById('root'))
  console.log('[MAIN] Root created successfully')
  
  root.render(
    <React.StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </React.StrictMode>,
  )
  console.log('[MAIN] Render called')
} catch (err) {
  console.error('[MAIN] Fatal error:', err)
}
