#!/usr/bin/env python3
"""
arXiv Search Helper Script

Searches arXiv via their public REST API and returns clean output.
No dependencies — uses only Python stdlib.

Usage:
    python scripts/search_arxiv.py "GRPO reinforcement learning"
    python scripts/search_arxiv.py "transformer attention" --max 10 --sort date
    python scripts/search_arxiv.py --author "Yann LeCun" --max 5
    python scripts/search_arxiv.py --category cs.AI --sort date
    python scripts/search_arxiv.py --id 2402.03300
    python scripts/search_arxiv.py --id 2402.03300,2401.12345
    python scripts/search_arxiv.py "LLM fine-tuning" --json
    python scripts/search_arxiv.py --id 1706.03762 --bibtex
"""

import sys
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
import json
import argparse
import time
import re

NS = {'a': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}

RATE_LIMIT = 3.0  # seconds between requests (arXiv: ~1 req / 3 sec)
_last_request = 0.0


def rate_limit():
    """Ensure we respect arXiv rate limits."""
    global _last_request
    elapsed = time.time() - _last_request
    if elapsed < RATE_LIMIT:
        time.sleep(RATE_LIMIT - elapsed)
    _last_request = time.time()


def fetch_url(url: str) -> str:
    """Fetch a URL and return the response text."""
    rate_limit()
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Hermes-ArXiv-Skill/1.0 (mailto:hermes@nousresearch.com)'
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8')


def search_arxiv(query: str, max_results: int = 10, sort_by: str = 'submittedDate',
                 sort_order: str = 'descending', start: int = 0) -> list:
    """Search arXiv papers by keyword."""
    params = {
        'search_query': query,
        'max_results': max_results,
        'sortBy': sort_by,
        'sortOrder': sort_order,
        'start': start,
    }
    url = f"https://export.arxiv.org/api/query?{urllib.parse.urlencode(params)}"
    xml_data = fetch_url(url)
    return parse_arxiv_response(xml_data)


def fetch_papers_by_id(id_list: str) -> list:
    """Fetch specific papers by arXiv ID (comma-separated)."""
    url = f"https://export.arxiv.org/api/query?id_list={id_list}"
    xml_data = fetch_url(url)
    return parse_arxiv_response(xml_data)


def parse_arxiv_response(xml_data: str) -> list:
    """Parse arXiv Atom XML response into a list of paper dicts."""
    root = ET.fromstring(xml_data)
    papers = []
    for entry in root.findall('a:entry', NS):
        paper = {}

        title_el = entry.find('a:title', NS)
        paper['title'] = title_el.text.strip().replace('\n', ' ').replace('  ', ' ') if title_el is not None else ''

        id_el = entry.find('a:id', NS)
        raw_id = id_el.text.strip().split('/abs/')[-1] if id_el is not None else ''
        paper['id'] = re.sub(r'v\d+$', '', raw_id)
        paper['versioned_id'] = raw_id

        published_el = entry.find('a:published', NS)
        paper['published'] = published_el.text[:10] if published_el is not None else ''

        updated_el = entry.find('a:updated', NS)
        paper['updated'] = updated_el.text[:10] if updated_el is not None else ''

        authors = []
        for author_el in entry.findall('a:author', NS):
            name_el = author_el.find('a:name', NS)
            if name_el is not None:
                authors.append(name_el.text.strip())
        paper['authors'] = authors

        summary_el = entry.find('a:summary', NS)
        paper['summary'] = summary_el.text.strip().replace('\n', ' ') if summary_el is not None else ''

        cats = []
        for cat_el in entry.findall('a:category', NS):
            term = cat_el.get('term')
            if term:
                cats.append(term)
        paper['categories'] = cats

        primary_cat = entry.find('arxiv:primary_category', NS)
        paper['primary_category'] = primary_cat.get('term') if primary_cat is not None else (cats[0] if cats else '')

        paper['pdf_url'] = f"https://arxiv.org/pdf/{paper['id']}"
        paper['abs_url'] = f"https://arxiv.org/abs/{paper['id']}"

        paper['is_withdrawn'] = 'withdrawn' in paper['summary'].lower()[:200]

        papers.append(paper)

    return papers


def format_papers(papers: list, show_full_abstract: bool = False) -> str:
    """Format papers as readable text."""
    lines = []
    for i, paper in enumerate(papers, 1):
        abstract = paper['summary']
        if not show_full_abstract and len(abstract) > 250:
            abstract = abstract[:250].rsplit(' ', 1)[0] + '...'

        status = ' [WITHDRAWN]' if paper.get('is_withdrawn') else ''
        lines.append(f"{i}. [{paper['id']}] {paper['title']}{status}")
        lines.append(f"   Authors: {', '.join(paper['authors'][:10])}{' et al.' if len(paper['authors']) > 10 else ''}")
        lines.append(f"   Published: {paper['published']} | Categories: {', '.join(paper['categories'])}")
        lines.append(f"   Abstract: {abstract}")
        lines.append(f"   PDF: {paper['pdf_url']}")
        lines.append(f"   URL: {paper['abs_url']}")
        lines.append('')
    return '\n'.join(lines)


def format_json(papers: list, indent: int = 2) -> str:
    """Format papers as JSON."""
    output = []
    for paper in papers:
        output.append({
            'id': paper['id'],
            'title': paper['title'],
            'authors': paper['authors'],
            'published': paper['published'],
            'updated': paper['updated'],
            'categories': paper['categories'],
            'primary_category': paper['primary_category'],
            'abstract': paper['summary'],
            'pdf_url': paper['pdf_url'],
            'abs_url': paper['abs_url'],
            'is_withdrawn': paper.get('is_withdrawn', False),
        })
    return json.dumps(output, indent=indent, ensure_ascii=False)


def generate_bibtex(paper: dict) -> str:
    """Generate a BibTeX entry for a paper."""
    title = paper['title']
    authors = ' and '.join(paper['authors'])
    year = paper['published'][:4] if paper['published'] else '?'
    raw_id = paper['versioned_id'] if 'v' in paper.get('versioned_id', '') else paper['id']
    primary = paper['primary_category']
    last_name = paper['authors'][0].split()[-1] if paper['authors'] else 'Unknown'

    bib_id = f"{last_name}{year}_{paper['id'].replace('.', '')}"

    lines = [
        f"@article{{{bib_id},",
        f"  title     = {{{title}}},",
        f"  author    = {{{authors}}},",
        f"  year      = {{{year}}},",
        f"  eprint    = {{{raw_id}}},",
        f"  archivePrefix = {{arXiv}},",
        f"  primaryClass  = {{{primary}}},",
        f"  url       = {{https://arxiv.org/abs/{paper['id']}}}",
        "}",
    ]
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Search arXiv papers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "GRPO reinforcement learning" --max 5 --sort date
  %(prog)s --author "Yann LeCun" --max 5
  %(prog)s --category cs.CL --max 10 --sort date
  %(prog)s --id 2402.03300
  %(prog)s --id 2402.03300,2401.12345
  %(prog)s "transformer attention" --json
  %(prog)s --id 1706.03762 --bibtex
        """
    )

    query_group = parser.add_mutually_exclusive_group()
    query_group.add_argument('query', nargs='?', type=str, default=None,
                             help='Search query (e.g. "GRPO reinforcement learning")')
    query_group.add_argument('--id', dest='paper_id', type=str, default=None,
                             help='arXiv paper ID(s), comma-separated')
    query_group.add_argument('--author', type=str, default=None,
                             help='Search by author name')
    query_group.add_argument('--category', type=str, default=None,
                             help='Search by arXiv category (e.g. cs.CL)')

    parser.add_argument('--max', '-m', type=int, default=10, dest='max_results',
                        help='Maximum results (default: 10)')
    parser.add_argument('--sort', '-s', type=str, default='relevance',
                        choices=['relevance', 'date', 'updated'],
                        help='Sort order (default: relevance)')
    parser.add_argument('--start', type=int, default=0,
                        help='Result offset (default: 0)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    parser.add_argument('--full-abstract', action='store_true',
                        help='Show full abstract text')
    parser.add_argument('--bibtex', action='store_true',
                        help='Output BibTeX citation(s)')

    args = parser.parse_args()

    sort_map = {
        'relevance': ('relevance', 'descending'),
        'date': ('submittedDate', 'descending'),
        'updated': ('lastUpdatedDate', 'descending'),
    }
    sort_by, sort_order = sort_map[args.sort]

    papers = []
    if args.paper_id:
        papers = fetch_papers_by_id(args.paper_id)
    elif args.author:
        query = f'au:"{args.author}"'
        papers = search_arxiv(query, args.max_results, sort_by, sort_order, args.start)
    elif args.category:
        query = f'cat:{args.category}'
        papers = search_arxiv(query, args.max_results, sort_by, sort_order, args.start)
    elif args.query:
        papers = search_arxiv(args.query, args.max_results, sort_by, sort_order, args.start)
    else:
        parser.print_help()
        sys.exit(1)

    if not papers:
        print("No papers found.")
        sys.exit(0)

    if args.bibtex:
        for paper in papers:
            print(generate_bibtex(paper))
            print()
    elif args.json:
        print(format_json(papers))
    else:
        print(format_papers(papers, show_full_abstract=args.full_abstract))


if __name__ == '__main__':
    main()
