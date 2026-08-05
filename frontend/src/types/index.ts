export interface User {
  id: string
  username: string
  email: string
  full_name: string | null
  role: 'employee' | 'data_manager' | 'super_admin'
  department: string | null
  is_active: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface DocumentCategory {
  id: number
  name: string
  description: string | null
  created_at: string
}

export interface Document {
  id: string
  title: string
  description: string | null
  category_id: number | null
  file_type: string
  file_size: number | null
  version: number
  status: 'draft' | 'active' | 'inactive' | 'archived'
  is_latest_version: boolean
  created_at: string
  updated_at: string
}

export interface DocumentList {
  id: string
  title: string
  description: string | null
  category_id: number | null
  category_name: string | null
  file_type: string
  version: number
  status: string
  created_at: string
}

export interface Citation {
  document_name: string
  bab: string | null
  pasal: string | null
  ayat: string | null
  excerpt: string
}

export interface ChatResponse {
  conversation_id: string
  message_id: string
  answer: string
  citations: Citation[]
}

export interface Conversation {
  id: string
  title: string | null
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations: Citation[] | null
  feedback: 'up' | 'down' | null
  created_at: string
}
