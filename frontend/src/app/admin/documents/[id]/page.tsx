'use client'

import { useCallback, useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { getDocumentChunks, updateChunk as apiUpdateChunk, reparseDocument } from '@/lib/api'
import { useToast } from '@/components/Layout/Toast'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { IconArrowLeft } from '@/components/icons'

interface Chunk {
  id: string
  bab: string | null
  bab_judul: string | null
  pasal: string | null
  pasal_judul: string | null
  ayat: string | null
  teks: string
  halaman: number | null
  chunk_index: number
  document_title: string | null
}

export default function DocumentChunksPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const docId = params.id as string
  const [chunks, setChunks] = useState<Chunk[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState<string | null>(null)
  const [reparsing, setReparsing] = useState(false)
  const [reparseConfirm, setReparseConfirm] = useState(false)

  const fetchChunks = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getDocumentChunks(docId)
      setChunks(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [docId])

  useEffect(() => { fetchChunks() }, [fetchChunks])

  async function handleUpdateChunk(chunkId: string, field: string, value: string) {
    setSaving(chunkId)
    try {
      const updated = await apiUpdateChunk(chunkId, { [field]: value || null })
      setChunks((prev) => prev.map((c) => (c.id === chunkId ? updated : c)))
      toast('Chunk updated', 'success')
    } catch (err: any) {
      toast(err.message, 'error')
    } finally {
      setSaving(null)
    }
  }

  const [useAi, setUseAi] = useState(false)

  function handleReparseClick() {
    setReparseConfirm(true)
  }

  async function handleReparseConfirm() {
    const method = useAi ? 'AI-assisted' : 'regex'
    setReparsing(true)
    setReparseConfirm(false)
    try {
      await reparseDocument(docId, useAi)
      await fetchChunks()
      toast(`Document reparsed with ${method} parsing`, 'success')
    } catch (err: any) {
      toast(err.message, 'error')
    } finally {
      setReparsing(false)
    }
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <button
            onClick={() => router.push('/admin/documents')}
            className="mb-2 flex items-center gap-1 text-nav-link text-brand-teal hover:text-brand-teal/80"
          >
            <IconArrowLeft />
            Back to Documents
          </button>
          <h1 className="text-title-lg text-ink">Document Chunks</h1>
          <p className="mt-1 text-body-sm text-muted">
            {chunks.length > 0 ? chunks[0].document_title : 'Loading...'} &middot; {chunks.length} chunks
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-1.5 text-sm text-gray-600">
            <input
              type="checkbox"
              checked={useAi}
              onChange={(e) => setUseAi(e.target.checked)}
              className="h-4 w-4 rounded"
            />
            AI Parsing
          </label>
          <button
            onClick={handleReparseClick}
            disabled={reparsing}
            className="rounded-md border border-warning/30 bg-warning/10 px-4 py-2 text-button text-warning hover:bg-warning/20 disabled:opacity-50"
          >
            {reparsing ? 'Reparsing...' : 'Reparse Document'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded-md bg-error/10 p-3 text-body-sm text-error">{error}</div>
      )}

      {loading ? (
        <div className="card p-8 text-center text-muted">Loading...</div>
      ) : chunks.length === 0 ? (
        <div className="card p-8 text-center text-muted">
          No chunks found. Click &quot;Reparse Document&quot; to process this document.
        </div>
      ) : (
        <div className="space-y-4">
          {chunks.map((chunk) => (
            <div key={chunk.id} className="card p-4">
              <div className="mb-2 grid grid-cols-4 gap-2 text-body-sm">
                <div>
                  <label className="block text-caption text-muted">BAB</label>
                  <input
                    type="text"
                    defaultValue={chunk.bab || ''}
                    onBlur={(e) => {
                      if (e.target.value !== (chunk.bab || '')) {
                        handleUpdateChunk(chunk.id, 'bab', e.target.value)
                      }
                    }}
                    className="input-field mt-1 w-full"
                    placeholder="e.g. II"
                  />
                </div>
                <div>
                  <label className="block text-caption text-muted">Pasal</label>
                  <input
                    type="text"
                    defaultValue={chunk.pasal || ''}
                    onBlur={(e) => {
                      if (e.target.value !== (chunk.pasal || '')) {
                        handleUpdateChunk(chunk.id, 'pasal', e.target.value)
                      }
                    }}
                    className="input-field mt-1 w-full"
                    placeholder="e.g. 12"
                  />
                </div>
                <div>
                  <label className="block text-caption text-muted">Ayat</label>
                  <input
                    type="text"
                    defaultValue={chunk.ayat || ''}
                    onBlur={(e) => {
                      if (e.target.value !== (chunk.ayat || '')) {
                        handleUpdateChunk(chunk.id, 'ayat', e.target.value)
                      }
                    }}
                    className="input-field mt-1 w-full"
                    placeholder="e.g. 1"
                  />
                </div>
                <div>
                  <label className="block text-caption text-muted">Halaman</label>
                  <div className="mt-1 px-2 py-1 text-body-sm text-muted">
                    {chunk.halaman ?? '-'}
                  </div>
                </div>
              </div>

              <div className="mb-2 grid grid-cols-2 gap-2 text-body-sm">
                <div>
                  <label className="block text-caption text-muted">Judul BAB</label>
                  <input
                    type="text"
                    defaultValue={chunk.bab_judul || ''}
                    onBlur={(e) => {
                      if (e.target.value !== (chunk.bab_judul || '')) {
                        handleUpdateChunk(chunk.id, 'bab_judul', e.target.value)
                      }
                    }}
                    className="input-field mt-1 w-full"
                  />
                </div>
                <div>
                  <label className="block text-caption text-muted">Judul Pasal</label>
                  <input
                    type="text"
                    defaultValue={chunk.pasal_judul || ''}
                    onBlur={(e) => {
                      if (e.target.value !== (chunk.pasal_judul || '')) {
                        handleUpdateChunk(chunk.id, 'pasal_judul', e.target.value)
                      }
                    }}
                    className="input-field mt-1 w-full"
                  />
                </div>
              </div>

              <div>
                <label className="block text-caption text-muted">Teks</label>
                <div className="mt-1 max-h-32 overflow-y-auto rounded-md border border-hairline bg-surface-soft p-2 text-body-sm text-body">
                  {chunk.teks}
                </div>
              </div>

              {saving === chunk.id && (
                <p className="mt-1 text-caption text-success">Saving...</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Reparse Confirmation Dialog */}
      <ConfirmDialog
        open={reparseConfirm}
        title="Reparse Dokumen"
        message={`Semua chunk yang ada akan dihapus dan di-generate ulang menggunakan ${useAi ? 'AI-assisted' : 'regex'} parsing. Lanjutkan?`}
        confirmLabel="Reparse"
        cancelLabel="Batal"
        variant="warning"
        onConfirm={handleReparseConfirm}
        onCancel={() => setReparseConfirm(false)}
      />
    </div>
  )
}
