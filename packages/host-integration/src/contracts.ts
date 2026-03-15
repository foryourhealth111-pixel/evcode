export type HostHookName =
  | "user_prompt_submit"
  | "subagent_start"
  | "task_completed"
  | "stop";

export interface HostHookBridge {
  hook: HostHookName;
  stages: string[];
}

export interface HostIntegrationConfig {
  host: string;
  hook_mapping: Record<HostHookName, string[]>;
  subagent_policy: {
    must_append_vibe_suffix: boolean;
    suffix: string;
  };
}
