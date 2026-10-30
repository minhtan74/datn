"""Câu đời thường thiếu thông tin, câu ngắn đã rõ và nối tiếp hội thoại. Không gọi dịch vụ AI."""
import pytest

from app.ai.rag import clarification, rag_pipeline

SELF_CONTAINED = [
    "Máy một lõi có làm đồng thời nhiều việc được không, điều đó có phải song song thật trên lõi đó không?",
    "HashMap.put cùng một khóa hai lần có tự báo lỗi trùng không? Nếu cần từ chối trùng nên làm gì?",
    "Sau khi sửa lỗi ghi danh trùng, chạy lại đúng ca từng gây lỗi đã thay thế được kiểm thử hồi quy chưa? Phân biệt confirmation testing với regression testing.",
    "may mot loi co lam dong thoi nhieu viec duoc khong, dieu do co phai song song that tren loi do khong?",
    "hashmap.put cung mot khoa hai lan co tu bao loi trung khong?",
    "Phân biệt confirmation testing và regression testing sau sửa lỗi.",
    "Em muốn so sánh lỗi biên dịch và lỗi runtime.",
    "Vòng lặp for trong Python, nó hoạt động thế nào?",
    "Một Promise có những trạng thái nào và nó chuyển trạng thái ra sao?",
    "Deadlock có thật sự làm các tiến trình chờ nhau không?",
    "Cách tránh IndexError khi duyệt danh sách Python?",
    "fetch nhận HTTP404 có tự báo lỗi không?",
]


@pytest.mark.parametrize("question", SELF_CONTAINED)
def test_self_contained_questions_reach_retrieval_without_generic_clarification(monkeypatch, question):
    queries = []
    monkeypatch.setattr(rag_pipeline.model_manager, "active_provider", lambda: "stub")
    monkeypatch.setattr(rag_pipeline.retriever, "retrieve", lambda db, query, **kw: queries.append(query) or [])
    result = rag_pipeline.answer(None, question, course_id=1)
    assert not result.get("needs_clarification")
    assert queries == [question]


@pytest.mark.parametrize("question,kind", [
    ("Code Python của em bị lỗi", "debug"), ("Chương trình Java của tôi không chạy", "debug"),
    ("Trong Python, nó là gì?", "topic"), ("Hàm này hoạt động thế nào?", "topic"),
    ("Nó có an toàn không?", "topic"), ("Sao code của em chạy không được?", "debug"),
    ("what is that?", "topic"), ("Explain it", "topic"),
])
def test_specificity_fix_still_asks_for_actually_missing_information(question, kind):
    assert clarification.request_kind(question) == kind


def test_complete_question_with_reference_becomes_anchor_and_does_not_inherit_old_topic():
    question = "Vòng lặp for trong Python, nó hoạt động thế nào?"
    old = [{"role": "user", "content": "HTTP là gì?"}, {"role": "assistant", "content": "HTTP là giao thức."}]
    assert rag_pipeline._search_query(question, old, use_llm=False) == question
    history = old + [{"role": "user", "content": question}, {"role": "assistant", "content": "for duyệt các phần tử."}]
    assert clarification.anchor_question(history) == question
    assert "Python" in rag_pipeline._search_query("Cho ví dụ đi", history, use_llm=False)


def test_clear_comparison_can_start_new_topic_after_a_debug_clarification():
    history = [{"role": "user", "content": "code em bị lỗi"}, {"role": "assistant", "content": "Bạn gửi code nhé.",
               "needs_clarification": True, "clarification_kind": "debug"}]
    question = "So sánh SQL JOIN và UNION"
    assert clarification.request_kind(question, history) is None
    assert rag_pipeline._search_query(question, history, use_llm=False) == question


MISSING = [
    ("Giải thích giúp em", "topic"), ("giai thich giup em", "topic"),
    ("Cái này là gì?", "topic"), ("Nó hoạt động thế nào?", "topic"),
    ("cho ví dụ đi", "topic"), ("Mình không hiểu chỗ này", "topic"),
    ("code em bị lỗi", "debug"), ("web em không chạy", "debug"),
    ("sao chạy không được?", "debug"), ("Sửa lỗi giúp mình", "debug"),
    ("Giải câu 2 giúp em", "exercise"), ("giải bài tập này", "exercise"),
    ("So sánh giúp em", "comparison"), ("Nên chọn cái nào?", "comparison"),
    ("explain this", "topic"), ("why doesn't it work?", "debug"),
    ("Sao lại vậy?", "topic"), ("Giải câu 5 của bài này", "exercise"),
]


@pytest.mark.parametrize("question,kind", MISSING)
def test_missing_information_asks_without_retrieval_or_llm(monkeypatch, question, kind):
    def unexpected(*args, **kwargs):
        pytest.fail("Câu hỏi chưa rõ không cần gọi truy hồi/embedding/LLM")
    monkeypatch.setattr(rag_pipeline.retriever, "retrieve", unexpected)
    monkeypatch.setattr(rag_pipeline.model_manager, "active_provider", unexpected)
    monkeypatch.setattr(rag_pipeline.model_manager, "generate", unexpected)
    result = rag_pipeline.answer(None, question, course_id=1)
    assert result["needs_clarification"] is True and result["clarification_kind"] == kind
    assert result["answer"] == clarification.PROMPTS[kind]
    assert result["sources"] == [] and result["used_context"] is False


@pytest.mark.parametrize("question", [
    "HTTP là gì?", "SQL JOIN", "Python", "IT là gì?", "AI là gì?", "AI", "Lỗi TypeError là gì?",
    "So sánh PUT và PATCH", "REST vs GraphQL", "Promise có những trạng thái nào?",
    "giai thich SQL JOIN", "Em không hiểu vòng lặp for trong Python",
    "Giải câu 2: tính 2 + 2", "Sao code bị lỗi: print(1 / 0)",
    "Cách nấu phở bò gia truyền?", "MongoDB là gì?",
])
def test_clear_questions_still_go_to_course_retrieval(monkeypatch, question):
    queries = []
    monkeypatch.setattr(rag_pipeline.model_manager, "active_provider", lambda: "stub")
    monkeypatch.setattr(rag_pipeline.retriever, "retrieve", lambda db, query, **kw: queries.append((query, kw)) or [])
    result = rag_pipeline.answer(None, question, course_id=12, lesson_id=34, lesson_only=True)
    assert not result.get("needs_clarification")
    assert queries == [(question, {"course_id": 12, "lesson_id": 34, "lesson_only": True})]
    assert result["answer"] == rag_pipeline.NO_ANSWER and result["sources"] == []


def exchange(question="HTTP là gì?", answer="HTTP là giao thức truyền tải.", **metadata):
    return [{"role": "user", "content": question}, {"role": "assistant", "content": answer, **metadata}]


@pytest.mark.parametrize("question", ["Cho ví dụ đi", "Nó hoạt động thế nào?", "giải thích thêm nữa"])
def test_known_followup_uses_existing_subject(question):
    history = exchange()
    assert clarification.request_kind(question, history) is None
    query = rag_pipeline._search_query(question, history, use_llm=False)
    assert "HTTP" in query and question in query


@pytest.mark.parametrize("reply", [rag_pipeline.NO_ANSWER, "[Lỗi gọi LLM: HTTP 429]"])
def test_refusal_or_error_is_not_a_resolved_subject(reply):
    assert clarification.request_kind("Nó hoạt động thế nào?", exchange(answer=reply)) == "topic"


def test_new_subject_does_not_inherit_old_subject_or_call_rewrite(monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("Câu mới đã rõ không cần viết lại")
    monkeypatch.setattr(rag_pipeline.model_manager, "generate", unexpected)
    assert rag_pipeline._search_query("SQL JOIN là gì?", exchange(), use_llm=True) == "SQL JOIN là gì?"


def test_clarification_reply_keeps_original_intent_and_can_change_subject():
    history = exchange("Cho ví dụ đi", clarification.PROMPTS["topic"], needs_clarification=True, clarification_kind="topic")
    assert clarification.request_kind("Python", history) is None
    query = rag_pipeline._search_query("Python", history, use_llm=False)
    assert "Cho ví dụ" in query and "Python" in query
    assert rag_pipeline._search_query("HTTP là gì?", history, use_llm=False) == "HTTP là gì?"


def test_only_language_name_is_not_enough_to_fix_an_unspecified_bug():
    history = exchange("code em bị lỗi", clarification.PROMPTS["debug"], needs_clarification=True, clarification_kind="debug")
    assert clarification.request_kind("Python", history) == "debug"
    assert clarification.request_kind("print(1 / 0)", history) is None
    assert clarification.request_kind("HTTP là gì?", history) is None


def test_previous_topic_does_not_supply_unknown_exercise_text():
    assert clarification.request_kind("Giải câu 2", exchange()) == "exercise"


def test_several_followups_keep_the_resolved_subject():
    history = exchange() + exchange("Cho ví dụ đi", "Ví dụ về HTTP: trình duyệt gửi GET.")
    assert clarification.request_kind("Giải thích thêm nữa", history) is None
    assert "HTTP" in rag_pipeline._search_query("Giải thích thêm nữa", history, use_llm=False)


def test_rewrite_failure_still_keeps_known_context(monkeypatch):
    monkeypatch.setattr(rag_pipeline.model_manager, "generate", lambda *a, **kw: "[Lỗi gọi LLM: HTTP 429]")
    assert "HTTP" in rag_pipeline._search_query("Cho ví dụ đi", exchange(), use_llm=True)


def test_friendly_service_error_is_not_a_resolved_subject():
    history = exchange(answer=rag_pipeline.AI_UNAVAILABLE, response_status="error")
    assert clarification.request_kind("Nó là gì?", history) == "topic"


@pytest.mark.parametrize("fallback", [False, True])
def test_llm_service_failure_is_distinct_from_knowledge_answer(monkeypatch, fallback):
    score = .9 if fallback else .35
    chunk = {"document_id": 1, "document_title": "HTTP", "page": 1, "score": score, "cosine": score,
             "content": "HTTP là giao thức trao đổi dữ liệu."}
    monkeypatch.setattr(rag_pipeline.model_manager, "active_provider", lambda: "gemini")
    monkeypatch.setattr(rag_pipeline.retriever, "retrieve", lambda *a, **kw: [chunk])
    monkeypatch.setattr(rag_pipeline.retriever, "expand_neighbors", lambda db, rows: rows)
    monkeypatch.setattr(rag_pipeline.model_manager, "generate", lambda *a, **kw: "[Lỗi gọi LLM: ReadTimeout]")
    monkeypatch.setattr(rag_pipeline.extractive, "answer", lambda *a, **kw: chunk["content"])
    result = rag_pipeline.answer(None, "HTTP là gì?", course_id=1)
    if fallback:
        assert result["response_status"] == "fallback" and result["used_context"]
        assert result["sources"] and chunk["content"] in result["answer"]
    else:
        assert result["response_status"] == "error" and result["retryable"]
        assert result["error_code"] == "ai_unavailable" and not result["sources"] and not result["used_context"]
        assert result["answer"] == rag_pipeline.AI_UNAVAILABLE
        assert "ReadTimeout" not in result["answer"] and "[Lỗi gọi LLM" not in result["answer"]


def test_llm_clarification_never_gets_fabricated_citations(monkeypatch):
    chunk = {"document_id": 1, "document_title": "Buffer", "page": 1, "score": .9, "cosine": .9,
             "content": "Tài liệu mô tả nhiều loại buffer."}
    monkeypatch.setattr(rag_pipeline.model_manager, "active_provider", lambda: "gemini")
    monkeypatch.setattr(rag_pipeline.retriever, "retrieve", lambda *a, **kw: [chunk])
    monkeypatch.setattr(rag_pipeline.retriever, "expand_neighbors", lambda db, rows: rows)
    monkeypatch.setattr(rag_pipeline.model_manager, "generate", lambda *a, **kw: "[CẦN LÀM RÕ] Bạn đang hỏi buffer trong ngữ cảnh nào?")
    result = rag_pipeline.answer(None, "Buffer là gì?", course_id=1)
    assert result["needs_clarification"] and result["sources"] == [] and not result["used_context"]
    assert result["answer"] == "Bạn đang hỏi buffer trong ngữ cảnh nào?"
