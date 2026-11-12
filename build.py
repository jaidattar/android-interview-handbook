#!/usr/bin/env python3
"""Assemble the Android Interview Handbook from chapter fragments.

Fragments in src/ hold only the topic sections. This script adds the page
shell, chapter header, key takeaways, navigation, consistent syntax
highlighting, topic colours and cross-links ({{ch:N}} -> link).
"""
import html
import pathlib
import re
import shutil

BASE = pathlib.Path(__file__).resolve().parent
SRC = BASE / "src"
ASSETS = BASE / "assets"
SITE = BASE / "site"

BOOK_TITLE = "Android Interview Handbook"

PALETTE = ["#2f7de1", "#e0457b", "#1fa37a", "#d98200", "#8a4fe0",
           "#0f9fb5", "#d6402f", "#6f8f1d", "#3a5fc8", "#b8508c"]

CHAPTERS = [
    dict(n=1, slug="01-kotlin-essentials", title="Kotlin Essentials",
         color="#7c5cff", frag="ch01.html",
         intro="The Kotlin features interviewers probe beyond syntax: why they exist, "
               "what the compiler generates, and what breaks in production.",
         related=[2, 3],
         takeaways=[
             "val is a read-only reference, not an immutable object. Use immutable collection types and copies.",
             "Use == for value equality and === only for identity. Never compare boxed numbers with ===.",
             "Data classes generate equals, hashCode, copy and toString; copy() is shallow.",
             "Sealed hierarchies give exhaustive when expressions and compile-time safety for UI state.",
             "HashMap relies on hashCode and equals together; mutable keys break lookups.",
             "Coroutines are cheap, suspendable tasks. Threads are expensive OS resources.",
         ]),
    dict(n=2, slug="02-android-architecture", title="Android Architecture",
         color="#15a38b", frag="ch02.html",
         intro="Architecture questions test trade-offs and real decisions, not diagrams. "
               "Each topic gives the question, a model answer, what to say out loud, and the traps.",
         related=[3, 4, 7],
         takeaways=[
             "Unidirectional data flow: events go up, state comes down.",
             "The dependency rule points inward: UI and data depend on the domain, not the reverse.",
             "A repository hides where data comes from. Room is the single source of truth.",
             "Prefer constructor injection. Use Hilt scopes deliberately.",
             "Collect flows with lifecycle awareness (repeatOnLifecycle or collectAsStateWithLifecycle).",
             "Modularise by feature first; use WorkManager for offline sync that must survive restarts.",
         ]),
    dict(n=3, slug="03-coroutines-and-flow", title="Coroutines & Flow",
         color="#2f7de1", frag="ch03.html",
         intro="Coroutine and Flow questions focus on failure, cancellation and threading: "
               "what happens if it fails, is cancelled, or runs on the wrong thread.",
         related=[2, 4, 5],
         takeaways=[
             "launch returns a Job and fire-and-forget; async returns a Deferred you await.",
             "Structured concurrency: parents wait for children and cancel them; failures propagate up.",
             "Cancellation is cooperative. Never swallow CancellationException.",
             "Use the right dispatcher: Main for UI, IO for blocking I/O, Default for CPU work.",
             "StateFlow for state, SharedFlow for events. Cold flows re-run per collector.",
             "Collect with repeatOnLifecycle or collectAsStateWithLifecycle, not a bare launch.",
         ]),
    dict(n=4, slug="04-jetpack-compose", title="Jetpack Compose",
         color="#e0457b", frag="ch04.html",
         intro="Compose questions centre on performance, state and side effects. "
               "Learn to explain how you would measure and debug a slow or incorrect screen.",
         related=[2, 5],
         takeaways=[
             "Measure before optimising: use a release build, Layout Inspector and compiler reports.",
             "Keep composables small and read state as late as possible.",
             "Stable, immutable models and keys let Compose skip work.",
             "remember for cheap rebuildable values; rememberSaveable for user-visible UI state.",
             "Effects: LaunchedEffect for suspend work, DisposableEffect for setup with cleanup.",
             "Hoist state to the lowest common ancestor and pass state down, events up.",
         ]),
    dict(n=5, slug="05-debugging-and-performance", title="Debugging & Performance",
         color="#e8833a", frag="ch05.html",
         intro="Debugging questions test your process. Reproduce, collect evidence, isolate the layer, "
               "fix the cause, guard it, and monitor. Use the same frame for every answer.",
         related=[3, 4, 7],
         takeaways=[
             "Use the seven-step frame: reproduce, collect, locate the layer, isolate, fix, test, monitor.",
             "ANRs: read the main thread state and who holds the lock, not only the top frame.",
             "Leaks: find the path from a GC root to the leaked object, then break that reference.",
             "Startup and jank: measure with Macrobenchmark and traces, then use Baseline Profiles.",
             "Design for the weakest device you support and prove it with real-device data.",
             "Retry only idempotent requests, with backoff and jitter.",
         ]),
    dict(n=6, slug="06-data-structures-and-algorithms", title="Data Structures & Algorithms in Kotlin",
         color="#3a9d23", frag="ch06.html",
         intro="Coding-round patterns. Learn the pattern behind each problem, not only the solution, "
               "so you recognise it in problems you have never seen.",
         related=[7],
         takeaways=[
             "Start with a brute force, state its complexity, then name the pattern that optimises it.",
             "HashMap for lookups, two pointers for sorted or symmetric data, sliding window for contiguous ranges.",
             "Stack for nesting and most-recent matching; binary search for sorted data or monotone answers.",
             "Sort then scan for intervals; recursion and DP when subproblems repeat.",
             "Test with an empty input, a single element, duplicates and the boundaries.",
             "Pattern recognition grows from repetition, not from reading solutions.",
         ]),
    dict(n=7, slug="07-system-design", title="System Design & Architecture",
         color="#0e7490", frag="ch07.html",
         intro="There is no single correct design. Interviewers score your questions, trade-offs and "
               "judgement. Each answer follows the same shape: requirements, design, deep-dive, trade-offs, failure.",
         related=[2, 3, 5, 8],
         takeaways=[
             "Clarify requirements before naming any pattern. Ask about offline use, scale and constraints.",
             "Room as source of truth, WorkManager for sync, idempotent writes for retries.",
             "Repositories expose Flow for streams and suspend for one-shot actions, with typed errors.",
             "Make code testable through constructor injection, interfaces at boundaries and injected dispatchers.",
             "Migrate incrementally with guardrails and a finish line. Choose by criteria, record decisions.",
             "Always end with what breaks first at 10x scale, how you would detect it, and what you would change.",
         ]),
    dict(n=8, slug="08-handling-gaps-honestly", title="Answering Honestly About Gaps",
         color="#b45309", frag="ch08.html",
         intro="How to talk about experience you do not have without bluffing. Show self-awareness, "
               "honest scope and fast learning.",
         related=[6, 7],
         takeaways=[
             "State the gap plainly, show adjacent real experience, explain your understanding, then name a concrete action.",
             "Describe your exact role. Never claim work you only observed.",
             "Keep numbers such as years of experience consistent everywhere.",
             "Say \u201cI don\u2019t know, but here is how I would find out\u201d instead of bluffing.",
             "Everything you say must survive three follow-up questions.",
         ]),
]

BY_N = {c["n"]: c for c in CHAPTERS}

# ---------------------------------------------------------------- highlighting
KOTLIN_KW = set("""
package import class interface object fun val var if else when for while do
return break continue try catch finally throw is as in null true false this super
typealias override open abstract sealed data inline noinline crossinline reified
suspend companion const lateinit private public protected internal by where init
constructor get set tailrec operator infix enum annotation vararg out
""".split())

BASH_KW = set("if then else elif fi for do done while case esac function export cd echo in".split())

KT_TOKEN = re.compile(
    r'(?P<bc>/\*.*?\*/)'
    r'|(?P<lc>//[^\n]*)'
    r'|(?P<ts>"""(?:.|\n)*?""")'
    r'|(?P<str>"(?:\\.|[^"\\\n])*")'
    r'|(?P<chr>\'(?:\\.|[^\'\\\n])+\')'
    r'|(?P<ann>@[A-Za-z_][\w.]*)'
    r'|(?P<num>\b(?:0x[0-9A-Fa-f_]+|\d[\d_]*(?:\.\d+)?)[LlFfuU]?\b)'
    r'|(?P<id>[A-Za-z_]\w*)'
    r'|(?P<ws>\s+)'
    r'|(?P<op>.)',
    re.S,
)
KT_CLASS = {"bc": "c", "lc": "c", "ts": "s", "str": "s", "chr": "s",
            "ann": "a", "num": "n", "op": "p"}

BASH_TOKEN = re.compile(
    r'(?P<lc>#[^\n]*)'
    r'|(?P<str>"(?:\\.|[^"\\])*"|\'[^\']*\')'
    r'|(?P<var>\$\{?\w+\}?)'
    r'|(?P<id>[A-Za-z_][\w./-]*)'
    r'|(?P<ws>\s+)'
    r'|(?P<op>.)',
    re.S,
)

XML_TOKEN = re.compile(
    r'(?P<cm><!--.*?-->)'
    r'|(?P<str>"[^"]*")'
    r'|(?P<tag></?[A-Za-z][\w:.-]*)'
    r'|(?P<attr>[A-Za-z_][\w:.-]*(?==))'
    r'|(?P<end>/?>)'
    r'|(?P<ws>\s+)'
    r'|(?P<op>.)',
    re.S,
)


def esc(s):
    return html.escape(s, quote=False)


def span(cls, tok):
    return f'<span class="{cls}">{esc(tok)}</span>'


def hl_kotlin(code):
    out = []
    for m in KT_TOKEN.finditer(code):
        kind, tok = m.lastgroup, m.group()
        if kind == "ws":
            out.append(tok)
        elif kind == "id":
            nxt = code[m.end():m.end() + 1]
            if tok in KOTLIN_KW:
                out.append(span("k", tok))
            elif nxt == "(":
                out.append(span("f", tok))
            elif tok[0].isupper():
                out.append(span("t", tok))
            else:
                out.append(esc(tok))
        elif kind == "op":
            out.append(span("p", tok) if tok in "+-*/=<>!?&|%:" else esc(tok))
        else:
            out.append(span(KT_CLASS[kind], tok))
    return "".join(out)


def hl_bash(code):
    out = []
    line_start = True
    for m in BASH_TOKEN.finditer(code):
        kind, tok = m.lastgroup, m.group()
        if kind == "ws":
            if "\n" in tok:
                line_start = True
            out.append(tok)
            continue
        if kind == "id":
            if tok in BASH_KW:
                out.append(span("k", tok))
            elif line_start:
                out.append(span("f", tok))
            else:
                out.append(esc(tok))
        elif kind == "lc":
            out.append(span("c", tok))
        elif kind == "str":
            out.append(span("s", tok))
        elif kind == "var":
            out.append(span("t", tok))
        else:
            out.append(span("p", tok) if tok in "|&;>" else esc(tok))
        line_start = False
    return "".join(out)


def hl_xml(code):
    out = []
    for m in XML_TOKEN.finditer(code):
        kind, tok = m.lastgroup, m.group()
        if kind == "ws":
            out.append(tok)
        elif kind == "cm":
            out.append(span("c", tok))
        elif kind == "str":
            out.append(span("s", tok))
        elif kind == "tag":
            out.append(span("tag", tok))
        elif kind == "attr":
            out.append(span("attr", tok))
        elif kind == "end":
            out.append(span("tag", tok))
        else:
            out.append(esc(tok))
    return "".join(out)


def highlight_block(raw):
    """raw is the text as written in the fragment (may contain raw < or &)."""
    code = html.unescape(raw).strip("\n")
    stripped = code.lstrip()
    if stripped.startswith("<") and not stripped.startswith("<!") and re.match(r"<[A-Za-z/]", stripped):
        body = hl_xml(code)
    elif re.match(r"(\$ |\./|adb |sh |gradle |\./gradlew)", stripped):
        body = hl_bash(code)
    else:
        body = hl_kotlin(code)
    return f"<pre><code>{body}</code></pre>"


PRE_RE = re.compile(r"<pre><code>(.*?)</code></pre>", re.S)
INLINE_RE = re.compile(r"<code>(.*?)</code>", re.S)


def process_body(body):
    # 1. Code blocks: highlight once, stash behind placeholders.
    blocks = []

    def stash(m):
        blocks.append(highlight_block(m.group(1)))
        return f"\x00PRE{len(blocks) - 1}\x00"

    body = PRE_RE.sub(stash, body)

    # 2. Inline <code>: normalise escaping so raw or escaped input both work.
    body = INLINE_RE.sub(lambda m: f"<code>{esc(html.unescape(m.group(1)))}</code>", body)

    # 3. Restore code blocks.
    body = re.sub(r"\x00PRE(\d+)\x00", lambda m: blocks[int(m.group(1))], body)

    # 4. Topic colours: cycle the palette over ordinary topic sections in order.
    counter = [0]

    def colour(m):
        c = PALETTE[counter[0] % len(PALETTE)]
        counter[0] += 1
        return f'<section class="topic" style="--c:{c}">'

    body = re.sub(r'<section class="topic">', colour, body)

    # 5. Numbered topic headings: <h2>N. Title</h2> -> badge + title.
    body = re.sub(r'<h2>(\d+)\.\s*(.*?)</h2>',
                  r'<h2><span class="n">\1</span><span>\2</span></h2>', body)
    return body


def link_for(n):
    c = BY_N[n]
    return c["slug"] + ".html"


def xref(m):
    n = int(m.group(1))
    c = BY_N[n]
    return f'<a class="xref" href="{link_for(n)}">Chapter {n}: {esc(c["title"])}</a>'


def resolve_xrefs(text):
    return re.sub(r"\{\{ch:(\d+)\}\}", xref, text)


# ---------------------------------------------------------------- templates
def head(title):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)} · {BOOK_TITLE}</title>
<link rel="stylesheet" href="assets/book.css">
</head>
<body>
"""


def topbar(chapter_label):
    return f"""<header class="topbar">
<a class="brand" href="index.html">{BOOK_TITLE}</a>
<span class="chap-name">{esc(chapter_label)}</span>
<button class="theme-btn" type="button" aria-label="Switch light or dark theme">Dark</button>
<div class="progress"></div>
</header>
"""


def foot():
    return f"""<footer>{BOOK_TITLE} · Built for interview preparation</footer>
<script src="assets/book.js"></script>
</body>
</html>
"""


def related_chips(c):
    if not c["related"]:
        return ""
    links = " ".join(f'<a class="chip" href="{link_for(n)}">Ch {n}: {esc(BY_N[n]["title"])}</a>'
                     for n in c["related"])
    return f'<div class="chips"><span>Related:</span>{links}</div>'


def build_chapter(c):
    frag = (SRC / c["frag"]).read_text(encoding="utf-8")
    body = resolve_xrefs(process_body(frag))
    idx = CHAPTERS.index(c)
    prev_c = CHAPTERS[idx - 1] if idx > 0 else None
    next_c = CHAPTERS[idx + 1] if idx < len(CHAPTERS) - 1 else None

    prev_html = (f'<a href="{prev_c["slug"]}.html"><small>Previous</small>'
                 f'Ch {prev_c["n"]}: {esc(prev_c["title"])}</a>') if prev_c else '<span class="ghost"></span>'
    next_html = (f'<a class="next" href="{next_c["slug"]}.html"><small>Next</small>'
                 f'Ch {next_c["n"]}: {esc(next_c["title"])}</a>') if next_c else '<span class="ghost"></span>'

    takeaways = "".join(f"<li>{resolve_xrefs(esc(t))}</li>" for t in c["takeaways"])

    page = [
        head(f'Ch {c["n"]}: {c["title"]}'),
        topbar(f'Chapter {c["n"]} · {c["title"]}'),
        '<main class="page">',
        f'<header class="chap-head" style="--c:{c["color"]}">',
        f'<div class="chap-no">Chapter {c["n"]}</div>',
        f'<h1>{esc(c["title"])}</h1>',
        f'<p class="intro">{esc(c["intro"])}</p>',
        related_chips(c),
        '</header>',
        body,
        f'<aside class="takeaways"><h3>Key takeaways</h3><ul>{takeaways}</ul></aside>',
        f'<nav class="pager">{prev_html}<a class="home" href="index.html">Contents</a>{next_html}</nav>',
        '</main>',
        foot(),
    ]
    return "".join(page)


def topic_count(c):
    frag = (SRC / c["frag"]).read_text(encoding="utf-8")
    return len(re.findall(r'<section class="topic', frag))


def build_index():
    cards = []
    total_topics = 0
    for c in CHAPTERS:
        cnt = topic_count(c)
        total_topics += cnt
        cards.append(
            f'<li><a href="{c["slug"]}.html" style="--c:{c["color"]}">'
            f'<span class="num">{c["n"]}</span>'
            f'<span><span class="t">{esc(c["title"])}</span>'
            f'<span class="d">{esc(c["intro"])}</span>'
            f'<span class="meta">{cnt} topics · {len(c["takeaways"])} takeaways</span></span>'
            f'</a></li>'
        )
    page = [
        head(BOOK_TITLE),
        topbar("Contents"),
        '<main class="page">',
        '<section class="hero">',
        '<div class="kicker">Interview preparation guide</div>',
        f'<h1>{BOOK_TITLE}</h1>',
        '<p>Questions interviewers ask, model answers you can say out loud, and the traps to avoid, '
        'organised as one connected book from Kotlin basics to system design.</p>',
        f'<div class="stats"><span>{len(CHAPTERS)} chapters</span><span>{total_topics} topics</span>'
        '<span>Model answers and traps</span></div>',
        '</section>',
        '<section class="howto"><h2>How to use this book</h2>'
        '<p>Read the chapters in order, or jump straight to the topic you need. Each question comes with '
        'a model answer, the phrases worth saying in the room, and the follow-ups interviewers use to test you. '
        'Each chapter ends with key takeaways and links to related chapters.</p></section>',
        '<h2 class="toc-title">Chapters</h2>',
        '<ul class="toc">' + "".join(cards) + '</ul>',
        '</main>',
        foot(),
    ]
    return "".join(page)


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "assets").mkdir(parents=True)
    shutil.copy(ASSETS / "book.css", SITE / "assets" / "book.css")
    shutil.copy(ASSETS / "book.js", SITE / "assets" / "book.js")

    (SITE / "index.html").write_text(build_index(), encoding="utf-8")
    for c in CHAPTERS:
        (SITE / f'{c["slug"]}.html').write_text(build_chapter(c), encoding="utf-8")
    print("built", len(CHAPTERS) + 1, "pages in", SITE)


if __name__ == "__main__":
    main()
