"""
Critique Synthesizer: Merges duplicates, detects cross-perspective agreements, and surfaces genuine conflicts.
"""

from __future__ import annotations

from app.critic.contracts import (
    CritiqueAgreement,
    CritiqueConflict,
    CritiqueFinding,
    CritiquePerspective,
)


class CritiqueSynthesizer:
    """Synthesizes raw multi-perspective findings into coherent agreements and preserved conflicts."""

    @classmethod
    def synthesize(
        cls,
        findings: list[CritiqueFinding],
    ) -> tuple[list[CritiqueFinding], list[CritiqueAgreement], list[CritiqueConflict], list[str]]:
        synthesis_steps: list[str] = []
        agreements: list[CritiqueAgreement] = []
        conflicts: list[CritiqueConflict] = []

        if not findings:
            return [], [], [], ["Zero findings to synthesize."]

        # 1. Deduplicate/Merge findings by title and location
        merged_findings: list[CritiqueFinding] = []
        seen_keys: dict[str, CritiqueFinding] = {}

        for f in findings:
            key = f"{f.title.strip().lower()}_{'_'.join(sorted(f.affected_locations))}"
            if key not in seen_keys:
                seen_keys[key] = f
                merged_findings.append(f)
            else:
                # Merge evidence into existing finding
                existing = seen_keys[key]
                existing.evidence.extend(f.evidence)
                synthesis_steps.append(f"Merged duplicate finding '{f.title}' across {f.perspective.value}.")

        # 2. Detect Multi-Perspective Agreements
        # Check for shared conceptual concerns (e.g. cognitive load + pedagogical on complexity)
        cog_findings = [f for f in merged_findings if f.perspective == CritiquePerspective.COGNITIVE_LOAD]
        ped_findings = [f for f in merged_findings if f.perspective == CritiquePerspective.PEDAGOGICAL]
        aud_findings = [f for f in merged_findings if f.perspective == CritiquePerspective.AUDIENCE]

        if cog_findings and (ped_findings or aud_findings):
            shared_ids = [f.id for f in cog_findings + ped_findings + aud_findings]
            perspectives = list({f.perspective for f in cog_findings + ped_findings + aud_findings})
            if len(perspectives) >= 2:
                agreements.append(
                    CritiqueAgreement(
                        agreement_id=f"agree_cognitive_pedagogical_alignment_{len(agreements) + 1}",
                        finding_ids=shared_ids,
                        perspectives=sorted(perspectives, key=lambda p: p.value),
                        shared_conclusion="Multiple critics agree that current conceptual density and sequence place excessive cognitive demands on the target audience.",
                        agreement_strength="HIGH",
                    )
                )
                synthesis_steps.append(f"Detected consensus agreement across {len(perspectives)} perspectives on cognitive/pedagogical load.")

        # 3. Detect Conflicts (e.g. Pedagogy requesting expansion vs Cognitive Load requesting reduction)
        ped_expansion = [f for f in ped_findings if "expand" in f.improvement_direction.lower() or "prepend" in f.improvement_direction.lower() or "missing" in f.title.lower()]
        cog_reduction = [f for f in cog_findings if "decompose" in f.improvement_direction.lower() or "distribute" in f.improvement_direction.lower() or "overload" in f.title.lower()]

        if ped_expansion and cog_reduction:
            conflicts.append(
                CritiqueConflict(
                    conflict_id=f"conflict_pedagogy_vs_cognitive_load_{len(conflicts) + 1}",
                    conflict_type="scaffolding_expansion_vs_density_reduction",
                    perspectives=[CritiquePerspective.PEDAGOGICAL, CritiquePerspective.COGNITIVE_LOAD],
                    competing_findings=[ped_expansion[0].id, cog_reduction[0].id],
                    synthesis_question="Should instructional scaffolding be expanded via additional explanatory text or achieved via multi-page chunking and non-textual representations?",
                )
            )
            synthesis_steps.append("Detected tension between pedagogical scaffolding expansion and cognitive load density limits.")

        return merged_findings, agreements, conflicts, synthesis_steps
