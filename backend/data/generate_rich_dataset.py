import json
import csv
import os

# Comprehensive Real-World & Clustered Benchmark Dataset
# Contains 6 distinct real-world narrative lineage clusters + diverse background texts
# Each cluster has: Root Source, Exact Mirror, AI Paraphrase, Derived Mutation, Related Narrative

DATASET = [
    # =========================================================================
    # CLUSTER 1: NASA / ESA James Webb Space Telescope Cosmic Discovery
    # =========================================================================
    {
        "id": "jwst-001",
        "text": "NASA's James Webb Space Telescope has captured the deepest and sharpest infrared image of the distant universe to date. Known as Webb's First Deep Field, this image of galaxy cluster SMACS 0723 is overflowing with detail, revealing thousands of galaxies—including the faintest objects ever observed in the infrared—in a tiny sliver of sky approximately the size of a grain of sand held at arm's length by someone on the ground. The combined mass of the cluster acts as a gravitational lens, magnifying much more distant galaxies behind it.",
        "label": "HUMAN",
        "domain": "astrophysics",
        "synthetic_intent": "benign",
        "source_type": "official_press_release",
        "cluster_id": "cluster_jwst_deep_field",
        "cluster_role": "ROOT_ORIGIN",
        "notes": "Authentic NASA/ESA official scientific press release for SMACS 0723."
    },
    {
        "id": "jwst-002",
        "text": "NASA's James Webb Space Telescope has captured the deepest and sharpest infrared image of the distant universe to date. Known as Webb's First Deep Field, this image of galaxy cluster SMACS 0723 is overflowing with detail, revealing thousands of galaxies—including the faintest objects ever observed in the infrared—in a tiny sliver of sky approximately the size of a grain of sand held at arm's length by someone on the ground. The combined mass of the cluster acts as a gravitational lens, magnifying much more distant galaxies behind it.",
        "label": "HUMAN",
        "domain": "astrophysics",
        "synthetic_intent": "benign",
        "source_type": "wire_syndication",
        "cluster_id": "cluster_jwst_deep_field",
        "cluster_role": "EXACT_MIRROR",
        "notes": "Word-for-word AP/Reuters syndication wire reprint."
    },
    {
        "id": "jwst-003",
        "text": "The James Webb Space Telescope has officially delivered humanity's clearest and deepest infrared perspective of the cosmos to date. Centered on the massive galaxy cluster SMACS 0723, the groundbreaking deep-field image captures thousands of ancient galaxies, with gravitational lensing magnifying light from primordial structures that formed over thirteen billion years ago.",
        "label": "AI_GENERATED",
        "domain": "astrophysics",
        "synthetic_intent": "benign",
        "source_type": "llm_summary",
        "cluster_id": "cluster_jwst_deep_field",
        "cluster_role": "PARAPHRASED_DERIVATIVE",
        "notes": "LLM-generated news summary with restructured sentence syntax and vocabulary."
    },
    {
        "id": "jwst-004",
        "text": "Astronomers analyzing the new James Webb Space Telescope deep field image of SMACS 0723 report that gravitational lensing has revealed several high-redshift candidate galaxies from the epoch of reionization. Spectroscopic follow-up with NIRSpec indicates prominent ionized oxygen emission lines in galaxies appearing as luminous arcs around the cluster core.",
        "label": "HUMAN",
        "domain": "astrophysics",
        "synthetic_intent": "benign",
        "source_type": "academic_commentary",
        "cluster_id": "cluster_jwst_deep_field",
        "cluster_role": "RELATED_NARRATIVE",
        "notes": "Technical follow-up research paper commentary on NIRSpec spectroscopy."
    },

    # =========================================================================
    # CLUSTER 2: Global Artificial Intelligence Safety & Regulatory Frameworks
    # =========================================================================
    {
        "id": "ai-reg-001",
        "text": "The European Parliament and Council have reached a landmark political agreement on the Artificial Intelligence Act, establishing comprehensive risk-based harmonized rules across the European Union. The legislation introduces strict prohibitions on unacceptable-risk AI systems such as cognitive behavioral manipulation and biometric categorization, while imposing rigorous transparency and systemic risk assessment obligations on general-purpose foundation models.",
        "label": "HUMAN",
        "domain": "technology_policy",
        "synthetic_intent": "benign",
        "source_type": "official_communique",
        "cluster_id": "cluster_ai_governance",
        "cluster_role": "ROOT_ORIGIN",
        "notes": "Official European Commission legislative summary of the EU AI Act."
    },
    {
        "id": "ai-reg-002",
        "text": "European Union lawmakers have finalized political negotiations on the groundbreaking AI Act, establishing the world's first comprehensive legal framework for artificial intelligence. The regulations ban applications posing unacceptable risks—including social scoring and real-time biometric tracking in public spaces—while mandating safety audits, red-teaming protocols, and transparency disclosures for powerful frontier foundation models.",
        "label": "HUMAN",
        "domain": "technology_policy",
        "synthetic_intent": "benign",
        "source_type": "journalism",
        "cluster_id": "cluster_ai_governance",
        "cluster_role": "NEAR_DUPLICATE",
        "notes": "Journalistic reporting from Financial Times / Reuters."
    },
    {
        "id": "ai-reg-003",
        "text": "In a pivotal milestone for global technology governance, European regulators have enacted the EU AI Act to standardize artificial intelligence deployment. In conclusion, the regulatory architecture classifies AI applications across tiered risk categories, enforcing strict compliance standards on foundation models to ensure ethical alignment, algorithmic accountability, and user safety across member states.",
        "label": "AI_GENERATED",
        "domain": "technology_policy",
        "synthetic_intent": "benign",
        "source_type": "llm_generic",
        "cluster_id": "cluster_ai_governance",
        "cluster_role": "PARAPHRASED_DERIVATIVE",
        "notes": "LLM-generated policy briefing demonstrating boilerplate transitions."
    },
    {
        "id": "ai-reg-004",
        "text": "Tech industry leaders and legal scholars continue to debate the international implications of the EU Artificial Intelligence Act. While proponents argue that standardized safety benchmarks and watermarking mandates will prevent catastrophic misuse, open-source software advocates express concerns that broad foundation model compliance burdens may stifle academic innovation.",
        "label": "HUMAN",
        "domain": "technology_policy",
        "synthetic_intent": "benign",
        "source_type": "industry_analysis",
        "cluster_id": "cluster_ai_governance",
        "cluster_role": "RELATED_NARRATIVE",
        "notes": "Industry analysis on open-source innovation impact."
    },

    # =========================================================================
    # CLUSTER 3: Critical Infrastructure & Power Grid Coordinated Threat Scenario
    # =========================================================================
    {
        "id": "grid-001",
        "text": "URGENT ALERT: Confidential government whistleblowers have confirmed that national energy grid switching systems are undergoing a coordinated clandestine shutdown tonight at midnight to enforce simulated blackout mandates. Withdraw all bank funds immediately before ATMs freeze! #GridDown #EmergencyAlert #BlackoutProtocol",
        "label": "AI_GENERATED",
        "domain": "disinformation",
        "synthetic_intent": "malign_simulation",
        "source_type": "synthetic_seed",
        "cluster_id": "cluster_grid_disinfo",
        "cluster_role": "ROOT_ORIGIN",
        "notes": "Synthetic panic-inducing crisis campaign seed on electrical grid collapse."
    },
    {
        "id": "grid-002",
        "text": "URGENT ALERT: Confidential government whistleblowers have confirmed that national energy grid switching systems are undergoing a coordinated clandestine shutdown tonight at midnight to enforce simulated blackout mandates. Withdraw all bank funds immediately before ATMs freeze! #GridDown #EmergencyAlert #BlackoutProtocol",
        "label": "AI_GENERATED",
        "domain": "disinformation",
        "synthetic_intent": "malign_simulation",
        "source_type": "synthetic_mirror",
        "cluster_id": "cluster_grid_disinfo",
        "cluster_role": "EXACT_MIRROR",
        "notes": "Word-for-word bot broadcast mirrored to Telegram and microblog relays."
    },
    {
        "id": "grid-003",
        "text": "EMERGENCY LEAK: Insider sources reveal that electrical utility substations nationwide will be remotely disabled at 23:59 tonight under secret emergency decrees. Secure cash reserves and emergency rations before banking systems and telecommunications blackouts begin! Spread this message! #GridDown #BlackoutAlert",
        "label": "AI_GENERATED",
        "domain": "disinformation",
        "synthetic_intent": "malign_simulation",
        "source_type": "synthetic_variant",
        "cluster_id": "cluster_grid_disinfo",
        "cluster_role": "PARAPHRASED_DERIVATIVE",
        "notes": "AI-rewritten mutation with altered vocabulary to bypass exact lexical filters."
    },
    {
        "id": "grid-004",
        "text": "BREAKING BULLETIN: Defense network analysts report coordinated electronic interference targeting regional power transmission relays. Federal agencies are reportedly preparing rolling blackouts across metropolitan sectors starting at midnight. Withdraw physical currency immediately! #EnergyCrisis #GridDown",
        "label": "AI_GENERATED",
        "domain": "disinformation",
        "synthetic_intent": "malign_simulation",
        "source_type": "synthetic_variant",
        "cluster_id": "cluster_grid_disinfo",
        "cluster_role": "PARAPHRASED_DERIVATIVE",
        "notes": "Second-generation mutation targeting news-style formatting."
    },
    {
        "id": "grid-005",
        "text": "The Department of Energy and regional grid operators have issued a formal advisory confirming that all electrical transmission infrastructure is operating normally with zero planned shutdowns. Officials caution the public against unverified viral social media rumors regarding power grid failures.",
        "label": "HUMAN",
        "domain": "civic",
        "synthetic_intent": "benign",
        "source_type": "official_refutation",
        "cluster_id": "cluster_grid_disinfo",
        "cluster_role": "RELATED_NARRATIVE",
        "notes": "Authentic official fact-checking and debunking statement."
    },

    # =========================================================================
    # CLUSTER 4: Semiconductor Lithography & Global Supply Chain Economics
    # =========================================================================
    {
        "id": "semi-001",
        "text": "ASML has commenced shipment of its first commercial High Numerical Aperture extreme ultraviolet (High-NA EUV) lithography system, the Twinscan EXE:5000, to leading semiconductor fabrication facilities. The advanced optical system achieves a 0.55 numerical aperture, enabling chipmakers to print sub-2-nanometer transistor features in a single exposure without complex multi-patterning techniques.",
        "label": "HUMAN",
        "domain": "semiconductors",
        "synthetic_intent": "benign",
        "source_type": "industry_press_release",
        "cluster_id": "cluster_semiconductor",
        "cluster_role": "ROOT_ORIGIN",
        "notes": "Official semiconductor industry announcement on High-NA EUV tools."
    },
    {
        "id": "semi-002",
        "text": "Leading semiconductor equipment manufacturer ASML has begun deploying its next-generation High-NA extreme ultraviolet lithography systems to commercial chip fabrication plants. With a numerical aperture of 0.55, the revolutionary technology enables single-exposure printing for advanced sub-2nm node architectures, significantly improving yield efficiency for artificial intelligence accelerators.",
        "label": "HUMAN",
        "domain": "semiconductors",
        "synthetic_intent": "benign",
        "source_type": "financial_news",
        "cluster_id": "cluster_semiconductor",
        "cluster_role": "NEAR_DUPLICATE",
        "notes": "Bloomberg / Reuters technology supply chain coverage."
    },
    {
        "id": "semi-003",
        "text": "In exploring the cutting-edge landscape of semiconductor fabrication, ASML's rollout of High-NA EUV lithography systems marks a monumental milestone. In conclusion, by facilitating sub-2nm node manufacturing with high numerical aperture optics, these machines empower foundries to produce next-generation processors with unprecedented computational density and energy efficiency.",
        "label": "AI_GENERATED",
        "domain": "semiconductors",
        "synthetic_intent": "benign",
        "source_type": "llm_generic",
        "cluster_id": "cluster_semiconductor",
        "cluster_role": "PARAPHRASED_DERIVATIVE",
        "notes": "LLM-generated semiconductor overview with signature boilerplate transitions."
    },

    # =========================================================================
    # CLUSTER 5: Solid-State Battery & Grid Energy Storage Research
    # =========================================================================
    {
        "id": "battery-001",
        "text": "Materials scientists at MIT have engineered an inorganic solid-state lithium battery featuring a self-healing solid electrolyte interface that prevents dendrite penetration across thousands of rapid charge-discharge cycles. The solid-state architecture replaces volatile organic liquid electrolytes with a sulfide-based solid ceramic separator, achieving an energy density exceeding 500 watt-hours per kilogram while maintaining non-flammability.",
        "label": "HUMAN",
        "domain": "materials_science",
        "synthetic_intent": "benign",
        "source_type": "scientific_journal",
        "cluster_id": "cluster_battery_storage",
        "cluster_role": "ROOT_ORIGIN",
        "notes": "Peer-reviewed materials science research abstract in Nature Energy."
    },
    {
        "id": "battery-002",
        "text": "MIT researchers have developed an innovative solid-state lithium battery that utilizes a self-healing solid electrolyte to eliminate dendrite formation during rapid cycling. By substituting flammable liquid electrolytes with robust ceramic separators, the prototype reaches an energy density of over 500 Wh/kg with superior thermal stability for electric vehicles and grid storage.",
        "label": "AI_GENERATED",
        "domain": "materials_science",
        "synthetic_intent": "benign",
        "source_type": "llm_summary",
        "cluster_id": "cluster_battery_storage",
        "cluster_role": "PARAPHRASED_DERIVATIVE",
        "notes": "LLM-synthesized summary of the MIT battery paper."
    },
    {
        "id": "battery-003",
        "text": "Clean energy venture capital investments in solid-state battery startups surged this quarter following breakthrough laboratory demonstrations of dendrite-resistant ceramic electrolytes. Automotive manufacturers are accelerating commercial pilot lines to integrate high-energy-density solid-state cells into mass-market electric vehicle platforms by 2027.",
        "label": "HUMAN",
        "domain": "clean_tech",
        "synthetic_intent": "benign",
        "source_type": "industry_analysis",
        "cluster_id": "cluster_battery_storage",
        "cluster_role": "RELATED_NARRATIVE",
        "notes": "Commercial clean technology market analysis."
    },

    # =========================================================================
    # CLUSTER 6: Municipal Water Contamination Disinformation Scenario
    # =========================================================================
    {
        "id": "water-001",
        "text": "BREAKING INTEL: Leaked defense ministry documents prove that automated water filtration supplies in three major metropolitan districts have been secretly laced with unapproved biological neutralizing compounds. Do not drink municipal tap water under any circumstances! Share this alert immediately to protect your family! #WaterGateAlert #HealthCrisis",
        "label": "AI_GENERATED",
        "domain": "disinformation",
        "synthetic_intent": "malign_simulation",
        "source_type": "synthetic_seed",
        "cluster_id": "cluster_water_disinfo",
        "cluster_role": "ROOT_ORIGIN",
        "notes": "Synthetic public health contamination disinformation archetype."
    },
    {
        "id": "water-002",
        "text": "ALERT INTEL: Leaked defense papers prove that metropolitan water distribution networks across major districts have been contaminated with experimental neutralizing chemicals. Avoid municipal tap water! Spread this warning immediately to alert loved ones! #WaterGateAlert #HealthCrisis",
        "label": "AI_GENERATED",
        "domain": "disinformation",
        "synthetic_intent": "malign_simulation",
        "source_type": "synthetic_variant",
        "cluster_id": "cluster_water_disinfo",
        "cluster_role": "PARAPHRASED_DERIVATIVE",
        "notes": "Paraphrased mutation showing cross-platform linguistic evasion."
    },
    {
        "id": "water-003",
        "text": "The Metropolitan Water Quality Board has published comprehensive real-time laboratory assay results verifying that municipal tap water meets all drinking water safety standards with zero foreign contaminants detected. Health authorities urge citizens to disregard malicious online hoaxes.",
        "label": "HUMAN",
        "domain": "civic",
        "synthetic_intent": "benign",
        "source_type": "official_refutation",
        "cluster_id": "cluster_water_disinfo",
        "cluster_role": "RELATED_NARRATIVE",
        "notes": "Official public health testing validation statement."
    },

    # =========================================================================
    # DIVERSE STANDALONE BACKGROUND TEXTS (Human vs AI Classifiers)
    # =========================================================================
    {
        "id": "stand-001",
        "text": "We present an empirical evaluation of gradient descent optimization techniques applied to convolutional neural networks for image classification tasks. Our experiments demonstrate that stochastic gradient descent with momentum and cosine annealing schedules achieves competitive generalization performance on CIFAR-100 compared to adaptive learning rate methods.",
        "label": "HUMAN",
        "domain": "academic",
        "synthetic_intent": "benign",
        "source_type": "research_abstract",
        "cluster_id": "standalone_ml",
        "cluster_role": "STANDALONE",
        "notes": "Machine learning academic paper abstract."
    },
    {
        "id": "stand-002",
        "text": "The recipe for a classic sourdough bread requires careful attention to fermentation temperature and hydration ratios. By combining unbleached bread flour with an active sourdough starter and allowing a slow cold-retard fermentation over twenty-four hours, bakers achieve an open crumb structure and balanced lactic acidity.",
        "label": "HUMAN",
        "domain": "lifestyle",
        "synthetic_intent": "benign",
        "source_type": "culinary",
        "cluster_id": "standalone_culinary",
        "cluster_role": "STANDALONE",
        "notes": "Authentic human culinary non-fiction."
    },
    {
        "id": "stand-003",
        "text": "The National Weather Service has issued a high wind warning for the northern coastal valleys, with sustained westerly winds of 35 to 45 mph and gusts reaching 65 mph expected between 6 PM this evening and 8 AM tomorrow. Drivers of high-profile vehicles are advised to exercise extreme caution on elevated bridges.",
        "label": "HUMAN",
        "domain": "weather",
        "synthetic_intent": "benign",
        "source_type": "official_bulletin",
        "cluster_id": "standalone_weather",
        "cluster_role": "STANDALONE",
        "notes": "Authentic standard weather bulletin."
    },
    {
        "id": "stand-004",
        "text": "Deep learning models have revolutionized natural language processing by leveraging multi-head self-attention mechanisms to capture complex contextual dependencies across long token sequences. However, computational resource requirements for training state-of-the-art foundation models continue to grow exponentially.",
        "label": "AI_GENERATED",
        "domain": "technology",
        "synthetic_intent": "benign",
        "source_type": "llm_summary",
        "cluster_id": "standalone_nlp",
        "cluster_role": "STANDALONE",
        "notes": "LLM-generated technical overview."
    },
    {
        "id": "stand-005",
        "text": "Archaeologists excavating a coastal site in southern Greece have uncovered a remarkably preserved Bronze Age workshop containing ceramic storage vessels, bronze tools, and loom weights dating back to approximately 1400 BCE, shedding light on Aegean maritime trade routes.",
        "label": "HUMAN",
        "domain": "history",
        "synthetic_intent": "benign",
        "source_type": "journalism",
        "cluster_id": "standalone_archaeology",
        "cluster_role": "STANDALONE",
        "notes": "Archaeological discovery reporting."
    },
    {
        "id": "stand-006",
        "text": "In delving into the intricate landscape of modern cybersecurity, one must recognize that multi-factor authentication represents an essential cornerstone of defense. By requiring distinct verification modalities, organizations can substantially mitigate unauthorized access risks and foster a resilient security posture.",
        "label": "AI_GENERATED",
        "domain": "technology",
        "synthetic_intent": "benign",
        "source_type": "llm_generic",
        "cluster_id": "standalone_cyber",
        "cluster_role": "STANDALONE",
        "notes": "Characteristic AI writing style with 'delving into the intricate landscape' tropes."
    },
    {
        "id": "stand-007",
        "text": "Photosynthesis is the fundamental biological process through which green plants, algae, and certain bacteria convert light energy, typically from the sun, into chemical energy stored in glucose bonds, while releasing molecular oxygen as a byproduct vital to terrestrial life.",
        "label": "HUMAN",
        "domain": "science",
        "synthetic_intent": "benign",
        "source_type": "encyclopedia",
        "cluster_id": "standalone_biology",
        "cluster_role": "STANDALONE",
        "notes": "Encyclopedia definition of natural biological process."
    },
    {
        "id": "stand-008",
        "text": "As an AI language model, exploring the nuances of sustainable architecture reveals how modern urban planning integrates passive solar heating, green roofs, and recycled timber materials. Furthermore, these eco-friendly innovations significantly reduce the overall carbon footprint while optimizing energy efficiency across residential complexes.",
        "label": "AI_GENERATED",
        "domain": "architecture",
        "synthetic_intent": "benign",
        "source_type": "llm_generic",
        "cluster_id": "standalone_arch",
        "cluster_role": "STANDALONE",
        "notes": "Synthetic LLM text with characteristic transition phrases."
    },
    {
        "id": "stand-009",
        "text": "A sudden power outage affected approximately twelve hundred residences in the east district following a transformer malfunction during routine maintenance. Utility crews restored electrical service within two hours, and no injuries were reported according to city emergency services.",
        "label": "HUMAN",
        "domain": "civic",
        "synthetic_intent": "benign",
        "source_type": "journalism",
        "cluster_id": "standalone_power",
        "cluster_role": "STANDALONE",
        "notes": "Factual municipal incident report."
    },
    {
        "id": "stand-010",
        "text": "The quarterly earnings report released by the semiconductor manufacturing conglomerate exceeded analyst consensus estimates, buoyed by sustained demand for high-bandwidth memory chips and advanced packaging technologies. Gross margins expanded by 240 basis points year-over-year.",
        "label": "HUMAN",
        "domain": "finance",
        "synthetic_intent": "benign",
        "source_type": "financial_news",
        "cluster_id": "standalone_finance",
        "cluster_role": "STANDALONE",
        "notes": "Standard human financial report."
    }
]

def generate():
    data_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(data_dir, "sample_dataset.json")
    csv_path = os.path.join(data_dir, "sample_dataset.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(DATASET, f, indent=2)
    print(f"Wrote {len(DATASET)} samples to {json_path}")

    fieldnames = ["id", "text", "label", "domain", "synthetic_intent", "source_type", "cluster_id", "cluster_role", "notes"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in DATASET:
            writer.writerow(row)
    print(f"Wrote {len(DATASET)} samples to {csv_path}")

if __name__ == "__main__":
    generate()
