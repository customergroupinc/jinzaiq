"""JINZAiQ RSS collector. No paid API calls."""
import argparse
import hashlib
import html
import sqlite3
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB = BASE / "news.db"
JST = timezone(timedelta(hours=9))
# 日本国内で外国人材を採用する企業向けに、制度・採用・定着を幅広く収集する。
# 元の4語を残し、実務記事を拾う検索語を追加。RSS自体が検索結果を保証するものではない。
SEARCH_TERMS = [
    "特定技能",
    "育成就労",
    "技能実習",
    "外国人雇用",
    "外国人材 採用 企業",
    "外国人材 人手不足",
    "外国人材 定着 支援",
    "外国人社員 研修",
    "外国人材 受け入れ 事例",
    "外国人採用 費用 手続き",
    "在留資格 就労 企業",
    "登録支援機関 企業",
]
CATEGORIES = {
    "育成就労": "育成就労",
    "特定技能": "特定技能",
    "技能実習": "技能実習",
    "在留資格": "在留資格",
}


def connect():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL,
        source TEXT NOT NULL DEFAULT '', published TEXT NOT NULL,
        category TEXT NOT NULL, summary TEXT NOT NULL DEFAULT '',
        collected_at TEXT NOT NULL
    )""")
    return con


def classify(title):
    for keyword, category in CATEGORIES.items():
        if keyword in title:
            return category
    return "外国人雇用"


def parse_date(item):
    pub = item.findtext("pubDate") or item.findtext("{http://purl.org/dc/elements/1.1/}date")
    try:
        d = parsedate_to_datetime(pub)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(JST)
    except (TypeError, ValueError, IndexError):
        return None


def collect(limit=0, days=14):
    now = datetime.now(JST)
    cutoff = now - timedelta(days=days)
    found = {}
    successful_feeds = 0
    for term in SEARCH_TERMS:
        query = urllib.parse.quote(f"{term} when:{days}d")
        url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "JINZAiQ-demo/0.1"})
            with urllib.request.urlopen(req, timeout=15) as response:
                root = ET.fromstring(response.read(2_000_000))
            successful_feeds += 1
            for item in root.findall("./channel/item"):
                title = html.unescape((item.findtext("title") or "").strip())
                link = (item.findtext("link") or "").strip()
                when = parse_date(item)
                if not title or not link or when is None or not cutoff <= when <= now + timedelta(hours=1):
                    continue
                raw_source = item.find("source")
                source = raw_source.text.strip() if raw_source is not None and raw_source.text else "Google ニュース"
                # Don't use generated summaries or copy article text: source/link/title only.
                canonical_title = title.rsplit(" - ", 1)[0].strip()
                key = hashlib.sha256(canonical_title.casefold().encode("utf-8")).hexdigest()
                existing = found.get(key)
                if existing is None or when > existing["published"]:
                    found[key] = {"id": key, "title": canonical_title, "url": link,
                                  "source": source, "published": when, "category": classify(canonical_title)}
        except Exception as exc:
            print(f"取得できませんでした ({term}): {type(exc).__name__}: {exc}")
    # すべてのRSS取得が失敗した場合は、安全のためサイトの再生成を止める。
    if successful_feeds == 0:
        raise RuntimeError("すべてのニュースRSS取得に失敗しました。既存公開ページを維持するため更新を中止します。")
    entries = sorted(found.values(), key=lambda x: x["published"], reverse=True)
    if limit > 0:
        entries = entries[:limit]
    with connect() as con:
        before = con.total_changes
        # ニュースは公開日から指定期間だけ保持。過去データも整理する。
        con.execute("DELETE FROM articles WHERE published < ? AND id NOT LIKE 'demo-%'", (cutoff.isoformat(),))
        deleted = con.total_changes - before
        before = con.total_changes
        for a in entries:
            con.execute("""INSERT OR IGNORE INTO articles
                (id,title,url,source,published,category,summary,collected_at)
                VALUES (?,?,?,?,?,?,?,?)""",
                (a["id"], a["title"], a["url"], a["source"],
                 a["published"].isoformat(), a["category"], "", now.isoformat()))
        inserted = con.total_changes - before
        total = con.execute("SELECT COUNT(*) FROM articles WHERE id NOT LIKE 'demo-%'").fetchone()[0]
    print(f"RSS取得成功 {successful_feeds}/{len(SEARCH_TERMS)} / 取得候補 {len(found)} 件 / 今回の処理対象 {len(entries)} 件")
    print(f"新規保存 {inserted} 件 / 期限切れ削除 {deleted} 件 / 現在の保存件数 {total} 件")
    if not found:
        print("取得候補が0件です。RSSへの接続や検索条件を確認してください。")


def demo():
    now = datetime.now(JST).isoformat()
    samples = [
        ("デモ：特定技能に関する記事を表示する場所", "特定技能"),
        ("デモ：育成就労に関する記事を表示する場所", "育成就労"),
        ("デモ：外国人雇用に関する記事を表示する場所", "外国人雇用"),
    ]
    with connect() as con:
        for i, (title, category) in enumerate(samples):
            con.execute("""INSERT OR IGNORE INTO articles
                (id,title,url,source,published,category,summary,collected_at)
                VALUES (?,?,?,?,?,?,?,?)""",
                (f"demo-{i}", title, "", "デモ記事（実際の報道ではありません）", now,
                 category, "表示テスト用のダミーデータです。", now))
    print("デモ記事を登録しました。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="ダミー記事を追加（通信なし）")
    parser.add_argument("--limit", type=int, default=0, help="0=制限なし（初期値）")
    parser.add_argument("--days", type=int, default=14, help="保持・取得期間（日数、初期値14）")
    args = parser.parse_args()
    if args.demo:
        demo()
    else:
        collect(limit=max(0, args.limit), days=max(1, min(args.days, 90)))
