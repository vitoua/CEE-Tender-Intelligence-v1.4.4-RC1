# v1.4.3 validation

PASS: compilation; byte-identical preservation of all supplied connector modules and common.py; original four locked SHA-256 hashes; unchanged legacy translate.py and filters.json; 9 HTTP routes including Excel export; selection controls; invalid-date handling; empty translation selection; UTF-8 byte splitting; mocked translation, cache hit and failure without cache pollution.

NOT VERIFIED: live translation provider, live portal requests, Docker image build and Render deployment. Mock fixtures test behavior only and are not real tender data.
