import { ChevronDown, ChevronRight } from 'lucide-react';
import type { Threat } from '../types/analysis';
import { getDreadScoreColor, STRIDE_DESCRIPTIONS } from '../constants/riskLevels';

interface ThreatCardProps {
  threat: Threat;
  index: number;
  expanded: boolean;
  onToggle: () => void;
}

function getSeverityFromScore(score: number): 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' {
  if (score >= 8) return 'CRITICAL';
  if (score >= 6) return 'HIGH';
  if (score >= 3) return 'MEDIUM';
  return 'LOW';
}

const SEVERITY_STYLES: Record<string, string> = {
  CRITICAL: 'bg-red-500/20 text-red-300 border-red-500/50',
  HIGH: 'bg-red-500/15 text-red-200 border-red-500/40',
  MEDIUM: 'bg-orange-500/20 text-orange-300 border-orange-500/50',
  LOW: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50',
};

export function ThreatCard({ threat, index, expanded, onToggle }: ThreatCardProps) {
  const scoreColor = threat.dread_score
    ? getDreadScoreColor(threat.dread_score)
    : 'text-gray-400';
  const severity =
    threat.dread_score !== undefined ? getSeverityFromScore(threat.dread_score) : 'LOW';
  const severityStyle = SEVERITY_STYLES[severity] || SEVERITY_STYLES.LOW;

  return (
    <div className="rounded-lg border border-white/10 overflow-hidden bg-white/5 hover:border-indigo-500/30 transition-colors">
      <button
        type="button"
        onClick={onToggle}
        className="w-full flex items-center gap-3 p-4 text-left"
      >
        {expanded ? (
          <ChevronDown className="w-5 h-5 text-gray-400 shrink-0" />
        ) : (
          <ChevronRight className="w-5 h-5 text-gray-400 shrink-0" />
        )}
        <span className="text-xs text-gray-500 shrink-0">#{index + 1}</span>
        <h3 className="font-medium text-indigo-300 flex-1 truncate">{threat.threat_type}</h3>
        <span className={`px-2 py-0.5 rounded text-xs font-medium border ${severityStyle}`}>
          {severity}
        </span>
        {threat.dread_score !== undefined && (
          <span className={`text-sm font-mono shrink-0 ${scoreColor}`}>
            {threat.dread_score.toFixed(1)}
          </span>
        )}
      </button>

      {expanded && (
        <div className="px-4 pb-4 pt-0 border-t border-white/5 space-y-3">
          {STRIDE_DESCRIPTIONS[threat.threat_type] && (
            <p className="text-xs text-gray-500 italic">{STRIDE_DESCRIPTIONS[threat.threat_type]}</p>
          )}
          <p className="text-sm text-gray-300">{threat.description}</p>
          <div className="bg-emerald-500/10 border border-emerald-500/30 p-3 rounded-lg">
            <strong className="text-emerald-300 text-sm">Mitigação:</strong>
            <p className="text-sm text-emerald-200/90 mt-1">{threat.mitigation}</p>
          </div>
          {threat.dread_details && (
            <div className="grid grid-cols-5 gap-2 text-xs">
              <ScoreItem label="D" value={threat.dread_details.damage} title="Damage" />
              <ScoreItem
                label="R"
                value={threat.dread_details.reproducibility}
                title="Reproducibility"
              />
              <ScoreItem
                label="E"
                value={threat.dread_details.exploitability}
                title="Exploitability"
              />
              <ScoreItem
                label="A"
                value={threat.dread_details.affected_users}
                title="Affected Users"
              />
              <ScoreItem
                label="D"
                value={threat.dread_details.discoverability}
                title="Discoverability"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

interface ScoreItemProps {
  label: string;
  value: number;
  title: string;
}

function ScoreItem({ label, value, title }: ScoreItemProps) {
  return (
    <div className="text-center p-1 bg-white/5 rounded" title={title}>
      <span className="text-gray-500">{label}</span>
      <span className={`ml-1 ${getDreadScoreColor(value)}`}>{value}</span>
    </div>
  );
}
