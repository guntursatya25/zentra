'use client'

import { createContext, useCallback, useContext, useState } from 'react'

interface Toast {
  id: number
  msg: string
  type: 'success' | 'error' | 'info'
}

interface ToastContextType {
  toast: (msg: string, type?: 'success' | 'error' | 'info') => void
}

const ToastContext = createContext<ToastContextType>({ toast: () => {} })

export const useToast = () => useContext(ToastContext)

let nextId = 0

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [list, setList] = useState<Toast[]>([])

  const addToast = useCallback((msg: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = nextId++
    setList((prev) => [...prev, { id, msg, type }])
    setTimeout(() => setList((prev) => prev.filter((t) => t.id !== id)), 3000)
  }, [])

  const colors = {
    success: 'bg-green-600 text-white',
    error: 'bg-red-600 text-white',
    info: 'bg-gray-800 text-white',
  }

  return (
    <ToastContext.Provider value={{ toast: addToast }}>
      {children}
      {/* Toast container */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2">
        {list.map((t) => (
          <div
            key={t.id}
            className={`animate-slide-up rounded-lg px-4 py-3 text-sm font-medium shadow-lg ${colors[t.type]}`}
          >
            {t.msg}
          </div>
        ))}
      </div>
      <style jsx global>{`
        @keyframes slide-up {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
        .animate-slide-up {
          animation: slide-up 0.25s ease-out;
        }
      `}</style>
    </ToastContext.Provider>
  )
}
