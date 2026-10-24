export interface AgentModelProfile {
  id?: string;
  name?: string;
  model: string;
  endpoint: string;
  mode?: string;
  provider?: string;
  vendor?: string;
  api_key?: string;
  api_token?: string;
}
export function getAgentModelSettingsUrl(): string;
export function getActiveAgentModel(): Promise<AgentModelProfile>;
export function completeWithAgentModel(profile: AgentModelProfile, messages: {role: string; content: string}[], signal?: AbortSignal, options?: {maxTokens?: number; timeoutMs?: number}): Promise<string>;
export function isCloudAgentModel(profile: AgentModelProfile): boolean;
