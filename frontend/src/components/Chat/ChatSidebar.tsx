'use client'

import { useState } from 'react'
import Link from 'next/link'
import type { DocumentList, Conversation } from '@/types'
import type { User } from '@/types'
import { IconDocument, IconX, IconPlus, IconLogOut, IconAdmin, IconChevronDown } from '@/components/icons'

interface ChatSidebarProps {
  user: User
  conversations: Conversation[]
  activeConvId: string | null
  documents: DocumentList[]
  onSelectConversation: (id: string) => void
  onNewChat: () => void
  onDeleteConversation: (id: string) => void
  onLogout: () => void
}

export function ChatSidebar({
  user,
  conversations,
  activeConvId,
  documents,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  onLogout,
}: ChatSidebarProps) {
  const [showSources, setShowSources] = useState(false)

  return (
    <aside className="flex w-64 flex-col border-r border-hairline bg-surface-soft">
      {/* Logo */}
      <div className="flex h-16 items-center justify-between border-b border-hairline px-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-brand-teal text-xs font-bold text-on-dark">
            S
          </div>
          <span className="text-title-sm text-ink">Zentra</span>
        </div>
        <div className="flex items-center gap-1">
          {(user.role === 'super_admin' || user.role === 'data_manager') && (
            <Link
              href="/admin"
              className="rounded-md p-1.5 text-muted hover:bg-surface-card hover:text-ink transition-colors"
              title="Admin Panel"
            >
              <IconAdmin className="h-4 w-4" />
            </Link>
          )}
          <button
            onClick={onLogout}
            className="rounded-md p-1.5 text-muted hover:bg-brand-pink/10 hover:text-brand-pink transition-colors"
            title="Logout"
          >
            <IconLogOut className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          <IconPlus className="h-4 w-4" />
          Percakapan Baru
        </button>
      </div>

      {/* Conversations */}
      <div className="flex-1 overflow-y-auto px-2">
        <p className="mb-1 px-2 text-caption-uppercase text-muted">
          Riwayat
        </p>
        {conversations.length === 0 ? (
          <p className="px-2 py-4 text-center text-caption text-muted-soft">
            Belum ada percakapan
          </p>
        ) : (
          conversations.map((c) => (
            <div key={c.id} className={`group flex items-center gap-1 rounded-md px-2 py-1.5 ${
              activeConvId === c.id ? 'bg-surface-card' : 'hover:bg-surface-soft'
            }`}>
              <button
                onClick={() => onSelectConversation(c.id)}
                className={`flex-1 truncate text-left text-nav-link ${
                  activeConvId === c.id ? 'text-ink font-semibold' : 'text-body'
                }`}
              >
                {c.title || 'Percakapan baru'}
              </button>
              <button
                onClick={() => onDeleteConversation(c.id)}
                className="hidden rounded-sm p-1 text-muted-soft hover:bg-brand-pink/20 hover:text-brand-pink group-hover:block"
                title="Hapus percakapan"
              >
                <IconX className="h-3 w-3" />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Document sources */}
      <div className="border-t border-hairline">
        <button
          onClick={() => setShowSources(!showSources)}
          className="flex w-full items-center justify-between px-4 py-3 text-caption text-muted hover:bg-surface-soft transition-colors"
        >
          <span className="flex items-center gap-1.5">
            <IconDocument className="h-3.5 w-3.5" />
            Sumber Dokumen ({documents.length})
          </span>
          <IconChevronDown className={`h-3 w-3 transition-transform ${showSources ? 'rotate-180' : ''}`} />
        </button>
        {showSources && (
          <div className="max-h-40 overflow-y-auto px-3 pb-3">
            {documents.length === 0 ? (
              <p className="text-caption text-muted-soft py-2">Belum ada dokumen</p>
            ) : (
              documents.map((d) => (
                <div key={d.id} className="flex items-center gap-2 truncate py-1.5 text-caption text-body">
                  <span className={`h-1.5 w-1.5 flex-shrink-0 rounded-full ${
                    d.status === 'active' ? 'bg-success' : 'bg-muted-soft'
                  }`} />
                  <span className="truncate">{d.title}</span>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* User info */}
      <div className="border-t border-hairline px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-lavender text-xs font-bold text-ink">
            {user.full_name?.[0] || user.username[0].toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="truncate text-nav-link font-medium text-ink">{user.full_name || user.username}</p>
            <p className="truncate text-[11px] text-muted-soft">
              {user.role === 'super_admin' ? 'Super Admin' : user.role === 'data_manager' ? 'Data Manager' : 'Employee'}
            </p>
          </div>
        </div>
      </div>
    </aside>
  )
}
