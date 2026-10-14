"""Additive no-key translator. Legacy app.translate is deliberately unchanged."""
import asyncio, hashlib, html, os, re, sqlite3, time
from pathlib import Path
import httpx
DB=Path(os.getenv('FREE_TRANSLATION_DB','data/translations_free.sqlite3'))
STATE={'translated':0,'failed':0,'last_error':'','last_translation':None}
SOURCE={'prozorro':'uk','bzp':'pl','germany':'de','ekap':'tr','latvia':'lv','nen':'cs','slovakia':'sk','cvpis':'lt','ekr':'hu','estonia':'et'}
COUNTRY={'POL':'pl','DEU':'de','CZE':'cs','SVK':'sk','LVA':'lv','EST':'et','LTU':'lt','HUN':'hu','UKR':'uk','TUR':'tr','ESP':'es','FRA':'fr','ITA':'it','AUT':'de','ROU':'ro'}
TERMS=re.compile(r'\b(?:SSD|NVMe|DRAM|DDR[345]|USB|NAS|SAN|PCIe|SATA|microSD)\b',re.I)
LOCK=asyncio.Lock()
def db():
 DB.parent.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect(DB)
 c.execute('CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, title TEXT, description TEXT)')
 c.execute('CREATE TABLE IF NOT EXISTS quota (day TEXT PRIMARY KEY, used INTEGER)')
 return c
def status():
 with db() as c:
  count=c.execute('SELECT COUNT(*) FROM cache').fetchone()[0]
  row=c.execute('SELECT used FROM quota WHERE day=?',(time.strftime('%Y-%m-%d'),)).fetchone()
 return {'provider':'MyMemory (no key)','configured':True,'cache_records':count,'daily_budget':5000,'daily_used':row[0] if row else 0,**STATE}
def chunks(text,limit=480):
 out=[];part=''
 for char in text:
  if len((part+char).encode('utf-8'))>limit:out.append(part);part=''
  part+=char
 if part:out.append(part)
 return out
async def segment(client,text,source,target):
 if not text.strip():return text
 day=time.strftime('%Y-%m-%d')
 with db() as c:
  row=c.execute('SELECT used FROM quota WHERE day=?',(day,)).fetchone();used=row[0] if row else 0
  if used+len(text)>5000:raise RuntimeError('Free daily translation budget reached. Cached translations remain available.')
  c.execute('INSERT OR REPLACE INTO quota VALUES (?,?)',(day,used+len(text)))
 r=await client.get('https://api.mymemory.translated.net/get',params={'q':text,'langpair':source+'|'+target},timeout=20)
 r.raise_for_status();data=r.json()
 if int(data.get('responseStatus',0))!=200:raise RuntimeError(str(data.get('responseDetails') or 'Translation provider rejected request'))
 value=(data.get('responseData') or {}).get('translatedText')
 if not isinstance(value,str) or not value.strip():raise RuntimeError('Translation provider returned empty text')
 if 'MYMEMORY WARNING' in value.upper():raise RuntimeError(value[:180])
 return html.unescape(value)
async def text_translate(client,text,source,target):
 if source==target:return text
 # Preserve exact storage abbreviations rather than asking the provider to translate them.
 out=[];pos=0
 for match in TERMS.finditer(text):
  for part in chunks(text[pos:match.start()]):out.append(await segment(client,part,source,target))
  out.append(match.group());pos=match.end()
 for part in chunks(text[pos:]):out.append(await segment(client,part,source,target))
 return ''.join(out)
async def translate_tender(t,lang,provider='free',source_language='auto'):
 if provider!='free':
  from app.translate import translate_tender as old
  return await old(t,lang,provider)
 async with LOCK:
  try:
   if lang not in ('pl','uk','en','es'):raise RuntimeError('Unsupported target language')
   source=source_language if source_language!='auto' else SOURCE.get(t.source,COUNTRY.get(t.country,'en'))
   key=hashlib.sha256((t.source+'\0'+t.procurement_id+'\0'+source+'\0'+lang+'\0'+t.title+'\0'+t.description).encode()).hexdigest()
   with db() as c:row=c.execute('SELECT title,description FROM cache WHERE key=?',(key,)).fetchone()
   if row:t.translations[lang]={'title':row[0],'description':row[1]};return True
   async with httpx.AsyncClient() as client:
    title=await text_translate(client,t.title,source,lang)
    description=await text_translate(client,t.description,source,lang)
   with db() as c:c.execute('INSERT OR REPLACE INTO cache VALUES (?,?,?)',(key,title,description))
   t.translations[lang]={'title':title,'description':description}
   STATE.update(translated=STATE['translated']+1,last_error='',last_translation=time.strftime('%Y-%m-%d %H:%M:%S'))
   return True
  except Exception as e:
   STATE.update(failed=STATE['failed']+1,last_error=f'{type(e).__name__}: {e}')
   return False
async def translate_many(items,lang,provider='free',limit=50,source_language='auto'):
 ok=0
 for t in list(items)[:limit]:
  if await translate_tender(t,lang,provider,source_language):ok+=1
  else:break
 return ok
