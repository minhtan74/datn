"""Chuyển công thức Equation của Word (OMML, thẻ <m:oMath>) sang LaTeX để hiển thị bằng KaTeX.

Hỗ trợ các cấu trúc hay gặp trong đề thi: phân số, mũ / chỉ số, căn, tổng / tích / tích phân,
ngoặc (kể cả hệ phương trình), hàm (sin, log...), giới hạn, dấu mũ / gạch trên, ma trận.
Cấu trúc lạ không nhận ra thì giữ lại phần chữ bên trong (không làm mất nội dung).
Công thức MathType / Equation 3.0 là đối tượng nhúng (OLE), KHÔNG phải OMML -> không xử lý ở đây.
"""
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def _m(tag: str) -> str:
    return f"{{{M}}}{tag}"


# Ký tự Unicode trong công thức -> lệnh LaTeX
_SYMBOLS = {
    "×": r"\times ", "÷": r"\div ", "±": r"\pm ", "∓": r"\mp ", "·": r"\cdot ", "⋅": r"\cdot ", "∗": "*",
    "≤": r"\le ", "≥": r"\ge ", "≠": r"\ne ", "≈": r"\approx ", "≡": r"\equiv ", "∼": r"\sim ", "≃": r"\simeq ",
    "∞": r"\infty ", "∂": r"\partial ", "∇": r"\nabla ", "∅": r"\emptyset ", "°": r"^{\circ}", "′": "'",
    "→": r"\to ", "←": r"\leftarrow ", "↔": r"\leftrightarrow ", "⇒": r"\Rightarrow ", "⇐": r"\Leftarrow ",
    "⇔": r"\Leftrightarrow ", "↦": r"\mapsto ",
    "∈": r"\in ", "∉": r"\notin ", "⊂": r"\subset ", "⊃": r"\supset ", "⊆": r"\subseteq ", "⊇": r"\supseteq ",
    "∪": r"\cup ", "∩": r"\cap ", "∖": r"\setminus ", "∀": r"\forall ", "∃": r"\exists ", "¬": r"\neg ",
    "∧": r"\wedge ", "∨": r"\vee ", "⊥": r"\perp ", "∥": r"\parallel ", "∠": r"\angle ", "△": r"\triangle ",
    "…": r"\ldots ", "⋯": r"\cdots ", "⋮": r"\vdots ", "⋱": r"\ddots ",
    "ℕ": r"\mathbb{N}", "ℤ": r"\mathbb{Z}", "ℚ": r"\mathbb{Q}", "ℝ": r"\mathbb{R}", "ℂ": r"\mathbb{C}",
    "α": r"\alpha ", "β": r"\beta ", "γ": r"\gamma ", "δ": r"\delta ", "ε": r"\varepsilon ", "ϵ": r"\epsilon ",
    "ζ": r"\zeta ", "η": r"\eta ", "θ": r"\theta ", "ϑ": r"\vartheta ", "ι": r"\iota ", "κ": r"\kappa ",
    "λ": r"\lambda ", "μ": r"\mu ", "ν": r"\nu ", "ξ": r"\xi ", "π": r"\pi ", "ρ": r"\rho ", "σ": r"\sigma ",
    "τ": r"\tau ", "υ": r"\upsilon ", "φ": r"\varphi ", "ϕ": r"\phi ", "χ": r"\chi ", "ψ": r"\psi ", "ω": r"\omega ",
    "Γ": r"\Gamma ", "Δ": r"\Delta ", "∆": r"\Delta ", "Θ": r"\Theta ", "Λ": r"\Lambda ", "Ξ": r"\Xi ",
    "Π": r"\Pi ", "Σ": r"\Sigma ", "Φ": r"\Phi ", "Ψ": r"\Psi ", "Ω": r"\Omega ",
    "−": "-", "–": "-", "⁡": "", "⁢": "", "⁣": "", "​": "",
}
# Ký tự có nghĩa đặc biệt trong LaTeX -> phải thoát
_ESCAPE = {"\\": r"\backslash ", "{": r"\{", "}": r"\}", "%": r"\%", "#": r"\#", "&": r"\&", "$": r"\$", "_": r"\_"}

# Ngoặc của m:d -> LaTeX (chuỗi rỗng = không có ngoặc)
_DELIMS = {
    "(": "(", ")": ")", "[": "[", "]": "]", "{": r"\{", "}": r"\}", "|": "|", "‖": r"\|", "⟨": r"\langle ",
    "⟩": r"\rangle ", "〈": r"\langle ", "〉": r"\rangle ", "⌊": r"\lfloor ", "⌋": r"\rfloor ", "⌈": r"\lceil ",
    "⌉": r"\rceil ", "": ".",
}
# Dấu của m:nary (tổng, tích phân...)
_NARY = {
    "∑": r"\sum", "∏": r"\prod", "∐": r"\coprod", "∫": r"\int", "∬": r"\iint", "∭": r"\iiint", "∮": r"\oint",
    "⋃": r"\bigcup", "⋂": r"\bigcap", "⋁": r"\bigvee", "⋀": r"\bigwedge",
}
# Dấu phía trên của m:acc
_ACCENTS = {
    "̂": r"\hat", "̄": r"\bar", "̅": r"\overline", "⃗": r"\vec", "→": r"\vec",
    "̃": r"\tilde", "̇": r"\dot", "̈": r"\ddot", "̌": r"\check", "̆": r"\breve",
}
# Tên hàm có sẵn trong LaTeX
_FUNCS = {
    "sin", "cos", "tan", "cot", "sec", "csc", "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh", "coth",
    "log", "ln", "lg", "exp", "lim", "max", "min", "sup", "inf", "det", "gcd", "deg", "dim", "ker", "arg",
}


def _val(el, path: str, default: str | None = None) -> str | None:
    """Thuộc tính m:val của thẻ con theo đường dẫn "fPr/type"."""
    node = el
    for tag in path.split("/"):
        node = node.find(_m(tag)) if node is not None else None
    if node is None:
        return default
    return node.get(_m("val"), default)


def _hidden(el, path: str) -> bool:
    return _val(el, path) in ("1", "on", "true")


def _text(s: str) -> str:
    return "".join(_SYMBOLS.get(ch, _ESCAPE.get(ch, ch)) for ch in s)


def _child(el, tag: str):
    return el.find(_m(tag))


def _conv(el) -> str:
    """Chuyển 1 phần tử (và con của nó) sang LaTeX."""
    if el is None:
        return ""
    tag = el.tag.rsplit("}", 1)[-1] if el.tag.startswith(f"{{{M}}}") else None
    if tag is None:  # thẻ ngoài namespace math (w:r bên trong công thức...) -> lấy chữ
        return _text("".join(el.itertext()))
    handler = _HANDLERS.get(tag)
    if handler:
        return handler(el)
    return _children(el)


def _children(el) -> str:
    return "".join(_conv(c) for c in el if not c.tag.endswith("Pr"))


def _g(el) -> str:
    """Nội dung bọc trong {} để làm đối số."""
    return "{" + _children(el) + "}" if el is not None else "{}"


def _run(el) -> str:
    text = "".join(t.text or "" for t in el.iter(_m("t")))
    if text in _FUNCS:
        return "\\" + text + " "
    # Chữ thường (không nghiêng) nhiều ký tự trong công thức, vd "cm", "km/h"
    if _val(el, "rPr/sty") == "p" and len(text) > 1 and text.isalpha():
        return r"\mathrm{" + text + "}"
    return _text(text)


def _frac(el) -> str:
    kind = _val(el, "fPr/type")
    num, den = _g(_child(el, "num")), _g(_child(el, "den"))
    if kind == "lin":
        return f"{num}/{den}"
    if kind == "noBar":
        return rf"\genfrac{{}}{{}}{{0pt}}{{}}{num}{den}"
    return rf"\frac{num}{den}"


def _nary(el) -> str:
    op = _NARY.get(_val(el, "naryPr/chr", "∫") or "∫", r"\int")
    out = op
    if not _hidden(el, "naryPr/subHide") and _child(el, "sub") is not None and _children(_child(el, "sub")):
        out += "_" + _g(_child(el, "sub"))
    if not _hidden(el, "naryPr/supHide") and _child(el, "sup") is not None and _children(_child(el, "sup")):
        out += "^" + _g(_child(el, "sup"))
    return out + " " + _g(_child(el, "e"))


def _delim(el) -> str:
    beg = _val(el, "dPr/begChr", "(")
    end = _val(el, "dPr/endChr", ")")
    sep = _val(el, "dPr/sepChr", "|")
    parts = [_children(e) for e in el.findall(_m("e"))]
    body = (f" {_DELIMS.get(sep, sep)} " if sep else ", ").join(parts)
    return rf"\left{_DELIMS.get(beg, beg)} {body} \right{_DELIMS.get(end, end)} "


def _rad(el) -> str:
    deg = _child(el, "deg")
    body = _g(_child(el, "e"))
    if _hidden(el, "radPr/degHide") or deg is None or not _children(deg):
        return rf"\sqrt{body}"
    return rf"\sqrt[{_children(deg)}]{body}"


def _func(el) -> str:
    name = _children(_child(el, "fName")).strip()
    plain = name.replace(r"\mathrm{", "").replace("}", "").strip("\\ ")
    if plain in _FUNCS and not name.startswith("\\"):
        name = "\\" + plain
    elif not name.startswith("\\"):
        name = rf"\operatorname{{{name}}}"
    return f"{name} {_g(_child(el, 'e'))}"


def _lim_low(el) -> str:
    base = _children(_child(el, "e")).strip()
    lim = _g(_child(el, "lim"))
    if base.strip("\\ ") in ("lim", "max", "min", "sup", "inf"):
        return f"\\{base.strip(chr(92) + ' ')}_{lim} "
    return rf"\underset{lim}{{{base}}}"


def _acc(el) -> str:
    cmd = _ACCENTS.get(_val(el, "accPr/chr", "̂") or "̂", r"\hat")
    return cmd + _g(_child(el, "e"))


def _matrix(el) -> str:
    rows = [" & ".join(_children(e) for e in mr.findall(_m("e"))) for mr in el.findall(_m("mr"))]
    return r"\begin{matrix} " + r" \\ ".join(rows) + r" \end{matrix}"


def _eq_arr(el) -> str:
    rows = [_children(e) for e in el.findall(_m("e"))]
    return r"\begin{array}{l} " + r" \\ ".join(rows) + r" \end{array}"


_HANDLERS = {
    "r": _run,
    "f": _frac,
    "sSup": lambda el: _g(_child(el, "e")) + "^" + _g(_child(el, "sup")),
    "sSub": lambda el: _g(_child(el, "e")) + "_" + _g(_child(el, "sub")),
    "sSubSup": lambda el: _g(_child(el, "e")) + "_" + _g(_child(el, "sub")) + "^" + _g(_child(el, "sup")),
    "sPre": lambda el: "{}_" + _g(_child(el, "sub")) + "^" + _g(_child(el, "sup")) + _g(_child(el, "e")),
    "rad": _rad,
    "nary": _nary,
    "d": _delim,
    "func": _func,
    "limLow": _lim_low,
    "limUpp": lambda el: r"\overset" + _g(_child(el, "lim")) + _g(_child(el, "e")),
    "acc": _acc,
    "bar": lambda el: (r"\underline" if _val(el, "barPr/pos") == "bot" else r"\overline") + _g(_child(el, "e")),
    "groupChr": lambda el: (r"\overbrace" if _val(el, "groupChrPr/pos") == "top" else r"\underbrace") + _g(_child(el, "e")),
    "m": _matrix,
    "eqArr": _eq_arr,
    "box": lambda el: _children(_child(el, "e")),
    "borderBox": lambda el: r"\boxed" + _g(_child(el, "e")),
}


def omml_to_latex(omath) -> str:
    """<m:oMath> -> chuỗi LaTeX (một dòng, không chứa "]]" để không đụng ký hiệu [[math:...]])."""
    latex = _children(omath)
    latex = " ".join(latex.split())  # gom khoảng trắng
    while "]]" in latex:
        latex = latex.replace("]]", "] ]")
    return latex.strip()
