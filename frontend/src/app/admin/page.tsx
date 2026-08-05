'use client'

import { useCallback, useEffect, useState } from 'react'
import { useAuth } from '@/lib/auth'
import { getAnalyticsOverview, getAnalyticsPerDay } from '@/lib/api'
import { IconBuilding } from '@/components/icons'

interface Overview {
  total_documents: number
  active_documents: number
  total_chunks: number
  total_conversations: number
  questions_today: number
  questions_total: number
}

export default function AdminDashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState<Overview | null>(null)
  const [perDay, setPerDay] = useState<{ date: string; count: number }[]>([])
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const [data, dayData] = await Promise.all([
        getAnalyticsOverview(),
        getAnalyticsPerDay(14).catch(() => []),
      ])
      setStats(data)
      setPerDay(dayData)
    } catch (err: any) {
      setError(err.message)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const maxDay = Math.max(...perDay.map((d) => d.count), 1)
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-title-lg text-ink">Dashboard</h1>
        <p className="mt-1 text-body-sm text-muted">Ringkasan aktivitas sistem SAsis</p>
      </div>

      {error && (
        <div className="rounded-md border border-error/30 bg-error/10 p-4 text-sm text-error">{error}</div>
      )}

      {/* Stats Grid */}
      {stats && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <StatsCard
            title="Total Dokumen"
            value={stats.total_documents}
            color="blue"
            subtitle={`${stats.active_documents} aktif`}
          />
          <StatsCard
            title="Chunks"
            value={stats.total_chunks}
            color="indigo"
            subtitle="dari parsing"
          />
          <StatsCard
            title="Percakapan"
            value={stats.total_conversations}
            color="green"
            subtitle="total"
          />
          <StatsCard
            title="Pertanyaan Hari Ini"
            value={stats.questions_today}
            color="amber"
            subtitle="24 jam terakhir"
          />
          <StatsCard
            title="Total Pertanyaan"
            value={stats.questions_total}
            color="purple"
            subtitle="semua waktu"
          />
          <StatsCard
            title="Dokumen Aktif"
            value={stats.active_documents}
            color="teal"
            subtitle={`dari ${stats.total_documents} total`}
          />
        </div>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Per-day Bar Chart */}
        {perDay.length > 0 && (
          <div className="col-span-1 lg:col-span-2 card p-5">
            <h3 className="mb-4 text-title-sm text-ink">Pertanyaan per Hari (14 hari)</h3>
            <div className="flex items-end gap-1.5" style={{ height: 120 }}>
              {perDay.map((d) => {
                const date = new Date(d.date)
                const dayName = days[date.getDay()]
                return (
                  <div key={d.date} className="flex flex-1 flex-col items-center gap-1">
                    <span className="text-[10px] font-medium text-muted">{d.count || ''}</span>
                    <div
                      className="w-full rounded-t-md bg-brand-teal transition-opacity hover:opacity-80"
                      style={{ height: `${Math.max((d.count / maxDay) * 100, 3)}px`, minHeight: d.count > 0 ? '4px' : '2px' }}
                      title={`${d.date}: ${d.count} pertanyaan`}
                    />
                    <span className="text-[10px] text-muted">{dayName}</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Welcome Card */}
        <div className="card p-5">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-lavender text-lg font-bold text-ink mb-3"
               role="img" aria-label={user?.full_name || user?.username}>
            {user?.full_name?.[0] || user?.username[0]?.toUpperCase() || 'U'}
          </div>
          <h3 className="text-title-sm text-ink">
            Selamat datang, {user?.full_name || user?.username}
          </h3>
          <div className="mt-2 space-y-1.5 text-caption text-muted">
            <p className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1 rounded-pill bg-surface-card px-2 py-0.5 text-caption text-ink">
                {user?.role === 'super_admin' ? 'Super Admin' : user?.role === 'data_manager' ? 'Data Manager' : 'Employee'}
              </span>
            </p>
            {user?.department && (
              <p className="flex items-center gap-2">
                <IconBuilding className="h-3.5 w-3.5 text-muted-soft" />
                {user.department}
              </p>
            )}
          </div>
          <div className="mt-4 border-t border-hairline pt-3 text-caption text-muted-soft">
            <p>Gunakan menu di sidebar untuk mengelola konten.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatsCard({ title, value, color, subtitle }: { title: string; value: number; color: string; subtitle: string }) {
  const colors: Record<string, string> = {
    blue: 'text-brand-teal',
    indigo: 'text-brand-lavender',
    green: 'text-success',
    amber: 'text-brand-ochre',
    purple: 'text-brand-pink',
    teal: 'text-brand-mint',
  }
  return (
    <div className="card p-4 transition-opacity hover:opacity-90">
      <p className="text-caption text-muted">{title}</p>
      <p className={`mt-1 text-display-sm ${colors[color] || colors.blue}`}>
        {value}
      </p>
      <p className="mt-0.5 text-[11px] text-muted-soft">{subtitle}</p>
    </div>
  )
}
