// Gom dữ liệu thật theo tháng cho các biểu đồ cột .bar-chart (6 tháng gần nhất, tính cả tháng hiện tại).
// API trả ngày dạng "YYYY-MM-DD HH:MM:SS" — đổi dấu cách thành "T" để Safari parse được.
function parseDate(str) {
  if (!str) return null;
  const d = new Date(String(str).replace(' ', 'T'));
  return Number.isNaN(d.getTime()) ? null : d;
}

// Tạo dữ liệu cột theo tháng: chia items vào từng tháng theo getDate, cộng dồn getValue,
// rồi quy chiều cao cột về % so với tháng cao nhất
export function monthlyBars(items, getDate, getValue = () => 1, formatValue = String, months = 6) {
  const now = new Date();
  const buckets = [];
  for (let i = months - 1; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    buckets.push({ key: `${d.getFullYear()}-${d.getMonth()}`, label: `Th${d.getMonth() + 1}`, value: 0 });
  }
  const index = new Map(buckets.map((b) => [b.key, b]));
  items.forEach((item) => {
    const d = parseDate(getDate(item));
    const b = d && index.get(`${d.getFullYear()}-${d.getMonth()}`);
    if (b) b.value += Number(getValue(item) || 0);
  });
  const max = Math.max(...buckets.map((b) => b.value));
  return buckets.map((b) => ({
    label: b.label,
    value: b.value,
    // Cột 0 vẫn hiện một vạch mỏng để thấy rõ tháng đó không có dữ liệu.
    height: max > 0 ? Math.max(2, Math.round((b.value / max) * 100)) : 2,
    tooltip: formatValue(b.value),
  }));
}
