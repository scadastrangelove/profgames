"""Reviewed English copy and explicit classification for the November stack release."""

# title, factual summary, limits. Russian evidence stays in the research packets.
EN = {
"PHP2SHELL_DISCOVERY_REMEDIATION": (
 "PHP2Shell: AI-assisted validation meets a constrained repair pipeline",
 "PHP Foundation released fixes for CVE-2026-109618 and CVE-2026-109619. One issue had a research history dating to 2024; compatibility, agreement on the fix and scarce expertise delayed remediation. Wiz describes AI-assisted research, exploit demonstrations and patch validation. The Foundation reports 15 CVEs since July and over 100 invalid, duplicate or unreproducible reports. Palo Alto Networks subsequently confirmed exploitation of exposed PAN-OS management interfaces; Singapore's CSA described chaining with Fragnesia on November 3. On November 4, MDDI reported government/CII mitigation and no evidence of exploitation in those systems.",
 "This was not an autonomous discovery without prior human work. PHP market share is not compromised-site share; attacker AI use is not established. November 3 dates the advisory, not the first attack. A PHP fix does not mean every dependent product is patched. Singapore's statement does not establish that government sites were breached or shut down."),
"OPENAI_KERNEL_PIPELINE": (
 "OpenAI reports a large AI-assisted Linux vulnerability-validation pipeline",
 "OpenAI reports 1,724 dynamically reproduced vulnerabilities and exploit demonstrations for 948 distinct local privilege-escalation cases, at about $1.21 million in API credits. Researchers reviewed findings before submission. At the end of the ten-day analysis, 61 LPE cases already had upstream fixes, 43 had staging patches and 299 were publicly discussed.",
 "948 is not a count of new CVEs or remotely breached systems. LPE assumes local access. API spending excludes total labour and operating costs. The corpus and methodology are reported by OpenAI, not independently reproduced here."),
"GPT6_CYBER_RESTRICTED_RELEASE": (
 "GPT-6 Cyber: stronger capabilities behind verified-access requirements",
 "OpenAI rates GPT-6 Cyber Critical under its own cyber-capability framework and limits access to Daybreak Red. Requirements include identity and organisational-security checks, SSO, MFA and allowed API IP addresses. The company reports improved compliance with task boundaries in evaluations.",
 "Critical is OpenAI's classification, not a regulator's determination. Controlled boundary tests do not guarantee the absence of future authority violations."),
"GEMINI_CARBON_DEFENDERS_FIRST": (
 "Google starts Gemini 4 Carbon access with defenders and vetted partners",
 "Google announced initial Carbon access for selected cyber defenders, subsequent expansion through Fairwind and participation in the voluntary U.S. pre-release government-testing process.",
 "An announcement is not universal availability. Vendor comparisons do not generalise to all real attacks; the government process is described as voluntary."),
"STORM0940_ARTEX_CONNECTWISE": (
 "Microsoft links ARTEX to compromised ConnectWise cloud-application trust",
 "Microsoft attributes the campaign to China-focused Storm-0940 and describes ARTEX-assisted attacks and abuse of application privileges at ConnectWise customers. Sign-in attempts targeted more than 2,250 tenants; follow-on credential and privilege changes were observed in some environments.",
 "2,250 is an attempted-sign-in target count, not confirmed breaches. Microsoft saw no successful sign-ins in the separately described password-spray episode. Attribution and the agent-tooling assessment belong to Microsoft."),
"VAPOR_PANDA_ARTEX": (
 "CrowdStrike describes human-directed parallel espionage with ARTEX",
 "CrowdStrike describes VAPOR PANDA using ARTEX, DeepSeek and a second commercial model. More than 200 organisations were targeted; the investigator confirmed post-exploitation activity at nine. It distinguishes this campaign from Storm-0940 and describes human-directed parallel activity.",
 "Not 200 confirmed breaches or a spontaneous autonomous swarm. Shared tooling does not establish a shared actor; unknown victim overlaps must not be added together."),
"ARTEX_CLOUD_SECRETS": (
 "Microsoft observes five minutes from a GitHub secret to Key Vault exfiltration",
 "Microsoft describes agent-assisted secret discovery and cloud activity; one observation took five minutes from a GitHub search to Azure Key Vault exfiltration. Another phase began on October 28. A November 6 report describes financially motivated Storm-3358 using ARTEX, primarily against Southeast Asian financial organisations.",
 "Five minutes is one observation, not a mean. Related reports are not necessarily independent victim samples; this record does not establish the exact model."),
"GITBOOK_CREDENTIAL_CHAIN": (
 "GitBook acknowledges intrusion and service shutdown to revoke infrastructure access",
 "GitBook describes an SSO flaw, GitHub integration and cloud credential leading into production infrastructure. It revoked service privileges, stopped the service and rotated secrets. The initial disclosure describes AI-agent involvement; the postmortem treats accessible customer data as potentially exposed rather than all proven exfiltrated.",
 "The attacker's model and degree of autonomy are not established. Potential access is not proof that all customer data was downloaded."),
"EMUDHRA_TRUST_REVOCATION": (
 "Mozilla revokes trust after compromised eMudhra intermediate keys",
 "Mozilla reports eight compromised eMudhra intermediate keys and OneCRL blocking delivered to standard Firefox configurations within three hours of notification.",
 "The source does not establish AI involvement in the compromise. Blocking delivery is not identical to recovery across all clients; some configurations required updates."),
"NIST_AGENT_IDENTITY_TENETS": (
 "NIST proposes separating agent permissions from agent reasoning",
 "NIST sets out ten proposed agent-identity design tenets, including distinct identities, bounded delegation, short-lived revocable privileges, independent logs and access policy separate from reasoning. It favours deterministic access controls and notes that guardrails alone are insufficient.",
 "This is proposed architecture in a NIST publication, not a new binding law or certification of implemented controls."),
"MISTRAL_OPEN_AND_VETTED_CYBER": (
 "Mistral combines open weights with separately vetted cyber access",
 "Mistral released Large 4 weights after the October 6 API preview and separately describes vetted enterprise access to a specialised cyber variant for agreed purposes. Its weight licence requires a separate commercial agreement for specified Model-as-a-Service uses, with an internal-use exception.",
 "Modified MIT is not unconditional MIT. Open weights for the base offering do not imply unrestricted access to the specialised variant. The exact first weight-release day is not established here; the record retains month precision."),
"CHINA_AI_TECH_EXPORT_CATALOGUE": (
 "China proposes AI cyber export controls and introduces interim registration",
 "MOFCOM and MOST consulted on 40 technologies, including 23 AI technologies. The explanation places AI malware generation/modification under proposed prohibitions and AI vulnerability discovery under restrictions. Interim pre-export registration applies from the announcement; consultation on the catalogue runs to November 15. Exemptions and distinctions cover public technologies, open development, overseas deployment and API access.",
 "The draft catalogue is not a fully enacted general ban on Chinese models or APIs. Interim registration has a different legal stage. Detailed thresholds require separate examination of the annexes."),
"CHINA_H200_IMPORT_GATE": (
 "Reuters: roughly 600,000 H200 chips await mainland China import approval",
 "Reuters, citing two informed people, reports roughly 600,000 H200 chips in Hong Kong awaiting large mainland shipments. Beijing reportedly has not granted broad import approval, although some small shipments arrived.",
 "Anonymous reporting, without independent inventory or public company/regulator confirmation. Stored chips are not operating capacity; the delay is not attributed solely to U.S. export restrictions."),
"NEW_YORK_DC_PERMIT_MORATORIUM": (
 "New York pauses a defined class of large data-centre permits",
 "Executive Order 62 directs DEC to pause specified incomplete discretionary permit applications for data-centre construction or expansion pending a generic environmental impact statement. The definition includes a 50 MW threshold and research, educational and other exceptions; local permits are outside this provision.",
 "This July measure predates the November election. It is neither a U.S.-wide construction ban nor closure of existing sites. An anticipated one-year pause differs from the order's GEIS completion condition."),
"TEXAS_ELECTION_DC_PAUSE_PLEDGE": (
 "Texas election follow-up: a data-centre pause remains a political commitment",
 "Gina Hinojosa supported a pause on data-centre approvals pending statutory protections for residents. The Texas Tribune describes her as governor-elect and dates a specific pledge to October 22. Abbott's pause and audit preceded the election; the incoming administration takes office on January 19, 2027.",
 "New promises are not enacted measures. This does not establish that the data-centre position caused the election outcome, a nationwide halt, or a new version of the earlier Abbott audit."),
"ASML_CAPACITY_AND_SERVICE": (
 "ASML: manufacturing capacity and installed-base service constrain the stack",
 "ASML disclosed EUR 3.289 billion in Q3 installed-base service and field-option revenue. It expects planned 2027-2028 deliveries to fall short of customer demand.",
 "Shortage guidance comes from the supplier. Service revenue establishes neither remote shutdown rights nor specific political intervention."),
"TSMC_N2_REVENUE": (
 "TSMC reports 2 nm production in realised wafer revenue",
 "In its Q3 disclosure, TSMC reports 2 nm at 8% of wafer revenue, 3 nm at 33%, and 7 nm and newer processes together at 79%.",
 "These are TSMC revenue shares, not global market shares or AI-chip counts. They do not measure each U.S. or Chinese model's dependence on TSMC."),
"SKHYNIX_LONG_TERM_ALLOCATION": (
 "SK hynix assigns more than half of 2027-2028 capacity through long-term agreements",
 "SK hynix reports long-term agreements covering over 50% of 2027-2028 production capacity and growing HBM4 shipments.",
 "Not all capacity is sold, and the cited capacity is not exclusively HBM. Further shortages are guidance, not an already realised outcome."),
"HUAWEI_COMMERCIAL_STACK_ROADMAP": (
 "Huawei reports commercial Atlas 950 deployment and a broader domestic stack",
 "Huawei reports over 1,000 deployed Atlas 900 A3 SuperPoDs and large-scale commercial use of Atlas 950. It presented 11 UnifiedBus chips and scheduled Ascend 960DT availability for Q1 2027.",
 "Deployment scale and results are Huawei's claims. Ascend 960DT is not counted as delivered; independent parity with NVIDIA on performance, cost and reliability is not established."),
"ALIBABA_STACK_EXPORT": (
 "Alibaba links chips, cloud, models and agent services to overseas expansion",
 "Alibaba presented AgentCore and Agent Security Center and plans for its first cloud regions in Turkey, Finland and the Netherlands. Zhenwu V900 mass production is planned for Q1 2027; the capacity target above 20 GW refers to 2032.",
 "New regions, V900 and 20 GW are plans, not verified available capacity. A vendor announcement is not independent evidence of full-stack parity or dependency-free overseas deployment."),
"LUMI_AI_PROCUREMENT": (
 "EuroHPC signs LUMI-AI procurement with shared compute allocation",
 "EuroHPC signed with Bull to acquire, deliver, install and maintain LUMI-AI for EUR 387.8 million, funded equally by EuroHPC and the national consortium. User access is expected in 2027; resources are shared in proportion to investments.",
 "The new machine is not already operational. The existing LUMI AI Factory has offered services on the different LUMI system since April 2025."),
"EUROHPC_GIGAFACTORY_DEADLINE": (
 "EuroHPC extends the first AI Gigafactory lot for national budget procedures",
 "The November 5 amendment to EUROHPC-2026-CEI-AIGF-01 moves lot 1 to February 4, 2027 to complete national budget procedures and funding commitments. Lot 2 remains due December 3, 2026. Authorities will buy compute time from selected consortia.",
 "One lot's extension is not cancellation. The original call opened July 30; this event dates the amendment."),
"AWS_EU_DISCONNECTION_EXERCISE": (
 "AWS reports a European cloud exercise without two global systems",
 "AWS reports disabling its global backbone and controlled operational-data exchange for a multi-hour exercise. Traffic used the public internet while European staff continued operations and workloads and data remained available.",
 "AWS's report is not an independent audit. This was not disconnection from the entire internet, indefinite autonomy, portability to another supplier or legal immunity."),
"UK_DATACENTRE_COVENANT": (
 "UK links prioritised data-centre support to energy, community and resilience conditions",
 "The Data Centre Covenant ties additional support for strategic data centres to energy-cost coverage, local benefits, environmental reporting and resilience. It describes prioritised grid connections and a future limited temporary-generation regime before grid access.",
 "Not every provision is an effective universal legal duty. Some criteria and rules remain to be defined; 6 GW by 2030 is a target, not current capacity."),
"ARAMCO_HUMAIN_CLOSING": (
 "Aramco acquires 49% of HUMAIN, linking energy, capital and AI ownership",
 "PIF and Aramco announced closing: PIF retains 51%, while Aramco receives 49% and contributes AI assets and about SAR 9.9 billion ($2.6 billion) in cash during 2026. Deployment of 3 GW by 2030 remains planned.",
 "Closing does not establish an independent full stack, completion of every cash contribution or commissioning of the planned 3 GW."),
"JAIS3_OPEN_ARABIC_AGENTS": (
 "Jais 3: Arabic models built on K2 Horizon, with inspectable training checkpoints",
 "IFM and partners released six Jais 3 models, 0.9B-375B parameters, based on their K2 Horizon family rather than Qwen. The developer reports 201.45B continued-pretraining tokens (75% Arabic, 25% replay) and 41.1B SFT tokens; 59% of Arabic data was synthetically translated. Apache 2.0 weights and training-stage checkpoints are published, with a sample rather than the full corpus. The inspected 7B card still lists code as coming soon.",
 "Lineage, training figures and comparative results are developer reports, not an audit of all training or independent Arabic-quality evaluation. Do not conflate Jais 3 with older Qwen-based K2Think. Available weights do not establish hardware independence, full reproducibility or frontier superiority; the largest checkpoint is not economical autonomy for every user."),
"ABUDHABI_MACHINE_READABLE_GOVERNMENT": (
 "Abu Dhabi embeds locally executed OpenAI in a government-rule pilot",
 "Abu Dhabi reports an operating Machine-Readable Government food-import pilot at ADAFSA. Selected rules are machine-readable, outputs trace to rules and officials retain final decisions. OpenAI compute runs in the UAE. ADNOC and Mubadala agreements were announced the same day.",
 "One reported pilot is not a government-wide transition. Independent accuracy, portability and continuity audits are not published; OpenAI control of final administrative decisions is not established."),
"YANDEX_ALICE_FOUNDATION_RELEASE": (
 "Yandex publishes Apache-licensed Alice AI Foundation and reports training from scratch",
 "Yandex released AliceAI-Foundation-80B-A3B-Base with 80B parameters, 3B active and Apache 2.0 licensing. The company and model card report training from scratch; this experimental base model is also intended for further training.",
 "Training provenance is a developer statement, not a full pipeline audit. It does not establish independence from foreign accelerators, a production-ready agent or universal frontier parity. Vendor benchmarks are separate from the release itself."),
"YANDEX_DATACENTRE_PHYSICAL_RESILIENCE": (
 "Russian data-centre damage exposes the physical limits of local sovereignty",
 "Yandex Cloud reports severe damage and shutdown at Sasovo after a drone attack overnight on October 8, and an attack at Kaluga on October 9. Customer Mindbox reports restoring checkout/loyalty for 90% of customers in 53 minutes after the first outage; after another October 11 outage, 99% regained full functionality within 20 hours.",
 "Not a cyber intrusion or destruction of all Russian AI capacity. Lost GPU numbers are unconfirmed. Mindbox recovery is not restoration of all Yandex equipment; customer testimony is not independent attack attribution."),
"UK_CST_SOVEREIGN_AGENCY": (
 "UK CST defines AI sovereignty through agency and resilience under pressure",
 "CST recommends distinguishing capabilities the UK should own, dependencies it can accept and areas of potential leadership. Sovereignty is framed as sufficient agency across the value chain and resilience under pressure.",
 "An advisory letter is not an adopted government strategy, statute or already established exit capability."),
"UK_AI_DEFENCE_INCIDENT_READINESS": (
 "UK links AI-assisted remediation, model evaluation and agent-incident readiness",
 "The government reports two pilots helped find and fix over 1,000 potential vulnerabilities in government systems. It announced wider defensive model use, AISI testing and work on serious agent incidents and near-miss reporting.",
 "A government pilot report is not an independently published corpus of 1,000 new CVEs. Considering Cyber Security and Resilience Bill changes does not make all proposed duties effective."),
"COMMON_AI_TRAINING_SIGNAL": (
 "OpenAI commits to a common website AI-training preference signal",
 "OpenAI announced its intention to honour a shared robots.txt signal expressing website preferences for foundation generative-model training, with implementation in coming months. Existing crawler-specific controls remain.",
 "A voluntary commitment, not an already effective universal standard. It establishes neither compensation, mandatory citation nor a search-retrieval prohibition; training and retrieval are different uses."),
"ORACLE_OPENAI_ENTERPRISE_SECURITY": (
 "Oracle and OpenAI combine decision interfaces, enterprise data and managed defence",
 "Oracle announced AI Workspace connecting OpenAI models and ChatGPT with applications, data and OCI, and AI Security Mesh for vulnerability discovery and remediation. Customers define authorised testing scope; Oracle manages verification and safeguards.",
 "An architecture/product announcement does not measure deployment, exit cost or defensive effectiveness. It does not establish Oracle's final authority over customer decisions."),
"OPENAI_ONEGOV_EXPANSION": (
 "OneGov expands subsidised public-sector AI and cyber access",
 "OpenAI and GSA announced a 27-month agreement waiving per-user licence fees and discounting usage by 50%, extended to state, local and tribal bodies. Vetted government organisations can access Daybreak Blue; Red requires a separate request and commercial pricing.",
 "Eligibility is not active-user uptake. A free licence is not free usage or absence of later dependency. Terms come from the vendor announcement, not the complete GSA contract."),
"NVIDIA_SOVEREIGN_RUNTIME": (
 "NVIDIA proposes a hardware/software agent-control stack for European clouds",
 "NVIDIA describes European cloud projects using DSX and its announced OpenShell architecture: model execution, agent tool environments and BlueField-4/Sentry controls. Partners support the architecture for bounding permitted agent actions.",
 "Reference architecture is not proof of unbreakable containment or universal deployment. NVIDIA operation of every customer control is not established. Nebius is not Russian sovereign compute capacity."),
"BIS_CIRCULAR_AI_FINANCE": (
 "BIS research links AI investment relationships with supply contracts",
 "BIS Bulletin 137 authors estimate that in 2021-2025, pairs also linked by commercial supply accounted for 46.4% of AI inter-firm investment deal value and 16.1% of deal count.",
 "A historical sample, not 2026 deal share or evidence of fictitious revenue, collusion or an inevitable bubble. The authors' findings need not represent BIS or central-bank positions."),
}

# actors, jurisdictions (cyber packet lacks these), layers, domain numbers,
# AI role (D=defence, A=attack, P=protected), artifact, force, stage, priority.
CLASS = {
"PHP2SHELL_DISCOVERY_REMEDIATION": (['PHP Foundation','Wiz','Palo Alto Networks','CSA Singapore'],['Global','Singapore'],['cyber_security_patch'],[3,4],'D','disclosure','not_applicable','remediated',1),
"OPENAI_KERNEL_PIPELINE": (['OpenAI','Linux kernel maintainers'],['US','Global'],['cyber_security_patch','finance_rent'],[3,4],'D','research','not_applicable','reported',1),
"GPT6_CYBER_RESTRICTED_RELEASE": (['OpenAI'],['US'],['model_weights','cyber_security_patch','governance_law'],[2],'D','access_program','contractual','limited_access',1),
"GEMINI_CARBON_DEFENDERS_FIRST": (['Google'],['US'],['model_weights','cyber_security_patch','governance_law'],[2],'D','access_program','contractual','limited_access',1),
"STORM0940_ARTEX_CONNECTWISE": (['Microsoft','ConnectWise','Storm-0940'],['China','Global'],['cyber_security_patch','cloud_inference'],[1,4],'A','incident','not_applicable','reported',1),
"VAPOR_PANDA_ARTEX": (['CrowdStrike','VAPOR PANDA','DeepSeek'],['China','Global'],['cyber_security_patch','model_weights'],[1,4],'A','incident','not_applicable','reported',2),
"ARTEX_CLOUD_SECRETS": (['Microsoft','Storm-3358'],['Global'],['cyber_security_patch','cloud_inference','data_telemetry'],[1,4],'A','incident','not_applicable','reported',1),
"GITBOOK_CREDENTIAL_CHAIN": (['GitBook'],['Global'],['cyber_security_patch','cloud_inference','data_telemetry'],[4,1],'A','incident','not_applicable','investigated',1),
"EMUDHRA_TRUST_REVOCATION": (['Mozilla','eMudhra'],['Global'],['cyber_security_patch','data_telemetry'],[4],'','incident','not_applicable','remediated',2),
"NIST_AGENT_IDENTITY_TENETS": (['NIST'],['US'],['cyber_security_patch','governance_law'],[1,5],'P','guidance','advisory','published',1),
"MISTRAL_OPEN_AND_VETTED_CYBER": (['Mistral'],['France','EU'],['model_weights','cyber_security_patch','governance_law'],[2],'D','product','contractual','available',1),
"CHINA_AI_TECH_EXPORT_CATALOGUE": (['China Ministry of Commerce','China Ministry of Science and Technology'],['China'],['model_weights','governance_law','cyber_security_patch'],[2],'','consultation','conditional','partly_effective',1),
"CHINA_H200_IMPORT_GATE": (['NVIDIA','China Government'],['China','Hong Kong','US'],['energy_compute_chips','governance_law'],[],'','market_observation','undetermined','reported',2),
"NEW_YORK_DC_PERMIT_MORATORIUM": (['New York State Government'],['US'],['energy_compute_chips','governance_law'],[],'','government_order','binding','effective',2),
"TEXAS_ELECTION_DC_PAUSE_PLEDGE": (['Gina Hinojosa','Texas State Government'],['US'],['energy_compute_chips','governance_law'],[],'','political_declaration','not_applicable','announced',2),
"ASML_CAPACITY_AND_SERVICE": (['ASML'],[],[],[],'','market_observation','not_applicable','reported',2),
"TSMC_N2_REVENUE": (['TSMC'],[],[],[],'','market_observation','not_applicable','reported',2),
"SKHYNIX_LONG_TERM_ALLOCATION": (['SK hynix'],[],[],[],'','market_observation','contractual','reported',2),
"HUAWEI_COMMERCIAL_STACK_ROADMAP": (['Huawei'],[],[],[],'','deployment','not_applicable','reported',2),
"ALIBABA_STACK_EXPORT": (['Alibaba'],[],[],[],'','product','not_applicable','announced',2),
"LUMI_AI_PROCUREMENT": (['EuroHPC JU','Bull'],[],[],[],'','government_program','contractual','signed',2),
"EUROHPC_GIGAFACTORY_DEADLINE": (['EuroHPC JU'],[],[],[],'','government_program','contractual','published',2),
"AWS_EU_DISCONNECTION_EXERCISE": (['Amazon / AWS'],[],[],[4],'P','evaluation','not_applicable','reported',1),
"UK_DATACENTRE_COVENANT": (['UK Government'],[],[],[4],'','policy_framework','conditional','announced',2),
"ARAMCO_HUMAIN_CLOSING": (['PIF','Saudi Aramco','HUMAIN'],[],[],[],'','market_observation','contractual','signed',2),
"JAIS3_OPEN_ARABIC_AGENTS": (['IFM','MBZUAI','Inception42'],[],[],[],'','product','contractual','available',2),
"ABUDHABI_MACHINE_READABLE_GOVERNMENT": (['Abu Dhabi Government','ADAFSA','OpenAI'],[],[],[5],'P','deployment','not_applicable','reported',2),
"YANDEX_ALICE_FOUNDATION_RELEASE": (['Yandex'],[],[],[],'','product','contractual','available',2),
"YANDEX_DATACENTRE_PHYSICAL_RESILIENCE": (['Yandex','Mindbox'],[],[],[4],'','incident','not_applicable','reported',1),
"UK_CST_SOVEREIGN_AGENCY": (['UK Council for Science and Technology'],[],[],[5],'','policy_letter','advisory','published',2),
"UK_AI_DEFENCE_INCIDENT_READINESS": (['UK Government','UK AI Security Institute','NCSC'],[],[],[3,2],'D','government_program','not_applicable','reported',1),
"COMMON_AI_TRAINING_SIGNAL": (['OpenAI'],[],[],[],'','provider_policy','advisory','announced',2),
"ORACLE_OPENAI_ENTERPRISE_SECURITY": (['Oracle','OpenAI'],[],[],[1,3],'PD','product','not_applicable','announced',2),
"OPENAI_ONEGOV_EXPANSION": (['OpenAI','US General Services Administration'],[],[],[2,3],'D','access_program','contractual','effective',1),
"NVIDIA_SOVEREIGN_RUNTIME": (['NVIDIA'],[],[],[1],'P','product','not_applicable','announced',2),
"BIS_CIRCULAR_AI_FINANCE": (['Bank for International Settlements'],[],[],[],'','research','not_applicable','published',2),
}
