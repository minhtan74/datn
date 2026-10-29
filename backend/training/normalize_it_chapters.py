"""Normalize chapter names only for the three newly added IT courses."""
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import text
from app.core.database import engine

SLUGS = ('mang-may-tinh-co-ban', 'cau-truc-du-lieu-giai-thuat-co-ban', 'kiem-thu-phan-mem-nhap-mon')


def chapter_title(name, order):
    base = re.sub(r'^chương\s+\d+\s*[:.\-–]?\s*', '', name.strip(), flags=re.IGNORECASE)
    return f'Chương {order}: {base}'


def normalize():
    changed = []
    with engine.begin() as conn:
        rows = conn.execute(text('''SELECT ch.id,ch.chapter_name,ch.order_index,c.slug
            FROM chapters ch JOIN courses c ON c.id=ch.course_id
            WHERE c.slug IN (:a,:b,:c) ORDER BY c.id,ch.order_index,ch.id'''),dict(zip(('a','b','c'),SLUGS))).mappings().all()
        for row in rows:
            title = chapter_title(row['chapter_name'], row['order_index'])
            if title != row['chapter_name']:
                conn.execute(text('UPDATE chapters SET chapter_name=:n WHERE id=:id'),dict(n=title,id=row['id']))
                changed.append(row['id'])
    return changed


if __name__ == '__main__':
    print(json.dumps({'updated_chapter_ids': normalize()}))
