import { Fragment, useMemo } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import { apiUrl } from '../../api/axiosClient';

// Ký hiệu trong nội dung câu hỏi: [[math:LaTeX]] = công thức, [[img:/uploads/...]] = ảnh (xem word_quiz_parser.py)
const TOKEN = /\[\[(math|img):([\s\S]*?)\]\]/g;

// Có ký hiệu ảnh / công thức / bảng không (để quyết định có cần xem trước)
export function hasRichTokens(text) {
  return /\[\[(math:|img:|table\]\])/.test(text || '');
}

// Công thức -> HTML của KaTeX; công thức lỗi hiện nguyên văn LaTeX màu đỏ thay vì làm vỡ trang.
// \displaystyle: phân số / tổng / tích phân hiện cỡ lớn như trong Word (kiểu nội dòng mặc định quá nhỏ để đọc đề)
function renderMath(latex) {
  try {
    return katex.renderToString(`\\displaystyle ${latex}`, { throwOnError: false, output: 'html', strict: 'ignore' });
  } catch {
    return null;
  }
}

// Bảng số liệu: [[table]]ô | ô || ô | ô[[/table]] (hàng cách nhau " || ", ô cách nhau " | "; ô có thể chứa công thức)
const TABLE = /\[\[table\]\]([\s\S]*?)\[\[\/table\]\]/g;

// Tách chuỗi theo 1 biểu thức ký hiệu -> [{kind: 'text'|..., value}]
function splitBy(src, re, kindOf) {
  const out = [];
  let last = 0;
  for (const m of src.matchAll(re)) {
    if (m.index > last) out.push({ kind: 'text', value: src.slice(last, m.index) });
    out.push(kindOf(m));
    last = m.index + m[0].length;
  }
  if (last < src.length) out.push({ kind: 'text', value: src.slice(last) });
  return out;
}

/** Bảng số liệu trong câu hỏi (hàng đầu là tiêu đề) */
function DataTable({ body }) {
  const rows = body.split(' || ').map((r) => r.split(' | '));
  return (
    <div style={{ overflowX: 'auto', margin: '0.5rem 0' }}>
      <table style={{ borderCollapse: 'collapse', fontSize: '0.9em', whiteSpace: 'normal' }}>
        <tbody>
          {rows.map((row, r) => (
            <tr key={r}>
              {row.map((cell, c) => (
                <td
                  key={c}
                  style={{
                    border: '1px solid var(--border, #cbd5e1)', padding: '0.3rem 0.6rem',
                    fontWeight: r === 0 ? 700 : 400, background: r === 0 ? 'var(--primary-light, #eff6ff)' : 'transparent',
                  }}
                >
                  <RichText text={cell} imgMaxHeight={120} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/**
 * Hiển thị nội dung câu hỏi / phương án / giải thích có chèn ảnh, công thức và bảng số liệu.
 * Phần chữ giữ nguyên (xuống dòng theo whiteSpace của thẻ cha); chỉ nhận ảnh nằm trong /uploads/images/.
 */
export default function RichText({ text, imgMaxHeight = 260 }) {
  const parts = useMemo(() => {
    // Bảng trước (ô bảng có thể chứa công thức), rồi tới ảnh / công thức trong phần chữ còn lại
    return splitBy(text || '', TABLE, (m) => ({ kind: 'table', value: m[1] })).flatMap((p) =>
      p.kind === 'text' ? splitBy(p.value, TOKEN, (m) => ({ kind: m[1], value: m[2] })) : [p],
    );
  }, [text]);

  return parts.map((p, i) => {
    if (p.kind === 'table') return <DataTable key={i} body={p.value} />;
    if (p.kind === 'math') {
      const html = renderMath(p.value);
      return html ? (
        <span key={i} className="rich-math" dangerouslySetInnerHTML={{ __html: html }} />
      ) : (
        <code key={i} style={{ color: 'var(--danger, #DC2626)' }}>{p.value}</code>
      );
    }
    if (p.kind === 'img') {
      // Chỉ hiện ảnh của hệ thống (đường dẫn tương đối /uploads/images/...), không nhúng ảnh ngoài
      if (!p.value.startsWith('/uploads/images/')) return <Fragment key={i}>[ảnh]</Fragment>;
      return (
        <img
          key={i}
          src={apiUrl(p.value)}
          alt="Hình minh họa"
          style={{ display: 'block', maxWidth: '100%', maxHeight: imgMaxHeight, margin: '0.4rem 0', borderRadius: 6 }}
        />
      );
    }
    return <Fragment key={i}>{p.value}</Fragment>;
  });
}
