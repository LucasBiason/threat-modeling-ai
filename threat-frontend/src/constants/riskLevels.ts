/**
 * Risk level configuration for styling and display.
 */

import type { RiskLevel } from '../types/analysis';

export interface RiskLevelConfig {
  label: string;
  bgColor: string;
  textColor: string;
  borderColor: string;
  description: string;
}

export const RISK_LEVEL_CONFIG: Record<RiskLevel, RiskLevelConfig> = {
  LOW: {
    label: 'Low Risk',
    bgColor: 'bg-yellow-900/50',
    textColor: 'text-yellow-300',
    borderColor: 'border-yellow-500/50',
    description: 'Minimal security concerns identified',
  },
  MEDIUM: {
    label: 'Medium Risk',
    bgColor: 'bg-orange-900/50',
    textColor: 'text-orange-300',
    borderColor: 'border-orange-500/50',
    description: 'Moderate security concerns that should be addressed',
  },
  HIGH: {
    label: 'High Risk',
    bgColor: 'bg-red-900/50',
    textColor: 'text-red-300',
    borderColor: 'border-red-500/50',
    description: 'Significant security risks requiring prompt attention',
  },
  CRITICAL: {
    label: 'Critical Risk',
    bgColor: 'bg-red-900/60',
    textColor: 'text-red-200',
    borderColor: 'border-red-500/60',
    description: 'Severe security vulnerabilities requiring immediate action',
  },
};

export const STRIDE_CATEGORIES = [
  'Spoofing',
  'Tampering',
  'Repudiation',
  'Information Disclosure',
  'Denial of Service',
  'Elevation of Privilege',
] as const;

export const STRIDE_DESCRIPTIONS: Record<string, string> = {
  Spoofing: 'Pretending to be someone or something else',
  Tampering: 'Modifying data or code without authorization',
  Repudiation: 'Denying having performed an action',
  'Information Disclosure': 'Exposing information to unauthorized parties',
  'Denial of Service': 'Making a system unavailable',
  'Elevation of Privilege': 'Gaining unauthorized access or capabilities',
};

export function getDreadScoreColor(score: number): string {
  if (score < 3) return 'text-green-400';
  if (score < 6) return 'text-yellow-400';
  if (score < 8) return 'text-orange-400';
  return 'text-red-400';
}
