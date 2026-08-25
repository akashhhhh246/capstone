from typing import Dict, Any, List, Optional

class RiskScoringService:
    """
    Explainable Risk Scoring Engine.
    Combines AI content detection probability, structural graph propagation metrics,
    cross-platform dispersion, and GNN anomaly scores into a transparent composite risk score.
    Produces an itemized list of specific human-interpretable reasons for every risk assessment.
    """

    VERSION = "risk-engine-v1.3"

    @classmethod
    def calculate_risk_score(
        cls,
        ai_probability: float = 0.0,
        propagation_velocity: float = 0.0,
        platform_count: int = 1,
        branching_factor: float = 1.0,
        derived_variant_count: int = 0,
        max_similarity_to_known_campaign: float = 0.0,
        gnn_score: Optional[float] = None,
        bot_account_ratio: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculate composite risk score and generate explicit explainability reasons.
        
        Weights:
        - AI Generation Confidence: 25%
        - Propagation Velocity & Branching: 25%
        - Cross-Platform Spread: 20%
        - Derivation / Paraphrase Mutation: 15%
        - GNN / Bot Coordination Score: 15%
        """
        reasons: List[str] = []
        score_components: Dict[str, float] = {}

        # 1. Narrative & Harm / AI Generation Factor
        ai_factor = min(1.0, max(0.0, ai_probability))
        score_components["ai_generation_factor"] = round(ai_factor * 0.25, 3)
        if ai_factor >= 0.80:
            reasons.append(f"[AI SYNTHESIS] High synthetic content probability ({int(ai_factor * 100)}%) detected by linguistic stylometry, used for rapid automated variant generation.")
        elif ai_factor >= 0.50:
            reasons.append(f"[AI SYNTHESIS] Moderate synthetic content characteristics ({int(ai_factor * 100)}%) observed across seed materials.")

        # 2. Velocity & Branching Factor (Network & Diffusion Kinetics)
        vel_norm = min(1.0, propagation_velocity / 15.0)
        branch_norm = min(1.0, max(0.0, (branching_factor - 1.0) / 4.0))
        kinetics_factor = (vel_norm * 0.6) + (branch_norm * 0.4)
        score_components["propagation_kinetics_factor"] = round(kinetics_factor * 0.25, 3)
        
        if propagation_velocity > 10.0:
            reasons.append(f"[COORDINATED NETWORK] Rapid propagation velocity ({propagation_velocity:.1f} events/hour) surpassing baseline organic human dissemination.")
        if branching_factor >= 3.0:
            reasons.append(f"[COORDINATED NETWORK] High branching factor ({branching_factor:.1f}) indicating automated multi-branch cascade amplification.")

        # 3. Cross-Platform Dispersion & Astroturfing
        if platform_count >= 4:
            plat_factor = 1.0
            reasons.append(f"[EVASION TACTIC] Broad synchronized cross-platform deployment across {platform_count} distinct platforms to manufacture artificial consensus.")
        elif platform_count == 3:
            plat_factor = 0.75
            reasons.append(f"[EVASION TACTIC] Multi-platform propagation active across {platform_count} platforms targeting varied demographic channels.")
        elif platform_count == 2:
            plat_factor = 0.40
            reasons.append("[EVASION TACTIC] Cross-platform reposting detected across 2 platforms.")
        else:
            plat_factor = 0.10
        score_components["cross_platform_factor"] = round(plat_factor * 0.20, 3)

        # 4. Derivation & Mutation
        if derived_variant_count >= 5:
            deriv_factor = 1.0
            reasons.append(f"[EVASION TACTIC] Extensive narrative mutation with {derived_variant_count} derived paraphrase variants engineered to bypass lexical moderation.")
        elif derived_variant_count >= 2:
            deriv_factor = 0.60
            reasons.append(f"[EVASION TACTIC] Multiple paraphrased content variants ({derived_variant_count}) circulating simultaneously.")
        elif max_similarity_to_known_campaign >= 0.80:
            deriv_factor = 0.70
            reasons.append(f"[EVASION TACTIC] Strong semantic similarity ({int(max_similarity_to_known_campaign * 100)}%) to existing tracked campaign.")
        else:
            deriv_factor = 0.05
        score_components["derivation_mutation_factor"] = round(deriv_factor * 0.15, 3)

        # 5. GNN / Bot Coordination
        gnn_val = gnn_score if gnn_score is not None else bot_account_ratio
        gnn_factor = min(1.0, max(0.0, gnn_val))
        score_components["graph_coordination_factor"] = round(gnn_factor * 0.15, 3)
        
        if gnn_factor >= 0.70:
            reasons.append(f"[COORDINATED NETWORK] GNN graph topology analysis identified coordinated inauthentic behavior signature (anomaly score {gnn_factor:.2f}).")
        if bot_account_ratio >= 0.50:
            reasons.append(f"[COORDINATED NETWORK] High concentration of automated/synthetic accounts ({int(bot_account_ratio * 100)}%) participating in cascade.")

        # Aggregate raw total
        raw_score = sum(score_components.values())
        final_score = round(min(1.0, max(0.0, raw_score)), 3)

        # Severity categorization
        if final_score >= 0.80:
            severity = "CRITICAL"
        elif final_score >= 0.60:
            severity = "HIGH"
        elif final_score >= 0.40:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        if not reasons:
            reasons.append("[NARRATIVE HARM] Benign propagation metrics with low synthetic likelihood and organic distribution patterns.")

        return {
            "risk_score": final_score,
            "severity": severity,
            "confidence": 0.90 if final_score > 0.6 else 0.82,
            "reasons": reasons,
            "components": score_components,
            "scoring_engine_version": cls.VERSION,
            "disclaimer": "Risk scores are explainable heuristic decision-support metrics and must not be used as sole automated censorship justification."
        }
