import asyncio, hashlib, json, tempfile
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app, JOB
from app.models import Tender
import app.translate_free as free
root=Path('.')
for path,record in json.loads((root/'PRESERVATION_REPORT.json').read_text()).items():
 assert hashlib.sha256((root/path).read_bytes()).hexdigest()==record['baseline']
for meta in json.loads((root/'CONNECTOR_HASHES.json').read_text()).values():
 assert hashlib.sha256((root/meta['file']).read_bytes()).hexdigest()==meta['sha256'],meta['file']

client=TestClient(app)
for url in ['/','/health','/analytics','/cpv','/keywords','/sources','/status','/about','/export.xlsx']:
 assert client.get(url).status_code==200,url
assert client.get('/health').json()['version']=='1.4.3'
assert 'data-check="countries"' in client.get('/').text
assert 'data-clear="sources"' in client.get('/').text
assert client.post('/refresh/start',data={'countries':'POL','sources':'bzp','published_from':'bad'}).status_code==400
assert client.post('/translate-visible').status_code==400
for chunk in free.chunks('Український текст '*100):assert len(chunk.encode())<=480
assert ''.join(free.chunks('abc'*1000))=='abc'*1000
async def check():
 with tempfile.TemporaryDirectory() as tmp:
  free.DB=Path(tmp)/'cache.sqlite'
  calls=[]
  async def fake_segment(client,text,source,target):calls.append(text);return 'translated '+text
  t=Tender('1','ted','', 'Supply SSD',description='Memory DDR5',procurement_id='1')
  with patch.object(free,'segment',fake_segment):
   assert await free.translate_tender(t,'pl')
   assert 'SSD' in t.translations['pl']['title']
   assert 'DDR5' in t.translations['pl']['description']
   n=len(calls)
   assert await free.translate_tender(t,'pl')
   assert len(calls)==n
  async def fail(*args):raise RuntimeError('quota exhausted')
  with patch.object(free,'segment',fail):
   bad=Tender('2','ted','', 'Supply drives',procurement_id='2')
   assert not await free.translate_tender(bad,'pl')
   assert not bad.translations
   assert free.status()['cache_records']==1
   assert 'quota exhausted' in free.status()['last_error']
asyncio.run(check())
print('PASS: exact connector/legacy preservation, 9 routes, selection UI, invalid date, empty translation selection, UTF-8 splitting, mocked translation/cache/error tests')
