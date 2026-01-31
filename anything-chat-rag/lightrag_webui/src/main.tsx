
// @ts-expect-error  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TUVWa2FnPT06NGRhOTM4ZDk=

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
// Import extensions first to ensure global side effects are loaded
import '@/lib/extensions'
import AppRouter from './AppRouter'
import './i18n.ts';
import 'katex/dist/katex.min.css';

// NOTE  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TUVWa2FnPT06NGRhOTM4ZDk=


createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppRouter />
  </StrictMode>
)
