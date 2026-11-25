"""Discover candidate journal articles through Crossref; never modify published data.
Requires internet access. Python 3 standard library only. Use --help for options.
Search relevance is not a determination of empirical design, validity, or failure.
"""
import argparse, csv, html, json, re, time, unicodedata
from pathlib import Path
from urllib.parse import urlencode, unquote
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
ROOT=Path(__file__).resolve().parent
SEEDS={
'psychology': [('Social psychology','Embodied cognition',q) for q in ['physical cleanliness moral judgment','incidental disgust moral judgment','physical weight abstract judgment','physical warmth interpersonal warmth','social exclusion physical temperature','money priming social behavior','behavioral priming stereotype walking speed','color red performance attraction','power posing hormones risk','superstition performance luck','unconscious goal priming','religious priming morality','food priming generosity']]+[('Evolutionary psychology','Ovulation',q) for q in ['ovulation body odor attractiveness','menstrual cycle facial attractiveness','ovulation mate preferences','ovulation clothing ornamentation','fertility voice pitch','menstrual cycle creativity']]+[('Parapsychology','Anomalous cognition',q) for q in ['precognition retroactive influence experiment','extrasensory perception ganzfeld experiment','telepathy experiment','presentiment physiological anticipation']],
'neuroscience': [('Social neuroscience','Neural correlates',f'neural correlates {q} fMRI') for q in ['romantic love','moral beauty','moral judgment','guilt shame','embarrassment','pride','gratitude','envy jealousy','schadenfreude','forgiveness revenge','religious belief prayer','mystical experience','deception lying','political ideology','trustworthiness faces','social status','nostalgia','humor','aesthetic judgment']]+[('Neuroeconomics','Neuroforecasting',q) for q in ['neural prediction stock market trading bubble','brain activity financial market prediction','neural predictors music popularity','neuroforecasting advertising sales','neural prediction crowdfunding','neural predictors article sharing','EEG prediction movie popularity','neural prediction consumer choice']],
'medicine': [('Epidemiology','Calendar and health',q) for q in ['lunar phases hospital admissions','full moon psychiatric admission','lunar phases sleep menstrual cycle','birth month disease risk','birthday mortality surgery','Christmas holiday mortality','Friday the thirteenth hospital admission','zodiac sign health association']]+[('Alternative medicine','Unconventional therapies',q) for q in ['individualized homeopathy randomized placebo controlled trial','distant intercessory prayer randomized trial','distant healing randomized trial','therapeutic touch randomized clinical trial','magnetic bracelet randomized placebo controlled trial','homeopathy ultradilute clinical trial']]+[('Nutritional epidemiology','Food and health',q) for q in ['chocolate consumption cognitive function observational study','coffee consumption mortality cohort','chocolate consumption depression cross sectional','dietary intake personality mental health','food consumption unusual health outcomes observational']],
'political_science': [('Political psychology','Physical traits and ideology',q) for q in ['disgust sensitivity political conservatism','body odor political ideology','physical cleanliness political attitudes','taste sensitivity political ideology','facial appearance political ideology','face competence election outcome','facial attractiveness electoral success','voice pitch election outcomes','body height political preferences','handedness political ideology','upper body strength political attitudes','menstrual cycle political attitudes','testosterone political behavior','political ideology national flag priming','political affiliation odor preferences']]+[('Voting Behavior','Incidental events',q) for q in ['sports wins electoral outcomes voter','weather election vote choice','sunshine electoral turnout','shark attacks electoral outcomes','natural disaster electoral accountability','polling location priming voting','ballot order electoral outcomes','candidate name voter preferences']],
'economics_finance': [('Behavioral finance','Market anomalies',q) for q in ['lunar phase stock returns','Chinese zodiac stock market returns','astrology stock returns','superstition stock prices lucky numbers','weather stock returns investor mood','sunspots stock market returns','geomagnetic storms stock returns','temperature stock returns','sports sentiment stock returns','religious holiday stock returns','Ramadan stock returns','daylight saving stock market returns','music sentiment stock returns','Halloween stock returns','Friday thirteenth stock returns','Super Bowl indicator stock market']]+[('Corporate finance','Executive traits',q) for q in ['CEO facial width height ratio firm performance','CEO voice pitch compensation','CEO signature size investment','CEO narcissism accounting financial reporting','CEO facial masculinity tax avoidance','CEO physical attractiveness firm performance','CEO birth date firm performance','CEO golf firm performance']],
'marketing_consumer_research': [('Sensory marketing','Incidental sensory cues',q) for q in ['ambient temperature consumer choice','physical warmth product valuation','temperature conformity consumer preference','physical weight product judgment','packaging weight consumer perception','plate color food taste','cutlery color food consumption','background music wine perception','ambient scent purchase behavior','sound symbolism brand names','logo shapes brand judgment','product orientation embodied mental simulation','physical balance consumer choice','floor texture consumer judgment','physical touch consumer ownership','color red consumer choice','sensory discomfort consumer choice','cleanliness consumer judgment','psychological distance sensory consumer choice','superstition consumer choice','brand exposure creativity','money appearance consumer spending']]
}
COLS=['field','sub','topic','headline','title','venue','year','url','note','featured_rank','decision','query']
EXCLUDE=re.compile(r'\b(meta.analysis|systematic review|literature review|scoping review|editorial|commentary|corrigendum|erratum|retraction notice|retraction of|study protocol|registered report protocol|simulation study|methodological demonstration|reply to|comment on|dead salmon|beatles|parachute use to prevent)\b',re.I)
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKD',s).casefold() if c.isalnum())
def doi_of(s):
 s=unquote(s).lower().strip().rstrip('/')
 return s.split('doi.org/',1)[1] if 'doi.org/' in s else s if s.startswith('10.') else ''
def clean(s):return ' '.join(html.unescape(re.sub(r'<[^>]*>',' ',s)).split())
def metadata(item, field, sub, topic, q):
 if item.get('type')!='journal-article':return None
 title=clean(next(iter(item.get('title',[])),''));venue=clean(next(iter(item.get('container-title',[])),''));doi=item.get('DOI','')
 if not title or not venue or not doi.startswith('10.') or EXCLUDE.search(title):return None
 date=(item.get('published') or item.get('issued') or {}).get('date-parts',[])
 if not date or not date[0]:return None
 # Crossref search can return tangential matches; discard many obvious ones.
 terms={w for w in re.findall(r'[a-z]{4,}',q.lower()) if w not in {'with','from','effects','effect','study','trial','research'}}
 text=(title+' '+clean(item.get('abstract',''))).lower()
 if terms and sum(t in text for t in terms)<min(2,len(terms)):return None
 return dict(field=field,sub=sub,topic=topic,headline='',title=title,venue=venue,year=str(date[0][0]),url='https://doi.org/'+doi,note='',featured_rank='',decision='',query=q)
def query(q,rows,email):
 args={'query.bibliographic':q,'filter':'type:journal-article','rows':rows}
 if email:args['mailto']=email
 req=Request('https://api.crossref.org/works?'+urlencode(args),headers={'User-Agent':'ReplicationArchiveCandidateCollector/1.0'+(' (mailto:'+email+')' if email else '')})
 for attempt in range(3):
  try:
   with urlopen(req,timeout=30) as f:return json.load(f)['message']['items']
  except (URLError,TimeoutError) as e:
   if attempt==2:raise
   time.sleep(2**attempt)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--field',choices=SEEDS);p.add_argument('--limit',type=int,default=500,help='Maximum new unreviewed candidates per field (not guaranteed).');p.add_argument('--per-query',type=int,default=100);p.add_argument('--email',default='');a=p.parse_args()
 if not 1<=a.limit<=5000 or not 1<=a.per_query<=1000:p.error('Invalid limit or per-query')
 seen_titles=set();seen_dois=set();fields={}
 for f in (ROOT/'data').glob('*.csv'):
  for r in csv.DictReader(f.open(encoding='utf-8-sig')):
   fields[f.stem]=r['field'];seen_titles.add(norm(r['title']));seen_dois.add(doi_of(r['url']))
 out=ROOT/'candidates';out.mkdir(exist_ok=True)
 # Resume without overwriting editorial work. Deduplicate across all candidate files.
 existing={}
 for f in out.glob('*.csv'):
  rs=list(csv.DictReader(f.open(encoding='utf-8-sig')));existing[f.stem]=rs
  for r in rs:seen_titles.add(norm(r['title']));seen_dois.add(doi_of(r['url']))
 for key in ([a.field] if a.field else SEEDS):
  rs=existing.get(key,[]);f=out/(key+'.csv')
  for sub,topic,q in SEEDS[key]:
   if len(rs)>=a.limit:break
   try:items=query(q,a.per_query,a.email)
   except (URLError,TimeoutError) as e:print(f'Query failed: {q}: {e}');continue
   for item in items:
    r=metadata(item,fields[key],sub,topic,q)
    if not r:continue
    t=norm(r['title']);d=doi_of(r['url'])
    if t in seen_titles or d in seen_dois:continue
    rs.append(r);seen_titles.add(t);seen_dois.add(d)
    if len(rs)>=a.limit:break
   tmp=f.with_suffix('.tmp')
   with tmp.open('w',encoding='utf-8-sig',newline='') as handle:
    w=csv.DictWriter(handle,fieldnames=COLS);w.writeheader();w.writerows(rs)
   tmp.replace(f);print(f'{key}: {len(rs)} candidates | {q}',flush=True);time.sleep(0.25)
  print(f'{key}: {len(rs)} unreviewed candidates saved to {f}')
if __name__=='__main__':main()
