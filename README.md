# IP-SAKTI Sahayak (prototype)

Source-cited assistant for Ayurveda IP and regulatory questions, built for Smart India Hackathon 2026, problem statement SIH26045.
**Information and research support only. This is not legal advice.**

It proves one workflow end to end: question + jurisdiction -> classification -> retrieval -> plain-language answer with numbered citations -> confidence with reasons -> abstain or escalate.

## Run
```
pip install -r requirements.txt   # Flask is the only dependency
python app.py                     # http://127.0.0.1:8000
python eval.py                    # development tests
```
Optional environment variables: `ACCESS_CODE` (gates every `/api/` route; send header `X-Access-Code`), `IPSAKTI_DB` (SQLite path), `HOST`, `PORT`.

Docker: `docker build -t ip-sakti-sahayak . && docker run -p 8000:8000 -v ipsakti-data:/data ip-sakti-sahayak`. **The Dockerfile has not been built or run** (see "Tested").

## How it works
Python + Flask + SQLite + one static page. No LLM, no embeddings, no API key, no network calls. Topic routing uses keyword rules (13 topics); ranking uses a small BM25. Answers are sentences extracted from short summaries stored in `corpus.py`. See `ARCHITECTURE.md`.

## Demo flow
"I created a new Ayurvedic herbal formulation. Can I patent it in India?" -> three clarification questions -> classification -> s.3(p), s.3(d), TKDL, s.2, s.10(4)(d), s.25, Rule 158B, ABS checklist -> cautious answer, confidence capped at medium with reasons. Also try GI tag, NBA/ABS, advertising claims, GRATK, EU herbal registration, and an off-topic question (abstains).

## Corpus status (checked 2026-10-04)
33 entries: 23 India, 10 International. 16 of them also have a Hindi summary (`corpus_hi.py`). Each shows whether it is verified. "Verified" means checked against the sources named on the entry using web search results; for several entries those are reliable secondary sources (law-firm and news summaries, CDSCO and WIPO pages), **not** the Gazette or Act text itself.

Verified (8): `in_bda_2002`, `in_bda_2023`, `in_dc_r158b`, `in_dc_phyto`, `in_ndct_2019`, `in_fssai_aahar`, `in_dc_r170`, `int_gratk`.

**Unverified drafts (25):** `in_pat_s2`, `in_pat_s3d`, `in_pat_s3p`, `in_pat_s10_4d`, `in_pat_s25`, `in_tkdl`, `in_gi_1999`, `in_tm_1999`, `in_design_2000`, `in_copyright_1957`, `in_pvpfr_2001`, `in_trade_secret`, `in_dc_s3a`, `in_dc_ch4a` (Part numbers XVI-XVII not checked), `in_cosmetics`, `in_dmr_1954`, `int_trips_27`, `int_trips_22_24`, `int_cbd`, `int_nagoya`, `int_pct`, `int_madrid_hague`, `int_budapest`, `int_eu_2004_24`, `int_us_dshea`. These were written from general knowledge and are labelled "Draft summary, verify against official text". Source URLs for them are the issuing authority's site root, not deep links.

Facts the brief asked to be verified:
- **BDA 2023:** NBA approval for IPR moves to before grant; exemptions for codified traditional knowledge, cultivated medicinal plants and registered AYUSH practitioners. Confirmed in several secondary sources. Reports differ on Indian vs foreign applicants, which the entry says.
- **GRATK:** adopted 24 May 2024, not in force (needs 15). WIPO's table dated 13 March 2026 listed 3 ratifications; the EU IP Helpdesk reported Peru on 8 July 2026. No later official count found, so the entry says the count may be out of date.
- **Rule 158B vs NDCT 2019:** Rule 158B governing proof of safety/effectiveness for Ayurvedic drug categories is confirmed, as is the 2024 Supreme Court amicus challenge on new indications. **The claim that NDCT 2019 does not apply to new/proprietary Ayurvedic drugs was not confirmed**; the entry tells users to check with the licensing authority. NDCT 2019 does expressly cover phytopharmaceutical drugs (CDSCO).
- **Found while checking:** Rule 170 (Ayurvedic ad pre-approval) was omitted by a 1 July 2024 notification; the Supreme Court stayed that, and later reports say it vacated the stay. Included as `in_dc_r170` with the date of the final order not captured.

## Tested
- `eval.py`: 32 tests pass (6 new multilingual tests). It is a small development set written by the same person who wrote the corpus and keywords. It is not an accuracy claim.
- Every API route exercised with Flask's test client, including error paths (400, 401, 404).
- UI driven in headless Chromium (Playwright): toggle colour, clarify, answer, citation click, abstain, International view, escalate download, report download, keyboard focus outline, 375px width without horizontal overflow (19 checks).

## Changes in this revision
- Export questions: US DSHEA and EU entries now carry the `export` topic and the topic keywords include USA, EU, FDA, Europe. Under International, "export to the USA" now answers from those two entries. Under India, a question about another country gets a "switch to International" note and is capped at low confidence.
- Long answers: the first 6 findings show; the rest collapse under "Show N more findings". With more than 6 sources the list is collapsed, and clicking a citation opens it.
- English-only: a visible note under the question box, and non-Latin questions get an explicit English-only message when they abstain.
- Known side effect: an EU herbal registration question also returns the US DSHEA entry because both carry the `export` topic.
- This revision's UI was exercised with jsdom against the running server (clarify, answer, collapse, citation opens the source list, Hindi message). It was not re-run in a real browser.

## Languages (new)
- **English and Hindi**, offline, no API key. Pick the language with the toggle at the top. You can ask in either language and read the answer in either.
- Hindi questions: a Devanagari glossary (`i18n.py`, about 70 terms) adds English search terms, so topic routing and BM25 work on Hindi input. It only understands words in the glossary and common spellings; unusual wording can miss.
- Hindi answers: interface, clarification questions, confidence reasons, assumptions and notes are translated. Findings come from Hindi summaries for 16 key sources; the other sources show their English text with an "[अंग्रेज़ी पाठ]" marker. The English text stays authoritative, and the source viewer shows both.
- The Hindi was written for this prototype and **has not been reviewed by a native legal translator**. Titles, section numbers, authorities and the audit log, report and case file stay in English.
- Any other script (Tamil, Bengali and so on) abstains with a message that only English and Hindi are supported. Hinglish (Hindi in Latin letters) is not supported.
- Not done: other Indian languages, voice, Bhashini integration.

## Not tested
- **Docker image: not built.** The sandbox could start a Docker daemon but Docker Hub was blocked (403), so the base image could not be pulled. The Dockerfile is untested.
- Only Chromium was used; no Firefox/Safari, no real phone, no screen reader, no formal contrast audit.
- No load or concurrency testing. The server is Flask's built-in server, not production-hardened.
- No review of the corpus by a lawyer or Ayurveda domain expert.

## Not built (and not claimed)
Multilingual support, knowledge graph, agents, embeddings, LLM use, DPDP Act compliance, full legal coverage, 100% accuracy, zero hallucination, air-gapped certification. Also not built: user accounts, real escalation delivery (a case file is only saved locally and downloaded), live registry or TKDL search (links to official sites only), automatic corpus updates.

## Privacy note
Questions and results are stored in the local SQLite file (`ipsakti.db`) so reports and case files can be regenerated. Nothing leaves the machine.
