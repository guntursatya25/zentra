'use client'

import ReactMarkdown from 'react-markdown'
import type { Message } from '@/types'
import { IconDocument, IconThumbUp, IconThumbDown, IconInfo } from '@/components/icons'

interface MessageBubbleProps {
  message: Message
  onFeedback: (msgId: string, feedback: 'up' | 'down') => void
}

export function MessageBubble({ message, onFeedback }: MessageBubbleProps) {
  const m = message

  return (
    <div className={`mb-4 ${m.role === 'user' ? 'text-right' : ''}`}>
      <div
        className={`inline-block max-w-[75%] rounded-lg px-4 py-3 text-body-sm leading-relaxed ${
          m.role === 'user'
            ? 'bg-ink text-on-primary'
            : 'bg-surface-card text-ink'
        }`}
      >
        {m.role === 'assistant' ? (
          <div className="markdown-content">
            <ReactMarkdown
              components={{
                h1: ({node, ...props}) => <h1 {...props} />,
                h2: ({node, ...props}) => <h2 {...props} />,
                h3: ({node, ...props}) => <h3 {...props} />,
                h4: ({node, ...props}) => <h4 {...props} />,
                p: ({node, ...props}) => <p {...props} />,
                ul: ({node, ...props}) => <ul {...props} />,
                ol: ({node, ...props}) => <ol {...props} />,
                li: ({node, ...props}) => <li {...props} />,
                strong: ({node, ...props}) => <strong {...props} />,
                em: ({node, ...props}) => <em {...props} />,
                a: ({node, ...props}) => <a {...props} target="_blank" rel="noopener noreferrer" />,
                code: ({node, inline, className, children, ...props}: any) => {
                  const match = /language-(\w+)/.exec(className || '')
                  return !inline ? (
                    <pre>
                      <code className={className} {...props}>{children}</code>
                    </pre>
                  ) : (
                    <code className={className} {...props}>{children}</code>
                  )
                },
                blockquote: ({node, ...props}) => <blockquote {...props} />,
                hr: ({node, ...props}) => <hr {...props} />,
                table: ({node, ...props}) => <div className="overflow-x-auto"><table {...props} /></div>,
              }}
            >
              {m.content}
            </ReactMarkdown>
          </div>
        ) : (
          <div className="whitespace-pre-wrap">{m.content}</div>
        )}

        {/* Citations */}
        {m.role === 'assistant' && m.citations && m.citations.length > 0 && (
          <div className="mt-3 border-t border-hairline pt-2">
            <p className="mb-1 flex items-center gap-1 text-caption-uppercase text-muted">
              <IconDocument className="h-3 w-3" />
              Sumber:
            </p>
            {m.citations.map((c, i) => (
              <details key={i} className="mt-1.5">
                <summary className="cursor-pointer rounded-sm bg-canvas/60 px-2 py-1 text-caption text-brand-teal hover:bg-canvas">
                  {c.document_name}
                  {c.bab ? ` — BAB ${c.bab}` : ''}
                  {c.pasal ? `, Pasal ${c.pasal}` : ''}
                  {c.ayat ? `, Ayat (${c.ayat})` : ''}
                </summary>
                <div className="mt-1 rounded-sm bg-canvas/80 p-2 text-caption text-body">
                  &ldquo;{c.excerpt}&rdquo;
                </div>
              </details>
            ))}
          </div>
        )}

        {/* Not-found indicator */}
        {m.role === 'assistant' && m.content.includes('Tidak ditemukan referensi') && (
          <div className="mt-2 flex items-start gap-1.5 rounded-sm bg-warning/10 px-2 py-1 text-caption text-warning">
            <IconInfo className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" />
            <span>Jawaban ini tidak memiliki referensi dokumen. Mungkin SOP terkait belum tersedia.</span>
          </div>
        )}

        {/* Feedback buttons */}
        {m.role === 'assistant' && !m.content.startsWith('Error') && (
          <div className="mt-2 flex items-center gap-2">
            <button
              onClick={() => onFeedback(m.id, 'up')}
              className={`rounded-sm p-1 ${
                m.feedback === 'up' ? 'text-success' : 'text-muted-soft hover:text-muted'
              }`}
              title="Bermanfaat"
            >
              <IconThumbUp className="h-4 w-4" />
            </button>
            <button
              onClick={() => onFeedback(m.id, 'down')}
              className={`rounded-sm p-1 ${
                m.feedback === 'down' ? 'text-error' : 'text-muted-soft hover:text-muted'
              }`}
              title="Tidak bermanfaat"
            >
              <IconThumbDown className="h-4 w-4" />
            </button>
            {m.feedback && (
              <span className="text-[10px] text-muted-soft">
                {m.feedback === 'up' ? 'Terima kasih atas masukan!' : 'Terima kasih, masukan akan dievaluasi.'}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
