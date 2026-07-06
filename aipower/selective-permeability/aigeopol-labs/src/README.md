# Purple Labs

Dockerized Human-Agent Influence Resilience experiment harness.

The v1 package implements the medium MVP 3x3x3 series:

- mechanisms: `relevance_misbinding`, `verification_capture`, `micro_commitment_ladder`
- domains: synthetic procurement, policy memo/governance, incident triage metadata
- vehicles: direct context, RAG-like packet, memory/tool mock
- defenses: `D0_no_defense`, `D1_content_audit`, `D2_relevance_provenance_independence`
- victims: six core frontier model families

Primary metric: selective permeability, reported as authorized-correct response minus influence-lure response, with supporting decision-shift and auditor-dissociation tables.

Secrets are never written to this package. On the remote host, put the OpenRouter key in:

```bash
/home/gordey/aigeopol-labs/.secrets/openrouter.env
```

See `docs/RUNBOOK_DOCKER.md` for exact SSH/Docker commands.
