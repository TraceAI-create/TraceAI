"""Audit report generator for compliance and verification."""

from datetime import datetime, timezone
import json
from typing import Any
import uuid
from sqlalchemy.orm import Session

from app.db.models import Decision, ReplayRun
from app.services.decision_service import verify_decision_integrity


class AuditReporter:
    """Generates JSON and Markdown compliance audit reports for decisions.

    Gathers cryptographic verification results, timeline events, evidence items,
    replay simulations, and human reviewer notes into a clear summary report.
    """

    def __init__(self, db: Session):
        self.db = db

    def generate_json_report(self, decision_id: uuid.UUID) -> dict[str, Any]:
        """Compile complete audit data for a decision into a dictionary."""
        decision = self.db.get(Decision, decision_id)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")

        integrity = verify_decision_integrity(self.db, decision_id)

        # Build chronological list of audit events
        events_timeline = []
        for ev in sorted(decision.events, key=lambda x: x.sequence_number):
            events_timeline.append({
                "sequence": ev.sequence_number,
                "event_type": ev.event_type,
                "timestamp": ev.timestamp.isoformat(),
                "event_hash": ev.event_hash,
                "previous_hash": ev.previous_hash,
                "payload": ev.payload,
            })

        # Build list of linked evidence items
        evidence_inventory = []
        for link in decision.evidence_links:
            ev = link.evidence
            if ev:
                evidence_inventory.append({
                    "evidence_id": str(ev.id),
                    "type": ev.type,
                    "content_hash": ev.content_hash,
                    "storage_uri": ev.storage_uri,
                    "role": link.role,
                    "created_at": ev.created_at.isoformat(),
                })

        # Build list of human review actions
        reviews_log = []
        for rev in decision.review_actions:
            reviews_log.append({
                "review_id": str(rev.id),
                "reviewer_id": rev.reviewer_id,
                "action": rev.action,
                "comments": rev.comments,
                "timestamp": rev.created_at.isoformat(),
            })

        # Build list of replay verification runs
        replays_summary = []
        for r in decision.replays:
            replays_summary.append({
                "replay_id": str(r.id),
                "status": r.status,
                "replay_mode": r.replay_mode,
                "similarity_score": r.similarity_score,
                "diff_summary": r.diff_summary,
                "timestamp": r.created_at.isoformat(),
            })

        return {
            "report_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "report_format_version": "1.0",
                "system": "TraceAI Decision Audit System",
            },
            "decision": {
                "id": str(decision.id),
                "agent_id": decision.agent_id,
                "agent_version": decision.agent_version,
                "status": decision.status,
                "created_at": decision.created_at.isoformat(),
                "input_data": decision.input_data,
                "root_hash": decision.root_hash,
            },
            "cryptographic_verification": integrity,
            "audit_events_timeline": events_timeline,
            "evidence_inventory": evidence_inventory,
            "human_reviews": reviews_log,
            "replay_verification": replays_summary,
        }

    def generate_markdown_report(self, decision_id: uuid.UUID) -> str:
        """Format the decision audit report into a readable Markdown document."""
        report = self.generate_json_report(decision_id)
        dec = report["decision"]
        integ = report["cryptographic_verification"]

        md = []
        md.append(f"# TraceAI Compliance & Audit Report")
        md.append(f"**Generated:** {report['report_metadata']['generated_at']}  ")
        md.append(f"**System:** TraceAI Audit Platform  ")
        md.append("")
        md.append("---")
        md.append("## 1. Executive Summary")
        md.append(f"| Property | Value |")
        md.append(f"| :--- | :--- |")
        md.append(f"| **Decision ID** | `{dec['id']}` |")
        md.append(f"| **Agent ID** | `{dec['agent_id']}` (v{dec['agent_version']}) |")
        md.append(f"| **Status** | `{dec['status'].upper()}` |")
        md.append(f"| **Created At** | {dec['created_at']} |")
        md.append(f"| **Root Hash** | `{dec['root_hash']}` |")
        md.append("")

        md.append("## 2. Cryptographic Integrity Proof")
        valid_badge = "VALID (Tamper-Free)" if integ.get("valid") else "COMPROMISED"
        md.append(f"- **Chain Status:** [{valid_badge}]")
        md.append(f"- **Total Events Verified:** {integ.get('event_count', 0)}")
        md.append(f"- **Root Hash Anchored:** `{integ.get('root_hash', 'N/A')}`")
        if not integ.get("valid"):
            md.append(f"- **Integrity Failure Reason:** {integ.get('reason')}")
        md.append("")

        md.append("## 3. Evidence Store Inventory")
        if report["evidence_inventory"]:
            md.append("| Evidence ID | Type | Role | Content Hash (SHA-256) |")
            md.append("| :--- | :--- | :--- | :--- |")
            for ev in report["evidence_inventory"]:
                md.append(f"| `{ev['evidence_id'][:8]}...` | {ev['type']} | {ev['role']} | `{ev['content_hash'][:16]}...` |")
        else:
            md.append("*No evidence artifacts linked to this decision.*")
        md.append("")

        md.append("## 4. Chronological Audit Timeline")
        md.append("| Seq | Event Type | Timestamp | Hash (SHA-256) | Details |")
        md.append("| :--- | :--- | :--- | :--- |")
        for ev in report["audit_events_timeline"]:
            summary_str = json.dumps(ev["payload"], default=str)
            if len(summary_str) > 60:
                summary_str = summary_str[:57] + "..."
            md.append(f"| {ev['sequence']} | `{ev['event_type']}` | {ev['timestamp'][11:19]} | `{ev['event_hash'][:12]}...` | `{summary_str}` |")
        md.append("")

        md.append("## 5. Replay & Reproducibility Verification")
        if report["replay_verification"]:
            for r in report["replay_verification"]:
                md.append(f"### Replay `{r['replay_id'][:8]}` ({r['replay_mode'].upper()} Mode)")
                status_indicator = "[MATCHED]" if r["status"] == "matched" else f"[{r['status'].upper()}]"
                md.append(f"- **Result:** {status_indicator} (Similarity: {round(r['similarity_score'] * 100, 1)}%)")
                diff = r.get("diff_summary", {})
                if diff.get("summary"):
                    md.append(f"- **Summary:** {diff['summary']}")
                md.append("")
        else:
            md.append("*No replay simulations executed for this decision.*")
        md.append("")

        md.append("## 6. Human Review & Compliance Sign-Offs")
        if report["human_reviews"]:
            md.append("| Reviewer ID | Action | Timestamp | Comments |")
            md.append("| :--- | :--- | :--- | :--- |")
            for rev in report["human_reviews"]:
                md.append(f"| `{rev['reviewer_id']}` | **{rev['action'].upper()}** | {rev['timestamp']} | {rev['comments'] or 'N/A'} |")
        else:
            md.append("*Decision is pending auditor review.*")
        md.append("")

        return "\n".join(md)
