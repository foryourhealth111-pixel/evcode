export interface ProviderPolicySummary {
  profile: string;
  allowedProviderFamilies: string[];
  requiresExternalMcpForCoreClosure: boolean;
}

export interface AssistantProviderSummary {
  assistantName: "codex" | "claude" | "gemini";
  provider: string;
  baseUrl: string;
  model: string;
  enabled: boolean;
}

export function summarizePolicy(input: ProviderPolicySummary): ProviderPolicySummary {
  return { ...input };
}

export function summarizeAssistantProviders<T extends AssistantProviderSummary>(input: T[]): T[] {
  return input.map((item) => ({ ...item }));
}
