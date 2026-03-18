export type ProviderFamily = "embedded" | "api" | "mcp";
export type AssistantAuthorityTier = "advisory_only" | "isolated_candidate_apply" | "final_executor";

export interface CapabilityPolicy {
  profile: string;
  allowedProviderFamilies: ProviderFamily[];
  requiresExternalMcpForCoreClosure: boolean;
}

export interface AssistantCapabilityPolicy {
  assistantName: "codex" | "claude" | "gemini";
  enabled: boolean;
  authorityTier: AssistantAuthorityTier;
}

export function isProviderAllowed(policy: CapabilityPolicy, provider: ProviderFamily): boolean {
  return policy.allowedProviderFamilies.includes(provider);
}

export function canDelegateAssistant(policy: AssistantCapabilityPolicy): boolean {
  return policy.enabled && policy.authorityTier !== "final_executor";
}
