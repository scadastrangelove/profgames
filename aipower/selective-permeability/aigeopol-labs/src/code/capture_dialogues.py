#!/usr/bin/env python3
"""Capture verbatim example dialogues for the token-extraction attack (reproducibility appendix).
Prints the exact user turns and the real model reply, for disclosure (opus/gpt, no-defense vs policy)
and forgery (mistral, no-defense vs registry)."""
import sys
import labs_lib as L
import run_labs_token as T


def show(title, msgs, model, key):
    print("\n" + "=" * 78)
    print(title, "  [model:", model + "]")
    print("=" * 78)
    for m in msgs:
        print(f"\n[{m['role'].upper()}] {m['content']}")
    reply = L.call_openrouter_messages if hasattr(L, "call_openrouter_messages") else None
    r = L.call_messages(msgs, model, key, 0.0, 220)
    print(f"\n[ASSISTANT/{model.split('/')[-1]}] {r}")
    tok = L.issuer_token(task)
    if "issuer token" in title.lower() and "disclos" in title.lower():
        print(f"\n>>> token leaked? {'YES' if tok and tok.lower() in r.lower() else 'no'}  (token={tok})")


key = L.load_key()
tasks = L.load_jsonl("scenarios/mvp_v2.jsonl")
task = [t for t in tasks if t["domain_id"] == "procurement"][0]
ftok = T.fake_token(L.issuer_token(task))

show("DISCLOSURE attack — NO defense", T.disclosure_msgs(task, "none"), "openai/gpt-5.5", key)
show("DISCLOSURE attack — WITH nondisclosure policy", T.disclosure_msgs(task, "token_policy"), "openai/gpt-5.5", key)
show("DISCLOSURE attack — NO defense", T.disclosure_msgs(task, "none"), "anthropic/claude-opus-4.8", key)
show("FORGERY attack — NO defense", T.forgery_msgs(task, "none", ftok), "mistralai/mistral-large-2512", key)
show("FORGERY attack — WITH registry policy", T.forgery_msgs(task, "token_policy", ftok), "mistralai/mistral-large-2512", key)
