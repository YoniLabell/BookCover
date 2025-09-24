'use client'

import type { ValidationResult } from '@/lib/api'
import clsx from 'clsx'

interface ValidationReportProps {
  result: ValidationResult | null
  title?: string
}

export function ValidationReport({ result, title = 'Validation' }: ValidationReportProps) {
  if (!result) {
    return <p className="text-sm text-slate-400">No validation run yet.</p>
  }
  return (
    <div className="rounded border border-slate-800 bg-slate-900/60 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white">{title}</h3>
        <span className={clsx('rounded px-2 py-1 text-xs font-semibold uppercase', statusClass(result.status))}>
          {result.status}
        </span>
      </div>
      <dl className="space-y-2 text-sm">
        {result.checks.map((check) => (
          <div key={check.id} className="flex items-start justify-between gap-4">
            <dt className="text-slate-200">{check.id}</dt>
            <dd className={clsx('text-right text-xs font-semibold uppercase', check.ok ? 'text-emerald-400' : 'text-red-400')}>
              {check.ok ? 'pass' : 'fail'}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  )
}

function statusClass(status: ValidationResult['status']) {
  switch (status) {
    case 'pass':
      return 'bg-emerald-500/20 text-emerald-300'
    case 'warn':
      return 'bg-amber-500/20 text-amber-300'
    case 'fail':
    default:
      return 'bg-red-500/20 text-red-300'
  }
}
