export type RuntimeMode = "interactive_governed" | "benchmark_autonomous";

export interface WorkspaceState {
  workspacePath: string;
  hasRequirementDoc: boolean;
  hasExecutionPlan: boolean;
}

export interface GovernedTurnDecision {
  mode: RuntimeMode;
  stageOrder: string[];
  attachHiddenContext: boolean;
}

export interface SpecialistDelegationDecision {
  finalExecutor: "codex";
  routeKind: string;
  requestedDelegates: string[];
}

export const FIXED_STAGE_ORDER = [
  "skeleton_check",
  "deep_interview",
  "requirement_doc",
  "xl_plan",
  "plan_execute",
  "phase_cleanup"
];

export function resolveGovernedTurnDecision(mode: RuntimeMode): GovernedTurnDecision {
  return {
    mode,
    stageOrder: [...FIXED_STAGE_ORDER],
    attachHiddenContext: true
  };
}

export function resolveGovernedSpecialistDecision(requestedDelegates: string[]): SpecialistDelegationDecision {
  return {
    finalExecutor: "codex",
    routeKind: requestedDelegates.length > 0 ? "codex_with_specialists" : "codex_only",
    requestedDelegates: [...requestedDelegates]
  };
}
