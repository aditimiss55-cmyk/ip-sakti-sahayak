"""Small development test set for IP-SAKTI Sahayak.

This is NOT an accuracy measurement. The cases were written by the developer who also wrote
the corpus and keywords, so passing them shows the pipeline behaves as designed, nothing more.
Run: python eval.py
"""
import os
import sys
import tempfile

os.environ["IPSAKTI_DB"] = tempfile.mktemp(suffix=".db")
os.environ.pop("ACCESS_CODE", None)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app as A  # noqa: E402

client = A.app.test_client()
DEMO = "I created a new Ayurvedic herbal formulation. Can I patent it in India?"
CLAR_NEW = {"authoritative": "no", "disclosed": "no", "category": "new"}


def ask(q, j, clar=None):
    body = {"question": q, "jurisdiction": j}
    if clar:
        body["clarifications"] = clar
    return client.post("/api/ask", json=body).get_json()


def ids(r):
    return {s["id"] for s in r.get("sources", [])}


RESULTS = []


def test(name):
    def deco(fn):
        try:
            ok, detail = fn()
        except Exception as e:  # noqa: BLE001
            ok, detail = False, f"exception: {e!r}"
        RESULTS.append((name, ok, detail))
        return fn
    return deco


@test("demo patent question triggers clarification (India)")
def _():
    r = ask(DEMO, "india")
    return r["status"] == "clarify" and len(r["clarify"]["questions"]) == 3, r["status"]


@test("demo after clarification cites s.3(p), s.3(d), TKDL, Rule 158B, BDA 2023")
def _():
    r = ask(DEMO, "india", CLAR_NEW)
    need = {"in_pat_s3p", "in_pat_s3d", "in_tkdl", "in_dc_r158b", "in_bda_2023"}
    return r["status"] == "answered" and need <= ids(r), sorted(need - ids(r))


@test("demo answer is capped at medium and lists reasons")
def _():
    r = ask(DEMO, "india", CLAR_NEW)
    return r["confidence"]["level"] in ("low", "medium") and len(r["confidence"]["reasons"]) >= 2, r["confidence"]["level"]


@test("demo shows ABS checklist of 3 items, cited sources all in source list")
def _():
    r = ask(DEMO, "india", CLAR_NEW)
    chk = r.get("abs_checklist") or []
    nums = {s["n"] for s in r["sources"]}
    return len(chk) == 3 and all(set(c["cites"]) <= nums and c["cites"] for c in chk), len(chk)


@test("patent question without India does not ask clarification (International)")
def _():
    r = ask("Can I get a patent for a herbal invention under the PCT?", "international")
    return r["status"] == "answered" and "int_pct" in ids(r), r["status"]


@test("GI question -> Geographical Indications Act (India)")
def _():
    return "in_gi_1999" in ids(ask("Can I get a GI tag for my region's herbal oil?", "india")), ""


@test("NBA/ABS approval question -> BDA 2002 and 2023 (India)")
def _():
    r = ask("Do I need NBA approval and benefit sharing for medicinal plants?", "india")
    return {"in_bda_2002", "in_bda_2023"} <= ids(r), sorted(ids(r))


@test("advertising claims -> Drugs and Magic Remedies Act (India)")
def _():
    return "in_dmr_1954" in ids(ask("Can I advertise that my churna cures diabetes?", "india")), ""


@test("GRATK question -> treaty entry stating it is NOT in force (International)")
def _():
    r = ask("Is the WIPO GRATK treaty in force and what disclosure does it require?", "international")
    g = next((s for s in r["sources"] if s["id"] == "int_gratk"), None)
    return g is not None and "NOT in force" in g["status"], ""


@test("EU herbal registration -> Directive 2004/24/EC (International)")
def _():
    return "int_eu_2004_24" in ids(ask("How do I register a traditional herbal medicine in the EU?", "international")), ""


@test("phytopharmaceutical category forces CDSCO phyto and NDCT sources")
def _():
    r = ask(DEMO, "india", {"authoritative": "no", "disclosed": "no", "category": "phyto"})
    return {"in_dc_phyto", "in_ndct_2019"} <= ids(r), sorted(ids(r))


@test("Ayurveda Aahar category forces FSSAI regulations")
def _():
    r = ask(DEMO, "india", {"authoritative": "yes", "disclosed": "no", "category": "aahar"})
    return "in_fssai_aahar" in ids(r), sorted(ids(r))


@test("cosmetic category forces cosmetics source")
def _():
    r = ask(DEMO, "india", {"authoritative": "no", "disclosed": "no", "category": "cosmetic"})
    return "in_cosmetics" in ids(r), sorted(ids(r))


@test("off-topic question abstains (India and International)")
def _():
    rs = [ask(q, j) for q in ("What is the capital of France?", "Best pizza recipe for dinner?") for j in ("india", "international")]
    return all(r["status"] == "abstained" and not r["sources"] and r["escalation_recommended"] for r in rs), [r["status"] for r in rs]


@test("no answer mixes jurisdictions (every question, both toggles)")
def _():
    qs = [DEMO, "Can I get a GI tag?", "NBA approval ABS", "advertising claims for herbal cure", "GRATK disclosure",
          "EU herbal registration", "trademark brand logo", "dietary supplement food", "export of medicinal plants",
          "copyright for my book", "trade secret formula"]
    bad = []
    for q in qs:
        for j in ("india", "international"):
            r = ask(q, j, CLAR_NEW if j == "india" and A.needs_clarification(j, A.detect_topics(q), q) else None)
            prefix = "in_" if j == "india" else "int_"
            for s in r.get("sources", []):
                if not s["id"].startswith(prefix) or A.BY_ID[s["id"]]["jurisdiction"] != j:
                    bad.append((q, j, s["id"]))
    return not bad, bad


@test("international answers never exceed medium confidence")
def _():
    rs = [ask(q, "international") for q in ("GRATK disclosure", "Nagoya protocol benefit sharing", "TRIPS geographical indications")]
    return all(r["confidence"]["level"] != "high" for r in rs), [r["confidence"]["level"] for r in rs]


@test("any unverified retrieved source caps confidence below high")
def _():
    bad = []
    for q in ("Can I get a GI tag?", "NBA approval ABS", "advertising claims cure", "trademark brand"):
        r = ask(q, "india")
        if r["status"] == "answered" and any(not s["verified"] for s in r["sources"]) and r["confidence"]["level"] == "high":
            bad.append(q)
    return not bad, bad


@test("every citation number exists in the source list; every source is cited")
def _():
    r = ask(DEMO, "india", CLAR_NEW)
    nums = {s["n"] for s in r["sources"]}
    used = set()
    for f in r["answer"]["findings"]:
        used |= set(f["cites"])
    for c in r["abs_checklist"]:
        used |= set(c["cites"])
    return used <= nums and nums <= used, (sorted(used - nums), sorted(nums - used))


@test("conflicting inputs (classical but not from authoritative text) cap confidence at low")
def _():
    r = ask(DEMO, "india", {"authoritative": "no", "disclosed": "no", "category": "classical"})
    return r["confidence"]["level"] == "low" and r["escalation_recommended"], r["confidence"]["level"]


@test("Indian question under International returns no Indian sources and says so")
def _():
    r = ask("What does the NBA require for ABS approval in India?", "international")
    notes = [f["text"] for f in r["answer"]["findings"] if f["heading"] == "Note"]
    return all(s["id"].startswith("int_") for s in r["sources"]) and any("switch to India" in n for n in notes), notes


@test("escalation creates a case file with sources and stores it in SQLite")
def _():
    r = ask(DEMO, "india", CLAR_NEW)
    c = client.post("/api/escalate", json={"audit_id": r["id"]}).get_json()
    again = client.get(f"/api/case/{c['case_id']}")
    return c["sources"] and c["jurisdiction"] == "india" and again.status_code == 200, c.get("case_id")


@test("report contains question, citations, confidence reasons and 'not legal advice'")
def _():
    r = ask(DEMO, "india", CLAR_NEW)
    md = client.get(f"/api/report/{r['id']}").get_data(as_text=True)
    return all(k in md for k in ("## Question", "## Citations", "## Confidence", "Not legal advice", "[1]")), ""


@test("ACCESS_CODE gates /api when set")
def _():
    os.environ["ACCESS_CODE"] = "letmein"
    try:
        a = client.post("/api/ask", json={"question": "GI tag", "jurisdiction": "india"}).status_code
        b = client.post("/api/ask", json={"question": "GI tag", "jurisdiction": "india"}, headers={"X-Access-Code": "letmein"}).status_code
    finally:
        os.environ.pop("ACCESS_CODE")
    return a == 401 and b == 200, (a, b)


@test("export question under International returns US DSHEA and no Indian sources")
def _():
    r = ask("Can I export Ayurvedic products to the USA?", "international")
    return r["status"] == "answered" and "int_us_dshea" in ids(r) and all(s["id"].startswith("int_") for s in r["sources"]), (r["status"], sorted(ids(r)))


@test("foreign-market question under India carries a 'switch to International' note")
def _():
    r = ask("Can I export Ayurvedic products to the USA?", "india")
    notes = [f["text"] for f in r.get("answer", {}).get("findings", []) if f["heading"] == "Note"]
    return r["status"] == "answered" and r["confidence"]["level"] == "low" and any("switch to International" in n for n in notes), (r["confidence"]["level"], notes)


@test("Hindi patent question triggers the clarification flow, with Hindi questions")
def _():
    r = client.post("/api/ask", json={"question": "क्या मैं अपनी नई आयुर्वेदिक दवा का पेटेंट भारत में करा सकता हूँ?", "jurisdiction": "india", "lang": "hi"}).get_json()
    q = r.get("clarify", {}).get("questions", [])
    return r["status"] == "clarify" and len(q) == 3 and "क्या" in q[0]["text"], r["status"]


@test("Hindi answer cites the same sources as the English question and is in Hindi")
def _():
    en = ask(DEMO, "india", CLAR_NEW)
    hi = client.post("/api/ask", json={"question": "मैंने एक नया आयुर्वेदिक फॉर्मूलेशन बनाया है। क्या मैं भारत में इसका पेटेंट करा सकता हूँ?", "jurisdiction": "india",
                                      "lang": "hi", "clarifications": CLAR_NEW}).get_json()
    deva = sum("\u0900" <= c <= "\u097f" for f in hi["answer"]["findings"] for c in f["text"])
    return hi["status"] == "answered" and {"in_pat_s3p", "in_pat_s3d", "in_tkdl"} <= ids(hi) and deva > 300, (sorted(ids(en) ^ ids(hi)), deva)


@test("Hindi GI and advertising questions route to the right sources")
def _():
    a = client.post("/api/ask", json={"question": "क्या मेरे क्षेत्र के हर्बल तेल को भौगोलिक संकेत (जीआई) मिल सकता है?", "jurisdiction": "india", "lang": "hi"}).get_json()
    b = client.post("/api/ask", json={"question": "क्या मैं विज्ञापन में दावा कर सकता हूँ कि मेरा चूर्ण इलाज करता है?", "jurisdiction": "india", "lang": "hi"}).get_json()
    return "in_gi_1999" in ids(a) and "in_dmr_1954" in ids(b), (sorted(ids(a)), sorted(ids(b)))


@test("Hindi export question under International returns US DSHEA")
def _():
    r = client.post("/api/ask", json={"question": "क्या मैं आयुर्वेदिक उत्पाद अमेरिका को निर्यात कर सकता हूँ?", "jurisdiction": "international", "lang": "hi"}).get_json()
    return "int_us_dshea" in ids(r), sorted(ids(r))


@test("Hindi interface strings: no untranslated English in classification, assumptions, reasons, intro")
def _():
    r = client.post("/api/ask", json={"question": "क्या मैं नई आयुर्वेदिक दवा का पेटेंट करा सकता हूँ, भारत में?", "jurisdiction": "india", "lang": "hi", "clarifications": {"authoritative": "unsure", "disclosed": "yes", "category": "phyto"}}).get_json()
    strings = [r["classification"]["label"], r["answer"]["intro"], r["disclaimer"]] + r["assumptions"] + r["confidence"]["reasons"] + [c["q"] for c in r["abs_checklist"]]
    bad = [s for s in strings if sum("a" <= c.lower() <= "z" for c in s) > 0.4 * len(s)]
    return not bad, bad


@test("Tamil question abstains and says only English and Hindi are supported")
def _():
    r = client.post("/api/ask", json={"question": "நான் ஆயுர்வேத மருந்துக்கு காப்புரிமை பெற முடியுமா?", "jurisdiction": "india", "lang": "en"}).get_json()
    return r["status"] == "abstained" and "English and Hindi" in r["message"], r.get("message", "")[:70]


@test("localised responses never mix jurisdictions and the audit log keeps the English record")
def _():
    r = client.post("/api/ask", json={"question": "जीआई टैग क्या है?", "jurisdiction": "india", "lang": "hi"}).get_json()
    rep = client.get(f"/api/report/{r['id']}").get_data(as_text=True)
    return all(s["id"].startswith("in_") for s in r["sources"]) and "Not legal advice" in rep, ""


if __name__ == "__main__":
    passed = 0
    for name, ok, detail in RESULTS:
        passed += ok
        print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else f"   -> {detail}"))
    print(f"\n{passed}/{len(RESULTS)} passed.")
    print("This is a small development set written by the same person who wrote the corpus and keyword rules.")
    print("It checks that the pipeline behaves as designed. It is NOT an accuracy claim and says nothing about real-world legal correctness.")
    sys.exit(0 if passed == len(RESULTS) else 1)
