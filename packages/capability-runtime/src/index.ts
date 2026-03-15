export type ProviderFamily = "embedded" | "api" | "mcp";

export interface CapabilityPolicy {
  profile: string;
  allowedProviderFamilies: ProviderFamily[];
  requiresExternalMcpForCoreClosure: boolean;
}

export function isProviderAllowed(policy: CapabilityPolicy, provider: ProviderFamily): boolean {
  return policy.allowedProviderFamilies.includes(provider);
}
