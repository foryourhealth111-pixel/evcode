export interface ProviderPolicySummary {
  profile: string;
  allowedProviderFamilies: string[];
  requiresExternalMcpForCoreClosure: boolean;
}

export function summarizePolicy(input: ProviderPolicySummary): ProviderPolicySummary {
  return { ...input };
}
