/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_BACKEND_URL: string
  readonly VITE_ENABLE_BACKEND: string
  readonly VITE_ENABLE_AI: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
