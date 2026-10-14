# GOODRAM Tender Intelligence v1.4.3

Full deployment package built from the supplied v1.4.2 files. All connector modules, common helpers, filters and legacy app/translate.py are unchanged. See PRESERVATION_REPORT.json.

## Deploy
Upload the contents of this project directory to the repository root. Dockerfile and render.yaml are included. Preserve your existing APIFY_API_TOKEN. No Azure/OpenAI key is needed for the new Free provider. Existing Azure/LibreTranslate providers remain available if configured.

## Translate
Choose the UI language, then Translate or Translate visible. Default source language is inferred from the portal/country, not detected automatically. For TED or multilingual tenders select the actual source language using the dropdown. System Status > Test translator tests the Free provider.

MyMemory is an external service, not offline translation. Public tender titles/descriptions are sent to it. Do not use it for confidential text. Anonymous usage is limited to 5000 characters/day, each request to 500 bytes. The app splits text into bounded chunks and retains storage abbreviations. A local quota guard does not override provider limits; shared hosting IP limits may also apply. Failures preserve originals and display an error; failed translations are not cached. No guaranteed free public LibreTranslate endpoint is hard-coded.

Cache: data/translations_free.sqlite3. On ephemeral hosting it can be lost after redeploy. A persistent disk/database is needed for durable cache.

## Checks
Run: PYTHONPATH=. python tests/test_v143.py
Original tests/baseline_v142.py.txt is retained as historical baseline; its version assertion is intentionally not a v1.4.3 test.

Beta discovery-only modules are unchanged: Slovakia, Hungary, Lithuania and Estonia can still report discovery failures or no tenders. This release does not claim to repair their integrations.
