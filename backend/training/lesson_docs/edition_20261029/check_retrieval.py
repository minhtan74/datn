"""Verify new material is retrievable in the exact course and lesson scope, without LLM calls."""
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import manage
from app.core.database import SessionLocal
from app.ai.rag.retriever import retrieve
from sqlalchemy import text

cases=[
 (1,2,'Sao print("2" + 3) báo lỗi, cần đổi số hay chuỗi?'),
 (2,11,'const rồi mà sao vẫn push vào array được?'),
 (3,20,'Scanner nextInt rồi đọc tên bị chuỗi rỗng, nên làm gì?'),
 (4,29,'Input cần label và dùng bàn phím như thế nào?'),
 (5,39,'setState nhiều lần nhưng không tăng đúng, nên dùng updater ra sao?'),
 (6,46,'Hai học sinh có cùng id khóa chính được không?'),
 (6,49,'Tìm học viên chưa ghi danh khóa nào bằng LEFT JOIN'),
 (7,55,'Máy mở nhiều app thì lag, có liên quan CPU RAM và I/O không?'),
 (513,351,'Connection refused và timeout khác nhau thế nào?'),
 (514,309,'bisect_left trả vị trí chèn, làm sao biết đã tìm thấy?'),
 (515,343,'AI trả HTTP 200 nhưng có thông báo lỗi thì có tính thành công không?'),
]
m=manage.load();by_lesson={x['id']:x for x in m['lessons']};results=[]
with SessionLocal()as db:
    for course,lesson,question in cases:
        found=retrieve(db,question,course_id=course,lesson_id=lesson,lesson_only=True,k=6)
        target=by_lesson[lesson]['document_id']
        passed=any(x['document_id']==target for x in found)
        assert found
        for row in found:
            doc=db.execute(text('SELECT course_id,lesson_id FROM documents WHERE id=:id'),{'id':row['document_id']}).mappings().one()
            assert doc['lesson_id']==lesson and doc['course_id']==course
        results.append({'course_id':course,'lesson_id':lesson,'question':question,'new_document_retrieved':passed,
                        'top_sources':[{'document_id':x['document_id'],'page':x['page'],'score':x['score']}for x in found]})
        print('Retrieval',lesson,passed,flush=True)
manage.dump(HERE/'generated'/'retrieval-validation.json',results)
assert all(x['new_document_retrieved']for x in results)
print('All',len(results),'scoped retrieval cases passed; no LLM calls or chat history created.')
