'use client'

import { useCallback, useEffect, useState } from 'react'
import { getAnalyticsOverview, getAnalyticsFaq, getAnalyticsUnanswered, getAnalyticsPerDay, getAuditLogs, getAnalyticsWeeklyReport, getAnalyticsTrends, getAnalyticsSatisfaction } from '@/lib/api'

interface Overview {
  total_documents: number
  active_documents: number
  total_chunks: number
  total_conversations: number
  questions_today: number
  questions_total: number
}

interface FaqItem {
  question: string
  count: number
}

interface UnansweredItem {
  question: string
  answer: string
  created_at: string
}

interface DayCount {
  date: string
  count: number
}

interface WeeklyReport {
  week_start: string
  total_questions: number
  unique_users: number
  conversations: number
}

interface TrendItem {
  question: string
  recent_count: number
  older_count: number
  change: number
  trend: 'rising' | 'falling' | 'new' | 'gone' | 'stable'
}

interface SatisfactionDay {
  date: string
  up: number
  down: number
  total: number
  satisfaction: number
}

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<Overview | null>(null)
  const [faq, setFaq] = useState<FaqItem[]>([])
  const [unanswered, setUnanswered] = useState<UnansweredItem[]>([])
  const [perDay, setPerDay] = useState<DayCount[]>([])
  const [weeklyReport, setWeeklyReport] = useState<WeeklyReport[]>([])
  const [trends, setTrends] = useState<TrendItem[]>([])
  const [satisfaction, setSatisfaction] = useState<SatisfactionDay[]>([])
  const [tab, setTab] = useState<'faq' | 'unanswered' | 'weekly' | 'trends' | 'satisfaction' | 'audit'>('faq')

  const fetchData = useCallback(async () => {
    try {
      const [ov, f, ua, pd, wt, tr, sa] = await Promise.all([
        getAnalyticsOverview().catch(() => null),
        getAnalyticsFaq().catch(() => []),
        getAnalyticsUnanswered().catch(() => []),
        getAnalyticsPerDay(14).catch(() => []),
        getAnalyticsWeeklyReport().catch(() => []),
        getAnalyticsTrends().catch(() => []),
        getAnalyticsSatisfaction().catch(() => []),
      ])
      setOverview(ov)
      setFaq(f)
      setUnanswered(ua)
      setPerDay(pd)
      setWeeklyReport(wt)
      setTrends(tr)
      setSatisfaction(sa)
    } catch {}
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const maxFaqCount = Math.max(...faq.map((f) => f.count), 1)
  const maxDayCount = Math.max(...perDay.map((d) => d.count), 1)

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-title-lg text-ink">Analytics</h1>
        <p className="mt-1 text-body-sm text-muted">Statistik penggunaan sistem</p>
      </div>

      {/* Overview cards */}
      {overview && (
        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <Card label="Total Dokumen" value={overview.total_documents} />
          <Card label="Dokumen Aktif" value={overview.active_documents} />
          <Card label="Total Chunks" value={overview.total_chunks} />
          <Card label="Total Percakapan" value={overview.total_conversations} />
          <Card label="Pertanyaan Hari Ini" value={overview.questions_today} />
          <Card label="Total Pertanyaan" value={overview.questions_total} />
        </div>
      )}

      {/* Daily trend bar chart */}
      {perDay.length > 0 && (
        <div className="mb-6 card p-4">
          <h2 className="mb-3 text-title-sm text-ink">Pertanyaan per Hari (14 hari)</h2>
          <div className="flex items-end gap-1" style={{ height: 80 }}>
            {perDay.map((d) => (
              <div key={d.date} className="flex flex-1 flex-col items-center">
                <div
                  className="w-full rounded-t bg-brand-teal"
                  style={{
                    height: `${Math.max((d.count / maxDayCount) * 70, 4)}px`,
                    minHeight: d.count > 0 ? '4px' : '0',
                  }}
                  title={`${d.date}: ${d.count}`}
                />
                <span className="mt-1 text-[10px] text-muted">
                  {d.date.slice(5)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab bar */}
      <div className="mb-4 border-b border-hairline flex gap-1 overflow-x-auto">
        <button
          onClick={() => setTab('faq')}
          className={`border-b-2 px-3 py-2 text-nav-link whitespace-nowrap ${
            tab === 'faq' ? 'border-brand-teal text-brand-teal' : 'border-transparent text-muted hover:text-ink'
          }`}
        >
          Top FAQ
        </button>
        <button
          onClick={() => setTab('unanswered')}
          className={`border-b-2 px-3 py-2 text-nav-link whitespace-nowrap ${
            tab === 'unanswered' ? 'border-brand-teal text-brand-teal' : 'border-transparent text-muted hover:text-ink'
          }`}
        >
          Unanswered ({unanswered.length})
        </button>
        <button
          onClick={() => setTab('weekly')}
          className={`border-b-2 px-3 py-2 text-nav-link whitespace-nowrap ${
            tab === 'weekly' ? 'border-brand-teal text-brand-teal' : 'border-transparent text-muted hover:text-ink'
          }`}
        >
          Weekly Report
        </button>
        <button
          onClick={() => setTab('trends')}
          className={`border-b-2 px-3 py-2 text-nav-link whitespace-nowrap ${
            tab === 'trends' ? 'border-brand-teal text-brand-teal' : 'border-transparent text-muted hover:text-ink'
          }`}
        >
          Trends
        </button>
        <button
          onClick={() => setTab('satisfaction')}
          className={`border-b-2 px-3 py-2 text-nav-link whitespace-nowrap ${
            tab === 'satisfaction' ? 'border-brand-teal text-brand-teal' : 'border-transparent text-muted hover:text-ink'
          }`}
        >
          Satisfaction
        </button>
        <button
          onClick={() => setTab('audit')}
          className={`border-b-2 px-3 py-2 text-nav-link whitespace-nowrap ${
            tab === 'audit' ? 'border-brand-teal text-brand-teal' : 'border-transparent text-muted hover:text-ink'
          }`}
        >
          Audit Logs
        </button>
      </div>

      {/* FAQ tab */}
      {tab === 'faq' && (
        <div className="card">
          {faq.length === 0 ? (
            <div className="p-8 text-center text-body-sm text-muted">
              Belum ada data pertanyaan. Mulai gunakan fitur chat untuk mengumpulkan data.
            </div>
          ) : (
            <div className="divide-y divide-hairline">
              {faq.map((item, i) => (
                <div key={i} className="flex items-center gap-4 px-4 py-3">
                  <span className="w-6 text-right text-nav-link text-muted">
                    {i + 1}
                  </span>
                  <div className="flex-1 text-body-sm text-ink">{item.question}</div>
                  <div className="flex items-center gap-2">
                    <div
                      className="h-2 rounded-sm bg-brand-teal/30"
                      style={{ width: `${Math.max((item.count / maxFaqCount) * 100, 10)}px` }}
                    />
                    <span className="w-8 text-right text-caption text-muted">{item.count}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Unanswered tab */}
      {tab === 'unanswered' && (
        <div className="card">
          {unanswered.length === 0 ? (
            <div className="p-8 text-center text-body-sm text-muted">
              Tidak ada pertanyaan yang tidak terjawab. Sistem berhasil menemukan referensi untuk semua pertanyaan.
            </div>
          ) : (
            <div className="divide-y divide-hairline">
              {unanswered.map((item, i) => (
                <div key={i} className="px-4 py-3">
                  <p className="text-body-sm font-semibold text-ink">{item.question}</p>
                  <p className="mt-1 text-caption text-warning">{item.answer}</p>
                  <p className="mt-0.5 text-caption text-muted-soft">
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Weekly Report tab */}
      {tab === 'weekly' && (
        <div className="card">
          {weeklyReport.length === 0 ? (
            <div className="p-8 text-center text-body-sm text-muted">
              Belum ada data weekly report.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-left text-xs uppercase text-gray-500">
                  <tr>
                    <th className="px-4 py-3">Minggu</th>
                    <th className="px-4 py-3 text-right">Pertanyaan</th>
                    <th className="px-4 py-3 text-right">User Unik</th>
                    <th className="px-4 py-3 text-right">Percakapan</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {weeklyReport.map((w, i) => (
                    <tr key={i} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium">{w.week_start}</td>
                      <td className="px-4 py-3 text-right">{w.total_questions}</td>
                      <td className="px-4 py-3 text-right">{w.unique_users}</td>
                      <td className="px-4 py-3 text-right">{w.conversations}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Trends tab */}
      {tab === 'trends' && (
        <div className="card">
          {trends.length === 0 ? (
            <div className="p-8 text-center text-body-sm text-muted">
              Belum ada data trend. Butuh minimal 7 hari data.
            </div>
          ) : (
            <div className="divide-y divide-hairline">
              {trends.map((t, i) => (
                <div key={i} className="flex items-center gap-4 px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    t.trend === 'rising' ? 'bg-green-100 text-green-700' :
                    t.trend === 'falling' ? 'bg-red-100 text-red-700' :
                    t.trend === 'new' ? 'bg-blue-100 text-blue-700' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {t.trend === 'rising' ? '↑ Rising' :
                     t.trend === 'falling' ? '↓ Falling' :
                     t.trend === 'new' ? '★ New' :
                     t.trend === 'gone' ? '✕ Gone' : '— Stable'}
                  </span>
                  <div className="flex-1 text-body-sm text-ink">{t.question}</div>
                  <div className="text-caption text-muted">
                    {t.recent_count} → {t.older_count}
                    <span className={`ml-2 ${t.change > 0 ? 'text-green-600' : t.change < 0 ? 'text-red-600' : ''}`}>
                      ({t.change > 0 ? '+' : ''}{t.change})
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Satisfaction tab */}
      {tab === 'satisfaction' && (
        <div className="card">
          {satisfaction.length === 0 ? (
            <div className="p-8 text-center text-body-sm text-muted">
              Belum ada data feedback. User perlu memberikan thumbs up/down di chat.
            </div>
          ) : (
            <div className="p-4">
              <div className="mb-4 flex items-center gap-6 text-body-sm">
                <span className="text-muted">Rata-rata satisfaction:</span>
                <span className="text-title-md font-bold text-brand-teal">
                  {satisfaction.length > 0
                    ? Math.round(satisfaction.reduce((s, d) => s + d.satisfaction, 0) / satisfaction.length)
                    : 0}%
                </span>
                <span className="text-caption text-muted">
                  ({satisfaction.reduce((s, d) => s + d.total, 0)} total feedback)
                </span>
              </div>
              <div className="flex items-end gap-1" style={{ height: 100 }}>
                {satisfaction.map((d) => (
                  <div key={d.date} className="flex flex-1 flex-col items-center">
                    <span className="text-[10px] text-muted">{d.satisfaction}%</span>
                    <div
                      className={`w-full rounded-t ${d.satisfaction >= 70 ? 'bg-green-400' : d.satisfaction >= 40 ? 'bg-yellow-400' : 'bg-red-400'}`}
                      style={{ height: `${Math.max(d.satisfaction, 3)}px` }}
                      title={`${d.date}: 👍${d.up} 👎${d.down} (${d.satisfaction}%)`}
                    />
                    <span className="mt-1 text-[10px] text-muted">{d.date.slice(5)}</span>
                  </div>
                ))}
              </div>
              <div className="mt-4 flex gap-4 text-caption text-muted">
                <span>👍 = helpful</span>
                <span>👎 = not helpful</span>
                <span>Green ≥ 70% | Yellow ≥ 40% | Red &lt; 40%</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Audit tab */}
      {tab === 'audit' && <AuditLogViewer />}
    </div>
  )
}

function Card({ label, value }: { label: string; value: number }) {
  return (
    <div className="card p-3">
      <p className="text-caption text-muted">{label}</p>
      <p className="mt-1 text-title-lg text-ink">{value}</p>
    </div>
  )
}

function AuditLogViewer() {
  const [logs, setLogs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAuditLogs()
      .then(setLogs)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="p-4 text-center text-caption text-muted">Loading...</div>

  return (
    <div className="overflow-hidden card">
      {logs.length === 0 ? (
        <div className="p-8 text-center text-body-sm text-muted">
          Belum ada log audit.
        </div>
      ) : (
        <table className="w-full text-body-sm">
          <thead className="bg-surface-soft text-left text-caption-uppercase text-muted">
            <tr>
              <th className="px-4 py-3">Time</th>
              <th className="px-4 py-3">User</th>
              <th className="px-4 py-3">Action</th>
              <th className="px-4 py-3">Entity</th>
              <th className="px-4 py-3">Detail</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-hairline">
            {logs.map((log: any) => (
              <tr key={log.id} className="hover:bg-surface-soft">
                <td className="whitespace-nowrap px-4 py-3 text-muted">
                  {new Date(log.created_at).toLocaleString()}
                </td>
                <td className="px-4 py-3 text-body">{log.username || log.user_id?.slice(0, 8) || '-'}</td>
                <td className="px-4 py-3">
                  <span className="rounded-sm bg-surface-card px-2 py-0.5 text-caption text-ink">
                    {log.action}
                  </span>
                </td>
                <td className="px-4 py-3 text-body">
                  {log.entity_type ? `${log.entity_type} ${log.entity_id?.slice(0, 8) || ''}` : '-'}
                </td>
                <td className="max-w-xs truncate px-4 py-3 text-muted">
                  {log.details ? JSON.stringify(log.details).slice(0, 80) : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
