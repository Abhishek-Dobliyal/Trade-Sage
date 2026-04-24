/**
 * Format a number with Indian locale (e.g. 1,00,000.50).
 */
export function formatNum(n) {
  if (n == null) return '\u2014'
  return n.toLocaleString('en-IN', { maximumFractionDigits: 2 })
}

/**
 * Format an ISO timestamp as a relative time string.
 */
export function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const diff = Math.floor((Date.now() - d.getTime()) / 60000)
  if (diff < 60) return `${diff}m ago`
  if (diff < 1440) return `${Math.floor(diff / 60)}h ago`
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}

/**
 * Return Tailwind classes for a recommendation action badge.
 */
export function actionClass(action) {
  switch (action) {
    case 'BUY': return 'bg-emerald-500/20 text-emerald-400'
    case 'SELL': return 'bg-rose-500/20 text-rose-400'
    default: return 'bg-amber-500/20 text-amber-400'
  }
}
