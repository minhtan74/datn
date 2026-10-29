"""Verify and attach public YouTube videos to the three introductory IT courses.

--verify checks YouTube oEmbed and saves source metadata (no database writes).
--apply attaches verified links, preserving any existing video and lesson text.
No arguments: preview the target lessons without writing.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import text
from app.core.database import engine

MANIFEST = Path(__file__).with_name('it_course_videos.json')
# Slug, lesson title, video ID, expected original channel.
VIDEOS = [
    ('mang-may-tinh-co-ban', 'Mô hình TCP/IP và thiết bị mạng', 'wvPe4Zb0tUA', 'Neso Academy'),
    ('mang-may-tinh-co-ban', 'Địa chỉ IPv4 và mạng con', 'BWZ-MHIhqjM', 'Practical Networking'),
    ('mang-may-tinh-co-ban', 'DNS và phân giải tên miền', 'mpQZVYPuDGU', 'PowerCert Animated Videos'),
    ('mang-may-tinh-co-ban', 'HTTP và HTTPS', 'hExRDVZHhig', 'PowerCert Animated Videos'),
    ('cau-truc-du-lieu-giai-thuat-co-ban', 'Mảng và danh sách liên kết', 'lC-yYCOnN8Q', 'mycodeschool'),
    ('cau-truc-du-lieu-giai-thuat-co-ban', 'Ngăn xếp và hàng đợi', 'wjI1WNcIntg', 'HackerRank'),
    ('cau-truc-du-lieu-giai-thuat-co-ban', 'Tìm kiếm tuyến tính và nhị phân', 'j5uXyPJ0Pew', 'mycodeschool'),
    ('cau-truc-du-lieu-giai-thuat-co-ban', 'Sắp xếp và độ phức tạp', 'TzeBrDU-JaY', 'mycodeschool'),
    ('kiem-thu-phan-mem-nhap-mon', 'Mục tiêu và các mức kiểm thử', 'TDynSmrzpXw', 'Guru99'),
    ('kiem-thu-phan-mem-nhap-mon', 'Thiết kế test case', 'BBmA5Qp6Ghk', 'Guru99'),
    ('kiem-thu-phan-mem-nhap-mon', 'Phân vùng tương đương và giá trị biên', 'P1Hv2sUPKeM', 'Guru99'),
    ('kiem-thu-phan-mem-nhap-mon', 'Báo cáo lỗi và kiểm thử hồi quy', 'aeu5zacsHsI', 'Guru99'),
]


def fetch_metadata(video):
    slug, lesson, video_id, channel = video
    assert re.fullmatch(r'[A-Za-z0-9_-]{11}', video_id)
    url = f'https://www.youtube.com/watch?v={video_id}'
    endpoint = 'https://www.youtube.com/oembed?' + urlencode(dict(url=url, format='json'))
    request = Request(endpoint, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(request, timeout=25) as response:
        data = json.load(response)
    if data.get('author_name', '').casefold() != channel.casefold():
        raise RuntimeError(f'Unexpected video author: {video_id}')
    if f'/embed/{video_id}' not in data.get('html', ''):
        raise RuntimeError(f'No YouTube embed returned: {video_id}')
    return dict(course_slug=slug, lesson_title=lesson, video_id=video_id, url=url,
                title=data['title'], channel=data['author_name'], author_url=data.get('author_url'),
                language='en', checked_at=datetime.now(timezone.utc).isoformat(),
                verification='YouTube oEmbed metadata and embed URL; browser playback not verified')


def attach(apply=False):
    metadata = json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else []
    checked = {row['video_id']: row for row in metadata}
    report = []
    with engine.begin() as conn:
        for slug, title, video_id, channel in VIDEOS:
            matches = conn.execute(text('''SELECT l.id,l.video_url,l.description FROM lessons l
                JOIN chapters ch ON ch.id=l.chapter_id JOIN courses c ON c.id=ch.course_id
                WHERE c.slug=:slug AND l.title=:title'''), dict(slug=slug,title=title)).mappings().all()
            if len(matches) != 1:
                raise RuntimeError(f'Expected exactly one lesson: {slug} / {title}')
            lesson = matches[0]
            if lesson['video_url']:
                report.append(dict(lesson_id=lesson['id'],state='kept-existing'))
                continue
            if apply:
                source = checked.get(video_id)
                if not source or source['channel'] != channel:
                    raise RuntimeError(f'Run --verify before applying: {video_id}')
                url = f'https://www.youtube.com/watch?v={video_id}'
                description = (lesson['description'] or '') + f"\n\nVideo tham khảo (tiếng Anh): {source['title']} — {source['channel']}.\nNguồn gốc: {url}\nVideo minh họa một phần nội dung; đọc kết hợp bài học và bài tập tiếng Việt phía trên."
                conn.execute(text('UPDATE lessons SET video_url=:url,description=:description WHERE id=:id AND (video_url IS NULL OR video_url=\'\')'),dict(url=url,description=description,id=lesson['id']))
            report.append(dict(lesson_id=lesson['id'],video_id=video_id,state='attached' if apply else 'preview'))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--verify', action='store_true')
    group.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if args.verify:
        with ThreadPoolExecutor(max_workers=4) as pool:
            result = list(pool.map(fetch_metadata, VIDEOS))
        MANIFEST.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n',encoding='utf-8')
        print(f'YouTube oEmbed verified: {len(result)} videos')
    else:
        print(json.dumps(attach(args.apply),ensure_ascii=True,indent=2))
