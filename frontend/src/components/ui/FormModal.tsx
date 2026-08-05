'use client'

import { useEffect, useRef } from 'react'

interface FormModalProps {
  open: boolean
  title: string
  titleId?: string
  onClose: () => void
  children: React.ReactNode
  maxWidth?: string
}

export function FormModal({ open, title, titleId = 'modal-title', onClose, children, maxWidth = 'max-w-md' }: FormModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [open, onClose])

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-10 flex items-center justify-center bg-ink/30"
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
    >
      <div ref={dialogRef} className={`w-full ${maxWidth} card p-6`}>
        <h2 id={titleId} className="mb-4 text-title-md text-ink">{title}</h2>
        {children}
      </div>
    </div>
  )
}
