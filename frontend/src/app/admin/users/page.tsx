'use client'

import { useCallback, useEffect, useState } from 'react'
import { listUsers, updateUser } from '@/lib/api'
import { useAuth } from '@/lib/auth'
import { useToast } from '@/components/Layout/Toast'
import { FormModal } from '@/components/ui/FormModal'

interface UserData {
  id: string
  username: string
  email: string
  full_name: string | null
  role_name: string
  department: string | null
  is_active: boolean
  created_at: string
  last_login: string | null
}

export default function UsersPage() {
  const { user } = useAuth()
  const { toast } = useToast()
  const [users, setUsers] = useState<UserData[]>([])
  const [editing, setEditing] = useState<UserData | null>(null)
  const [fullName, setFullName] = useState('')
  const [department, setDepartment] = useState('')
  const [roleId, setRoleId] = useState(0)
  const [isActive, setIsActive] = useState(true)

  const load = useCallback(async () => {
    try { setUsers(await listUsers()) } catch {}
  }, [])

  useEffect(() => { load() }, [load])

  function startEdit(u: UserData) {
    setEditing(u)
    setFullName(u.full_name || '')
    setDepartment(u.department || '')
    setIsActive(u.is_active)
    // role_name → role_id mapping
    const roleMap: Record<string, number> = { employee: 1, data_manager: 2, super_admin: 3 }
    setRoleId(roleMap[u.role_name] || 1)
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    if (!editing) return
    try {
      await updateUser(editing.id, { full_name: fullName || null, department: department || null, role_id: roleId, is_active: isActive })
      toast('User updated', 'success')
      setEditing(null)
      load()
    } catch (err: any) {
      toast(err.message, 'error')
    }
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-title-lg text-ink">Users</h1>
        <p className="mt-1 text-body-sm text-muted">Kelola pengguna sistem</p>
      </div>

      {/* Edit modal */}
      <FormModal open={!!editing} title={`Edit User: ${editing?.username || ''}`} onClose={() => setEditing(null)}>
        {editing && (
          <form onSubmit={handleSave} className="space-y-3">
            <div>
              <label className="mb-1.5 block text-nav-link text-body-strong">Full Name</label>
              <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)}
                className="input-field w-full" />
            </div>
            <div>
              <label className="mb-1.5 block text-nav-link text-body-strong">Department</label>
              <input type="text" value={department} onChange={(e) => setDepartment(e.target.value)}
                className="input-field w-full" />
            </div>
            <div>
              <label className="mb-1.5 block text-nav-link text-body-strong">Role</label>
              <select value={roleId} onChange={(e) => setRoleId(Number(e.target.value))}
                className="input-field w-full">
                <option value={1}>Employee</option>
                <option value={2}>Data Manager</option>
                <option value={3}>Super Admin</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="active" checked={isActive} onChange={(e) => setIsActive(e.target.checked)}
                className="h-4 w-4 rounded-sm" />
              <label htmlFor="active" className="text-nav-link text-body-strong">Active</label>
            </div>
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setEditing(null)}
                className="btn-secondary">Cancel</button>
              <button type="submit"
                className="btn-primary">Save</button>
            </div>
          </form>
        )}
      </FormModal>

      <div className="overflow-hidden card">
        <table className="w-full text-body-sm">
          <thead className="bg-surface-soft text-left text-caption-uppercase text-muted">
            <tr>
              <th className="px-4 py-3">Username</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Full Name</th>
              <th className="px-4 py-3">Role</th>
              <th className="px-4 py-3">Department</th>
              <th className="px-4 py-3">Active</th>
              <th className="px-4 py-3">Last Login</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-hairline">
            {users.map((u) => (
              <tr key={u.id} className="hover:bg-surface-soft">
                <td className="px-4 py-3 font-medium text-ink">{u.username}</td>
                <td className="px-4 py-3 text-body">{u.email}</td>
                <td className="px-4 py-3 text-body">{u.full_name || '-'}</td>
                <td className="px-4 py-3">
                  <span className={`inline-block rounded-pill px-2 py-0.5 text-caption ${
                    u.role_name === 'super_admin' ? 'bg-brand-pink/20 text-brand-pink' :
                    u.role_name === 'data_manager' ? 'bg-brand-teal/20 text-brand-teal' :
                    'bg-surface-card text-muted'
                  }`}>{u.role_name}</span>
                </td>
                <td className="px-4 py-3 text-body">{u.department || '-'}</td>
                <td className="px-4 py-3">
                  <span className={`inline-block h-2 w-2 rounded-full ${u.is_active ? 'bg-success' : 'bg-error'}`} />
                </td>
                <td className="px-4 py-3 text-muted">
                  {u.last_login ? new Date(u.last_login).toLocaleString() : 'Never'}
                </td>
                <td className="px-4 py-3">
                  {user?.role === 'super_admin' && (
                    <button onClick={() => startEdit(u)}
                      className="rounded-md bg-brand-teal/10 px-2 py-1 text-caption text-brand-teal hover:bg-brand-teal/20">Edit</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
