"""Gộp đánh giá từng câu đã đối chiếu nội dung; không tự mặc định câu không lỗi là đúng."""
import csv
import json
import math
from pathlib import Path
import statistics
import sys

sys.stdout.reconfigure(encoding="utf-8")
D = Path(__file__).resolve().parent
P = "ai-accuracy-current-2026-10-30"
read = lambda name: json.loads((D / name).read_text(encoding="utf-8"))
raw = [row for phase in ("baseline", "extra", "clarification") for row in read(f"{P}-{phase}-results.json")]
states = {phase: read(f"{P}-{phase}-state.json") for phase in ("baseline", "extra", "clarification")}
reviews = [row for name in ("student", "manager", "new") for row in read(f"{P}-{name}-review.json")]
assert len(raw) == 68 and len({r["id"] for r in raw}) == 68
assert len(reviews) == 60 and len({r["id"] for r in reviews}) == 60
by_review = {r["id"]: r for r in reviews}
assert set(by_review) == {r["id"] for r in raw if r["group"] != "clarification"}
assert all(s["recorded"] == expected for s, expected in zip(states.values(), [50, 10, 8]))
assert all(s["counts_restored"] and s["code_unchanged"] for s in states.values())
assert len({json.dumps(s["code_before"], sort_keys=True) for s in states.values()}) == 1
assert all(r["cleaned"] for r in raw)

graded = []
for row in raw:
    if row["group"] == "clarification":
        passed = (row.get("needs_clarification") is True and row.get("clarification_kind") == row["gold"]
                  and row.get("sources") == [] and row.get("used_context") is False and bool(row.get("answer")))
        review = {"score": 2 if passed else 0, "verdict": "correct_clarification" if passed else "incorrect_clarification",
                  "review": "Hỏi đúng loại thông tin còn thiếu, không tự đưa kết luận hay gắn nguồn cho lời hỏi lại."
                            if passed else "Chưa hỏi đúng thông tin cần bổ sung theo rubric.",
                  "citation_core_support": "no_sources", "supporting_chunk_ids": [],
                  "hallucinated_material_claim": False if passed else None, "reviewer": "clarification_control_check"}
    else:
        review = by_review[row["id"]]
        assert review["score"] in (0, 1, 2)
        cited = {chunk["id"] for e in row.get("citation_evidence", []) for chunk in e["chunks"]}
        assert set(review["supporting_chunk_ids"]).issubset(cited)
        if review["score"] == 2 and row["group"] == "knowledge":
            assert not row.get("refused") and not row.get("needs_clarification") and not row.get("error")
    graded.append({**row, **review})

knowledge = [r for r in graded if r["group"] == "knowledge"]
boundary = [r for r in graded if r["group"] == "boundary"]
clarification = [r for r in graded if r["group"] == "clarification"]
correct = [r for r in knowledge if r["score"] == 2]
failed = [r for r in knowledge if r["score"] != 2]
sourced = [r for r in correct if r["citation_core_support"] == "supported"]
substantive = [r for r in knowledge if r.get("answer") and not r.get("refused")
               and not r.get("needs_clarification") and not r.get("llm_error") and not r.get("error")]
percent = lambda a, b: round(a / b * 100, 2) if b else None
assert len(knowledge) == 50 and len(boundary) == 10 and len(clarification) == 8
times = sorted(r["elapsed_seconds"] for r in graded)

# Tên khóa từ bảng danh mục đã kiểm tra, không suy ra từ tên tài liệu của câu trả lời.
titles = {1: "Python cơ bản", 2: "JavaScript", 3: "Java", 4: "HTML & CSS", 5: "ReactJS", 6: "MySQL",
          7: "Nguyên lí hệ điều hành", 513: "Mạng máy tính", 514: "Cấu trúc dữ liệu và giải thuật", 515: "Kiểm thử phần mềm"}
per_course = []
for course in sorted({r["course_id"] for r in knowledge}):
    group = [r for r in knowledge if r["course_id"] == course]
    count = sum(r["score"] == 2 for r in group)
    per_course.append({"course_id": course, "title": titles[course], "correct": count, "total": len(group), "percent": percent(count, len(group))})

summary = {
    "date": "2026-10-30", "engine": states["baseline"]["engine"], "total_cases": len(graded),
    "knowledge_total": len(knowledge), "correct_complete": len(correct), "strict_knowledge_accuracy_percent": percent(len(correct), len(knowledge)),
    "partial": sum(r["score"] == 1 for r in knowledge), "refused_knowledge": sum(r.get("refused", False) for r in knowledge),
    "unnecessary_clarifications": sum(r.get("needs_clarification", False) for r in knowledge),
    "factual_errors": sum(r["hallucinated_material_claim"] is True for r in knowledge),
    "correct_and_cited_core_supported": len(sourced), "grounded_end_to_end_percent": percent(len(sourced), len(knowledge)),
    "citation_core_supported_among_correct": percent(len(sourced), len(correct)),
    "substantive_answers": len(substantive), "correct_among_substantive_percent": percent(len(correct), len(substantive)),
    "fixed_knowledge_correct": sum(r["score"] == 2 for r in knowledge if r["sample"] == "fixed"), "fixed_knowledge_total": 40,
    "new_knowledge_correct": sum(r["score"] == 2 for r in knowledge if r["sample"] == "new"), "new_knowledge_total": 10,
    "boundary_correct": sum(r["score"] == 2 for r in boundary), "boundary_total": len(boundary),
    "clarification_correct": sum(r["score"] == 2 for r in clarification), "clarification_total": len(clarification),
    "citation_metadata_valid": all(r.get("citation_metadata_valid", True) for r in raw if r.get("sources")),
    "citations_total": sum(len(r.get("sources", [])) for r in raw),
    "fallback_answers": sum(r.get("fallback", False) for r in raw),
    "transport_or_llm_errors": sum(bool(r.get("error")) or r.get("llm_error", False) for r in raw),
    "per_course": per_course, "latency_seconds": {"median": statistics.median(times), "mean": statistics.mean(times),
                                                  "p95_nearest_rank": times[math.ceil(.95 * len(times)) - 1], "max": max(times)},
    "code_unchanged_across_phases": True, "counts_before": states["baseline"]["counts_before"],
    "counts_after": states["clarification"]["counts_after"], "all_test_conversations_cleaned": True,
    "method_limitations": ["Bộ câu hỏi chọn có chủ đích, không phải mẫu ngẫu nhiên của toàn bộ câu hỏi người dùng.",
                           "Chấm bởi trợ lý AI theo rubric và tài liệu nguồn, chưa có giảng viên kiểm định độc lập.",
                           "Một lượt trả lời đầu tiên/câu, không chọn câu trả lời đẹp sau nhiều lần thử.",
                           "Số đúng là khả năng đáp ứng đầu cuối, gồm cả lỗi không trả lời và hỏi lại thừa trong mẫu.",
                           "Không phát hiện khẳng định sai trong mẫu không chứng minh AI sẽ không bịa ở câu khác."],
}
(D / f"{P}-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
(D / f"{P}-reviewed.json").write_text(json.dumps(graded, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
with (D / f"{P}-scores.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "Tài khoản", "Khóa", "Nhóm", "Bộ", "Câu hỏi", "Đáp án chuẩn", "AI trả lời", "Điểm /2", "Kết luận",
                     "Nhận xét", "Nguồn hỗ trợ ý chính", "Chunk kiểm chứng", "Khẳng định sai trọng yếu", "Giây"])
    for r in graded:
        writer.writerow([r["id"], states["baseline"]["accounts"][r["role"]], titles[r["course_id"]], r["group"], r["sample"],
                         r["question"], r["gold"], r.get("answer", ""), r["score"], r["verdict"], r["review"], r["citation_core_support"],
                         ";".join(map(str, r["supporting_chunk_ids"])), r["hallucinated_material_claim"], r["elapsed_seconds"]])

lines = ["# Đánh giá độ chính xác AI Tutor — 30/10/2026", "",
         f"**Kết quả chính: {len(correct)}/50 câu kiến thức được trả lời đúng và đủ = {summary['strict_knowledge_accuracy_percent']:.0f}%.**",
         "Đây là tỷ lệ đáp ứng đầu cuối trên bộ câu hỏi này; không phải cam kết đúng cho mọi câu hỏi.", "",
         "## Cách đo", "",
         "- Gọi API thật trên localhost bằng 5 tài khoản mẫu: Em, Phương, An, Bình và Admin; model "
         f"`{summary['engine']['llm']['provider']} / {summary['engine']['llm']['model']}`.",
         "- 50 câu kiến thức, chia đều 5 câu cho mỗi khóa trong 10 khóa: 40 câu cố định từ lần đo trước và 10 câu mới được đóng băng rubric trước khi gửi.",
         "- Thêm 10 ca ngoài phạm vi và 8 ca thiếu thông tin, báo riêng, không cộng các ca dễ từ chối/hỏi lại vào tỷ lệ kiến thức.",
         "- Chỉ lấy câu trả lời đầu tiên; không sửa prompt, mã AI, ngưỡng truy hồi hoặc tài liệu trong lúc đo. Mã nguồn được kiểm tra SHA-256 trước/sau cả ba phase.",
         "- Điểm 2: đúng và đủ yêu cầu chính; 1: thiếu ý trọng yếu; 0: sai/lạc đề/không trả lời/hỏi lại thừa/lỗi dịch vụ. Không buộc câu trả lời phải nói thêm các chi tiết không được câu hỏi yêu cầu.",
         "- Chấm nội dung và hỗ trợ nguồn theo từng câu bởi trợ lý AI, có rà soát độc lập; chưa có giảng viên kiểm định độc lập.", "",
         "## Kết quả", "", "| Chỉ số | Kết quả |", "|---|---:|",
         f"| Đúng và đủ trên toàn bộ câu kiến thức | **{len(correct)}/50 = {summary['strict_knowledge_accuracy_percent']:.0f}%** |",
         f"| Đúng và đủ trên 40 câu cố định | {summary['fixed_knowledge_correct']}/40 |",
         f"| Đúng và đủ trên 10 câu mới | {summary['new_knowledge_correct']}/10 |",
         f"| Hỏi lại thừa khi câu kiến thức đã rõ | {summary['unnecessary_clarifications']}/50 |",
         f"| Không trả lời câu kiến thức (từ chối) | {summary['refused_knowledge']}/50 |",
         f"| Có khẳng định kiến thức sai trọng yếu được phát hiện | {summary['factual_errors']} trong {len(substantive)} câu có trả lời nội dung |",
         f"| Câu đúng và ý chính có chứng cứ trong trang được trích | {len(sourced)}/50 = {summary['grounded_end_to_end_percent']:.0f}% |",
         f"| Từ chối phù hợp khi ngoài phạm vi | {summary['boundary_correct']}/10 |",
         f"| Hỏi lại đúng khi thật sự thiếu thông tin | {summary['clarification_correct']}/8 |", "",
         "Không trình bày tỷ lệ đúng trong riêng các câu có nội dung trả lời làm kết quả chính: loại bỏ 5 câu không được trả lời sẽ làm số đẹp hơn và che mất thất bại đầu cuối.", "",
         "## Những câu chưa đạt", "", "| ID | Câu hỏi | Kết quả |", "|---|---|---|"]
for r in failed:
    question = r["question"].replace("|", "\\|").replace("\n", " ")
    lines.append(f"| {r['id']} | {question} | {r['review']} |")
lines += ["", "Ba trường hợp hỏi lại nhầm cho thấy bước làm rõ hiện còn quá nhạy với từ như ‘nó’, ‘báo lỗi’, ‘sửa lỗi’, dù câu hỏi đã đủ chủ đề. "
          "Các ca này được chấm 0 trong lần đo và giữ nguyên mã AI, không sửa rồi đo lại để thay kết quả.", "",
          "Ca Python có quy tắc chuyển kiểu/cộng chuỗi-số trong các chunk 1332, 2014, 2016 của khóa, nhưng lượt trả lời vẫn từ chối. "
          "Ca nút không submit chưa thấy quy tắc `type=\"button\"` trong các chunk HTML đã kiểm tra: đây còn là giới hạn bao phủ tài liệu. "
          "Từ chối ở ca này phù hợp nguyên tắc không đoán khi thiếu nguồn, nhưng vẫn không đáp ứng nhu cầu kiến thức nên giữ điểm 0 đầu cuối theo rubric đã định trước.", "",
          "## Nguồn trích dẫn và việc ‘bịa’", "",
          f"Có {summary['citations_total']} lượt gắn nguồn; metadata tài liệu/khóa/trang đều hợp lệ. Tuy nhiên, metadata đúng không chứng minh câu trả lời được tài liệu đó hỗ trợ.",
          "Câu chia nguyên/chia thực Java cho đúng 7 và 7.5, nhưng các trang gắn kèm chỉ nói Map, kiểu dữ liệu/ép kiểu, String; không chứng minh trực tiếp quy tắc chia. "
          "Câu này vẫn đúng về kiến thức nhưng không đạt tiêu chí ý chính được trang trích dẫn hỗ trợ.",
          "Một số câu có nguồn phụ ít liên quan, ví dụ câu `None` kèm trang if/else, câu `==`/`===` kèm trang hàm/Promise; vẫn có nguồn khác trong cùng câu chứng minh ý chính. "
          "Một số ví dụ phụ trong câu mạng máy tính chưa được trang được chọn chứng minh đầy đủ. Không tuyên bố mọi ý/mọi nguồn gắn kèm đều chính xác.",
          "Chưa phát hiện khẳng định kiến thức sai trọng yếu trong các câu có nội dung trả lời của mẫu này. Điều đó không đồng nghĩa tỷ lệ bịa luôn bằng 0%; "
          "đặc biệt, vấn đề nguồn chưa hỗ trợ đủ vẫn tồn tại.", "", "## Theo khóa học", "", "| Khóa | Đúng / tổng | Tỷ lệ |", "|---|---:|---:|"]
for c in per_course:
    lines.append(f"| {c['title']} | {c['correct']}/{c['total']} | {c['percent']:.0f}% |")
lat = summary["latency_seconds"]
lines += ["", "Mỗi khóa chỉ có 5 câu; không dùng bảng này để kết luận một khóa luôn chính xác ở mức đó.", "",
          "## Thời gian và dữ liệu kiểm thử", "",
          f"68 lượt: trung vị {lat['median']:.2f}s, trung bình {lat['mean']:.2f}s, P95 {lat['p95_nearest_rank']:.2f}s, chậm nhất {lat['max']:.2f}s. "
          f"Lỗi transport/LLM hiển thị: {summary['transport_or_llm_errors']}; câu dự phòng: {summary['fallback_answers']}.",
          "Chỉ tạo hội thoại audit rỗng với mã duy nhất và xóa đúng các id đó sau từng lượt. Trước/sau vẫn là 4 hội thoại, 18 tin nhắn, 176 tài liệu, 2063 chunk; "
          "giữ nguyên lịch sử, tài liệu và tài khoản có sẵn.", "",
          "## Giới hạn", "",
          "Bộ câu hỏi được chọn có chủ đích và khá nhỏ; 40 câu đã được sử dụng trước đây, 10 câu mới vẫn dựa trên tài liệu hiện có. "
          "Đây là kiểm tra hồi quy và một mẫu mở rộng, không phải đánh giá ngẫu nhiên hay bộ kiểm định độc lập. Kết quả có thể đổi theo cách hỏi, tài liệu, "
          "model và tình trạng dịch vụ. Nên có giảng viên kiểm tra thêm trước khi dùng tỷ lệ này làm cam kết chất lượng.", "",
          "## Tệp đối chiếu", "",
          f"- [Bảng điểm 68 câu, UTF-8 cho Excel]({P}-scores.csv)",
          f"- [Tóm tắt số liệu]({P}-summary.json)",
          f"- [Câu trả lời và đánh giá từng câu, kèm trang nguồn]({P}-reviewed.json)",
          "- [Runner giữ câu trả lời đầu tiên](ai-accuracy-current-run.py)",
          f"- [Đề 10 câu mới, rubric và chứng cứ đã đóng băng]({P}-new-plan.json)", ""]
(D / f"{P}.md").write_text("\n".join(lines), encoding="utf-8")
print(json.dumps({k: summary[k] for k in ["total_cases", "knowledge_total", "correct_complete", "strict_knowledge_accuracy_percent",
                 "unnecessary_clarifications", "refused_knowledge", "correct_and_cited_core_supported", "grounded_end_to_end_percent",
                 "boundary_correct", "clarification_correct", "factual_errors"]}, ensure_ascii=False, indent=2))
