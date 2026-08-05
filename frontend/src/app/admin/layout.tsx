'use client'

import { IconHome, IconFile, IconFolder, IconUsers, IconChart, IconChat, IconLogOut, IconChevron } from '@/components/icons'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { useAuth } from '@/lib/auth'


const navigation = [
  { name: 'Dashboard', href: '/admin', icon: IconHome },
  { name: 'Documents', href: '/admin/documents', icon: IconFile },
  { name: 'Categories', href: '/admin/categories', icon: IconFolder },
  { name: 'Users', href: '/admin/users', icon: IconUsers },
  { name: 'Analytics', href: '/admin/analytics', icon: IconChart },
]

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (!loading && (!user || (user.role !== 'super_admin' && user.role !== 'data_manager'))) {
      router.push('/login')
    }
  }, [user, loading, router])

  if (loading || !user) return null

  return (
    <div className="flex h-screen overflow-hidden bg-canvas">
      {/* Sidebar */}
      <aside className="hidden w-64 flex-shrink-0 border-r border-hairline bg-surface-soft lg:flex lg:flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center gap-3 border-b border-hairline px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-brand-teal text-sm font-bold text-on-dark">
            S
          </div>
          <div>
            <h1 className="text-title-sm text-ink">Zentra</h1>
            <p className="text-[10px] font-medium text-muted-soft">Admin Panel</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`group flex items-center gap-3 rounded-md px-3 py-2.5 text-nav-link transition-all ${
                  isActive
                    ? 'bg-surface-card text-ink font-semibold'
                    : 'text-body hover:bg-surface-soft hover:text-ink'
                }`}
              >
                <item.icon className={`h-4 w-4 flex-shrink-0 ${isActive ? 'text-brand-teal' : 'text-muted group-hover:text-body'}`} />
                {item.name}
                {isActive && <IconChevron />}
              </Link>
            )
          })}
        </nav>

        {/* Chat link */}
        <div className="border-t border-hairline px-3 py-3">
          <Link
            href="/chat"
            className="flex items-center gap-3 rounded-md px-3 py-2.5 text-nav-link text-body transition-all hover:bg-surface-soft hover:text-ink"
          >
            <IconChat />
            Chat
            <span className="ml-auto rounded-pill bg-surface-card px-2 py-0.5 text-[10px] font-medium text-muted">Open</span>
          </Link>
        </div>

        {/* User */}
        <div className="border-t border-hairline px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-lavender text-xs font-bold text-ink">
              {user.full_name?.[0] || user.username[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="truncate text-nav-link font-semibold text-ink">{user.full_name || user.username}</p>
              <p className="truncate text-caption text-muted-soft">
                <span className="inline-flex items-center gap-1">
                  <span className={`h-1.5 w-1.5 rounded-full ${user.role === 'super_admin' ? 'bg-brand-pink' : 'bg-brand-teal'}`} />
                  {user.role === 'super_admin' ? 'Super Admin' : user.role === 'data_manager' ? 'Data Manager' : 'Employee'}
                </span>
                {user.department && <span> · {user.department}</span>}
              </p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        <header className="flex h-16 items-center justify-between border-b border-hairline bg-canvas px-6">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-1.5 text-caption text-muted">
            <Link href="/admin" className="hover:text-ink transition-colors">Admin</Link>
            {pathname !== '/admin' && (
              <>
                <span className="text-muted-soft">/</span>
                <span className="text-ink font-medium">
                  {navigation.find((n) => n.href === pathname)?.name || ''}
                </span>
              </>
            )}
          </nav>
          <div className="flex items-center gap-4">
            <Link
              href="/chat"
              className="flex items-center gap-2 rounded-md bg-surface-soft px-3 py-2 text-nav-link text-body transition-colors hover:bg-surface-card"
            >
              <IconChat />
              <span className="hidden sm:inline">Chat</span>
            </Link>
            <button
              onClick={logout}
              className="flex items-center gap-2 rounded-md px-3 py-2 text-nav-link text-muted transition-colors hover:bg-brand-pink/10 hover:text-brand-pink"
            >
              <IconLogOut />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-canvas p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
