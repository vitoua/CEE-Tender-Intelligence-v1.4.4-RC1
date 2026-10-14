# v1.4.3
- Added independent Free translation module with MyMemory, SQLite cache, UTF-8 request splitting, quota guard and explicit errors.
- Preserved all connector modules, filters, legacy translator and original lock manifests.
- Added source-language selection and retained legacy providers.
- Fixed refresh endpoint event-loop usage and double-start guard in main.py.
- Added Dockerfile and no-key default deployment configuration.

# v1.4.2
- Locked regression-tested TED, Prozorro, Latvia IUB and EKAP connector modules.
- Restored Select all and Clear selection controls.
- Added Translator V2 via Azure AI Translator without removing legacy LibreTranslate V1.
- Added translation cache, translate-one, translate-visible and translator diagnostic test.
- Corrected BZP required request parameters and response diagnostics.
- Optimized NEN detail loading with bounded concurrency.
- Added Slovakia and Hungary HTML diagnostics, cleaner Estonia URL discovery, and Germany filter counters.
- Retained PL/UA/EN/ES UI, list view, Analytics, CPV, Keywords, Sources, Status, About and Excel export.
