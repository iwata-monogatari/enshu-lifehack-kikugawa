#!/usr/bin/env python3
"""Build the Kikugawa guides, questions, checklists, directory and home sections.

Editorial data: data/portal_content.json. Existing article bodies and shared
footer/consultation sections are preserved. Run after generate_pages.py.
"""
import hashlib, html, json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parent.parent
SITE='https://kikugawa.enshu-lifehack.com'
DATA=json.loads((ROOT/'data/portal_content.json').read_text(encoding='utf-8'))
DATE=DATA['date']
CURRENT=DATA['current_information']
NOTICES={notice['id']:notice for notice in CURRENT['notices']}
FACT_LABELS=json.loads((ROOT/'data/fact_labels.json').read_text(encoding='utf-8'))
TOPICS=json.loads((ROOT/'data/topics_master.json').read_text(encoding='utf-8'))
CONTENTS={x['href']:x for p in (ROOT/'data/content').glob('*.json') for x in json.loads(p.read_text(encoding='utf-8'))}
e=lambda s:html.escape(str(s),quote=True)
pages=[]
NAV='<nav class="portal-nav" aria-label="サイト内の案内">'+''.join(f'<a href="{u}">{t}</a>' for u,t in [('/','ホーム'),('/guide/','暮らしのガイド'),('/questions/','質問から探す'),('/checklists/','手続きチェック'),('/places/','菊川を訪ねる'),('/support/','支援・補助'),('/updates/','更新情報')])+'</nav>'
CSS='<link rel="stylesheet" href="/assets/portal.css?v=20261121b">'
JS='<script src="/assets/portal.js?v=20261121" defer></script>'
CURRENT_CSS='<link rel="stylesheet" href="/assets/portal-current.css?v=20261124">'
def links(items):return '<div class="portal-links">'+''.join(f'<a href="{e(x["href"])}">{e(x["title"])}</a>' for x in items)+'</div>'
def sources(items):return '<section class="portal-sources"><h2>公式情報・確認先</h2><p>確認日：'+DATE+'。開館・募集・制度の変更はリンク先でご確認ください。</p><ul>'+''.join(f'<li><a href="{e(x["url"])}" target="_blank" rel="noopener">{e(x["label"])}</a>'+ (f' <small>（{e(x["checked_on"])}確認）</small>' if x.get('checked_on') else '')+'</li>' for x in items)+'</ul></section>'
def notice_item(notice, detail=False, show_guide=True):
 title=e(notice['title'])
 schedule=e(notice['schedule'])
 url=e(notice['url'])
 official=e(notice['official'])
 href=notice.get('href')
 guide=f' <a href="{e(href)}{("#current-information" if "#" not in href and href in CURRENT["guide_notes"] else "")}" aria-label="{title}の関連ガイド">関連ガイド</a>' if detail and href and show_guide else ''
 summary=f'<p>{e(notice["summary"])}</p>' if detail else ''
 return f'<li><h3>{title}</h3><p>{schedule}</p>{summary}<p><a href="{url}">{official}</a>{guide}</p></li>'

def current_information(detail=False):
 notices=CURRENT['notices'] if detail else [NOTICES[key] for key in CURRENT['home']]
 items=''.join(notice_item(notice, detail) for notice in notices)
 more='' if detail else links([{'href':'/updates/#current-information','title':'更新内容と確認先をまとめて見る'}])
 return f'<section id="current-information" class="portal-panel current-information"><p class="portal-kicker"><time datetime="{CURRENT["date"]}">{CURRENT["date"]}</time> 公式情報確認</p><h2>菊川の最新情報</h2><ul>{items}</ul>{more}</section>'

def current_guide_note(config):
 items=''.join(notice_item(NOTICES[key], True, show_guide=False) for key in config['notices'])
 related=links(config['links']) if config.get('links') else ''
 return f'<aside id="current-information" class="portal-panel current-information"><h2>{e(config["title"])}</h2><p class="mini">公式情報確認：<time datetime="{CURRENT["date"]}">{CURRENT["date"]}</time></p><ul>{items}</ul>{related}</aside>'

def home_hero(question_count):
 return f'''<section class="portal-hero kikugawa-home-hero">
 <div class="home-hero-copy">
  <p class="eyebrow">静岡県菊川市</p>
  <h1>菊川で暮らす。訪ねる。<br>家族を支える。</h1>
  <p class="lead">手続き、子育て、親の介護、実家のこと。知りたいことを、答えと次の行動につなげる暮らしのガイドです。</p>
  <div class="portal-stats"><span>155の暮らしのガイド</span><span>{question_count}の質問と回答</span></div>
  <nav class="home-hero-links" aria-label="菊川の案内"><a href="#current-information">菊川の最新情報</a><a href="/for/visit/">菊川の散策ガイド</a></nav>
 </div>
 <figure>
  <img src="/assets/kikugawa-tea-fields-1280.webp" srcset="/assets/kikugawa-tea-fields-480.webp 480w, /assets/kikugawa-tea-fields-1280.webp 1280w" sizes="(max-width: 840px) 90vw, (max-width: 1160px) 44vw, 490px" width="1280" height="720" alt="菊川の丘に広がる茶畑。緑の茶の畝が斜面に沿って並ぶ" fetchpriority="high">
  <figcaption>菊川の茶畑。写真は<a href="https://opendata.pref.shizuoka.jp/dataset/8297.html">菊川市「菊川市の風景」</a>を縮小・WebP化（<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>）。<a href="https://kikugawaalb.atawi.link/features/tea-fields-shinkansen/">菊川の茶畑の写真特集へ</a></figcaption>
 </figure>
</section>'''

def card(url,title,desc,icon='🧭',meta=''):
 return f'<a class="portal-card" href="{e(url)}"><span class="icon" aria-hidden="true">{e(icon)}</span><h3>{e(title)}</h3><p>{e(desc)}</p>'+ (f'<p class="meta">{e(meta)}</p>' if meta else '')+'<span class="more">詳しく見る →</span></a>'
def write(href,title,lead,body,category='暮らしのガイド',synonyms=None,page_date=DATE):
 headcss=(ROOT/'parts/head-css.html').read_text(encoding='utf-8').strip()
 header=(ROOT/'parts/header.html').read_text(encoding='utf-8').strip()
 disclaimer=(ROOT/'parts/disclaimer.html').read_text(encoding='utf-8').strip()
 footer=(ROOT/'parts/footer.html').read_text(encoding='utf-8').strip()
 document=f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} | 菊川ライフハック</title><meta name="description" content="{e(lead)}"><link rel="canonical" href="{SITE}{href}"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<!-- PART:head-css:START -->{headcss}<!-- PART:head-css:END -->{CSS}{CURRENT_CSS if 'id="current-information"' in body else ''}{JS}</head><body>
<!-- PART:header:START -->{header}<!-- PART:header:END -->
<!-- PART:disclaimer:START -->{disclaimer}<!-- PART:disclaimer:END -->
<!-- PORTAL:NAV:START -->{NAV}<!-- PORTAL:NAV:END -->
<main class="portal"><div class="wrap"><p class="portal-kicker"><a href="/">菊川ライフハック</a> / {e(category)}</p>
<section class="portal-hero"><p class="eyebrow">KIKUGAWA LIFE GUIDE</p><h1>{e(title)}</h1><p class="lead">{e(lead)}</p></section>
{body}<div class="portal-bottom-nav">{links([{'href':'/','title':'ホームへ'},{'href':'/guide/','title':'暮らしのガイド一覧'},{'href':'/updates/','title':'更新・確認記録'}])}</div></div></main>
<!-- PART:footer:START -->{footer}<!-- PART:footer:END --></body></html>'''
 path=ROOT/href.strip('/')/'index.html';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(document,encoding='utf-8',newline='\n')
 pages.append({'href':href,'title':title,'lead':lead,'category':category,'icon':'🍵','synonyms':synonyms or [],'date':page_date})

# Purpose-oriented authored guides.
for a in DATA['articles']:
 body='<p class="portal-count">情報確認・編集：2026年11月21日</p>'
 latest=a.get('latest_sections')
 if latest:
  body+=f'<p class="portal-count">追加確認：<time datetime="{e(latest["date"])}">{e(latest["date"])}</time>（{"、".join(e(a['sections'][i]['title']) for i in latest['sections'])}）</p>'
 body+='<ul class="portal-toc">'+''.join(f'<li><a href="#section-{i}">{e(s["title"])}</a></li>' for i,s in enumerate(a['sections']))+'</ul>'
 for i,s in enumerate(a['sections']):
  body+=f'<section id="section-{i}"><h2>{e(s["title"])}</h2>'+''.join(f'<p>{e(p)}</p>' for p in s['paragraphs'])+links(s['links'])+'</section>'
  if i==0 and a.get('table'):
   t=a['table'];body+='<section><h2>目的別に条件を比較する</h2><p class="portal-count">表は横にスクロールできます。</p><div class="portal-table-wrap" tabindex="0" role="region" aria-label="支援制度の比較表"><table class="portal-table"><thead><tr>'+''.join(f'<th scope="col">{e(h)}</th>' for h in t['headers'])+'</tr></thead><tbody>'
   for row in t['rows']:body+='<tr>'+''.join(f'<td>{e(v)}</td>' for v in row[:-1])+f'<td><a href="/life/{e(row[-1])}/">詳細・窓口を見る</a></td></tr>'
   body+='</tbody></table></div></section>'
 body+=sources(a['sources'])
 write(a['href'],a['title'],a['lead'],body, '目的別ガイド', page_date=latest['date'] if latest else DATE)

def filters(categories,placeholder,pagesize=0):
 return f'<section data-filter data-page-size="{pagesize}"><div class="portal-search"><div class="search-word"><label for="filter-word">言葉で探す</label><input id="filter-word" type="search" data-search-input placeholder="{e(placeholder)}"></div><div><label for="filter-category">分野を選ぶ</label><select id="filter-category" data-category-input><option value="">すべての分野</option>'+''.join(f'<option value="{e(c)}">{e(c)}</option>' for c in categories)+'</select></div></div><p class="portal-count" data-result-count aria-live="polite"></p><p class="portal-empty" data-no-results hidden>該当する項目がありません。別の言葉で探すか、分野を「すべて」に戻してください。</p>'
def pager():return '<div class="portal-pager" data-pager hidden><button class="portal-button" type="button" data-previous>前のページ</button><span data-page-status aria-live="polite"></span><button class="portal-button" type="button" data-next>次のページ</button></div>'
categories=list(dict.fromkeys(t['category'] for t in TOPICS))
body='<p class="portal-note">全155項目を分野・言葉から探せます。個別ページには窓口、必要な準備、よくある質問、公式リンクを掲載。更新日は、そのページで確認した範囲を示しています。</p>'+filters(categories,'例：保育園／水道／空き家／介護／税金')+'<div class="portal-grid two">'
for t in TOPICS:
 content=CONTENTS.get(t['href'],{});review=t.get('content_review')
 date=('一部情報更新：'+review['date']) if review else ('基礎情報確認：'+(t.get('verified_date') or t.get('ai_checked_date') or '未記録'))
 c=card(t['href'],t['title'],content.get('lead','公式窓口と関連する手続きを確認します。'),t['icon'],date)
 body+=f'<div data-search-item data-category="{e(t["category"])}">'+c+'</div>'
body+='</div></section>'
write('/guide/','菊川の暮らしのガイド｜155項目から探す','引っ越し、子育て、学校、介護、空き家、税金、防災。制度名が分からなくても、気になる言葉から手続きと相談先を探せます。',body,synonyms=['手続き一覧','ガイド','全記事'])

# All distinct question/answer pairs, with topic and original confirmation scope.
questions=[];seen=set()
for t in TOPICS:
 for q in CONTENTS.get(t['href'],{}).get('qa',[]):
  key=(q['question'],q['answer'])
  if key in seen:continue
  seen.add(key);questions.append((t,q))
body='<p class="portal-note">各ガイドの質問と回答をまとめました。同じ質問でも手続きが違う場合があります。分野と元のページを確認してください。回答の基礎情報は元ページの確認日、最新の差分は更新記録に記載しています。</p>'+filters(categories,'例：土日／持ち物／補助／締切／転入',24)
for t,q in questions:
 qid=hashlib.sha256((t['href']+q['question']).encode()).hexdigest()[:12]
 review=t.get('content_review');date='一部情報更新：'+review['date'] if review else '基礎情報確認：'+(t.get('verified_date') or t.get('ai_checked_date') or '未記録')
 body+=f'<details class="portal-question" data-search-item data-category="{e(t["category"])}" id="q-{qid}"><summary>{e(q["question"])}</summary><div class="answer"><p>{q["answer"]}</p><p class="meta">{e(t["category"])} / {e(date)}</p><a href="{e(t["href"])}">{e(t["title"])} — 出典と手順を確認 →</a></div></details>'
body+=pager()+'</section>'
write('/questions/',f'菊川の暮らしの質問集｜{len(questions)}の回答を検索','疑問の言葉から、回答・窓口・手続きの説明へ進めます。質問を開くと、関連するガイドと公式確認先への入口が見つかります。',body,'質問と回答',['よくある質問','FAQ','相談'])

# Persistable and printable situation-specific checklists.
for c in DATA['checklists']:
 body=f'<section data-checklist="{e(c["slug"])}"><div class="portal-panel"><p class="portal-check-progress" data-check-progress aria-live="polite">0 / {len(c["items"])} 完了</p><p class="mini" data-save-status>チェック状況の保存にはJavaScriptを使用します。入力欄に氏名・住所などを書く必要はありません。</p><div class="portal-links"><button type="button" class="portal-button" data-check-reset>チェックを外す</button><button type="button" class="portal-button" data-print>印刷する</button></div></div>'
 for i,item in enumerate(c['items']):
  iid=c['slug']+'-'+hashlib.sha256(item['title'].encode()).hexdigest()[:8]
  body+=f'<div class="portal-check-item"><input type="checkbox" id="{iid}"><div><label for="{iid}">{i+1}. {e(item["title"])}</label><p>{e(item["body"])}</p><a href="{e(item["href"])}">必要書類・期限・公式窓口を確認 →</a></div></div>'
 body+='</section><p class="portal-note">チェック済みは利用者自身の作業メモです。申請の受理や制度の利用決定を示すものではありません。詳細は各手続きの公式案内で確認してください。</p>'
 write('/checklists/'+c['slug']+'/',c['title']+'｜手続きチェックリスト',c['lead'],body,'手続きチェック',['チェックリスト',c['title']])
body='<div class="portal-grid two">'+''.join(card('/checklists/'+c['slug']+'/',c['title'],c['lead'],'✅') for c in DATA['checklists'])+'</div>'
write('/checklists/','暮らしの手続きチェックリスト','やることを順番に確認し、済んだものにチェックを付けられます。チェックはこのブラウザだけに保存され、印刷して持ち出すこともできます。',body,'手続きチェック',['引っ越し','結婚','出産','転職','介護'])

# Directory covers the city's tourism list, with current closure/access caveats.
body='<p class="portal-note">市公式の観光スポット一覧をもとに、重複する「歴史街道館」と「塩の道公園」は一つに整理し、文化財センターを加えています。市内のすべての寺社・施設を網羅する一覧ではありません。確認できなかった情報は各項目に明記しています。</p>'+filters(list(dict.fromkeys(p['category'] for p in DATA['places'])),'例：公園／黒田／棚田／寺／下平川')+'<div class="portal-grid two">'
icons={'寺社':'⛩️','史跡・資料館':'🏛️','公園・運動':'🌳','自然・景観':'🌿','農園・体験':'🫐'}
for i,p in enumerate(DATA['places']):
 photo=p.get('photo')
 photo_link=f'<p><a href="{e(photo["href"])}">{e(photo["title"])} →</a></p>' if photo else ''
 body+=f'<article class="portal-card" data-search-item data-category="{e(p["category"])}" id="place-{i+1}"><p class="portal-kicker">{e(p["category"])}</p><h3><span aria-hidden="true">{icons[p["category"]]}</span> {e(p["name"])}</h3><p>{e(p["body"])}</p><p><strong>場所：</strong>{e(p["address"])}</p><p><strong>訪問前に：</strong>{e(p["note"])}</p><p><a href="{e(p["url"])}" target="_blank" rel="noopener">公式の説明・地図を見る →</a></p>{photo_link}<p class="meta">公開情報確認：{DATE}（現地確認ではありません）</p></article>'
body+='</div></section>'+links([{'href':'/for/visit/','title':'訪問計画の立て方'},{'href':'/life/start-living/public-transit/','title':'バス・公共交通'},{'href':'/life/play-out/rent-public-facilities/','title':'施設予約の方法'}])
body+='<aside class="portal-panel"><h2>訪ねる前に、昔の風景も見てみませんか</h2><p>菊川駅、堀之内、旧小笠町。菊川懐かし写真館では、場所・年代・出典から地域の写真をたどれます。いまの行き先案内と見比べると、まちの変化に気づくきっかけになります。</p>'+links([{'href':'https://kikugawaalb.atawi.link/','title':'菊川懐かし写真館で写真を探す'}])+'</aside>'
write('/places/','菊川の地域スポット案内｜史跡・寺社・公園・農園','菊川の景色と歴史を、行き先の名前や分野から探せます。見学範囲、季節営業、予約、開館日を、訪問前に一緒に確認しましょう。',body,'菊川を訪ねる',['観光','寺院','神社','公園','農園','史跡','資料館'])

# Dated, source-linked editorial update log rather than a blanket freshness claim.
updated=[t for t in TOPICS if t.get('content_review',{}).get('date')==DATE]
body=current_information(detail=True)+'<section class="portal-panel"><h2>11月21日に確認した範囲</h2><p>既存155項目の参照先を横断し、菊川市公式の参照URL217件を取得確認しました。期限・年度・窓口時間・料金・リンク先を照合し、差異や不足があったページを下に記録しています。URLが開くことと、掲載事項すべてを再確認したことは区別しています。</p><p>新しい目的別ガイド、地域スポット案内、質問検索、チェックリストも追加しました。質問集は既存の回答を統合したもので、全回答を11月21日に確認済みとするものではありません。</p><p>水道電子申請・一部窓口時間・空き家バンクの提出先は公式案内に表記差があるため、利用前の確認先を明記しています。相続空き家の税特例と相続登記は、国税庁・法務省の現行案内も照合しました。電話照会・現地訪問・実際の申請や施設利用は実施していません。</p></section><section><h2>11月21日に更新した内容と根拠</h2>'
for t in updated:
 r=t['content_review'];label={s['url']:s['label'] for s in t.get('sources_kikugawa',[])}
 body+=f'<article class="portal-panel"><h3><a href="{e(t["href"])}">{e(t["title"])}</a></h3><p>{e(r["summary"])}</p><ul>'+''.join(f'<li><a href="{e(u)}" target="_blank" rel="noopener">{e(label.get(u,"菊川市公式の確認先"))}</a></li>' for u in r['sources'])+'</ul></article>'
body+='</section>'
write('/updates/','菊川の最新情報・更新記録','菊川駅の送迎、図書館・バス・ごみ収集の年末年始、市の募集や催しを確認できます。更新日と公式の確認先を掲載しています。',body,'更新記録',['最新','2026','2027','令和9年度'],page_date=CURRENT['date'])

# Home: preserve the original category accordion and the Nov 19 photo/consultation area.
homepath=ROOT/'index.html';home=homepath.read_text(encoding='utf-8')
home=re.sub(r'<section class="(?:hero|portal-hero(?: kikugawa-home-hero)?)">.*?</section>',lambda _:home_hero(len(questions)),home,count=1,flags=re.S)
home_css='<link rel="stylesheet" href="/assets/kikugawa-home.css?v=20261124">'
if home_css not in home:home=home.replace('</head>',home_css+CURRENT_CSS+'</head>',1)
home=home.replace('<main><div class="wrap">','<main class="portal"><div class="wrap">',1)
purpose='<section><p class="portal-kicker">まずは、あなたの目的から</p><h2>菊川で、何をしたいですか？</h2><div class="portal-grid">'+card('/for/visit/','菊川を訪ねる','お茶、歴史、公園。開館日と見学範囲を確かめて、出かける計画を。','🍵')+card('/for/family/','菊川に親・実家がある','親の暮らし、介護、家の管理。帰省前に確認する順番を整理。','🏡')+card('/for/move/','移住・住み替えを考える','交通、学校、保育、住まい。契約前と引っ越し後を分けて準備。','🌿')+'</div></section>'
urgent='<section class="portal-urgent"><h2>急いで確認したいとき</h2><div class="portal-grid">'+''.join(f'<a href="{u}">{t}</a>' for u,t in [('/life/emergency/fire-ambulance/','🚑 救急車・消防の連絡'),('/life/health-medical/holiday-night-emergency-care/','🏥 夜間・休日の診療'),('/life/emergency/evacuation-hazard-map/','🗺️ 避難所・ハザードマップ'),('/life/emergency/road-river-info/','🌧️ 道路・河川情報'),('/life/troubles-consult/consumer-fraud/','⚠️ 消費者被害・詐欺'),('/life/troubles-consult/living-costs-trouble/','🤝 生活費の相談')])+'</div><p>命に関わる緊急時は119番。上のリンクは行政・救急の確認先へご案内します。</p></section>'
# Decorative emoji in the urgent links are hidden from assistive technologies.
urgent=re.sub(r'(<a href="[^"]+">)([^ ]+) ',r'\1<span aria-hidden="true">\2</span> ',urgent)
fresh='<section><p class="portal-kicker">2026年11月21日確認</p><h2>受付時期・制度の変更を確認する</h2><div class="portal-grid two">'
for url,status,cls,title,desc in [
 ('/life/family-grow/nursery-school/','第2期受付中','','2027年度の保育園・こども園','第2期は2027年1月8日まで。途中入園との違い、書類の準備を確認。'),
 ('/life/education/after-school-club/','一斉受付終了','ended','2027年度の放課後児童クラブ','期間後はこども政策課へ。12月14日以降の提出は2027年5月の入所調整。'),
 ('/life/work-life/start-business/','12月1日受付開始','soon','創業支援補助金の二次公募','12月15日17時必着。新たに必要な資金計画書と申請条件を確認。'),
 ('/life/start-living/city-hall-branches/','窓口運用変更','info','水曜・日曜の窓口を利用する前に','水曜延長は18:30まで。日曜は予約済みマイナンバーカード交付のみ。')]:
 fresh+=f'<a class="portal-card" href="{url}"><span class="portal-date {cls}">{status}</span><h3 style="margin-top:14px">{title}</h3><p>{desc}</p><span class="more">詳しく確認 →</span></a>'
fresh+='</div>'+links([{'href':'/updates/','title':'検診・税・住宅など、今回の更新をすべて見る'},{'href':'/support/','title':'支援・補助制度の対象と金額を比較する'}])+'</section>'
tools='<section><p class="portal-kicker">探す・整理する</p><h2>暮らしの疑問を、次の行動へ</h2><div class="portal-grid">'+card('/questions/','質問から答えを探す','「土日でもできる？」「何を持っていく？」分野とキーワードで回答を検索。','💬')+card('/checklists/','手続きをチェックする','転入、出産、結婚、転職、帰省。チェックを保存して、印刷もできます。','✅')+card('/places/','菊川の行き先を探す','史跡・寺社・公園・農園の特徴と、見学前に確かめたいこと。','🗺️')+'</div></section>'
memories='<section class="portal-panel" id="kikugawa-memories"><p class="portal-kicker">まちの記憶と、いまの暮らし</p><h2>昔の菊川を見て、いまの菊川を歩く。</h2><p>菊川駅や堀之内、旧小笠町の風景を写真でたどる「菊川懐かし写真館」。見慣れた場所の昔の姿を知ったら、現在の散策情報と合わせて、まちを訪ねてみませんか。</p>'+links([{'href':'https://kikugawaalb.atawi.link/','title':'菊川懐かし写真館を見る'},{'href':'/for/visit/','title':'いまの菊川の散策ガイドへ'}])+'</section>'
block='<!-- PORTAL:HOME:START -->'+purpose+urgent+current_information()+fresh+tools+memories+'<!-- PORTAL:HOME:END -->'
if '<!-- PORTAL:HOME:START -->' in home:home=re.sub(r'<!-- PORTAL:HOME:START -->.*?<!-- PORTAL:HOME:END -->',lambda m:block,home,flags=re.S)
else:home=home.replace('<section id="category-links">',block+'<section id="category-links">',1)
home=re.sub(r'<section class="updates">.*?</section>','<section class="portal-panel"><h2>情報の確認状況</h2><p>市公式の参照先と、期限・窓口・制度の変更を照合しました。ページごとの確認範囲と、公式ページ間で案内が異なる事項は更新記録にまとめています。</p>'+links([{'href':'/updates/','title':'更新・確認記録を見る'},{'href':'https://www.city.kikugawa.shizuoka.jp/','title':'菊川市公式サイトへ'}])+'</section>',home,count=1,flags=re.S)
homepath.write_text(home,encoding='utf-8',newline='\n')

# Shared discoverability without touching existing prose, metadata or footers.
targets=[homepath,ROOT/'terms/index.html']+list((ROOT/'life').rglob('index.html'))
for path in targets:
 text=path.read_text(encoding='utf-8')
 for key,label in FACT_LABELS.items():text=text.replace('<b>'+key+'</b>：','<b>'+e(label)+'</b>：')
 text=re.sub(r'/assets/portal.css\?v=[^\"]+', '/assets/portal.css?v=20261121b',text)
 if '/assets/portal.css' not in text:text=text.replace('</head>',CSS+'</head>',1)
 if '<!-- PORTAL:NAV:START -->' in text:text=re.sub(r'<!-- PORTAL:NAV:START -->.*?<!-- PORTAL:NAV:END -->',lambda m:'<!-- PORTAL:NAV:START -->'+NAV+'<!-- PORTAL:NAV:END -->',text,flags=re.S)
 else:text=re.sub(r'(<main\b)',lambda m:'<!-- PORTAL:NAV:START -->'+NAV+'<!-- PORTAL:NAV:END -->'+m.group(),text,count=1)
 guide_path='/'+path.parent.relative_to(ROOT).as_posix()+'/'
 guide_note=CURRENT['guide_notes'].get(guide_path)
 if guide_note:
  if CURRENT_CSS not in text:text=text.replace('</head>',CURRENT_CSS+'</head>',1)
  note='<!-- PORTAL:CURRENT:START -->'+current_guide_note(guide_note)+'<!-- PORTAL:CURRENT:END -->'
  if '<!-- PORTAL:CURRENT:START -->' in text:
   text=re.sub(r'<!-- PORTAL:CURRENT:START -->.*?<!-- PORTAL:CURRENT:END -->',lambda _:note,text,flags=re.S)
  else:
   text=text.replace('<h2 class="sec">先に知っておきたいこと',note+'<h2 class="sec">先に知っておきたいこと',1)
 path.write_text(text,encoding='utf-8',newline='\n')
(ROOT/'data/portal_pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
(ROOT/'data/portal_stats.json').write_text(json.dumps({'date':DATE,'life_pages':len(TOPICS),'questions':len(questions),'places':len(DATA['places']),'checklists':len(DATA['checklists']),'updated_life_pages':len(updated),'portal_pages':len(pages)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(f'Portal build: {len(pages)} pages, {len(questions)} questions, {len(DATA["places"])} places; existing content preserved')
