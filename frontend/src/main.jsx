import { StrictMode } from 'react' // Built-in React wrapper component that activates extra development-only checks and warnings to find and fix potential bugs early
import { createRoot } from 'react-dom/client' // Initialize and render a React application into the browser's DOM
import './index.css' // Import global CSS styles for the React application
import App from './App.jsx' // Import the root application component


// Entry point for the React application
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
