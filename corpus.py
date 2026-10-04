"""Source corpus for IP-SAKTI Sahayak.

Every entry is a SHORT PLAIN-LANGUAGE SUMMARY written for this prototype. It is not a
quotation of the official text. `verified=True` means the claims in `text` were checked
against the sources named in `checked` on the date shown. Everything else is a draft.

Verification was done on 2026-10-04 using web search results only (no access to the
Gazette PDFs themselves except where stated), so "verified" here means "checked against
the named reliable source", not "certified by a lawyer".
"""

CORPUS_VERSION = "0.1-dev-2026-10-04"
CHECK_DATE = "2026-10-04"

DRAFT_NOTE = "Draft summary, verify against official text"

ROOT_IPINDIA = "https://ipindia.gov.in"
ROOT_INDIACODE = "https://www.indiacode.nic.in"
ROOT_CDSCO = "https://cdsco.gov.in"
ROOT_WIPO = "https://www.wipo.int"
ROOT_WTO = "https://www.wto.org"
ROOT_CBD = "https://www.cbd.int"


def _e(id, jurisdiction, title, authority, section, version, status, url, topics, text,
       verified=False, checked=None):
    return dict(id=id, jurisdiction=jurisdiction, title=title, authority=authority,
                section=section, version=version, status=status, url=url, topics=topics,
                text=text, verified=verified, checked=checked)


CORPUS = [
    # ------------------------------------------------------------------ INDIA
    _e("in_pat_s2", "india", "Patents Act 1970: what counts as an invention",
       "Parliament of India; administered by the Indian Patent Office",
       "s.2(1) (invention, new invention, inventive step)", "Patents Act 1970 as amended",
       "In force (status not re-checked)", ROOT_IPINDIA, ["patent"],
       "An invention must be new, involve an inventive step and be capable of industrial application. "
       "The Act defines these terms in section 2(1). "
       "A new invention is one not already published or used anywhere before the filing date, so publishing or selling a formulation before you file can count against you.",
       False, None),
    _e("in_pat_s3d", "india", "Patents Act 1970: new forms of known substances",
       "Parliament of India; administered by the Indian Patent Office",
       "s.3(d)", "Patents Act 1970 as amended", "In force (status not re-checked)", ROOT_IPINDIA, ["patent"],
       "Section 3(d) says that discovering a new form of a known substance is not an invention unless it clearly improves the known efficacy. "
       "It also excludes the mere discovery of a new property or new use of a known substance, and the mere use of a known process. "
       "Whether a new herbal extract or preparation clears this bar depends on the evidence of improved efficacy and is a question for a patent attorney.",
       False, None),
    _e("in_pat_s3p", "india", "Patents Act 1970: traditional knowledge exclusion",
       "Parliament of India; administered by the Indian Patent Office",
       "s.3(p)", "Patents Act 1970 as amended", "In force (status not re-checked)", ROOT_IPINDIA, ["patent", "tk"],
       "Section 3(p) excludes from patent protection an invention that is, in effect, traditional knowledge, "
       "or that is an aggregation or duplication of known properties of traditionally known components. "
       "A formulation taken from, or only a combination of, classical Ayurvedic ingredients is therefore at real risk of being refused.",
       False, None),
    _e("in_pat_s10_4d", "india", "Patents Act 1970: disclosure of biological source",
       "Parliament of India; administered by the Indian Patent Office",
       "s.10(4)(d)", "Patents Act 1970 as amended", "In force (status not re-checked)", ROOT_IPINDIA, ["patent", "abs"],
       "Where an invention uses biological material, the patent specification must disclose the source and geographical origin of that material. "
       "This links patent filing to the access and benefit-sharing rules under the Biological Diversity Act.",
       False, None),
    _e("in_pat_s25", "india", "Patents Act 1970: opposition to a patent",
       "Parliament of India; administered by the Indian Patent Office",
       "s.25 (pre-grant and post-grant opposition)", "Patents Act 1970 as amended", "In force (status not re-checked)",
       ROOT_IPINDIA, ["patent", "tk"],
       "Section 25 lets third parties oppose a patent before grant and after grant. "
       "Grounds include that the invention was already published or known, including knowledge available within a local or indigenous community, "
       "and that the biological source was not disclosed or was wrongly stated. "
       "Traditional-knowledge prior art is a common basis for opposition.",
       False, None),
    _e("in_tkdl", "india", "Traditional Knowledge Digital Library (TKDL)",
       "Government of India (CSIR with the Ministry of Ayush)", "Database; not a statute",
       "Not versioned in this corpus", "Operating (status not re-checked)", "https://tkdl.res.in", ["tk", "patent"],
       "TKDL is a government digital library that records formulations from Indian traditional medicine texts in a form patent examiners can search. "
       "Its purpose is to help examiners find traditional-knowledge prior art and stop wrongly granted patents. "
       "Access for patent offices is under access agreements, so a TKDL search by you is not the same as an examiner's search. "
       "Use the official site for registry searches.",
       False, None),
    _e("in_bda_2002", "india", "Biological Diversity Act 2002: access and benefit sharing",
       "Parliament of India; National Biodiversity Authority (NBA), State Biodiversity Boards",
       "ss.3, 4 and 6 (as described in commentary)", "Act 18 of 2002 (pre-2023 position)", "In force; amended in 2023",
       "https://nbaindia.org", ["abs", "tk", "patent", "export"],
       "Foreign citizens, foreign-incorporated companies and non-resident Indians need NBA approval before accessing biological resources in India for research or commercial use (s.3). "
       "NBA approval is also needed before transferring research results based on Indian biological resources to foreigners (s.4). "
       "Before the 2023 amendment, s.6 required NBA approval before applying for any IPR on an invention based on Indian biological resources. "
       "Users of biological resources and associated knowledge must share benefits.",
       True, f"Checked {CHECK_DATE} against secondary legal commentary (Anantam IAS summary of ss.3, 4, 6; Sabrang India analysis of s.6; LiveLaw/PRS on the Act). "
             "Not checked against the Gazette text."),
    _e("in_bda_2023", "india", "Biological Diversity (Amendment) Act 2023",
       "Parliament of India; National Biodiversity Authority (NBA)",
       "Amendments to ss.6, 7 and related provisions (section numbers not independently checked)",
       "Passed by Parliament August 2023", "In force (reported); implementing rules not reviewed here",
       "https://nbaindia.org", ["abs", "tk", "patent", "export"],
       "The 2023 amendment moved the NBA approval requirement for IPR from before filing to before grant. "
       "It extended exemptions to users of codified traditional knowledge (knowledge from authoritative books in the First Schedule to the Drugs and Cosmetics Act), cultivated medicinal plants and registered AYUSH practitioners, "
       "for example from prior intimation to State Biodiversity Boards and from benefit sharing. "
       "Commentary notes that terms such as codified traditional knowledge are open to interpretation, and reports differ on how the rules treat Indian and foreign applicants, so read the Act and its rules for the exact scope.",
       True, f"Checked {CHECK_DATE} against LiveLaw (PRS summary of the Bill as passed), Mondaq overview, Khurana and Khurana analysis and Sabrang India commentary. "
             "These are secondary sources; the Act text and rules were not read."),
    _e("in_gi_1999", "india", "Geographical Indications of Goods (Registration and Protection) Act 1999",
       "Parliament of India; Geographical Indications Registry", "Act as a whole",
       "Act 48 of 1999", "In force (status not re-checked)", ROOT_IPINDIA, ["gi"],
       "The Act protects names of goods that come from a territory where a quality, reputation or other characteristic is essentially due to that origin. "
       "Registration is through the GI Registry and the right belongs to the producers of the region, not to one person. "
       "A GI protects a place-linked name, not a recipe or a method.",
       False, None),
    _e("in_tm_1999", "india", "Trade Marks Act 1999",
       "Parliament of India; Trade Marks Registry", "Act as a whole",
       "Act 47 of 1999", "In force (status not re-checked)", ROOT_IPINDIA, ["tm"],
       "The Act protects distinctive brand names, logos and other signs used for goods or services, through registration at the Trade Marks Registry. "
       "It does not protect a formulation or a process. "
       "Names that only describe the product or are common in the trade may be refused.",
       False, None),
    _e("in_design_2000", "india", "Designs Act 2000",
       "Parliament of India; Designs Wing of the Patent Office", "Act as a whole",
       "Act 16 of 2000", "In force (status not re-checked)", ROOT_IPINDIA, ["design"],
       "The Act protects the new and original shape, pattern, configuration or ornament applied to an article by an industrial process. "
       "It does not protect how an article works or what it contains. "
       "Packaging or bottle shape can qualify; the formulation inside cannot.",
       False, None),
    _e("in_copyright_1957", "india", "Copyright Act 1957",
       "Parliament of India; Copyright Office", "Act as a whole",
       "Act 14 of 1957", "In force (status not re-checked)", ROOT_INDIACODE, ["copyright"],
       "Copyright protects original expression such as texts, label artwork, drawings and software. "
       "It does not protect ideas, methods or formulas themselves. "
       "Your written monograph or label design can be protected while the formula it describes is not.",
       False, None),
    _e("in_pvpfr_2001", "india", "Protection of Plant Varieties and Farmers' Rights Act 2001",
       "Parliament of India; PPV&FR Authority", "Act as a whole",
       "Act 53 of 2001", "In force (status not re-checked)", ROOT_INDIACODE, ["pvp", "abs"],
       "The Act protects plant varieties that are new, distinct, uniform and stable, and recognises breeders' and farmers' rights. "
       "It matters if you develop or cultivate a new medicinal plant variety. "
       "It does not apply to a herbal formulation as such.",
       False, None),
    _e("in_trade_secret", "india", "Trade secrets in India (no dedicated statute)",
       "Courts; Indian Contract Act 1872 for contract terms", "Contract terms and breach of confidence",
       "Case-law based", "No statute; protection comes from contract and equity", ROOT_INDIACODE, ["trade secret"],
       "India has no dedicated trade-secret statute. "
       "Protection comes mainly from confidentiality terms in contracts and from the court-made action for breach of confidence. "
       "Secrecy is lost once the information is public, so keeping a formula secret and publishing it in a patent are choices that exclude each other.",
       False, None),
    _e("in_dc_s3a", "india", "Drugs and Cosmetics Act 1940: definition of Ayurvedic drug and First Schedule",
       "Parliament of India; CDSCO and State licensing authorities", "s.3(a) and First Schedule",
       "Act 23 of 1940 as amended", "In force (status not re-checked)", ROOT_CDSCO, ["drug", "tk"],
       "Section 3(a) treats a medicine as an Ayurvedic, Siddha or Unani drug when it is made exclusively in accordance with formulae in the authoritative books listed in the First Schedule. "
       "The First Schedule is the list of those books. "
       "A formulation that departs from those books needs to be looked at under other provisions, such as the rules on proprietary or new drugs.",
       False, None),
    _e("in_dc_ch4a", "india", "Drugs and Cosmetics Act 1940 Chapter IVA and Drugs Rules 1945 Parts XVI-XVII (Ayurvedic, Siddha and Unani drugs)",
       "Parliament of India; Ministry of Health; State licensing authorities", "Chapter IVA; Rules 151 to 159 (Part numbers not checked)",
       "Act 23 of 1940; Rules 1945, as amended", "In force (status not re-checked)", ROOT_CDSCO, ["drug"],
       "Chapter IVA applies the Act to Ayurvedic, Siddha and Unani drugs, covering manufacture, sale, standards and offences. "
       "A Ministry statement describes Rules 151 to 159 of the Drugs and Cosmetics Rules as the licensing and good-manufacturing-practice provisions for Ayurvedic medicines. "
       "Manufacturing licences for these drugs are issued by State licensing authorities.",
       False, f"Rules 151 to 159 range seen in a Ministry statement on {CHECK_DATE}; Part numbers and Chapter IVA contents not checked against the official text, so kept as a draft."),
    _e("in_dc_r158b", "india", "Drugs Rules 1945, Rule 158B: proof of safety and effectiveness for Ayurvedic drugs",
       "Ministry of Health and Family Welfare; State licensing authorities", "Rule 158B (including Rule 158B(II)(A))",
       "Drugs and Cosmetics Rules 1945 as amended", "In force; new-indication requirements questioned in the Supreme Court (2024)",
       ROOT_CDSCO, ["drug"],
       "Rule 158B sets out what proof of safety and effectiveness is needed for different categories of Ayurvedic drugs, including proprietary and new ones. "
       "In July 2024 the Supreme Court's amicus curiae argued in the misleading-advertisements case that a 2018 government notification had diluted the requirements for new indications without amending Rule 158B(II)(A), and the Court asked the Centre to respond. "
       "The outcome of that specific point was not verified here. "
       "Whether the New Drugs and Clinical Trials Rules 2019 also apply to a particular Ayurvedic product should be confirmed with the licensing authority.",
       True, f"Checked {CHECK_DATE} against a Ministry statement reproduced by BioVoice (Rule 158B prescribes proof of safety and effectiveness) and LiveLaw's 30 July 2024 report on the amicus submissions. "
             "Not checked: the Rule text itself, and whether the Rules 2019 exclude Ayurvedic drugs."),
    _e("in_dc_phyto", "india", "Phytopharmaceutical drugs: definition and approval",
       "CDSCO (New Drugs Division)", "Drugs Rules 1945 Rule 2(eb), Rule 122E; CDSCO FAQ",
       "CDSCO FAQ document (undated in the copy read)", "In force (as described in CDSCO FAQ)",
       "https://www.cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/New-Drugs/FAQs/New_Drugs_FAQs.doc",
       ["drug", "patent"],
       "A phytopharmaceutical drug is a purified and standardised fraction with defined bioactive or phytochemical compounds from a plant, as defined in the Drugs Rules. "
       "CDSCO treats a new phytopharmaceutical drug as a new drug, so permission to import or manufacture is needed (application in Form 44 per the CDSCO FAQ), and clinical trials follow the rules for new drugs. "
       "Parenteral dosage forms are not considered for market authorisation, per the CDSCO FAQ citing Rule 2(eb).",
       True, f"Checked {CHECK_DATE} against the CDSCO phytopharmaceutical FAQ pages and the CDSCO-hosted NDCT Rules 2019 text (new drug includes phytopharmaceutical drug)."),
    _e("in_ndct_2019", "india", "New Drugs and Clinical Trials Rules 2019",
       "Ministry of Health and Family Welfare; CDSCO", "Rule 2(1)(w) (new drug) and the Rules generally",
       "Notified 19 March 2019", "In force (as described by CDSCO)",
       "https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2022/new_DC_rules/NEW%20DRUGS%20ANDctrS%20RULE,%202019.pdf",
       ["drug"],
       "These Rules apply to new drugs and investigational new drugs for human use, clinical trials, bioavailability and bioequivalence studies and ethics committees. "
       "The definition of new drug expressly includes a phytopharmaceutical drug. "
       "They replaced Part XA and Schedule Y of the Drugs Rules for clinical trials as of 19 March 2019.",
       True, f"Checked {CHECK_DATE} against the CDSCO-hosted Rules text and CDSCO FAQ/presentation materials. Whether they apply to Ayurvedic proprietary or new drugs was not checked."),
    _e("in_cosmetics", "india", "Cosmetics under the Drugs and Cosmetics Act 1940",
       "Parliament of India; CDSCO", "Cosmetics provisions of the Act and Rules (section numbers not checked)",
       "Act 23 of 1940 as amended", "In force (status not re-checked)", ROOT_CDSCO, ["drug"],
       "Cosmetics are regulated under the Drugs and Cosmetics Act and Rules, with import and manufacture subject to registration or licensing. "
       "A herbal product that claims to treat or prevent disease may be a drug rather than a cosmetic, which changes the approval route. "
       "Check the claims on the label before choosing the category.",
       False, None),
    _e("in_fssai_aahar", "india", "Food Safety and Standards (Ayurveda Aahara) Regulations 2022",
       "Food Safety and Standards Authority of India (FSSAI), with the Ministry of Ayush", "Regulations as a whole; Schedule A lists authoritative books",
       "Notified May 2022 (sources give 5, 6 and 9 May for gazette, upload and effect; check the gazette PDF)",
       "In force (as reported in 2022; later amendments not checked)",
       "https://fssai.gov.in/upload/notifications/2022/05/62789a20b54bdGazette_Notification_Ayurveda_Aahara_09_05_2022.pdf",
       ["food"],
       "Ayurveda Aahara means food prepared by the recipes, ingredients or processes in the authoritative Ayurveda books listed in Schedule A of the Regulations. "
       "These foods need a licence or approval from FSSAI, carry a special logo, and their labels must state the intended purpose. "
       "Products in this category are approved by FSSAI rather than licensed as drugs.",
       True, f"Checked {CHECK_DATE} against the FSSAI notifications page listing, the USDA GAIN report IN2022-0054, and a Ministry of Ayush/FSSAI summary on Vikaspedia. Gazette PDF itself not opened."),
    _e("in_dmr_1954", "india", "Drugs and Magic Remedies (Objectionable Advertisements) Act 1954",
       "Parliament of India; State enforcement authorities", "Act as a whole (section numbers not checked)",
       "Act 21 of 1954", "In force (status not re-checked)", ROOT_INDIACODE, ["advertising", "drug"],
       "The Act prohibits advertisements that promote drugs or remedies for diseases and conditions listed in its Schedule, and advertisements that make magic-remedy claims. "
       "A Ministry statement says complaints about misleading advertisements of Ayurvedic drugs are forwarded to State authorities for action under this Act and the Drugs and Cosmetics Act. "
       "Claims such as cures or treatments for listed conditions are the main risk for herbal products.",
       False, f"Existence and use for Ayurvedic ads seen in a Ministry statement on {CHECK_DATE}; Schedule contents and offences not checked, so kept as a draft."),
    _e("in_dc_r170", "india", "Drugs Rules 1945, Rule 170 (advertisements of Ayurvedic, Siddha and Unani drugs)",
       "Ministry of Ayush; Supreme Court of India", "Rule 170 (omitted by notification of 1 July 2024)",
       "Omission notified 1 July 2024", "Omission challenged; reports say the Supreme Court later vacated its stay and closed the case",
       ROOT_CDSCO, ["advertising", "drug"],
       "Rule 170 required advertisements of Ayurvedic, Siddha and Unani drugs to be approved by the State licensing authority. "
       "The Ministry of Ayush notified its omission on 1 July 2024, the Supreme Court stayed that omission in August 2024, and later reports say the Court vacated the stay and closed the case, leaving liberty to approach the High Court. "
       "Check the current Rules before relying on or ignoring Rule 170.",
       True, f"Checked {CHECK_DATE} against LiveLaw, Bar and Bench and Verdictum reports. The date of the final order was not captured and the current text of the Rules was not read."),

    # ---------------------------------------------------------- INTERNATIONAL
    _e("int_trips_27", "international", "TRIPS Agreement Article 27: patentable subject matter",
       "World Trade Organization", "Art. 27", "TRIPS Agreement (1994)", "In force", ROOT_WTO, ["patent"],
       "Patents must be available for inventions in all fields of technology if they are new, involve an inventive step and are industrially applicable. "
       "Members may exclude diagnostic, therapeutic and surgical methods, and plants and animals other than microorganisms, and inventions whose commercial exploitation must be prevented to protect public order or morality. "
       "Each country still applies its own patent law.",
       False, None),
    _e("int_trips_22_24", "international", "TRIPS Agreement Articles 22-24: geographical indications",
       "World Trade Organization", "Arts. 22-24", "TRIPS Agreement (1994)", "In force", ROOT_WTO, ["gi"],
       "Article 22 gives general protection against misleading use of a geographical indication. "
       "Article 23 gives additional protection for wines and spirits. "
       "Article 24 contains exceptions and provides for further negotiations.",
       False, None),
    _e("int_cbd", "international", "Convention on Biological Diversity",
       "United Nations (Secretariat of the CBD)", "Arts. 8(j) and 15", "Adopted 1992", "In force", ROOT_CBD, ["abs", "tk"],
       "States have sovereign rights over their genetic resources, and access is subject to prior informed consent and mutually agreed terms (Art. 15). "
       "Article 8(j) asks parties to respect traditional knowledge and to promote its wider use with the approval of its holders and fair sharing of benefits.",
       False, None),
    _e("int_nagoya", "international", "Nagoya Protocol on Access and Benefit-sharing",
       "Convention on Biological Diversity", "Protocol as a whole", "Adopted 2010; in force 12 October 2014", "In force", "https://absch.cbd.int", ["abs", "tk"],
       "The Protocol puts the CBD's third objective into practice: fair and equitable sharing of benefits from using genetic resources and associated traditional knowledge. "
       "Parties set access rules, benefit-sharing terms and compliance measures, and the ABS Clearing-House publishes national information. "
       "Obligations depend on whether the provider and user countries are Parties.",
       False, None),
    _e("int_gratk", "international", "WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge (GRATK)",
       "World Intellectual Property Organization", "Treaty as a whole; entry into force under Art. 17",
       "Adopted 24 May 2024; status as of 4 October 2026 in this corpus",
       "NOT in force. Needs 15 ratifications or accessions, then enters into force three months later. WIPO's status table dated 13 March 2026 listed 3 (Albania, Malawi, Uganda); the EU IP Helpdesk reported Peru's ratification on 8 July 2026. The current count was not confirmed; check WIPO.",
       "https://www.wipo.int/en/web/treaties/ip/gratk/summary_gratk", ["abs", "tk", "patent"],
       "The treaty was adopted on 24 May 2024. Once in force it will require patent applicants to disclose the country of origin of genetic resources, "
       "or the Indigenous Peoples or local community that provided associated traditional knowledge, and the source if the origin is unknown. "
       "It will not apply to applications filed before it enters into force. It is not in force today.",
       True, f"Checked {CHECK_DATE} against the WIPO treaty summary page, WIPO's treaty status table dated 13 March 2026, WIPO GRATK Notification No. 2 (Uganda, 9 July 2025) and the EU IP Helpdesk item of 24 July 2026 on Peru. "
             "I did not find a later official count, so treat the number of ratifications as possibly out of date."),
    _e("int_pct", "international", "Patent Cooperation Treaty (PCT)",
       "World Intellectual Property Organization", "Treaty as a whole", "PCT (1970), as amended", "In force", ROOT_WIPO, ["patent"],
       "The PCT lets you file one international patent application that is searched and examined at an international stage. "
       "It does not grant an international patent: each country or region decides separately in the national phase. "
       "International searching authorities search a defined set of documents that includes traditional knowledge journals, which can matter for herbal inventions.",
       False, "The point about traditional knowledge journals was seen in an AIPPI article on 2026-10-04; the rest of this entry was not checked."),
    _e("int_madrid_hague", "international", "Madrid System (marks) and Hague System (designs)",
       "World Intellectual Property Organization", "Madrid Agreement and Protocol; Hague Agreement", "Current WIPO-administered systems", "In force", ROOT_WIPO, ["tm", "design"],
       "The Madrid System lets you apply for trade mark protection in many countries through one international application based on a home-country mark. "
       "The Hague System does the same for industrial designs. "
       "Neither gives a worldwide right: protection is decided country by country.",
       False, None),
    _e("int_budapest", "international", "Budapest Treaty on the deposit of microorganisms",
       "World Intellectual Property Organization", "Treaty as a whole", "Budapest Treaty (1977)", "In force", ROOT_WIPO, ["patent"],
       "The treaty requires member countries to recognise a deposit of a microorganism with any International Depositary Authority for patent procedure purposes. "
       "It matters when an invention involves a microorganism, such as a fermented or probiotic preparation. "
       "It does not help with plant-only herbal formulations.",
       False, None),
    _e("int_eu_2004_24", "international", "EU Directive 2004/24/EC: traditional herbal medicinal products",
       "European Union", "Directive 2004/24/EC amending Directive 2001/83/EC", "2004", "In force as amended (current EU text not checked)",
       "https://eur-lex.europa.eu", ["drug", "export"],
       "The Directive created a simplified registration route for traditional herbal medicinal products in the EU. "
       "Instead of full efficacy trials, the applicant shows long traditional use, generally at least 30 years including at least 15 years in the EU, "
       "while quality and safety requirements still apply. The route is for products used without medical supervision. "
       "Whether an Ayurvedic product qualifies depends on its evidence of use and on national authorities.",
       False, None),
    _e("int_us_dshea", "international", "US Dietary Supplement Health and Education Act 1994 (DSHEA)",
       "United States Congress; US Food and Drug Administration", "Act as a whole", "DSHEA (1994)", "In force (current FDA rules not checked)",
       "https://www.fda.gov", ["food", "export"],
       "DSHEA defines dietary supplements and regulates them as a category of food rather than as drugs. "
       "Manufacturers are responsible for safety and labelling, and structure or function claims are allowed with notice to FDA and a standard disclaimer. "
       "Claims to treat or cure disease are not allowed for supplements.",
       False, None),
]

assert len({c["id"] for c in CORPUS}) == len(CORPUS)
