'use client'

import { useCallback, useEffect, useState } from 'react'
import { listCategories, createCategory, updateCategory, deleteCategory } from '@/lib/api'
import type { DocumentCategory } from '@/types'
import { useAuth } from '@/lib/auth'
import { useToast } from '@/components/Layout/Toast'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'

export default function CategoriesPage() {
  const { user } = useAuth()
  const { toast } = useToast()
  const [categories, setCategories] = useState<DocumentCategory[]>([])
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState<{ open: boolean; id: number | null; name: string }>({ open: false, id: null, name: '' })

  const load = useCallback(async () => {
    try {
      setCategories(await listCategories())
    } catch {}
  }, [])

  useEffect(() => { load() }, [load])

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    try {
      if (editingId) {
        await updateCategory(editingId, { name, description: description || null })
        toast('Category updated', 'success')
      } else {
        await createCategory(name, description || undefined)
        toast('Category created', 'success')
      }
      setName(''); setDescription(''); setShowForm(false); setEditingId(null)
      load()
    } catch (err: any) {
      toast(err.message, 'error')
    }
  }

  function handleDeleteClick(id: number, name: string) {
    setDeleteConfirm({ open: true, id, name })
  }

  async function handleDeleteConfirm() {
    if (!deleteConfirm.id) return
    try {
      await deleteCategory(deleteConfirm.id)
      toast('Kategori berhasil dihapus', 'success')
      load()
    } catch (err: any) {
      toast(err.message, 'error')
    } finally {
      setDeleteConfirm({ open: false, id: null, name: '' })
    }
  }

  function startEdit(cat: DocumentCategory) {
    setEditingId(cat.id)
    setName(cat.name)
    setDescription(cat.description || '')
    setShowForm(true)
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-title-lg text-ink">Categories</h1>
          <p className="mt-1 text-body-sm text-muted">Kelola kategori dokumen</p>
        </div>
        {user?.role === 'super_admin' && (
          <button onClick={() => { setEditingId(null); setName(''); setDescription(''); setShowForm(true) }}
            className="btn-primary">
            + Add Category
          </button>
        )}
      </div>

      {showForm && (
        <div className="mb-6 card p-4">
          <form onSubmit={handleSave} className="space-y-3">
            <div>
              <label className="mb-1.5 block text-nav-link text-body-strong">Name</label>
              <input type="text" required value={name} onChange={(e) => setName(e.target.value)}
                className="input-field w-full" />
            </div>
            <div>
              <label className="mb-1.5 block text-nav-link text-body-strong">Description</label>
              <textarea value={description} onChange={(e) => setDescription(e.target.value)}
                className="input-field w-full" rows={2} />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn-primary">
                {editingId ? 'Update' : 'Save'}
              </button>
              <button type="button" onClick={() => { setShowForm(false); setEditingId(null) }}
                className="btn-secondary">Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="overflow-hidden card">
        <table className="w-full text-body-sm">
          <thead className="bg-surface-soft text-left text-caption-uppercase text-muted">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Description</th>
              <th className="px-4 py-3">Created</th>
              {user?.role === 'super_admin' && <th className="px-4 py-3">Actions</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-hairline">
            {categories.map((c) => (
              <tr key={c.id} className="hover:bg-surface-soft">
                <td className="px-4 py-3 font-medium text-ink">{c.name}</td>
                <td className="px-4 py-3 text-body">{c.description || '-'}</td>
                <td className="px-4 py-3 text-muted">{new Date(c.created_at).toLocaleDateString()}</td>
                {user?.role === 'super_admin' && (
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <button onClick={() => startEdit(c)}
                        className="rounded-md bg-brand-teal/10 px-2 py-1 text-caption text-brand-teal hover:bg-brand-teal/20">Edit</button>
                      <button onClick={() => handleDeleteClick(c.id, c.name)}
                        className="rounded-md bg-error/10 px-2 py-1 text-caption text-error hover:bg-error/20">Hapus</button>
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={deleteConfirm.open}
        title="Hapus Kategori"
        message={`Apakah Anda yakin ingin menghapus kategori "${deleteConfirm.name}"? Dokumen dalam kategori ini tidak akan dihapus.`}
        confirmLabel="Hapus"
        cancelLabel="Batal"
        variant="danger"
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteConfirm({ open: false, id: null, name: '' })}
      />
    </div>
  )
}
