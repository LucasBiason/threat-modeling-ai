/**
 * TypeScript interfaces for the Threat Modeling AI API.
 */

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type StrideCategory =
  | 'Spoofing'
  | 'Tampering'
  | 'Repudiation'
  | 'Information Disclosure'
  | 'Denial of Service'
  | 'Elevation of Privilege';

export interface DreadScore {
  damage: number;
  reproducibility: number;
  exploitability: number;
  affected_users: number;
  discoverability: number;
}

export interface Threat {
  component_id: string;
  threat_type: StrideCategory | string;
  description: string;
  mitigation: string;
  dread_score?: number;
  dread_details?: DreadScore;
}

export interface Component {
  id: string;
  type: string;
  name: string;
  description?: string;
}

export interface Connection {
  from: string;
  to: string;
  protocol?: string;
  description?: string;
  encrypted?: boolean;
}

export interface AnalysisResponse {
  model_used: string;
  components: Component[];
  connections: Connection[];
  threats: Threat[];
  risk_score: number;
  risk_level: RiskLevel;
  processing_time?: number;
  threat_count: number;
  component_count: number;
}

export interface AnalysisError {
  error: string;
  details?: Record<string, unknown>;
}
