"""Hindi support: query glossary (Hindi -> English search terms), Devanagari detection, and response localisation.
Offline and rule-based. Other languages are not supported."""
import copy, re
from corpus_hi import HI_TEXT

DEVANAGARI = re.compile(r"[\u0900-\u097F]")
GLOSS = [("पेटेंट", "patent"), ("पेटेन्ट", "patent"), ("आविष्कार", "invention"), ("नवीनता", "novelty"), ("पारंपरिक ज्ञान", "traditional knowledge"),
 ("टीकेडीएल", "TKDL"), ("जैव विविधता", "biodiversity"), ("जैविक संसाधन", "biological resources"), ("लाभ साझा", "benefit sharing"), ("लाभ बंटवारा", "benefit sharing"),
 ("एनबीए", "NBA"), ("भौगोलिक संकेत", "geographical indication GI"), ("जीआई", "GI"), ("ट्रेडमार्क", "trademark"), ("व्यापार चिह्न", "trademark"), ("ब्रांड", "brand"),
 ("लोगो", "logo"), ("डिज़ाइन", "design"), ("डिजाइन", "design"), ("कॉपीराइट", "copyright"), ("प्रतिलिप्यधिकार", "copyright"), ("पौध किस्म", "plant variety"),
 ("किसान अधिकार", "farmers rights"), ("व्यापार रहस्य", "trade secret"), ("गोपनीय", "confidential"), ("लाइसेंस", "licence"), ("अनुज्ञप्ति", "licence"),
 ("दवा", "drug medicine"), ("औषधि", "drug medicine"), ("फॉर्मूला", "formulation"), ("फॉर्मूलेशन", "formulation"), ("नुस्खा", "formulation"), ("शास्त्रीय", "classical"),
 ("फाइटोफार्मा", "phytopharmaceutical"), ("कॉस्मेटिक", "cosmetic"), ("सौंदर्य प्रसाधन", "cosmetic"), ("विज्ञापन", "advertisement"), ("इलाज", "cure"), ("दावा", "claim"),
 ("खाद्य", "food"), ("आहार", "food aahar"), ("सप्लीमेंट", "supplement"), ("न्यूट्रास्यूटिकल", "nutraceutical"), ("एफएसएसएआई", "FSSAI"), ("निर्यात", "export"),
 ("आयात", "import"), ("अमेरिका", "USA"), ("यूरोप", "Europe EU"), ("भारत", "India"), ("निर्माण", "manufacture"), ("नई दवा", "new drug"), ("मंजूरी", "approval"),
 ("अनुमोदन", "approval"), ("आयुर्वेद", "Ayurvedic"), ("जड़ी", "herbal"), ("हर्बल", "herbal"), ("ट्रिप्स", "TRIPS"), ("नागोया", "Nagoya"), ("डब्ल्यूआईपीओ", "WIPO")]

def is_devanagari(q):
    letters = [c for c in q if c.isalpha()]
    return bool(letters) and sum("\u0900" <= c <= "\u097F" for c in letters) / len(letters) > 0.3

def is_unsupported_script(q):
    letters = [c for c in q if c.isalpha()]
    return bool(letters) and sum(ord(c) > 0x24F and not ("\u0900" <= c <= "\u097F") for c in letters) / len(letters) > 0.3

def expand_query(q):
    if not DEVANAGARI.search(q):
        return q
    return q + " " + " ".join(dict.fromkeys(en for hi, en in GLOSS if hi in q))

UNSUPPORTED_EN = "This prototype supports English and Hindi questions only, so I cannot search the sources for this one. Please ask in English or Hindi, or escalate to a human reviewer. "
CAT = {"Classical Ayurvedic formulation": "शास्त्रीय आयुर्वेदिक फॉर्मूलेशन", "Proprietary Ayurvedic medicine": "मालिकाना आयुर्वेदिक दवा",
       "New or non-classical drug": "नई या गैर-शास्त्रीय दवा", "Phytopharmaceutical": "फाइटोफार्मास्यूटिकल",
       "Ayurveda Aahar or nutraceutical (food)": "आयुर्वेद आहार या न्यूट्रास्यूटिकल (खाद्य)", "Cosmetic": "कॉस्मेटिक",
       "Not classified": "वर्गीकृत नहीं", "Pending clarification": "स्पष्टीकरण लंबित"}
EXACT = dict(CAT, **{
 "Information and research support only. This is not legal advice.": "केवल जानकारी और शोध सहायता। यह कानूनी सलाह नहीं है।",
 "Yes": "हाँ", "No": "नहीं", "Not sure": "पता नहीं",
 "Is the formulation taken from an authoritative Ayurvedic text (one listed in the First Schedule of the Drugs and Cosmetics Act)?": "क्या फॉर्मूलेशन किसी प्रामाणिक आयुर्वेदिक ग्रंथ से लिया गया है (औषधि और प्रसाधन सामग्री अधिनियम की प्रथम अनुसूची में सूचीबद्ध)?",
 "Has the formulation been publicly disclosed (published, sold, presented) anywhere?": "क्या फॉर्मूलेशन का कहीं भी सार्वजनिक खुलासा हुआ है (प्रकाशित, बेचा गया, प्रस्तुत किया गया)?",
 "What is the intended category of the product?": "उत्पाद की इच्छित श्रेणी क्या है?",
 "These sources do not let this tool say whether your invention is patentable. They list the points an examiner or attorney would check.": "इन स्रोतों से यह टूल यह नहीं कह सकता कि आपका आविष्कार पेटेंट योग्य है या नहीं। ये वे बिंदु बताते हैं जिन्हें परीक्षक या अटॉर्नी जाँचेंगे।",
 "This is a summary of stored passages from the sources below. It is not a legal opinion.": "यह नीचे दिए स्रोतों के संग्रहीत अंशों का सारांश है। यह कानूनी राय नहीं है।",
 "You said the formulation is from an authoritative text.": "आपने बताया कि फॉर्मूलेशन किसी प्रामाणिक ग्रंथ से लिया गया है।",
 "You said the formulation is not from an authoritative text.": "आपने बताया कि फॉर्मूलेशन किसी प्रामाणिक ग्रंथ से नहीं लिया गया है।",
 "You said the formulation is of unknown textual origin (you were not sure).": "आपने बताया कि फॉर्मूलेशन का ग्रंथ-स्रोत अज्ञात है (आप निश्चित नहीं थे)।",
 "You said it has been publicly disclosed.": "आपने बताया कि इसका सार्वजनिक खुलासा हो चुका है।",
 "You said it has not been publicly disclosed.": "आपने बताया कि इसका सार्वजनिक खुलासा नहीं हुआ है।",
 "You said it may or may not have been disclosed (you were not sure).": "आपने बताया कि इसका खुलासा हुआ हो भी सकता है और नहीं भी (आप निश्चित नहीं थे)।",
 "Jurisdiction: India only. Sources from the other jurisdiction are not used.": "क्षेत्राधिकार: केवल भारत। दूसरे क्षेत्राधिकार के स्रोत उपयोग नहीं किए गए।",
 "Jurisdiction: International only. Sources from the other jurisdiction are not used.": "क्षेत्राधिकार: केवल अंतरराष्ट्रीय। दूसरे क्षेत्राधिकार के स्रोत उपयोग नहीं किए गए।",
 "International answers are capped at medium: treaty status and national implementation vary by country and change over time.": "अंतरराष्ट्रीय उत्तर अधिकतम मध्यम तक सीमित हैं: संधि की स्थिति और राष्ट्रीय कार्यान्वयन देश के अनुसार भिन्न होते हैं और समय के साथ बदलते हैं।",
 "Patentability is a case-specific legal judgment, so this tool never rates a patent answer higher than medium.": "पेटेंट योग्यता मामले-विशेष का कानूनी निर्णय है, इसलिए यह टूल पेटेंट उत्तर को मध्यम से ऊपर नहीं आँकता।",
 "Capped at medium: you were not sure about the textual origin or the disclosure history, and both change the answer.": "मध्यम पर सीमित: आप ग्रंथ-स्रोत या खुलासे के इतिहास के बारे में निश्चित नहीं थे, और दोनों उत्तर बदलते हैं।",
 "Capped at medium: prior public disclosure may already affect novelty and this tool cannot judge dates.": "मध्यम पर सीमित: पूर्व सार्वजनिक खुलासा नवीनता को पहले ही प्रभावित कर सकता है और यह टूल तिथियाँ नहीं आँक सकता।",
 "Capped at low: your inputs conflict (classical category but not from an authoritative text). Please resolve this or escalate.": "निम्न पर सीमित: आपके उत्तर आपस में टकराते हैं (शास्त्रीय श्रेणी, पर प्रामाणिक ग्रंथ से नहीं)। कृपया इसे सुलझाएँ या मानव समीक्षक को भेजें।",
 "Capped at low: no topic keyword matched, so retrieval relied only on text similarity.": "निम्न पर सीमित: कोई विषय-कीवर्ड मेल नहीं खाया, इसलिए खोज केवल पाठ-समानता पर निर्भर रही।",
 "Capped at medium: fewer than two sources were retrieved.": "मध्यम पर सीमित: दो से कम स्रोत मिले।",
 "Capped at low: the question is about another country's rules, which the India corpus does not cover.": "निम्न पर सीमित: प्रश्न किसी अन्य देश के नियमों के बारे में है, जिन्हें भारत का संग्रह कवर नहीं करता।",
 "No stored source matched the question well enough, so no answer is given.": "कोई संग्रहीत स्रोत प्रश्न से पर्याप्त मेल नहीं खाया, इसलिए उत्तर नहीं दिया जा रहा।",
 "The corpus is small by design; a gap here does not mean the law is silent.": "संग्रह जान-बूझकर छोटा है; यहाँ कमी का अर्थ यह नहीं कि कानून मौन है।",
 "I will not guess. The stored sources do not cover this question. You can escalate it to a human reviewer, which packages your question into a case file (nothing is sent anywhere).": "मैं अंदाज़ा नहीं लगाऊँगा। संग्रहीत स्रोत इस प्रश्न को कवर नहीं करते। आप इसे मानव समीक्षक को भेज सकते हैं, जिससे आपका प्रश्न एक केस फ़ाइल में पैक होता है (कहीं कुछ भेजा नहीं जाता)।",
 UNSUPPORTED_EN.strip(): "यह प्रोटोटाइप केवल अंग्रेज़ी और हिंदी प्रश्नों का समर्थन करता है, इसलिए मैं इस प्रश्न के लिए स्रोत नहीं खोज सकता। कृपया अंग्रेज़ी या हिंदी में पूछें, या मानव समीक्षक को भेजें।",
 "Public disclosure before filing may count against novelty, so the dates of any disclosure matter.": "आवेदन से पहले सार्वजनिक खुलासा नवीनता के विरुद्ध गिना जा सकता है, इसलिए खुलासे की तिथियाँ मायने रखती हैं।",
 "A formulation taken from authoritative texts faces the traditional-knowledge exclusion and TKDL prior art.": "प्रामाणिक ग्रंथों से लिए गए फॉर्मूलेशन को पारंपरिक ज्ञान के बहिष्करण और TKDL की पूर्व-कला का सामना करना पड़ता है।",
 "Your question mentions Indian bodies or law, but you selected International. No Indian sources are included; switch to India to see them.": "आपके प्रश्न में भारतीय संस्थाओं या कानून का उल्लेख है, पर आपने अंतरराष्ट्रीय चुना है। कोई भारतीय स्रोत शामिल नहीं है; उन्हें देखने के लिए भारत चुनें।",
 "Your question mentions another country. This India answer covers Indian law only; switch to International for treaties and export-market regimes such as the EU and US.": "आपके प्रश्न में किसी अन्य देश का उल्लेख है। यह भारत का उत्तर केवल भारतीय कानून को कवर करता है; EU और US जैसे निर्यात-बाज़ार नियमों के लिए अंतरराष्ट्रीय चुनें।",
 "Does the product use biological resources found in India, and is the applicant an Indian or a foreign entity?": "क्या उत्पाद भारत में पाए जाने वाले जैविक संसाधनों का उपयोग करता है, और आवेदक भारतीय है या विदेशी संस्था?",
 "Is the knowledge codified in an authoritative text, are the plants cultivated, and is the user a registered AYUSH practitioner? These may qualify for exemptions.": "क्या ज्ञान किसी प्रामाणिक ग्रंथ में संहिताबद्ध है, क्या पौधे उगाए गए हैं, और क्या उपयोगकर्ता पंजीकृत आयुष चिकित्सक है? इनसे छूट मिल सकती है।",
 "Do you plan to file for IPR or to transfer research results or resources abroad, and is NBA approval planned before grant or transfer?": "क्या आप बौद्धिक संपदा अधिकार के लिए आवेदन या शोध परिणाम/संसाधन विदेश भेजने की योजना बना रहे हैं, और क्या अधिकार दिए जाने या हस्तांतरण से पहले NBA की मंजूरी की योजना है?",
})
RX = [(re.compile(p), f) for p, f in [
 (r"You chose the category: (.*)\.", "आपने श्रेणी चुनी: {c}।"),
 (r"Capped at medium: (\d+) of (\d+) retrieved sources are draft summaries not yet checked against official text \((.*)\)\.", "मध्यम पर सीमित: प्राप्त {1} में से {0} स्रोत अभी आधिकारिक पाठ से जाँचे नहीं गए ड्राफ़्ट सारांश हैं ({2})।"),
 (r"All (\d+) retrieved sources are marked verified.*", "सभी {0} प्राप्त स्रोत सत्यापित चिह्नित हैं; जाँच की तिथि और संदर्भ हर स्रोत पर दिखाए गए हैं। जहाँ बताया गया है, सत्यापन में द्वितीयक स्रोत उपयोग हुए।"),
 (r"Topic routing matched: (.*)\.", "विषय-रूटिंग से मिले विषय: {0}।"),
 (r"Only (\d+) question term\(s\) appear in the (\w+) corpus \(at least (\d+) needed\) and the best match scored ([\d.]+)\.", "प्रश्न के केवल {0} शब्द {1} संग्रह में मिले (कम से कम {2} चाहिए) और सर्वोत्तम मिलान का स्कोर {3} रहा।"),
]]
def tr(s):
    if s in EXACT: return EXACT[s]
    for rx, f in RX:
        m = rx.fullmatch(s)
        if m:
            g = list(m.groups()); g = [CAT.get(x, x) for x in g]
            return f.format(*g, c=g[0]) if "{c}" in f else f.format(*g)
    return s

def localize(res, lang):
    if lang != "hi": return res
    r = copy.deepcopy(res)
    r["disclaimer"] = tr(r.get("disclaimer", ""))
    for k in ("classification",):
        if r.get(k): r[k]["label"] = tr(r[k]["label"])
    if r.get("trail"): r["trail"]["classification"] = tr(r["trail"].get("classification", ""))
    r["assumptions"] = [tr(a) for a in r.get("assumptions", [])] if "assumptions" in r else None
    if r["assumptions"] is None: del r["assumptions"]
    if r.get("confidence"): r["confidence"]["reasons"] = [tr(x) for x in r["confidence"]["reasons"]]
    if r.get("message"):
        pre, sep, rest = r["message"].partition("I will not guess.")
        r["message"] = (tr(pre.strip()) + " " if pre.strip() else "") + tr(sep + rest)
    if r.get("clarify"):
        for q in r["clarify"]["questions"]:
            q["text"] = tr(q["text"]); q["options"] = [[v, tr(l)] for v, l in q["options"]]
    id_of = {s["n"]: s["id"] for s in r.get("sources", [])}
    if r.get("answer"):
        r["answer"]["intro"] = tr(r["answer"]["intro"])
        for f in r["answer"]["findings"]:
            if f["heading"] == "Note": f["text"] = tr(f["text"])
            elif len(f["cites"]) == 1 and id_of.get(f["cites"][0]) in HI_TEXT: f["text"] = HI_TEXT[id_of[f["cites"][0]]]
            else: f["text"] = f["text"] + " [अंग्रेज़ी पाठ]"
    for c in r.get("abs_checklist") or []: c["q"] = tr(c["q"])
    for s in r.get("sources", []):
        if s["id"] in HI_TEXT: s["passage"] = HI_TEXT[s["id"]] + "\n\nEnglish (authoritative summary): " + s["passage"]
    return r
