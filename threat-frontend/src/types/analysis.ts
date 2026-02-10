/**
 * TypeScript interfaces for the Threat Modeling AI API.
 */

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type AnalysisStatus = 'EM_ABERTO' | 'PROCESSANDO' | 'ANALISADO' | 'FALHOU';

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

// API responses for threat-modeling-api
export interface AnalysisCreateResponse {
  id: string;
  code: string;
  status: AnalysisStatus;
  created_at: string;
  image_url?: string;
}

export interface AnalysisListItem {
  id: string;
  code: string;
  status: AnalysisStatus;
  created_at: string;
  image_url?: string;
  risk_level?: RiskLevel;
  risk_score?: number;
  threat_count?: number;
}

export interface AnalysisDetailResponse {
  id: string;
  code: string;
  status: AnalysisStatus;
  created_at: string;
  started_at?: string;
  finished_at?: string;
  image_url?: string;
  processing_logs?: string;
  error_message?: string;
  result?: AnalysisResponse;
}

export interface NotificationItem {
  id: string;
  analysis_id: string;
  title: string;
  message: string;
  is_read: boolean;
  link: string;
  created_at: string;
}

export interface NotificationsUnreadResponse {
  unread_count: number;
  notifications: NotificationItem[];
}
