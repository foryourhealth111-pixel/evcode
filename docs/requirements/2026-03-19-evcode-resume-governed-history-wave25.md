# EvCode Resume Governed History Wave25

Date: 2026-03-19
Workspace: `/home/lqf/table/table3`

## Goal

Fix `evcode resume` so it restores EvCode-governed session history instead of only passing through to the underlying host CLI.

## Problem Statement

EvCode stores governed runtime history under `outputs/runtime/vibe-sessions/<run-id>/...`, but the current `resume` behavior is host passthrough. As a result, users invoking `evcode resume` do not see EvCode actor-board history, specialist visibility, or governed receipts.

## Acceptance Criteria

- `evcode resume` without a run id restores the latest EvCode-governed session from the selected artifacts root.
- `evcode resume <run-id>` restores the specified EvCode-governed session.
- Restored output uses the same EvCode trace rendering surface as `evcode trace`.
- If no governed session exists, EvCode returns a clear error instead of silently pretending there is no history.
- Host-native passthrough remains available through an explicit path and is not removed accidentally.
- Existing governed artifacts, requirement freeze, verification evidence, and cleanup behavior remain intact.
