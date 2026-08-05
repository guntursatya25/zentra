'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { listDocuments, uploadDocument, listCategories, deleteDocument as apiDeleteDocument, updateDocument, uploadDocumentVersion } from '@/lib/api'
import type { DocumentList, DocumentCategory } from '@/types'
import { useAuth } from '@/lib/auth'
import { useToast } from '@/components/Layout/Toast'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { FormModal } from '@/components/ui/FormModal'

export default function DocumentsPage() {
  const { user } = useAuth()
  const { toast } = useToast()
  const [docs, setDocs] = useState<DocumentList[]>([])
  const [categories, setCategories] = useState<DocumentCategory[]>([])
  const [showUpload, setShowUpload] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [showVersionUpload, setShowVersionUpload] = useState<string | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<{ open: boolean; id: string | null; title: string }>({ open: false, id: null, title: '' })
  const [editDoc, setEditDoc] = useState<{ id: string; title: string; categoryId: number | null; description: string } | null>(null)
  const [saving, setSaving] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const load = useCallback(async () => {
    try {
      const [d, c] = await Promise.all([listDocuments(), listCategories()])
      setDocs(d)
      setCategories(c)
    } catch {}
  }, [])

  useEffect(() => { load() }, [load])

  function handleDeleteClick(id: string, title: string) {
    setDeleteConfirm({ open: true, id, title })
  }

  async function handleDeleteConfirm() {
    if (!deleteConfirm.id) return
    try {
      await apiDeleteDocument(deleteConfirm.id)
      toast('Dokumen berhasil dihapus', 'success')
      load()
    } catch (err: any) {
      toast(err.message, 'error')
    } finally {
      setDeleteConfirm({ open: false, id: null, title: '' })
    }
  }

  function handleEditClick(doc: DocumentList) {
    setEditDoc({
      id: doc.id,
      title: doc.title,
      categoryId: doc.category_id ?? null,
      description: doc.description || '',
    })
  }

  async function handleEditSave(e: React.FormEvent) {
    e.preventDefault()
    if (!editDoc) return
    setSaving(true)
    try {
      const form = new FormData()
      form.append('title', editDoc.title)
      form.append('category_id', String(editDoc.categoryId ?? -1))
      form.append('description', editDoc.description)
      await updateDocument(editDoc.id, form)
      toast('Dokumen berhasil diupdate', 'success')
      setEditDoc(null)
      load()
    } catch (err: any) {
      toast(err.message, 'error')
    } finally {
      setSaving(false)
    }
  }

  async function changeStatus(id: string, newStatus: string) {
    try {
      const form = new FormData()
      form.append('status', newStatus)
      await updateDocument(id, form)
      toast(`Status changed to ${newStatus}`, 'success')
      load()
    } catch (err: any) {
      toast(err.message, 'error')
    }
  }

  async function uploadNewVersion(docId: string, file: File) {
    try {
      await uploadDocumentVersion(docId, file)
      toast('New version uploaded', 'success')
      setShowVersionUpload(null)
      load()
    } catch (err: any) {
      toast(err.message, 'error')
    }
  }

  async function handleUpload(form: FormData) {
    setUploading(true)
    try {
      const file = form.get('file') as File
      const title = (form.get('title') as string) || file.name
      const categoryId = form.get('category_id') ? Number(form.get('category_id')) : undefined
      const description = form.get('description') as string
      await uploadDocument(file, title, categoryId, description)
      setShowUpload(false)
      toast('Dokumen berhasil diupload!', 'success')
      load()
    } catch (err: any) {
      toast(err.message, 'error')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-title-lg text-ink">Documents</h1>
          <p className="mt-1 text-body-sm text-muted">Kelola dokumen kebijakan dan SOP</p>
        </div>
        <button
          onClick={() => setShowUpload(true)}
          className="btn-primary"
        >
          + Upload
        </button>
      </div>

      {/* Upload modal */}
      <FormModal open={showUpload} title="Upload Document" onClose={() => setShowUpload(false)}>
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleUpload(new FormData(e.currentTarget))
          }}
          className="space-y-3"
        >
          <div>
            <label className="mb-1.5 block text-nav-link text-body-strong">File (PDF/DOCX)</label>
            <input ref={fileRef} type="file" name="file" accept=".pdf,.docx" required
              className="mt-1 block w-full text-sm" />
          </div>
          <div>
            <label className="mb-1.5 block text-nav-link text-body-strong">Title</label>
            <input type="text" name="title" className="input-field w-full" />
          </div>
          <div>
            <label className="mb-1.5 block text-nav-link text-body-strong">Category</label>
            <select name="category_id" className="input-field w-full">
              <option value="">None</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1.5 block text-nav-link text-body-strong">Description</label>
            <textarea name="description" className="input-field w-full" rows={2} />
          </div>
          <div className="flex justify-end gap-2">
            <button type="button" onClick={() => setShowUpload(false)}
              className="btn-secondary">Cancel</button>
            <button type="submit" disabled={uploading}
              className="btn-primary">
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        </form>
      </FormModal>

      {/* New version upload modal */}
      <FormModal open={!!showVersionUpload} title="Upload New Version" onClose={() => setShowVersionUpload(null)} maxWidth="max-w-sm">
        <input type="file" accept=".pdf,.docx" onChange={(e) => {
          const file = e.target.files?.[0]
          if (file && showVersionUpload) uploadNewVersion(showVersionUpload, file)
        }} className="mb-4 block w-full text-sm" />
        <button onClick={() => setShowVersionUpload(null)}
          className="btn-secondary">Cancel</button>
      </FormModal>

      {/* Edit document modal */}
      <FormModal open={!!editDoc} title="Edit Dokumen" onClose={() => setEditDoc(null)}>
        {editDoc && (
          <form onSubmit={handleEditSave} className="space-y-3">
            <div>
              <label className="mb-1.5 block text-nav-link text-body-strong">Judul</label>
              <input
                type="text"
                value={editDoc.title}
                onChange={(e) => setEditDoc({ ...editDoc, title: e.target.value })}
                className="input-field w-full"
                required
              />
            </div>
            <div>
              <label className="mb-1.5 block text-nav-link text-body-strong">Kategori</label>
              <select
                value={editDoc.categoryId ?? ''}
                onChange={(e) => setEditDoc({ ...editDoc, categoryId: e.target.value ? Number(e.target.value) : null })}
                className="input-field w-full"
              >
                <option value="">Tidak ada</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1.5 block text-nav-link text-body-strong">Deskripsi</label>
              <textarea
                value={editDoc.description}
                onChange={(e) => setEditDoc({ ...editDoc, description: e.target.value })}
                className="input-field w-full"
                rows={3}
              />
            </div>
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setEditDoc(null)}
                className="btn-secondary">Batal</button>
              <button type="submit" disabled={saving}
                className="btn-primary">
                {saving ? 'Menyimpan...' : 'Simpan'}
              </button>
            </div>
          </form>
        )}
      </FormModal>

      {/* Table */}
      <div className="overflow-hidden card">
        <table className="w-full text-body-sm">
          <thead className="bg-surface-soft text-left text-caption-uppercase text-muted">
            <tr>
              <th className="px-4 py-3">Title</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Version</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Created</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-hairline">
            {docs.map((d) => (
              <tr key={d.id} className="hover:bg-surface-soft">
                <td className="px-4 py-3 font-medium text-ink">{d.title}</td>
                <td className="px-4 py-3 text-body">{d.category_name || '-'}</td>
                <td className="px-4 py-3 text-body">{d.file_type}</td>
                <td className="px-4 py-3 text-body">v{d.version}</td>
                <td className="px-4 py-3">
                  {user?.role !== 'employee' ? (
                    <select
                      value={d.status}
                      onChange={(e) => changeStatus(d.id, e.target.value)}
                      className={`rounded-pill px-2 py-0.5 text-caption cursor-pointer border-0 ${
                        d.status === 'active' ? 'bg-success/20 text-success' :
                        d.status === 'draft' ? 'bg-warning/20 text-warning' :
                        d.status === 'archived' ? 'bg-surface-strong text-muted' :
                        'bg-surface-card text-muted'
                      }`}
                    >
                      <option value="draft">draft</option>
                      <option value="active">active</option>
                      <option value="inactive">inactive</option>
                      <option value="archived">archived</option>
                    </select>
                  ) : (
                    <span className={`inline-block rounded-pill px-2 py-0.5 text-caption ${
                      d.status === 'active' ? 'bg-success/20 text-success' :
                      d.status === 'draft' ? 'bg-warning/20 text-warning' :
                      'bg-surface-card text-muted'
                    }`}>{d.status}</span>
                  )}
                </td>
                <td className="px-4 py-3 text-muted">{new Date(d.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Link
                      href={`/admin/documents/${d.id}`}
                      className="rounded-md bg-brand-teal/10 px-2 py-1 text-caption text-brand-teal hover:bg-brand-teal/20"
                    >
                      Chunks
                    </Link>
                    {user?.role !== 'employee' && (
                      <>
                        <button
                          onClick={() => handleEditClick(d)}
                          className="rounded-md bg-brand-lavender/10 px-2 py-1 text-caption text-brand-lavender hover:bg-brand-lavender/20"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => setShowVersionUpload(d.id)}
                          className="rounded-md bg-success/10 px-2 py-1 text-caption text-success hover:bg-success/20"
                        >
                          New Version
                        </button>
                        <button
                          onClick={() => handleDeleteClick(d.id, d.title)}
                          className="rounded-md bg-error/10 px-2 py-1 text-caption text-error hover:bg-error/20"
                        >
                          Hapus
                        </button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {docs.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-muted">
                  No documents yet. Click &quot;+ Upload&quot; to add one.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={deleteConfirm.open}
        title="Hapus Dokumen"
        message={`Apakah Anda yakin ingin menghapus dokumen "${deleteConfirm.title}"? Semua chunk dan data terkait akan dihapus permanen.`}
        confirmLabel="Hapus"
        cancelLabel="Batal"
        variant="danger"
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteConfirm({ open: false, id: null, title: '' })}
      />
    </div>
  )
}
