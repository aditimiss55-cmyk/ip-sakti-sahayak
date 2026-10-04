"""IP-SAKTI Sahayak: source-cited Ayurveda IP and regulatory guidance (prototype).

Offline, no LLM, no embeddings. Retrieval = keyword topic routing + a small BM25.
Answers are extracted from stored passages in corpus.py, never generated.
"""
import json
import math
import os
import re
import sqlite3
import uuid
from collections import Counter
from datetime import datetime, timezone

from flask import Flask, Response, g, jsonify, request, send_from_directory

from i18n import expand_query, is_devanagari, is_unsupported_script, localize, UNSUPPORTED_EN
from corpus import CORPUS, CORPUS_VERSION, CHECK_DATE, DRAFT_NOTE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"), static_url_path="/static")

DISCLAIMER = "Information and research support only. This is not legal advice."
LEVELS = ["low", "medium", "high"]
MAX_SOURCES = 10
MIN_QUERY_HITS = 2      # off-topic guard: distinct query terms that must exist in the corpus
MIN_TOP_SCORE = 2.0     # off-topic guard: BM25 score needed when no topic keyword matched

# ------------------------------------------------------------------ topics
TOPIC_KEYWORDS = {
    "patent": [r"patent\w*", r"invention", r"prior art", r"novelty", r"inventive step", r"\bpct\b", r"budapest"],
    "tk": [r"traditional knowledge", r"\btkdl\b", r"classical", r"authoritative (?:text|book)s?", r"ancient text",
           r"charaka", r"sushruta", r"ayurvedic texts?", r"\bgrantha", r"prior art"],
    "abs": [r"\babs\b", r"access and benefit", r"benefit[- ]sharing", r"\bnba\b", r"national biodiversity",
            r"nagoya", r"biodiversity", r"biological resources?", r"genetic resources?", r"gratk",
            r"disclosure of origin", r"disclose (?:the )?(?:source|origin)", r"\bsbb\b", r"\bcbd\b"],
    "gi": [r"geographical indication", r"\bgi\b", r"\bgi tag", r"appellation"],
    "tm": [r"trade ?marks?", r"brand name", r"\blogo\b", r"madrid", r"\bbrand\b"],
    "design": [r"industrial design", r"design registration", r"\bdesigns?\b", r"hague", r"bottle shape"],
    "copyright": [r"copyright\w*", r"\bbooks?\b", r"textbook", r"label artwork"],
    "pvp": [r"plant variet\w+", r"\bbreeders?\b", r"farmers'? rights?", r"ppvfr", r"pvfr", r"seed variet\w+"],
    "trade secret": [r"trade secrets?", r"secret formula", r"know-how", r"\bnda\b", r"breach of confidence", r"confidential\w*"],
    "drug": [r"\bdrugs?\b", r"licen[cs]e", r"licen[cs]ing", r"\bcdsco\b", r"158 ?-?b", r"medicines?", r"formulat\w+",
             r"phytopharmaceutical\w*", r"regulatory approval", r"clinical trials?", r"proprietary", r"new drug",
             r"herbal registration", r"traditional herbal", r"\bthmpd\b", r"\bayush drug", r"cosmetics?",
             r"herbal (?:product|medicine|remedy)", r"polyherbal", r"registration of (?:a )?herbal"],
    "advertising": [r"advertis\w+", r"label claims?", r"health claims?", r"marketing claims?", r"\bcures?\b",
                    r"misleading", r"magic remed\w+", r"promot\w+ (?:my|our|the) (?:product|medicine|drug)",
                    r"claim (?:that|to) (?:it )?(?:cure|treat|prevent)"],
    "food": [r"\bfssai\b", r"\bfood\b", r"nutraceutical\w*", r"aahar\w*", r"dietary supplements?", r"\bdshea\b",
             r"health supplements?", r"food supplements?"],
    "export": [r"\bexport\w*", r"\bimport\w*", r"ship(?:ping)? abroad", r"sell(?:ing)? abroad", r"overseas",
               r"\busa\b", r"united states", r"\bfda\b", r"\beu\b", r"europe\w*", r"european union", r"market access"],
}
TOPICS = list(TOPIC_KEYWORDS)
_TOPIC_RE = {t: re.compile("|".join(p), re.I) for t, p in TOPIC_KEYWORDS.items()}

FORMULATION_RE = re.compile(r"formulat\w+|polyherbal|herbal (?:product|medicine|remedy|drug|preparation)|"
                            r"ayurvedic (?:product|medicine|drug|preparation)|kashayam|churna|\bvati\b|\barishta", re.I)
FOREIGN_RE = re.compile(r"\busa\b|united states|\bfda\b|\beu\b|europe|european union|\bjapan\b|\bchina\b|\bcanada\b|\baustralia\b|\buk\b", re.I)
INDIA_WORDS_RE = re.compile(r"\bindia\b|\bindian\b|\bipindia\b|\bnba\b|\bfssai\b|\bcdsco\b|\btkdl\b|ayush", re.I)

# ------------------------------------------------------------------ categories
CATEGORIES = {
    "classical": "Classical Ayurvedic formulation",
    "proprietary": "Proprietary Ayurvedic medicine",
    "new": "New or non-classical drug",
    "phyto": "Phytopharmaceutical",
    "aahar": "Ayurveda Aahar or nutraceutical (food)",
    "cosmetic": "Cosmetic",
}
CATEGORY_SOURCES = {
    "classical": ["in_dc_s3a", "in_tkdl", "in_bda_2023", "in_dc_ch4a"],
    "proprietary": ["in_dc_r158b", "in_dc_ch4a", "in_bda_2002", "in_bda_2023", "in_tkdl"],
    "new": ["in_dc_r158b", "in_dc_ch4a", "in_bda_2002", "in_bda_2023", "in_tkdl"],
    "phyto": ["in_dc_phyto", "in_ndct_2019", "in_bda_2002", "in_bda_2023", "in_pat_s3d"],
    "aahar": ["in_fssai_aahar"],
    "cosmetic": ["in_cosmetics"],
}
PATENT_SET = ["in_pat_s3p", "in_pat_s3d", "in_tkdl", "in_pat_s2", "in_pat_s10_4d", "in_pat_s25"]
ABS_CATEGORIES = {"new", "phyto", "proprietary"}

ABS_CHECKLIST = [
    {"q": "Does the product use biological resources found in India, and is the applicant an Indian or a foreign entity?",
     "ids": ["in_bda_2002", "in_bda_2023"]},
    {"q": "Is the knowledge codified in an authoritative text, are the plants cultivated, and is the user a registered AYUSH practitioner? These may qualify for exemptions.",
     "ids": ["in_bda_2023", "in_dc_s3a"]},
    {"q": "Do you plan to file for IPR or to transfer research results or resources abroad, and is NBA approval planned before grant or transfer?",
     "ids": ["in_bda_2002", "in_bda_2023", "in_pat_s10_4d"]},
]

POINTERS = {
    "india": [("Indian Patent Office (IP India)", "https://ipindia.gov.in"),
              ("TKDL (traditional knowledge database)", "https://tkdl.res.in"),
              ("National Biodiversity Authority", "https://nbaindia.org"),
              ("CDSCO (drugs regulator)", "https://cdsco.gov.in"),
              ("FSSAI (food regulator)", "https://fssai.gov.in")],
    "international": [("WIPO", "https://www.wipo.int"),
                      ("ABS Clearing-House (CBD)", "https://absch.cbd.int")],
}
POINTER_TOPICS = {
    "ipindia": {"patent", "gi", "tm", "design", "copyright"}, "tkdl": {"tk", "patent"}, "nba": {"abs", "export"},
    "cdsco": {"drug", "advertising"}, "fssai": {"food"}, "wipo": {"patent", "tm", "design", "abs", "tk", "gi"},
    "absch": {"abs", "tk"},
}

# ------------------------------------------------------------------ BM25
STOP = set("""a an and are as at be but by can could do does for from had has have how i if in into is it its may me my
of on or our should so than that the their then there these they this to was we were what when where which who why
will with would you your about any also not no yes get got want need tell please just""".split())


def stem(w):
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def tokenize(text):
    return [stem(w) for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and len(w) > 1]


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs, self.k1, self.b = docs, k1, b
        self.toks = {d["id"]: tokenize(" ".join([d["title"], d["section"], d["authority"], d["text"], " ".join(d["topics"])]))
                     for d in docs}
        self.tf = {i: Counter(t) for i, t in self.toks.items()}
        self.avgdl = sum(len(t) for t in self.toks.values()) / max(1, len(self.toks))
        self.df = Counter()
        for t in self.toks.values():
            self.df.update(set(t))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - df + 0.5) / (df + 0.5)) for t, df in self.df.items()}

    def score(self, q_tokens, doc_id):
        tf, dl, s = self.tf[doc_id], len(self.toks[doc_id]), 0.0
        for t in set(q_tokens):
            f = tf.get(t, 0)
            if f:
                s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
        return s


INDEX = {j: BM25([d for d in CORPUS if d["jurisdiction"] == j]) for j in ("india", "international")}
BY_ID = {d["id"]: d for d in CORPUS}


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.;])\s+", text) if s.strip()]


def best_sentences(doc, q_tokens, idx, k=2):
    sents = sentences(doc["text"])
    scored = []
    for i, s in enumerate(sents):
        toks = set(tokenize(s))
        scored.append((sum(idx.idf.get(t, 0) for t in q_tokens if t in toks), i, s))
    top = sorted([x for x in scored if x[0] > 0], key=lambda x: -x[0])[:k]
    if not top:
        return [sents[0]]
    return [s for _, _, s in sorted(top, key=lambda x: x[1])]


# ------------------------------------------------------------------ routing
def detect_topics(q):
    return [t for t in TOPICS if _TOPIC_RE[t].search(q)]


def needs_clarification(jurisdiction, topics, q):
    if jurisdiction != "india":
        return False
    if "patent" in topics:
        return True
    if FORMULATION_RE.search(q):
        specific = {"advertising", "gi", "tm", "design", "copyright", "pvp", "trade secret", "export", "food"}
        return not (set(topics) & specific)
    return False


CLARIFY_QUESTIONS = [
    {"id": "authoritative", "text": "Is the formulation taken from an authoritative Ayurvedic text (one listed in the First Schedule of the Drugs and Cosmetics Act)?",
     "options": [["yes", "Yes"], ["no", "No"], ["unsure", "Not sure"]]},
    {"id": "disclosed", "text": "Has the formulation been publicly disclosed (published, sold, presented) anywhere?",
     "options": [["yes", "Yes"], ["no", "No"], ["unsure", "Not sure"]]},
    {"id": "category", "text": "What is the intended category of the product?",
     "options": [[k, v] for k, v in CATEGORIES.items()]},
]


def validate_clarifications(c):
    if not isinstance(c, dict):
        return None
    ok = (c.get("authoritative") in ("yes", "no", "unsure") and c.get("disclosed") in ("yes", "no", "unsure")
          and c.get("category") in CATEGORIES)
    return {k: c[k] for k in ("authoritative", "disclosed", "category")} if ok else None


# ------------------------------------------------------------------ answer building
def cap(level, maximum):
    return LEVELS[min(LEVELS.index(level), LEVELS.index(maximum))]


def build_answer(question, jurisdiction, clar):
    q_tokens = tokenize(question)
    idx = INDEX[jurisdiction]
    topics = detect_topics(question)
    category = clar["category"] if clar else None
    if clar:
        topics = list(dict.fromkeys(topics + ["patent"] * ("patent" in topics) + ["drug"]))

    # classification
    classification, conflict = None, False
    if clar:
        classification = {"key": category, "label": CATEGORIES[category], "basis": "Selected by you in the clarification step."}
        if category == "classical" and clar["authoritative"] == "no":
            conflict = True
            classification["basis"] += " Conflict: you also said it is not from an authoritative text, so it may not be classical."
    elif jurisdiction == "india" and "food" in topics:
        classification = {"key": "aahar", "label": CATEGORIES["aahar"], "basis": "Inferred from food or nutraceutical keywords."}
    elif jurisdiction == "india" and re.search(r"cosmetic", question, re.I):
        classification = {"key": "cosmetic", "label": CATEGORIES["cosmetic"], "basis": "Inferred from the word cosmetic."}
    elif jurisdiction == "india" and re.search(r"phytopharmaceutical", question, re.I):
        classification = {"key": "phyto", "label": CATEGORIES["phyto"], "basis": "Inferred from the word phytopharmaceutical."}
    else:
        classification = {"key": None, "label": "Not classified", "basis": "No product category was needed or given."}

    # candidate retrieval (strictly inside the chosen jurisdiction)
    forced = []
    if jurisdiction == "india" and "patent" in topics:
        forced += PATENT_SET            # patentability first, then regulatory route
    if jurisdiction == "india" and category:
        forced += CATEGORY_SOURCES[category]
    elif jurisdiction == "india" and classification["key"]:
        forced += CATEGORY_SOURCES[classification["key"]]
    pool_ids = [d["id"] for d in idx.docs if set(d["topics"]) & set(topics)] if topics else [d["id"] for d in idx.docs]
    scores = {i: idx.score(q_tokens, i) for i in {d["id"] for d in idx.docs}}
    hits = [t for t in set(q_tokens) if t in idx.df]
    top_score = max(scores.values()) if scores else 0.0

    # abstention
    if not topics and (len(hits) < MIN_QUERY_HITS or top_score < MIN_TOP_SCORE):
        return {"abstain": True, "topics": topics, "classification": classification, "top_score": round(top_score, 2),
                "hits": len(hits), "jurisdiction": jurisdiction}

    ranked = sorted(pool_ids, key=lambda i: -scores[i])
    ranked = ranked[:4] if topics else [i for i in ranked if scores[i] > 0][:4]
    selected = list(dict.fromkeys([f for f in forced if f in {d["id"] for d in idx.docs}] + ranked))[:MAX_SOURCES]
    if not selected:
        return {"abstain": True, "topics": topics, "classification": classification, "top_score": round(top_score, 2),
                "hits": len(hits), "jurisdiction": jurisdiction}

    # ABS checklist
    show_abs = jurisdiction == "india" and ("abs" in topics or category in ABS_CATEGORIES
                                           or (classification["key"] in ABS_CATEGORIES))
    abs_items = None
    if show_abs:
        abs_items = [dict(q=c["q"], ids=list(c["ids"])) for c in ABS_CHECKLIST]
        for it in abs_items:
            for i in it["ids"]:
                if i not in selected:
                    selected.append(i)   # cited sources must always be in the list

    n_of = {i: n + 1 for n, i in enumerate(selected)}
    sources = []
    for i in selected:
        d = BY_ID[i]
        assert d["jurisdiction"] == jurisdiction, "jurisdiction leak"
        note = f"Checked {CHECK_DATE} against: {d['checked']}" if d["verified"] else DRAFT_NOTE
        if d["verified"]:
            note = d["checked"]
        elif d["checked"]:
            note = f"{DRAFT_NOTE}. {d['checked']}"
        sources.append({"n": n_of[i], "id": i, "title": d["title"], "authority": d["authority"], "section": d["section"],
                        "version": d["version"], "status": d["status"], "url": d["url"], "passage": d["text"],
                        "verified": d["verified"], "note": note})

    findings = []
    for i in selected:
        d = BY_ID[i]
        for sent in best_sentences(d, q_tokens, idx, k=2):
            findings.append({"heading": d["title"], "text": sent, "cites": [n_of[i]]})
    # merge findings per source so each heading appears once
    merged = {}
    for f in findings:
        m = merged.setdefault(f["cites"][0], {"heading": f["heading"], "text": "", "cites": f["cites"]})
        m["text"] = (m["text"] + " " + f["text"]).strip()
    findings = list(merged.values())

    assumptions = []
    notes = []
    if clar:
        a = {"yes": "from an authoritative text", "no": "not from an authoritative text", "unsure": "of unknown textual origin (you were not sure)"}
        assumptions.append(f"You said the formulation is {a[clar['authoritative']]}.")
        d_ = {"yes": "has been publicly disclosed", "no": "has not been publicly disclosed", "unsure": "may or may not have been disclosed (you were not sure)"}
        assumptions.append(f"You said it {d_[clar['disclosed']]}.")
        assumptions.append(f"You chose the category: {CATEGORIES[category]}.")
        if clar["disclosed"] in ("yes", "unsure") and "in_pat_s2" in n_of:
            notes.append({"text": "Public disclosure before filing may count against novelty, so the dates of any disclosure matter.", "cites": [n_of["in_pat_s2"]]})
        if clar["authoritative"] == "yes" and "in_pat_s3p" in n_of:
            notes.append({"text": "A formulation taken from authoritative texts faces the traditional-knowledge exclusion and TKDL prior art.", "cites": [n_of["in_pat_s3p"], n_of.get("in_tkdl", n_of["in_pat_s3p"])]})
    assumptions.append(f"Jurisdiction: {'India' if jurisdiction == 'india' else 'International'} only. Sources from the other jurisdiction are not used.")

    patent_q = "patent" in topics
    intro = ("These sources do not let this tool say whether your invention is patentable. They list the points an examiner or attorney would check."
             if patent_q else
             "This is a summary of stored passages from the sources below. It is not a legal opinion.")

    # confidence
    level, reasons = "high", []
    unv = [s["id"] for s in sources if not s["verified"]]
    if unv:
        level = cap(level, "medium")
        reasons.append(f"Capped at medium: {len(unv)} of {len(sources)} retrieved sources are draft summaries not yet checked against official text ({', '.join(unv)}).")
    else:
        reasons.append(f"All {len(sources)} retrieved sources are marked verified; the check date and reference are shown on each source. Verification used secondary sources where stated.")
    if jurisdiction == "international":
        level = cap(level, "medium")
        reasons.append("International answers are capped at medium: treaty status and national implementation vary by country and change over time.")
    if patent_q:
        level = cap(level, "medium")
        reasons.append("Patentability is a case-specific legal judgment, so this tool never rates a patent answer higher than medium.")
    if clar and (clar["authoritative"] == "unsure" or clar["disclosed"] == "unsure"):
        level = cap(level, "medium")
        reasons.append("Capped at medium: you were not sure about the textual origin or the disclosure history, and both change the answer.")
    if clar and clar["disclosed"] == "yes":
        level = cap(level, "medium")
        reasons.append("Capped at medium: prior public disclosure may already affect novelty and this tool cannot judge dates.")
    if conflict:
        level = cap(level, "low")
        reasons.append("Capped at low: your inputs conflict (classical category but not from an authoritative text). Please resolve this or escalate.")
    if not topics:
        level = cap(level, "low")
        reasons.append("Capped at low: no topic keyword matched, so retrieval relied only on text similarity.")
    else:
        reasons.append(f"Topic routing matched: {', '.join(topics)}.")
    if len(sources) < 2:
        level = cap(level, "medium")
        reasons.append("Capped at medium: fewer than two sources were retrieved.")
    if jurisdiction == "international" and INDIA_WORDS_RE.search(question):
        notes.append({"text": "Your question mentions Indian bodies or law, but you selected International. No Indian sources are included; switch to India to see them.", "cites": []})

    if jurisdiction == "india" and FOREIGN_RE.search(question):
        level = cap(level, "low")
        reasons.append("Capped at low: the question is about another country's rules, which the India corpus does not cover.")
        notes.append({"text": "Your question mentions another country. This India answer covers Indian law only; switch to International for treaties and export-market regimes such as the EU and US.", "cites": []})
    return {"abstain": False, "topics": topics, "classification": classification, "assumptions": assumptions,
            "intro": intro, "findings": findings, "notes": notes, "sources": sources, "abs": abs_items,
            "n_of": n_of, "level": level, "reasons": reasons, "top_score": round(top_score, 2), "jurisdiction": jurisdiction}


def pointers_for(jurisdiction, topics):
    out = []
    for label, url in POINTERS[jurisdiction]:
        key = next(k for k in POINTER_TOPICS if k in url)
        if not topics or POINTER_TOPICS[key] & set(topics) or jurisdiction == "international":
            out.append({"label": label, "url": url})
    return out or [{"label": l, "url": u} for l, u in POINTERS[jurisdiction]]


# ------------------------------------------------------------------ storage
def db_path():
    return os.environ.get("IPSAKTI_DB", os.path.join(BASE_DIR, "ipsakti.db"))


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(db_path())
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    con = sqlite3.connect(db_path())
    con.executescript("""
    CREATE TABLE IF NOT EXISTS audit(
      id TEXT PRIMARY KEY, ts TEXT, jurisdiction TEXT, classification TEXT, status TEXT, confidence TEXT,
      source_ids TEXT, corpus_version TEXT, question TEXT, result_json TEXT);
    CREATE TABLE IF NOT EXISTS cases(
      id TEXT PRIMARY KEY, ts TEXT, audit_id TEXT, case_json TEXT);""")
    con.commit()
    con.close()


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_result(res):
    get_db().execute(
        "INSERT INTO audit VALUES(?,?,?,?,?,?,?,?,?,?)",
        (res["id"], res["ts"], res["jurisdiction"], (res.get("classification") or {}).get("label"), res["status"],
         (res.get("confidence") or {}).get("level"), json.dumps([s["id"] for s in res.get("sources", [])]),
         CORPUS_VERSION, res["question"], json.dumps(res)))
    get_db().commit()


# ------------------------------------------------------------------ routes
@app.before_request
def gate():
    code = os.environ.get("ACCESS_CODE")
    if code and request.path.startswith("/api/"):
        if request.headers.get("X-Access-Code") != code:
            return jsonify(error="access code required"), 401


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health():
    return jsonify(ok=True, corpus_version=CORPUS_VERSION, entries=len(CORPUS),
                   access_code_required=bool(os.environ.get("ACCESS_CODE")))


@app.get("/api/corpus")
def corpus_list():
    j = request.args.get("jurisdiction")
    items = [{k: d[k] for k in ("id", "jurisdiction", "title", "authority", "section", "version", "status", "url", "topics", "verified")}
             for d in CORPUS if not j or d["jurisdiction"] == j]
    return jsonify(corpus_version=CORPUS_VERSION, entries=items)


@app.post("/api/ask")
def ask():
    body = request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()
    jurisdiction = body.get("jurisdiction")
    if jurisdiction not in ("india", "international"):
        return jsonify(error="jurisdiction must be 'india' or 'international'"), 400
    if len(question) < 3 or len(question) > 1500:
        return jsonify(error="question must be 3 to 1500 characters"), 400
    lang = body.get("lang") if body.get("lang") in ("en", "hi") else "en"
    qx = expand_query(question)
    clar = None
    if body.get("clarifications") is not None:
        clar = validate_clarifications(body["clarifications"])
        if clar is None:
            return jsonify(error="clarifications need authoritative (yes/no/unsure), disclosed (yes/no/unsure) and a valid category"), 400

    res = {"id": uuid.uuid4().hex[:12], "ts": now(), "question": question, "jurisdiction": jurisdiction,
           "disclaimer": DISCLAIMER, "corpus_version": CORPUS_VERSION, "escalation_recommended": False}
    topics = detect_topics(qx)
    if clar is None and needs_clarification(jurisdiction, topics, qx):
        res.update(status="clarify", topics=topics, clarify={"questions": CLARIFY_QUESTIONS},
                   classification={"key": None, "label": "Pending clarification", "basis": ""}, sources=[],
                   trail={"jurisdiction": jurisdiction, "classification": "pending", "topics": topics, "sources_retrieved": []})
        log_result(res)
        return jsonify(localize(res, lang))

    out = build_answer(qx, jurisdiction, clar)
    non_latin = is_unsupported_script(question)
    if out["abstain"]:
        res.update(status="abstained", topics=out["topics"], classification=out["classification"], sources=[],
                   confidence={"level": "low", "reasons": [
                       "No stored source matched the question well enough, so no answer is given.",
                       f"Only {out['hits']} question term(s) appear in the {jurisdiction} corpus (at least {MIN_QUERY_HITS} needed) and the best match scored {out['top_score']}.",
                       "The corpus is small by design; a gap here does not mean the law is silent."]},
                   message=(UNSUPPORTED_EN if non_latin else "") + "I will not guess. The stored sources do not cover this question. You can escalate it to a human reviewer, which packages your question into a case file (nothing is sent anywhere).",
                   escalation_recommended=True, pointers=pointers_for(jurisdiction, []),
                   trail={"jurisdiction": jurisdiction, "classification": out["classification"]["label"], "topics": out["topics"], "sources_retrieved": []})
        log_result(res)
        return jsonify(localize(res, lang))

    n_of = out["n_of"]
    abs_out = None
    if out["abs"]:
        abs_out = [{"q": it["q"], "cites": sorted(n_of[i] for i in it["ids"])} for it in out["abs"]]
    findings = out["findings"] + [dict(heading="Note", text=n["text"], cites=n["cites"]) for n in out["notes"]]
    res.update(status="answered", topics=out["topics"], classification=out["classification"], assumptions=out["assumptions"],
               answer={"intro": out["intro"], "findings": findings}, sources=out["sources"], abs_checklist=abs_out,
               confidence={"level": out["level"], "reasons": out["reasons"]},
               escalation_recommended=out["level"] == "low", pointers=pointers_for(jurisdiction, out["topics"]),
               trail={"jurisdiction": jurisdiction, "classification": out["classification"]["label"], "topics": out["topics"],
                      "sources_retrieved": [s["id"] for s in out["sources"]]})
    log_result(res)
    return jsonify(localize(res, lang))


def load_result(audit_id):
    row = get_db().execute("SELECT result_json FROM audit WHERE id=?", (audit_id,)).fetchone()
    return json.loads(row["result_json"]) if row else None


@app.post("/api/escalate")
def escalate():
    audit_id = (request.get_json(silent=True) or {}).get("audit_id", "")
    res = load_result(audit_id)
    if not res:
        return jsonify(error="unknown audit_id"), 404
    if res["status"] == "clarify":
        return jsonify(error="answer the clarification questions first"), 400
    case_id = "CASE-" + uuid.uuid4().hex[:8].upper()
    case = {"case_id": case_id, "created_at": now(), "audit_id": audit_id, "question": res["question"],
            "jurisdiction": res["jurisdiction"], "classification": res.get("classification"),
            "assumptions": res.get("assumptions", []), "status": res["status"], "confidence": res.get("confidence"),
            "findings": (res.get("answer") or {}).get("findings", []),
            "sources": [{k: s[k] for k in ("n", "id", "title", "authority", "section", "version", "status", "url", "verified", "note")}
                        for s in res.get("sources", [])],
            "corpus_version": CORPUS_VERSION, "disclaimer": DISCLAIMER,
            "handling": "Packaged locally and saved in this app's SQLite file. Nothing was sent anywhere."}
    get_db().execute("INSERT INTO cases VALUES(?,?,?,?)", (case_id, case["created_at"], audit_id, json.dumps(case)))
    get_db().commit()
    return jsonify(case)


@app.get("/api/case/<case_id>")
def get_case(case_id):
    row = get_db().execute("SELECT case_json FROM cases WHERE id=?", (case_id,)).fetchone()
    if not row:
        return jsonify(error="unknown case"), 404
    return Response(row["case_json"], mimetype="application/json",
                    headers={"Content-Disposition": f"attachment; filename={case_id}.json"})


def report_md(res):
    L = ["# IP-SAKTI Sahayak research report", "", f"> {DISCLAIMER}", "",
         f"- Generated: {res['ts']}", f"- Corpus version: {res['corpus_version']}",
         f"- Jurisdiction: {'India' if res['jurisdiction'] == 'india' else 'International'}",
         f"- Classification: {(res.get('classification') or {}).get('label')}", f"- Status: {res['status']}", "",
         "## Question", "", res["question"], ""]
    if res["status"] == "abstained":
        L += ["## Answer", "", res.get("message", ""), ""]
    else:
        L += ["## Assumptions", ""] + [f"- {a}" for a in res.get("assumptions", [])] + [""]
        ans = res.get("answer") or {}
        L += ["## Answer", "", ans.get("intro", ""), ""]
        for f in ans.get("findings", []):
            c = " ".join(f"[{n}]" for n in f["cites"])
            L += [f"**{f['heading']}.** {f['text']} {c}".strip(), ""]
        if res.get("abs_checklist"):
            L += ["## ABS checklist", ""]
            for i, it in enumerate(res["abs_checklist"], 1):
                L.append(f"{i}. {it['q']} " + " ".join(f"[{n}]" for n in it["cites"]))
            L.append("")
        L += ["## Citations", ""]
        for s in res.get("sources", []):
            L += [f"[{s['n']}] **{s['title']}**  ", f"Issuing authority: {s['authority']}  ", f"Section/article: {s['section']}  ",
                  f"Version/date: {s['version']}  ", f"Status: {s['status']}  ", f"Official URL: {s['url']}  ",
                  f"Verification: {s['note']}", ""]
    c = res.get("confidence") or {}
    L += [f"## Confidence: {c.get('level', 'n/a')}", ""] + [f"- {r}" for r in c.get("reasons", [])] + [""]
    L += ["## Not legal advice", "", DISCLAIMER + " Draft sources must be verified against official text. Consult a qualified IP or regulatory professional before acting.", ""]
    return "\n".join(L)


@app.get("/api/report/<audit_id>")
def report(audit_id):
    res = load_result(audit_id)
    if not res:
        return jsonify(error="unknown audit_id"), 404
    return Response(report_md(res), mimetype="text/markdown",
                    headers={"Content-Disposition": f"attachment; filename=ip-sakti-report-{audit_id}.md"})


@app.get("/api/history")
def history():
    rows = get_db().execute("SELECT id,ts,jurisdiction,classification,status,confidence,source_ids,corpus_version "
                            "FROM audit ORDER BY ts DESC, rowid DESC LIMIT 15").fetchall()
    return jsonify(history=[dict(r, source_ids=json.loads(r["source_ids"])) for r in rows])


init_db()

if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "8000")), debug=False)
