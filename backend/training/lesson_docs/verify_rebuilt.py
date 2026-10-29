"""Read-only verification of local lesson PDF downloads and rebuilt RAG indexes."""
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pypdf import PdfReader
from app.core.database import SessionLocal, q_all, q_one
from app.core.media import resolve_upload_path, signed_src
from app.routers.lessons import router


def main():
    app = FastAPI()
    app.include_router(router)
    expected = {r['lesson_id']: r for r in json.loads((HERE / 'rebuilt/verification.json').read_text(encoding='utf-8'))}
    checked = []
    with SessionLocal() as db, TestClient(app) as client:
        user = q_one(db, "SELECT id,role,is_active FROM users WHERE role='admin' AND is_active=1 LIMIT 1")
        if not user:
            raise RuntimeError('No active admin to verify downloads')
        lessons = q_all(db, 'SELECT * FROM lessons ORDER BY id')
        for row in lessons:
            path = Path(resolve_upload_path(row['document_url']))
            pdf = PdfReader(path)
            text = '\n'.join(p.extract_text() or '' for p in pdf.pages)
            assert text.strip() and 'Mục tiêu bài học' in text and 'Câu hỏi ôn tập' in text, row['id']
            assert hashlib.sha256(path.read_bytes()).hexdigest() == expected[row['id']]['sha256'], row['id']
            parsed = urlsplit(signed_src(user, row, 'document'))
            response = client.get(parsed.path + '?' + parsed.query)
            assert response.status_code == 200 and response.content.startswith(b'%PDF'), row['id']
            docs = q_all(db, 'SELECT id,file_path,status,chunk_count FROM documents WHERE lesson_id=:lid', lid=row['id'])
            primary = [d for d in docs if Path(d['file_path']).resolve() == path.resolve()]
            assert primary and all(d['status'] == 'indexed' and d['chunk_count'] > 0 for d in primary), row['id']
            checked.append(dict(lesson_id=row['id'], pages=len(pdf.pages), download_status=response.status_code, indexed_documents=[d['id'] for d in primary]))
    (HERE / 'rebuilt/applied_verification.json').write_text(json.dumps(checked, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Verified {len(checked)} PDF downloads, hashes, objectives/review and primary RAG indexes.')


if __name__ == '__main__':
    main()
