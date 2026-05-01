"""
pdf_extraction.py — pdfplumber helper for paper-survey skill.

Usage:
    python pdf_extraction.py extract_full <pdf_path> [out_md_path]
    python pdf_extraction.py extract_sampled <pdf_path> [out_md_path]
    python pdf_extraction.py extract_page <pdf_path> <page_num>
    python pdf_extraction.py verify_quote <pdf_path> <page_num> <quote>
    python pdf_extraction.py verify_quotes_batch <claims.json> [--workers 8]

claims.json 格式：
    [{"claim_id": "c001", "pdf_path": "...", "page_num": 3, "quote": "..."}, ...]

依赖: pdfplumber (pip install pdfplumber)
设计：基于 2026-05-01 benchmark（100 claims × 16 PDFs 实测 4 秒），按 PDF 分组并行（worker=8）。
"""

import sys
import re
import json
import pdfplumber
from concurrent.futures import ProcessPoolExecutor

# Windows GBK 控制台兼容
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

FUZZY_THRESHOLD = 0.8


def extract_full(pdf_path: str, out_md_path: str | None = None) -> str:
    """严格抽取整本 PDF 全文。"""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n\n".join(
            f"--- Page {i+1} ---\n{p.extract_text() or ''}" for i, p in enumerate(pdf.pages)
        )
    if out_md_path:
        with open(out_md_path, 'w', encoding='utf-8') as f:
            f.write(text)
    return text


def extract_sampled(pdf_path: str, out_md_path: str | None = None) -> str:
    """长 PDF 采样抽取（>15 页时按章节关键词采样，≤15 页等价 extract_full）。"""
    with pdfplumber.open(pdf_path) as pdf:
        n = len(pdf.pages)
        if n <= 15:
            text = "\n\n".join(
                f"--- Page {i+1} ---\n{p.extract_text() or ''}" for i, p in enumerate(pdf.pages)
            )
        else:
            keywords = ['abstract', 'introduction', 'method', 'experiment', 'result', 'conclusion', 'discussion', 'limitation']
            sampled = []
            for i, p in enumerate(pdf.pages):
                t = p.extract_text() or ''
                if i < 3 or i >= n - 3 or any(kw in t.lower()[:200] for kw in keywords):
                    sampled.append(f"--- Page {i+1} ---\n{t}")
            text = "\n\n".join(sampled)
    if out_md_path:
        with open(out_md_path, 'w', encoding='utf-8') as f:
            f.write(text)
    return text


def extract_page(pdf_path: str, page_num: int) -> str:
    """抽取指定页（1-indexed）。"""
    with pdfplumber.open(pdf_path) as pdf:
        if page_num < 1 or page_num > len(pdf.pages):
            return ''
        return pdf.pages[page_num - 1].extract_text() or ''


def _verify_text(page_text: str, quote: str, threshold: float = FUZZY_THRESHOLD) -> bool:
    """fuzzy 匹配：quote 词汇覆盖率 ≥ threshold 视为命中。"""
    quote_norm = re.sub(r'\s+', ' ', quote.lower().strip())
    if not page_text or not quote_norm:
        return False
    quote_words = set(re.findall(r'\w+', quote_norm))
    page_words = set(re.findall(r'\w+', page_text.lower()))
    if not quote_words:
        return False
    return len(quote_words & page_words) / len(quote_words) >= threshold


def verify_quote(pdf_path: str, page_num: int, quote: str, fuzzy_threshold: float = FUZZY_THRESHOLD) -> bool:
    """单次验证（向后兼容，且供单点抽样使用）。"""
    page_text = extract_page(pdf_path, page_num)
    return _verify_text(page_text, quote, fuzzy_threshold)


def _verify_pdf_group(args):
    """处理同一 PDF 的所有 claim — D 策略 worker 入口（按 PDF 分组）。"""
    pdf_path, group = args
    results = []
    page_cache = {}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            n_pages = len(pdf.pages)
            for c in group:
                pn = c['page_num']
                if pn not in page_cache:
                    page_cache[pn] = ((pdf.pages[pn - 1].extract_text() or '')
                                      if 1 <= pn <= n_pages else '')
                results.append({
                    'claim_id': c['claim_id'],
                    'pass': _verify_text(page_cache[pn], c['quote']),
                })
    except Exception as e:
        for c in group:
            results.append({'claim_id': c['claim_id'], 'pass': False, 'error': str(e)})
    return results


def verify_quotes_batch(claims: list[dict], workers: int = 8) -> list[dict]:
    """并行批量验证（D 策略：按 PDF 分组 + ProcessPoolExecutor）。

    benchmark 实测：100 claims × 16 PDFs ≈ 4s（worker=8）。
    """
    by_pdf = {}
    for c in claims:
        by_pdf.setdefault(c['pdf_path'], []).append(c)
    args_list = list(by_pdf.items())
    if len(args_list) == 1:
        # 单 PDF 直接串行（避免进程启动开销）
        return _verify_pdf_group(args_list[0])
    with ProcessPoolExecutor(max_workers=min(workers, len(args_list))) as ex:
        all_results = list(ex.map(_verify_pdf_group, args_list))
    return [r for batch in all_results for r in batch]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    try:
        if cmd == 'extract_full':
            out = sys.argv[3] if len(sys.argv) > 3 else None
            text = extract_full(sys.argv[2], out)
            if not out:
                print(text)
        elif cmd == 'extract_sampled':
            out = sys.argv[3] if len(sys.argv) > 3 else None
            text = extract_sampled(sys.argv[2], out)
            if not out:
                print(text)
        elif cmd == 'extract_page':
            print(extract_page(sys.argv[2], int(sys.argv[3])))
        elif cmd == 'verify_quote':
            ok = verify_quote(sys.argv[2], int(sys.argv[3]), sys.argv[4])
            print('PASS' if ok else 'FAIL')
            sys.exit(0 if ok else 1)
        elif cmd == 'verify_quotes_batch':
            claims_path = sys.argv[2]
            workers = 8
            if '--workers' in sys.argv:
                workers = int(sys.argv[sys.argv.index('--workers') + 1])
            with open(claims_path, 'r', encoding='utf-8') as f:
                claims = json.load(f)
            results = verify_quotes_batch(claims, workers=workers)
            print(json.dumps(results, ensure_ascii=False, indent=2))
            failed = sum(1 for r in results if not r.get('pass'))
            sys.exit(1 if failed > 0 else 0)
        else:
            print(f"unknown command: {cmd}")
            sys.exit(1)
    except Exception as e:
        print(json.dumps({'error': str(e), 'cmd': cmd}, ensure_ascii=False))
        sys.exit(2)


if __name__ == '__main__':
    main()
