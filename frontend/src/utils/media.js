// 新数据集的 poster_path 是 TMDB 相对路径（如 /abc.jpg），统一拼图片 CDN 前缀
const TMDB_IMG_BASE = 'https://image.tmdb.org/t/p/'

export function posterUrl (path, size = 'w300') {
  if (!path) return ''
  if (/^https?:\/\//.test(path)) return path
  return TMDB_IMG_BASE + size + (path.startsWith('/') ? path : '/' + path)
}

export function formatMoney (v) {
  if (v == null || v === '') return '-'
  return '$' + Number(v).toLocaleString('en-US', { maximumFractionDigits: 0 })
}

export function formatYi (v) {
  if (v == null || v === '') return '-'
  return (Number(v) / 1e8).toFixed(2) + ' 亿美元'
}
