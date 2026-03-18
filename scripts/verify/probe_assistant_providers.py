from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / 'packages' / 'assistant-adapters' / 'python'))
sys.path.insert(0, str(REPO_ROOT / 'packages' / 'specialist-routing' / 'python'))

from evcode_assistant_adapters import invoke_specialist_json, resolve_assistant_provider_catalog  # type: ignore
from evcode_specialist_routing import load_routing_policy  # type: ignore


VALIDATED_COMPATIBILITY = {
    'api_surface': 'openai_style',
    'primary_wire_api': 'chat_completions',
    'secondary_wire_api_support': 'responses_tolerant',
    'validated_runtime_scope': 'validated_on_current_rightcodes_codex_claude_gemini_paths',
}


def load_assistant_policy(repo_root: Path, channel: str) -> dict[str, Any]:
    policy_name = f'assistant-policy.{channel}.json'
    return json.loads((repo_root / 'config' / policy_name).read_text(encoding='utf-8'))


def load_profile(repo_root: Path, channel: str) -> dict[str, Any]:
    return json.loads((repo_root / 'profiles' / channel / 'profile.json').read_text(encoding='utf-8'))


def build_probe_packet(assistant_name: str) -> dict[str, Any]:
    packet = {
        'specialist_name': assistant_name,
        'task_id': f'probe-{assistant_name}',
        'run_id': 'provider-probe',
        'repository_path_summary': f'repo={REPO_ROOT.name}',
        'file_scope': ['config/', 'docs/'],
        'task_goal': 'Return a compact governed compatibility advisory.',
        'allowed_authority_tier': 'advisory_only',
        'delegation_reason': 'provider_probe',
        'delegation_purpose': 'provider_probe',
        'task_risk': 'low',
        'evidence_mode': 'targeted',
        'guardrails': ['Return JSON only.'],
        'architecture_notes': ['Codex remains the final executor.'],
        'design_system_notes': [],
        'skill_capsule': {
            'capsule_id': f'probe-{assistant_name}',
            'compiler': 'vco_skill_compiler',
            'version': '2026-03-18',
            'classes': ['provider_probe', 'governed_advisory'],
            'guidance': ['Return compact diagnostic JSON only.'],
            'prohibited_actions': ['never claim completion'],
            'output_contract': [
                'summary',
                'assumptions',
                'proposed_actions',
                'files_touched_or_proposed',
                'confidence_level',
                'unresolved_risks',
                'recommended_next_actor',
                'capability_requests',
                'receipt_refs',
            ],
        },
        'allowed_capabilities': {
            'mode': 'proxy_mediated',
            'direct_read_only_allowlist': [],
            'proxy_allowlist': [],
            'mutation_allowlist': [],
            'denied': ['filesystem_write', 'shell_execution'],
        },
        'required_receipts': ['routing_receipt', 'specialist_result_receipt'],
        'authoritative_context_refs': ['config/assistant-policy', 'config/specialist-routing'],
        'memory_policy': {
            'owner': 'vco_artifacts',
            'specialist_local_memory': 'ephemeral',
            'authoritative_sources': ['assistant_policy_snapshot', 'specialist_routing_receipt'],
        },
    }
    if assistant_name == 'gemini':
        packet.update(
            {
                'expected_output_type': 'visual_plan',
                'task_domain': 'frontend_visual',
                'exploration_mode': 'packetized',
                'mission_brief': 'Return a minimal visual advisory JSON object.',
            }
        )
    elif assistant_name == 'claude':
        packet.update(
            {
                'expected_output_type': 'plan_artifact',
                'task_domain': 'planning',
                'exploration_mode': 'autonomous',
                'mission_brief': 'Return a minimal planning advisory JSON object.',
            }
        )
    else:
        packet.update(
            {
                'expected_output_type': 'execution_plan',
                'task_domain': 'general_engineering',
                'exploration_mode': 'packetized',
                'mission_brief': 'Return a minimal engineering advisory JSON object.',
            }
        )
    return packet


def summarize_non_live_status(assistant_name: str, provider_spec: dict[str, Any], channel: str) -> dict[str, Any]:
    if not provider_spec.get('enabled'):
        status = 'policy_disabled'
        reason = provider_spec.get('suppression_reason') or 'assistant disabled by policy'
    elif not provider_spec.get('api_key_present'):
        status = 'missing_api_key'
        reason = f"missing {provider_spec.get('api_key_env_var') or 'provider api key'}"
    elif assistant_name != 'codex' and channel == 'benchmark':
        status = 'policy_suppressed_in_benchmark'
        reason = provider_spec.get('suppression_reason') or 'assistant suppressed in benchmark policy'
    elif assistant_name != 'codex' and not provider_spec.get('live_opt_in_enabled'):
        status = 'live_opt_in_disabled'
        reason = f"set {provider_spec.get('live_opt_in_env')} to enable live specialist probing"
    else:
        status = 'ready_for_live_probe'
        reason = 'configuration is sufficient for a live probe'
    return {
        'assistant_name': assistant_name,
        'status': status,
        'reason': reason,
        'wire_api': provider_spec.get('wire_api'),
        'base_url': provider_spec.get('base_url'),
        'model': provider_spec.get('model'),
        'enabled': provider_spec.get('enabled'),
        'authority_tier': provider_spec.get('authority_tier'),
        'capability_mode': provider_spec.get('capability_mode'),
        'required_skill_capsules': provider_spec.get('required_skill_capsules', []),
        'api_key_present': provider_spec.get('api_key_present'),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Probe configured assistant providers.')
    parser.add_argument('--repo-root', default=str(REPO_ROOT))
    parser.add_argument('--channel', choices=('standard', 'benchmark'), default='standard')
    parser.add_argument('--timeout-sec', type=int, default=45)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    profile = load_profile(repo_root, args.channel)
    policy = load_assistant_policy(repo_root, args.channel)
    routing_policy = load_routing_policy(repo_root)
    catalog = resolve_assistant_provider_catalog(policy, env=os.environ)

    results: list[dict[str, Any]] = []
    for assistant_name, provider_spec in catalog.items():
        summary = summarize_non_live_status(assistant_name, provider_spec, args.channel)
        if args.live and summary['status'] == 'ready_for_live_probe':
            try:
                live_provider_spec = dict(provider_spec)
                live_provider_spec['live_available'] = True
                payload = invoke_specialist_json(build_probe_packet(assistant_name), live_provider_spec, env=os.environ, timeout_sec=args.timeout_sec)
                summary.update(
                    {
                        'status': 'live_compatible',
                        'reason': 'live probe completed',
                        'response_keys': sorted(payload.keys()),
                        'recommended_next_actor': str(payload.get('recommended_next_actor', '')).lower() or None,
                    }
                )
            except Exception as exc:  # pragma: no cover - live network path
                summary.update(
                    {
                        'status': 'live_probe_failed',
                        'reason': str(exc),
                    }
                )
        results.append(summary)

    payload = {
        'channel': args.channel,
        'baseline_family': profile.get('baseline_family'),
        'baseline_families_config': profile.get('baseline_families_config'),
        'live_probe_requested': args.live,
        'compatibility_surface': VALIDATED_COMPATIBILITY,
        'governance_surface': {
            'persistent_memory_owner': policy.get('persistent_memory_owner'),
            'capability_classes': list((routing_policy.get('capability_policy', {}).get('classes') or {}).keys()),
        },
        'results': results,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for item in results:
            print(f"{item['assistant_name']}: {item['status']} | {item['model']} | {item['reason']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
