"""JINZAiQ: SQLiteニュースを読み取り、単体で開けるHTMLプレビューを生成する。
利用: /home/monta/jinzaiq/venv/bin/python /home/monta/jinzaiq/free_demo/build_jinzaiq_preview.py
既存アプリ・DBの変更なし。OpenAI API呼び出しなし。
"""
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB = BASE / 'news.db'
OUT = BASE / 'index.html'

HTML = r'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JINZAiQ｜外国人材のニュース・採用情報</title>
<meta name="description" content="外国人材の制度・採用・雇用に関するニュースを探せるJINZAiQです。">
<style>
:root{--navy:#102c46;--ink:#193047;--muted:#64768a;--green:#18aa94;--line:#e0e7ed;--bg:#f3f6f9;--white:#fff}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:var(--bg);font-family:-apple-system,BlinkMacSystemFont,"Noto Sans JP","Hiragino Kaku Gothic ProN",Meiryo,sans-serif;line-height:1.65}a{color:inherit;text-decoration:none}a:hover{color:#0a9584}.wrap{width:min(1160px,calc(100% - 36px));margin:auto}
.top{background:#081f33;color:#c8d7e2;font-size:11px}.top .wrap{display:flex;justify-content:space-between;gap:12px;padding:7px 0}.mast{background:var(--navy);color:white}.mast .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:25px 0}.brand{display:flex;align-items:center;gap:13px}.mark{width:39px;height:39px;border:2px solid #61d9c7;border-radius:10px;display:grid;place-items:center;color:#61d9c7;font-weight:900;font-size:23px}.logo{font-weight:900;letter-spacing:.05em;font-size:29px;line-height:1.1}.logo i{font-style:normal;color:#5de0c9}.sub{font-size:12px;color:#cadce9;margin-top:6px}.pillcta{display:inline-block;border-radius:6px;background:#29c4ac;color:#08293d;padding:10px 17px;font-size:12px;font-weight:800}.nav{background:white;border-bottom:1px solid var(--line)}.navinner{display:flex;gap:25px;align-items:center;overflow-x:auto;white-space:nowrap;min-height:50px;font-size:13px;font-weight:750}.navinner a:first-child{color:#087f76;border-bottom:3px solid var(--green);padding:15px 0}.ticker{background:#e7f5f2;border-bottom:1px solid #c8e5e0}.ticker .wrap{display:flex;gap:13px;align-items:center;padding:10px 0;font-size:12px}.tick{background:var(--green);color:#fff;border-radius:3px;font-weight:850;padding:3px 8px}.ticker span:last-child{color:#597b78;margin-left:auto}
.intro{padding:31px 0 23px;display:flex;align-items:end;justify-content:space-between;gap:18px}.eyebrow{letter-spacing:.13em;font-size:10px;color:#148779;font-weight:850}.intro h1{font-size:clamp(24px,3vw,34px);line-height:1.4;margin:7px 0}.intro p{margin:0;color:var(--muted);font-size:13px}.columns{display:grid;grid-template-columns:minmax(0,2fr) 310px;align-items:start;gap:25px}.hero{background:#102c46;color:white;border-radius:10px;padding:26px 30px;min-height:260px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden}.hero:after{content:"";position:absolute;right:-80px;top:-130px;width:400px;height:400px;border:65px solid rgba(69,199,178,.10);border-radius:50%;pointer-events:none}.hero .label{font-size:11px;font-weight:750;color:#8be0d1;letter-spacing:.1em}.hero h2{font-size:clamp(21px,2.6vw,29px);line-height:1.55;max-width:650px;margin:20px 0 14px;position:relative;z-index:1}.hero .foot{font-size:11px;color:#b7d1df;position:relative;z-index:1}.hero a{text-decoration:underline;text-underline-offset:4px}.section{margin:22px 0}.sectiontitle{display:flex;justify-content:space-between;gap:8px;align-items:center;margin-bottom:10px}.sectiontitle h2{font-size:19px;margin:0}.sectiontitle small{font-size:12px;color:var(--muted)}.panel{background:#fff;border:1px solid var(--line);border-radius:9px;overflow:hidden}.ai{padding:18px 20px;background:#effaf7;border-left:4px solid #26b99f}.ai b{font-size:14px}.ai p{font-size:12px;color:#536977;margin:7px 0 0}.controls{display:flex;gap:8px;flex-wrap:wrap;padding:19px 18px 13px}.chip{border:1px solid #dae5e9;background:#fff;border-radius:20px;padding:7px 12px;font-size:12px;cursor:pointer;color:#40556a}.chip.active{background:#0c766f;color:white;border-color:#0c766f}.searchrow{display:flex;gap:9px;padding:0 18px 16px}input[type=search]{width:100%;min-width:0;padding:11px 13px;border-radius:6px;border:1px solid #d5e0e8;font-size:14px}.count{color:var(--muted);font-size:12px;margin:auto 0;white-space:nowrap}.item{display:flex;gap:16px;padding:18px;border-top:1px solid #edf0f3;align-items:flex-start}.thumb{width:88px;min-width:88px;height:82px;background:#e7f3f0;color:#168979;border-radius:7px;display:grid;place-items:center;font-size:28px}.thumb.policy{background:#ebf0f9;color:#5772a8}.thumb.employment{background:#f1f1fa;color:#7d70aa}.itembody{min-width:0;flex:1}.category{color:#087f72;font-size:11px;font-weight:800}.item h3{font-size:15px;line-height:1.55;margin:5px 0 7px}.meta{font-size:11px;color:#79889a}.desc{font-size:12px;color:#617487;margin:7px 0 0}.pager{display:flex;align-items:center;justify-content:center;gap:14px;padding:20px;border-top:1px solid var(--line)}.pager button{background:#fff;border:1px solid var(--line);padding:9px 14px;border-radius:6px;cursor:pointer}.pager button:disabled{opacity:.35;cursor:default}.pager span{font-size:12px;color:var(--muted)}.empty{padding:26px;color:var(--muted);font-size:13px}.side .panel{padding:20px;margin-bottom:17px}.side h3{margin:0 0 12px;font-size:17px}.side p{font-size:12px;color:var(--muted);margin:7px 0;line-height:1.8}.side a.rank{display:flex;gap:13px;border-top:1px solid #edf0f3;padding:12px 0;font-size:12px;line-height:1.6}.num{color:#0eae95;font-size:17px;font-weight:900}.ad{border:1px dashed #c5ced6;border-radius:8px;min-height:178px;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:12px;color:#8b99a8;background:#edf1f4;margin-bottom:17px;font-size:13px}.ad small{font-size:10px;letter-spacing:.15em}.recruit{background:#102c46;color:white;border-radius:8px;padding:22px;margin-bottom:18px}.recruit h3{margin:0;font-size:19px}.recruit p{color:#c2d4df}.recruit .pillcta{margin-top:10px}.guides{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.guide{background:#fff;border:1px solid var(--line);padding:18px;border-radius:8px}.guide b{font-size:14px}.guide p{font-size:12px;color:var(--muted)}.guide .tag{font-size:11px;color:#0f8e7d;font-weight:800}.company{background:#102c46;color:#fff;border-radius:10px;margin:28px 0;padding:27px 30px;display:flex;justify-content:space-between;gap:20px;align-items:center}.company h2{margin:5px 0;font-size:21px}.company p{font-size:12px;color:#c4d5e0;margin:0}.footer{padding:28px 0 35px;color:#748394;font-size:11px;text-align:center}
@media(max-width:850px){.columns{grid-template-columns:1fr}.side{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.side>*{margin-bottom:0!important}.side .panel:first-child{grid-column:span 2}.guides{grid-template-columns:1fr 1fr}}
@media(max-width:580px){.mast .wrap{padding:17px 0}.logo{font-size:24px}.mast .pillcta{display:none}.ticker span:last-child{display:none}.intro{padding:24px 0 18px}.hero{padding:22px;min-height:240px}.item{gap:10px;padding:15px}.thumb{width:58px;min-width:58px;height:64px;font-size:22px}.item h3{font-size:14px}.side{grid-template-columns:1fr}.side .panel:first-child{grid-column:auto}.guides{grid-template-columns:1fr}.company{align-items:start;flex-direction:column}.count{display:none}}

/* JINZAiQ ライトブルーテーマ（既存デザインを保持） */
:root { --green:#397FC4; --bg:#F0F7FF; --line:#D8E6F4; }
body { background:#F0F7FF; }
.ticker { background:#E3F1FF; border-bottom-color:#C7E1F9; }
.tick,.chip.active { background:#397FC4; border-color:#397FC4; }
.ai { background:#EAF4FF; border-left-color:#397FC4; }
.pillcta { background:#78B8F2; color:#102C46; }
.mark { border-color:#89C8FF; color:#89C8FF; }
.logo i,.hero .label { color:#94CFFF; }
.thumb { background:#E4F1FF; color:#397FC4; }
.category,.num,.guide .tag,.eyebrow,.navinner a:first-child { color:#397FC4; }
.navinner a:first-child { border-bottom-color:#397FC4; }
/* トップ見出し3行制限 */
.hero h2 { display:-webkit-box; -webkit-box-orient:vertical; -webkit-line-clamp:3; overflow:hidden; overflow-wrap:anywhere; line-height:1.55; }

/* ニューステーマ別3コーナー：青色テーマとレスポンシブ表示 */
.topic-section{margin:24px 0 28px}
.topic-intro{color:#64768a;font-size:12px;margin:2px 0 12px}
.topic-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.topic-card{min-width:0;background:#fff;border:1px solid #D8E6F4;border-top:3px solid #397FC4;border-radius:9px;padding:15px 15px 12px}
.topic-card h3{margin:0 0 4px;color:#102c46;font-size:15px}
.topic-card .topic-note{margin:0 0 10px;color:#64768a;font-size:11px;min-height:30px}
.topic-card a{display:block;color:#193047;font-weight:700;font-size:12px;line-height:1.55;padding:10px 0;border-top:1px solid #eaf0f7;overflow-wrap:anywhere}
.topic-card a:hover{color:#397FC4;text-decoration:underline}
.topic-card .topic-meta{display:block;color:#788ba0;font-size:10px;font-weight:400;margin-top:3px}
.topic-card .topic-empty{font-size:12px;color:#64768a;padding:8px 0}
@media(max-width:850px){.topic-grid{grid-template-columns:1fr}}
@media(min-width:581px) and (max-width:850px){.topic-card .topic-note{min-height:0}}
</style></head><body>
<div class="top"><div class="wrap"><span>外国人材・特定技能・育成就労の情報メディア</span><span>外国人材のニュース・採用情報</span></div></div>
<header class="mast"><div class="wrap"><div class="brand"><span class="mark">Q</span><div><div class="logo">JINZA<i>iQ</i></div><div class="sub">外国人材の「今」がわかる。採用の「次」が見える。</div></div></div><a class="pillcta" href="#consult">企業向け採用相談（準備中）</a></div></header>
<nav class="nav"><div class="wrap navinner"><a href="#latest">トップ</a><a href="#latest">最新ニュース</a><a href="#latest" data-nav-category="特定技能">特定技能</a><a href="#latest" data-nav-category="育成就労">育成就労</a><a href="#latest" data-nav-category="外国人雇用">外国人雇用</a><a href="#guides">採用ガイド</a><a href="#consult">採用相談</a></div></nav>
<div class="ticker"><div class="wrap"><span class="tick">NEWS</span><span>収集済みの外国人材ニュースを表示中。最新情報はリンク先の元記事を確認してください。</span><span id="generatedAt"></span></div></div>
<div class="wrap"><section class="intro"><div><div class="eyebrow">FOREIGN TALENT & BUSINESS NEWS</div><h1>外国人材の最新情報を、ビジネスの力に。</h1><p>ニュースで動向をつかむ。制度を理解する。採用の次の一手につなげる。</p></div></section>
<div class="columns"><main><section class="hero"><div class="label">TOP STORY ／ 最新ニュース</div><div><h2 id="heroTitle">ニュースを読み込んでいます</h2><div class="foot" id="heroMeta"></div></div></section>
<section class="section"><div class="ai"><b>JINZAiQについて</b><p>外国人材の採用・雇用に関するニュースをカテゴリー別に掲載しています。詳しい内容は各記事のリンクからご確認ください。</p></div></section>
<section class="topic-section" aria-label="テーマ別ニュース">
  <div class="sectiontitle"><h2>テーマ別に読む</h2><small>採用担当者向けピックアップ</small></div>
  <p class="topic-intro">記事タイトルをもとに自動分類しています。詳しい情報は各媒体の元記事で確認してください。</p>
  <div class="topic-grid">
    <section class="topic-card"><h3>重要ニュース</h3><p class="topic-note">行政・政策・受入れ方針など</p><div id="topicImportant"></div></section>
    <section class="topic-card"><h3>制度改正</h3><p class="topic-note">特定技能・育成就労・在留資格</p><div id="topicPolicy"></div></section>
    <section class="topic-card"><h3>採用・雇用動向</h3><p class="topic-note">人材確保・企業の受入れ事例など</p><div id="topicHiring"></div></section>
  </div>
</section>
<section class="section" id="latest"><div class="sectiontitle"><h2>最新ニュース・トピックス</h2><small id="totalCount"></small></div><div class="panel"><div class="controls" id="categories"></div><div class="searchrow"><input type="search" id="search" placeholder="ニュースのタイトル・媒体名で検索" aria-label="ニュース検索"><span class="count" id="matchedCount"></span></div><div id="articles"></div><div class="pager"><button id="prev">← 前へ</button><span id="paging"></span><button id="next">次へ →</button></div></div></section>
<section class="section" id="guides"><div class="sectiontitle"><h2>外国人採用 お役立ちガイド</h2><small>今後公開予定</small></div><div class="guides"><div class="guide"><span class="tag">制度・基本</span><h3>特定技能とは？</h3><p>企業向けの制度解説記事を作成予定。</p></div><div class="guide"><span class="tag">採用実務</span><h3>外国人採用の費用と手続き</h3><p>手続きの流れを解説予定。</p></div><div class="guide"><span class="tag">定着支援</span><h3>外国人社員の受入れ準備</h3><p>教育・生活支援の実務を紹介予定。</p></div></div></section></main>
<aside class="side"><div class="panel"><h3>最新ニュース 5件</h3><div id="latestFive"></div></div><div class="recruit"><span class="eyebrow" style="color:#78d8c8">FOR BUSINESS</span><h3>外国人材の採用を<br>検討している企業様へ</h3><p>採用相談の窓口は今後設置予定。現段階ではフォーム送信や紹介は行いません。</p><a class="pillcta" href="#consult">ご相談案内（準備中）</a></div><div class="panel"><h3>JINZAiQについて</h3><p>外国人材のニュース・実務情報を整理する個人運営メディアです。出典の元記事リンクを掲載しています。</p></div></aside></div>
<section class="company" id="consult"><div><div class="eyebrow" style="color:#7de1cd">FOREIGN TALENT RECRUITMENT</div><h2>外国人材の採用を検討している企業様へ</h2><p>企業向け採用相談窓口は公開準備中です。個人情報の送信機能はありません。</p></div><span class="pillcta">公開準備中</span></section></div>
<footer class="footer">JINZAiQ ／ RSS記事の出典・リンクを掲載 ／ 個別ニュースの正確性は元記事でご確認ください</footer>
<script>
const rawNews=__ARTICLES_JSON__;
const generatedAt=__GENERATED_JSON__;
const news=rawNews.map(x=>({...x, title:String(x.title||''),source:String(x.source||''),category:String(x.category||'外国人雇用'),url:String(x.url||'')}));
const cats=['すべて',...new Set(news.map(x=>x.category))];let selected='すべて';let page=1;const perPage=20;
const $=s=>document.querySelector(s);
function text(tag,txt,cls){const e=document.createElement(tag);if(cls)e.className=cls;e.textContent=txt;return e}
function articleLink(x){const a=document.createElement('a');a.textContent=x.title;a.href=x.url||'#';if(x.url){a.target='_blank';a.rel='noopener noreferrer'}else{a.addEventListener('click',e=>e.preventDefault())}return a}
function filtered(){const q=$('#search').value.trim().toLocaleLowerCase();return news.filter(x=>(selected==='すべて'||x.category===selected)&&(!q||(x.title+' '+x.source+' '+x.category).toLocaleLowerCase().includes(q)))}
function render(){const hits=filtered();const pages=Math.max(1,Math.ceil(hits.length/perPage));page=Math.min(page,pages);const list=$('#articles');list.replaceChildren();for(const x of hits.slice((page-1)*perPage,page*perPage)){const row=text('article','','item');const thumb=text('div',x.category.includes('制度')||x.category.includes('技能')?'◇':'◈','thumb '+(x.category.includes('技能')?'policy':'employment'));row.append(thumb);const body=text('div','','itembody');body.append(text('div',x.category,'category'));const h=text('h3','');h.append(articleLink(x));body.append(h);body.append(text('div',[x.published.slice(0,16).replace('T',' '),x.source].filter(Boolean).join(' ・ '),'meta'));row.append(body);list.append(row)}if(!hits.length)list.append(text('div','該当するニュースが見つかりません。検索条件を変えてみてね。','empty'));$('#paging').textContent=`${page} / ${pages}ページ`;$('#prev').disabled=page===1;$('#next').disabled=page===pages;$('#matchedCount').textContent=`${hits.length}件`;$('#totalCount').textContent=`収集記事 ${news.length}件`}
function setCategory(c){selected=c;page=1;document.querySelectorAll('[data-cat]').forEach(b=>b.classList.toggle('active',b.dataset.cat===c));render()}
const chips=$('#categories');for(const c of cats){const btn=text('button',c,'chip');btn.type='button';btn.dataset.cat=c;btn.addEventListener('click',()=>setCategory(c));chips.append(btn)}
$('#search').addEventListener('input',()=>{page=1;render()});$('#prev').addEventListener('click',()=>{page--;render();$('#latest').scrollIntoView()});$('#next').addEventListener('click',()=>{page++;render();$('#latest').scrollIntoView()});document.querySelectorAll('[data-nav-category]').forEach(a=>a.addEventListener('click',()=>setCategory(a.dataset.navCategory)));
// 日本国内の採用実務との関連性を重視。タイトルと出典のみで判定する目安です。
// 海外のみのニュースは特集枠から外しやすくするが、一覧からは削除しません。
function isForeignOnly(x) {
  const title=String(x.title||'');
  const source=String(x.source||'');
  const overseas=/(?:韓国|中国|米国|アメリカ|英国|イギリス|ドイツ|フランス|カナダ|オーストラリア|台湾|フィリピン|インドネシア|ベトナム)(?:政府|企業|中小企業|労働省|労働者|国内|の雇用|の制度|の永住権)|グリーンカード|米政権|米労働省|韓国政府|中国政府|海外の労働市場/;
  const japaneseContext=/日本国内|日本企業|日本で|日本への|日本向け|日本政府|日本の受入れ|日本の受け入れ|日本の雇用|日本の採用|訪日|来日|在留資格|出入国在留管理庁|入管庁|特定技能|育成就労|技能実習|外国人材/;
  return overseas.test(title) && !japaneseContext.test(title) && !/日本経済新聞|厚生労働省|法務省/.test(source);
}
function domesticScore(x) {
  const t=String(x.title||'');
  const source=String(x.source||'');
  let score=0;
  if (/出入国在留管理庁|入管庁|厚生労働省|法務省|日本政府|閣議決定|政府有識者会議/.test(t)) score+=20;
  else if (/政府|有識者会議|自治体|都道府県|市役所|県庁/.test(t)) score+=5;
  if (/特定技能|育成就労|技能実習|在留資格/.test(t)) score+=10;
  if (/改正|見直し|施行|運用方針|受入れ方針|受け入れ方針|分野追加|対象分野|受入れ上限/.test(t)) score+=12;
  if (/日本企業|国内企業|国内の|日本国内|採用|外国人雇用|人材確保|人手不足|雇用実態|受入れ事例|受け入れ事例|マッチング/.test(t)) score+=7;
  if (/日本経済新聞|NHK|厚生労働省|法務省|出入国在留管理庁|国土交通省/.test(source)) score+=3;
  if (/無料.*セミナー|セミナー|ウェビナー|開催のお知らせ|参加者募集|キャンペーン|説明会|講座|広告|プレスリリース/.test(t)) score-=32;
  if (/PR TIMES|プレスリリース/.test(source)) score-=18;
  if (/逮捕|窃盗|強盗|殺人|詐欺|容疑|ひき逃げ|酒酔い|暴行|傷害|送検|起訴|空き家.*盗/.test(t)) score-=35;
  if (isForeignOnly(x)) score-=35;
  if (t.length>110) score-=3;
  return score;
}
// 日本の制度・採用関連が候補にあれば、その中から最重要の1件を選ぶ。
if(news.length) {
  const candidates=news.slice(0,80);
  const suitable=candidates.filter(x=>domesticScore(x)>0&&!isForeignOnly(x));
  const pool=suitable.length?suitable:candidates;
  const feature=pool.reduce((best,item)=>domesticScore(item)>domesticScore(best)?item:best,pool[0]);
  const hero=$('#heroTitle');hero.replaceChildren(articleLink(feature));
  hero.querySelector('a').title=feature.title;
  $('#heroMeta').textContent=[feature.category,feature.source,feature.published.slice(0,16).replace('T',' ')].filter(Boolean).join(' ・ ');
}else {
  $('#heroTitle').textContent='まだニュースがありません';
  $('#heroMeta').textContent='最新ニュースを準備しています';
}

// 右サイドバーのみ同じ話題の連続掲載を抑える。DBもメイン一覧も削除しない。
function normalizeNewsTitle(title) {
  return String(title||'').normalize('NFKC').toLowerCase()
    .replace(/[\s「」『』【】（）()、。・!！?？:：\-―ー\/\[\]［］]/g,'');
}
function trigrams(s) {
  const parts=new Set();
  for(let i=0;i<s.length-2;i++)parts.add(s.slice(i,i+3));
  return parts;
}
function threeGramSimilarity(a,b) {
  const aa=trigrams(a),bb=trigrams(b);
  if(!aa.size||!bb.size)return 0;
  let common=0;
  for(const part of aa)if(bb.has(part))common++;
  return 2*common/(aa.size+bb.size);
}
function sameTopic(a,b) {
  const x=normalizeNewsTitle(a.title),y=normalizeNewsTitle(b.title);
  if(x===y)return true;
  if(x.length<12||y.length<12)return false;
  // 公開日が大きく異なる場合は別ニュースとして扱う
  const ta=Date.parse(a.published),tb=Date.parse(b.published);
  if(Number.isFinite(ta)&&Number.isFinite(tb)&&Math.abs(ta-tb)>3*86400000)return false;
  const similarity=threeGramSimilarity(x,y);
  if(similarity>=0.82)return true;
  // 同一組織による同種類のイベントなら、言い換えの重複を検出
  const event=/研修会|講習会|説明会|セミナー|会議|シンポジウム|協議会/;
  const coreOrg=s=>{
    const m=s.match(/^.{2,24}?(?:協|組合|協会|連合会|大学|株式会社|会社|県庁|市役所|自治体|機構|グループ)/);
    return m?m[0]:'';
  };
  const orgX=coreOrg(x),orgY=coreOrg(y);
  if(orgX&&orgX===orgY&&event.test(x)&&event.test(y)&&similarity>=0.24)return true;
  // 冒頭表現の一致は単独では判断しない（誤削除防止）
  return x.slice(0,7)===y.slice(0,7)&&similarity>=0.57;
}
// 3つのテーマ別コーナー（元のニュース一覧やDBは変更しない）
// 記事タイトルに基づく無料の目安判定。誤分類の可能性があります。
function isPromotionOrIncident(x){
  return /セミナー|ウェビナー|講座|説明会|参加募集|開催のお知らせ|キャンペーン|無料Web|逮捕|窃盗|殺人|詐欺|容疑|ひき逃げ|酒酔い|送検|起訴/.test(x.title)
    || /PR TIMES/.test(x.source);
}
// 国内との関係が明確でない記事は特集枠では低く評価する。
const topicDefinitions=[
  {id:'topicImportant',test:x=>/政府|法務省|厚生労働省|入管庁|有識者会議|閣議|運用方針|受入れ方針|受け入れ方針|政策|規制|自治体|制度改正/.test(x.title),minScore:18},
  {id:'topicPolicy',test:x=>/特定技能|育成就労|在留資格|技能実習/.test(x.title)&&/改正|見直し|施行|制度|運用|方針|分野|受入れ|受け入れ|閣議/.test(x.title),minScore:12},
  {id:'topicHiring',test:x=>/人材確保|採用|雇用|人手不足|受入れ|受け入れ|マッチング|就職|外国人材紹介/.test(x.title),minScore:4}
];
const usedTopicArticles=[];
for(const section of topicDefinitions){
  const target=$('#'+section.id);
  const candidates=news
    .filter(x=>section.test(x)&&!isPromotionOrIncident(x)&&!isForeignOnly(x)&&domesticScore(x)>=section.minScore)
    .sort((a,b)=>domesticScore(b)-domesticScore(a)); // 同点は元の新着順を保持
  const selected=[];
  for(const item of candidates){
    if(usedTopicArticles.some(other=>sameTopic(item,other))||selected.some(other=>sameTopic(item,other)))continue;
    selected.push(item);
    if(selected.length>=2)break;
  }
  for(const item of selected){
    usedTopicArticles.push(item);
    const link=articleLink(item);
    link.append(text('span',[item.published.slice(0,10),item.source].filter(Boolean).join(' ・ '),'topic-meta'));
    target.append(link);
  }
  if(!selected.length)target.append(text('p','現在、該当する記事はありません。','topic-empty'));
}
const latest=$('#latestFive');
const uniqueNews=[];
for(const item of news) {
  if(!uniqueNews.some(previous=>sameTopic(item,previous)))uniqueNews.push(item);
  if(uniqueNews.length>=5)break;
}
for(let i=0;i<uniqueNews.length;i++) {
  const x=uniqueNews[i];const a=document.createElement('a');
  a.className='rank';a.href=x.url||'#';
  if(x.url){a.target='_blank';a.rel='noopener noreferrer';}
  a.append(text('span',String(i+1).padStart(2,'0'),'num'));
  const box=text('span',x.title);box.append(text('div',x.category,'meta'));
  a.append(box);latest.append(a);
}
$('#generatedAt').textContent='最終更新：'+generatedAt+' JST';setCategory('すべて');
</script></body></html>'''


def main():
    if not DB.is_file():
        raise SystemExit(f'ニュースDBがありません: {DB}')
    connection = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    try:
        articles = [dict(x) for x in connection.execute(
            "SELECT title,url,source,published,category FROM articles WHERE id NOT LIKE 'demo-%' ORDER BY published DESC")]
    except sqlite3.DatabaseError as exc:
        raise SystemExit(f'記事の読み込みに失敗: {exc}') from exc
    finally:
        connection.close()
    # JSONをHTML内に安全に埋め込む。タイトル等にHTMLタグがあってもコードとして動かさない。
    def safe_json(obj):
        return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    markup = HTML.replace('__ARTICLES_JSON__', safe_json(articles))
    markup = markup.replace('__GENERATED_JSON__', safe_json(datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M')))
    OUT.write_text(markup, encoding='utf-8')
    print(f'公開HTML生成OK：{len(articles)}件 / {OUT}')
    print('GitHub Actionsから更新できます。')


if __name__ == '__main__':
    main()
