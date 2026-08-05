'use client'

import { FormEvent, useState } from 'react'
import { useAuth } from '@/lib/auth'
import { IconLock, IconDocument, IconCheck, IconExclamation, IconEye, IconEyeSlash, IconSpinner } from '@/components/icons'

export default function LoginPage() {
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
    } catch (err: any) {
      setError(err.message || 'Login gagal. Periksa username dan password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-canvas">
      {/* Left - Brand Section */}
      <div className="hidden w-1/2 flex-col justify-between bg-brand-teal p-12 text-on-dark lg:flex">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-md bg-white/20 text-xl font-bold backdrop-blur-sm">
              S
            </div>
            <div>
              <h1 className="text-title-lg">Zentra</h1>
              <p className="text-sm text-on-dark-soft">Instant Assistant</p>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <blockquote className="border-l-2 border-white/30 pl-4 text-display-sm font-medium leading-tight text-on-dark">
            &ldquo;Temukan jawaban atas kebijakan dan SOP perusahaan dengan cepat dan akurat.&rdquo;
          </blockquote>
          <div className="flex items-center gap-4 text-sm text-on-dark-soft">
            <span className="flex items-center gap-1.5">
              <IconLock className="h-4 w-4" /> Data tetap internal
            </span>
            <span className="flex items-center gap-1.5">
              <IconDocument className="h-4 w-4" /> Berbasis dokumen resmi
            </span>
            <span className="flex items-center gap-1.5">
              <IconCheck className="h-4 w-4" /> Jawaban dengan sitasi
            </span>
          </div>
        </div>

        <div className="text-sm text-on-dark-soft">
          &copy; 2026 Perusahaan Internal
        </div>
      </div>

      {/* Right - Login Form */}
      <div className="flex w-full items-center justify-center px-6 lg:w-1/2">
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <div className="mb-8 text-center lg:hidden">
            <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-md bg-brand-teal text-xl font-bold text-on-dark">
              S
            </div>
            <h1 className="text-title-lg text-ink">Zentra</h1>
            <p className="text-sm text-muted">Internal Policy &amp; SOP Assistant</p>
          </div>

          <div className="rounded-lg border border-hairline bg-canvas p-8">
            <h2 className="mb-1 text-title-md text-ink">Masuk</h2>
            <p className="mb-6 text-body-sm text-muted">
              Gunakan akun internal perusahaan Anda
            </p>

            {error && (
              <div className="mb-4 flex items-center gap-2 rounded-md border border-error/30 bg-error/10 p-3 text-sm text-error">
                <IconExclamation className="h-4 w-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="username" className="mb-1.5 block text-nav-link text-body-strong">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="input-field w-full"
                  placeholder="Masukkan username"
                  autoComplete="username"
                />
              </div>

              <div>
                <label htmlFor="password" className="mb-1.5 block text-nav-link text-body-strong">
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input-field w-full pr-10"
                    placeholder="Masukkan password"
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-ink transition-colors"
                    tabIndex={-1}
                    aria-label={showPassword ? 'Sembunyikan password' : 'Tampilkan password'}
                  >
                    {showPassword ? (
                      <IconEyeSlash className="h-4 w-4" />
                    ) : (
                      <IconEye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <IconSpinner />
                    Memproses...
                  </span>
                ) : (
                  'Masuk'
                )}
              </button>
            </form>
          </div>

          <div className="mt-4 text-center text-xs text-muted-soft lg:hidden">
            <p>Demo: admin / admin123</p>
          </div>
        </div>
      </div>
    </div>
  )
}
