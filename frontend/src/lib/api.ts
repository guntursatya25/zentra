import type { ChatResponse, Conversation, Document, DocumentCategory, DocumentList, LoginResponse, Message } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const isFormData = options.body instanceof FormData
  const headers: Record<string, string> = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(options.headers as Record<string, string> || {}),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `HTTP ${res.status}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

// Auth
export const login = (username: string, password: string) =>
  request<LoginResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })

export const getMe = () => request<LoginResponse['user']>('/api/auth/me')

// Categories
export const listCategories = () =>
  request<DocumentCategory[]>('/api/categories')

export const createCategory = (name: string, description?: string) =>
  request<DocumentCategory>('/api/categories', {
    method: 'POST',
    body: JSON.stringify({ name, description }),
  })

export const updateCategory = (id: number, data: { name: string; description?: string | null }) =>
  request<DocumentCategory>(`/api/categories/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })

export const deleteCategory = (id: number) =>
  request<void>(`/api/categories/${id}`, { method: 'DELETE' })

// Documents
export const listDocuments = () =>
  request<DocumentList[]>('/api/documents')

export const getDocument = (id: string) =>
  request<Document>(`/api/documents/${id}`)

export const deleteDocument = (id: string) =>
  request<void>(`/api/documents/${id}`, { method: 'DELETE' })

export const updateDocument = (id: string, data: FormData) =>
  request<void>(`/api/documents/${id}`, { method: 'PUT', body: data })

export const uploadDocumentVersion = (docId: string, file: File) => {
  const form = new FormData()
  form.append('file', file)
  return request<void>(`/api/documents/${docId}/versions`, { method: 'POST', body: form })
}

export const getDocumentChunks = (docId: string) =>
  request<any[]>(`/api/documents/${docId}/chunks`)

export const updateChunk = (chunkId: string, data: Record<string, string | null>) =>
  request<any>(`/api/documents/chunks/${chunkId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })

export const reparseDocument = (docId: string, useAi: boolean = false) =>
  request<void>(`/api/documents/${docId}/reparse?use_ai=${useAi}`, { method: 'POST' })

export const uploadDocument = async (
  file: File,
  title: string,
  categoryId?: number,
  description?: string
): Promise<Document> => {
  const token = localStorage.getItem('token')
  const form = new FormData()
  form.append('file', file)
  form.append('title', title)
  if (categoryId) form.append('category_id', String(categoryId))
  if (description) form.append('description', description)

  const res = await fetch(`${API_BASE}/api/documents`, {
    method: 'POST',
    headers: (token ? { Authorization: `Bearer ${token}` } : {}) as Record<string, string>,
    body: form,
  })
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || 'Upload failed')
  return res.json()
}

// Chat
export const sendMessage = (message: string, conversationId?: string, categoryFilter?: number[]) =>
  request<ChatResponse>('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message, conversation_id: conversationId, category_filter: categoryFilter }),
  })

export const listConversations = () =>
  request<Conversation[]>('/api/conversations')

export const getConversation = (id: string) =>
  request<{ conversation: Conversation; messages: Message[] }>(`/api/conversations/${id}`)

export const deleteConversation = (id: string) =>
  request<void>(`/api/conversations/${id}`, { method: 'DELETE' })

export const sendFeedback = (messageId: string, feedback: 'up' | 'down') =>
  request<void>(`/api/messages/${messageId}/feedback`, {
    method: 'POST',
    body: JSON.stringify({ feedback }),
  })

// Admin
export const listUsers = () =>
  request<any[]>('/api/admin/users')

export const updateUser = (id: string, data: any) =>
  request<any>(`/api/admin/users/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })

export const getAnalyticsOverview = () =>
  request<any>('/api/admin/analytics/overview')

export const getAnalyticsFaq = () =>
  request<any[]>('/api/admin/analytics/faq')

export const getAnalyticsUnanswered = () =>
  request<any[]>('/api/admin/analytics/unanswered')

export const getAuditLogs = () =>
  request<any[]>('/api/admin/audit-logs')

export const getAnalyticsPerDay = (days: number = 14) =>
  request<{ date: string; count: number }[]>(`/api/admin/analytics/per-day?days=${days}`)

export const getAnalyticsWeeklyReport = () =>
  request<{ week_start: string; total_questions: number; unique_users: number; conversations: number }[]>('/api/admin/analytics/weekly-report')

export const getAnalyticsTrends = () =>
  request<{ question: string; recent_count: number; older_count: number; change: number; trend: 'rising' | 'falling' | 'new' | 'gone' | 'stable' }[]>('/api/admin/analytics/trends')

export const getAnalyticsSatisfaction = () =>
  request<{ date: string; up: number; down: number; total: number; satisfaction: number }[]>('/api/admin/analytics/satisfaction')
