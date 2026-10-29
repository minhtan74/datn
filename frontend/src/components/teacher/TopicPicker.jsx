import { useEffect, useState } from 'react';
import { topicService } from '../../services/topicService';

const normalized = (value) => (value || '').normalize('NFC').trim().replace(/\s+/g, ' ').toLocaleLowerCase('vi');
export default function TopicPicker({ courseId, topicId, topicName = '', onSelect }) {
  const [topics, setTopics] = useState([]);
  const [adding, setAdding] = useState(false);
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    let alive = true;
    const load = async () => {
      if (!courseId) return;
      const res = await topicService.get(courseId);
      if (alive) {
        setTopics(res?.data?.data?.topics || []);
        if (!res?.ok) setError(res?.data?.message || 'Không tải được danh mục chủ đề.');
      }
    };
    load();
    window.addEventListener('topic-catalog-changed', load);
    return () => { alive = false; window.removeEventListener('topic-catalog-changed', load); };
  }, [courseId]);
  const selected = topics.find((t) => Number(t.id) === Number(topicId)) || topics.find((t) => normalized(t.name) === normalized(topicName));
  async function add() {
    setBusy(true); setError('');
    const res = await topicService.create(courseId, name || topicName);
    setBusy(false);
    if (!res?.ok) { setError(res?.data?.message || 'Không thêm được chủ đề.'); return; }
    const topic = res.data.data;
    onSelect(topic.id, topic.name);
    topicService.invalidate(courseId);
    window.dispatchEvent(new Event('topic-catalog-changed'));
    setAdding(false); setName('');
  }
  return <div>
    <select className="form-control" aria-label="Chủ đề kiến thức" value={selected?.id || (topicName ? 'unlisted' : '')}
      disabled={!courseId || busy} onChange={(e) => {
        if (e.target.value === 'new') { setAdding(true); setName(topicName); return; }
        const topic = topics.find((t) => String(t.id) === e.target.value);
        onSelect(topic?.id || null, topic?.name || '');
      }}>
      <option value="">Chưa phân loại nội dung</option>
      {topicName && !selected && <option value="unlisted">Chủ đề đề xuất: {topicName}</option>}
      {topics.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
      <option value="new">+ Thêm chủ đề vào danh mục</option>
    </select>
    {adding && <div style={{ display: 'flex', gap: '.5rem', marginTop: '.5rem' }}>
      <input aria-label="Tên chủ đề mới" className="form-control" maxLength={100} value={name} onChange={(e) => setName(e.target.value)} />
      <button type="button" className="btn btn-primary btn-sm" disabled={busy || !(name || topicName).trim()} onClick={add}>Thêm</button>
      <button type="button" className="btn btn-ghost btn-sm" onClick={() => setAdding(false)}>Hủy</button>
    </div>}
    <small>Chọn cùng chủ đề cho các câu cùng nội dung để thống kê và gợi ý ôn tập. Có thể thêm chủ đề ngay tại đây.</small>
    {error && <div role="alert" style={{ color: '#DC2626' }}>{error}</div>}
  </div>;
}
