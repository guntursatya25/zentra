'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { useAuth } from '@/lib/auth'
import { listDocuments, sendMessage, listConversations, getConversation, deleteConversation, sendFeedback } from '@/lib/api'
import type { DocumentList, Message as MessageType, Conversation } from '@/types'
import { useRouter } from 'next/navigation'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { IconChat, IconSpinner } from '@/components/icons'
import { ChatSidebar } from '@/components/Chat/ChatSidebar'
import { MessageBubble } from '@/components/Chat/MessageBubble'
import { ChatInput } from '@/components/Chat/ChatInput'

const SUGGESTED_QUESTIONS = [
  'Berapa hari cuti tahunan untuk karyawan tetap?',
  'Bagaimana prosedur reimbursement perjalanan dinas?',
  'Berapa lama cuti melahirkan?',
  'Apa sanksi keterlambatan masuk kerja?',
  'Bagaimana cara mengajukan izin sakit?',
]

export default function ChatPage() {
  const { user, loading, logout } = useAuth()
  const router = useRouter()
  const [messages, setMessages] = useState<MessageType[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConvId, setActiveConvId] = useState<string | null>(null)
  const [documents, setDocuments] = useState<DocumentList[]>([])
  const [deleteConfirm, setDeleteConfirm] = useState<{ open: boolean; convId: string | null }>({ open: false, convId: null })
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!loading && !user) router.push('/login')
  }, [user, loading, router])

  useEffect(() => {
    if (user) {
      listConversations().then(setConversations).catch(() => {})
      listDocuments().then(setDocuments).catch(() => {})
    }
  }, [user])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadConversation = useCallback(async (id: string) => {
    setActiveConvId(id)
    const data = await getConversation(id)
    setMessages(data.messages)
  }, [])

  const handleSend = useCallback(async () => {
    if (!input.trim() || sending) return
    const q = input.trim()
    setInput('')
    setSending(true)

    const userMsg: MessageType = {
      id: 'temp-' + Date.now(),
      role: 'user',
      content: q,
      citations: null,
      feedback: null,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMsg])

    try {
      const res = await sendMessage(q, activeConvId || undefined)
      setActiveConvId(res.conversation_id)
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== userMsg.id),
        { ...userMsg, id: res.conversation_id + '-q' },
        {
          id: res.message_id,
          role: 'assistant',
          content: res.answer,
          citations: res.citations,
          feedback: null,
          created_at: new Date().toISOString(),
        },
      ])
      listConversations().then(setConversations).catch(() => {})
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: 'err-' + Date.now(),
          role: 'assistant',
          content: `Error: ${err.message}`,
          citations: null,
          feedback: null,
          created_at: new Date().toISOString(),
        },
      ])
    } finally {
      setSending(false)
    }
  }, [input, sending, activeConvId])

  const handleDeleteConfirm = useCallback(async () => {
    if (!deleteConfirm.convId) return
    try {
      await deleteConversation(deleteConfirm.convId)
      setConversations((prev) => prev.filter((c) => c.id !== deleteConfirm.convId))
      if (activeConvId === deleteConfirm.convId) {
        setActiveConvId(null)
        setMessages([])
      }
    } catch {}
    finally {
      setDeleteConfirm({ open: false, convId: null })
    }
  }, [deleteConfirm.convId, activeConvId])

  const handleFeedback = useCallback(async (msgId: string, feedback: 'up' | 'down') => {
    try {
      await sendFeedback(msgId, feedback)
      setMessages((prev) =>
        prev.map((m) => (m.id === msgId ? { ...m, feedback } : m))
      )
    } catch {}
  }, [])

  if (loading || !user) return null

  return (
    <div className="flex h-screen bg-canvas">
      <ChatSidebar
        user={user}
        conversations={conversations}
        activeConvId={activeConvId}
        documents={documents}
        onSelectConversation={loadConversation}
        onNewChat={() => { setActiveConvId(null); setMessages([]) }}
        onDeleteConversation={(id) => setDeleteConfirm({ open: true, convId: id })}
        onLogout={logout}
      />

      <div className="flex flex-1 flex-col">
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {messages.length === 0 && (
            <div className="flex h-full items-center justify-center">
              <div className="max-w-lg text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-xl bg-brand-teal/10">
                  <IconChat className="h-8 w-8 text-brand-teal" />
                </div>
                <h2 className="text-display-sm text-ink">
                  Tanyakan tentang kebijakan &amp; SOP
                </h2>
                <p className="mt-2 text-body-md text-muted">
                  Ajukan pertanyaan seputar kebijakan perusahaan dan dapatkan jawaban dengan referensi dokumen resmi.
                </p>
                <div className="mt-8 grid gap-2 sm:grid-cols-2">
                  {SUGGESTED_QUESTIONS.map((q) => (
                    <button
                      key={q}
                      onClick={() => setInput(q)}
                      className="rounded-md border border-hairline bg-canvas px-4 py-3 text-left text-body-sm text-body hover:border-brand-lavender hover:text-ink transition-colors"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {messages.map((m) => (
            <MessageBubble key={m.id} message={m} onFeedback={handleFeedback} />
          ))}

          {sending && (
            <div className="mb-4">
              <div className="inline-flex items-center gap-2 max-w-[70%] rounded-lg bg-surface-card px-4 py-3 text-body-sm text-muted">
                <IconSpinner />
                <span>Menjawab...</span>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        <ChatInput
          value={input}
          onChange={setInput}
          onSend={handleSend}
          sending={sending}
        />
      </div>

      <ConfirmDialog
        open={deleteConfirm.open}
        title="Hapus Percakapan"
        message="Apakah Anda yakin ingin menghapus percakapan ini? Tindakan ini tidak dapat dibatalkan."
        confirmLabel="Hapus"
        cancelLabel="Batal"
        variant="danger"
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteConfirm({ open: false, convId: null })}
      />
    </div>
  )
}
