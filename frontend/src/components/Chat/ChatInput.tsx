'use client'

import { IconSend } from '@/components/icons'

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  sending: boolean
}

export function ChatInput({ value, onChange, onSend, sending }: ChatInputProps) {
  return (
    <div className="border-t border-hairline bg-surface-soft px-6 py-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), onSend())}
          placeholder="Tanyakan tentang kebijakan..."
          className="input-field flex-1"
        />
        <button
          onClick={onSend}
          disabled={sending || !value.trim()}
          className="btn-primary flex items-center gap-2"
        >
          <IconSend className="h-4 w-4" />
          <span className="hidden sm:inline">Kirim</span>
        </button>
      </div>
      <p className="mt-2 text-center text-[11px] text-muted-soft">
        Zentra dapat membuat kesalahan. Verifikasi informasi penting dari dokumen sumber.
      </p>
    </div>
  )
}
