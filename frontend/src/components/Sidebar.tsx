import { Sliders, Cpu } from 'lucide-react';

interface SidebarProps {
  confidence: number;
  iou: number;
  onConfidenceChange: (v: number) => void;
  onIouChange: (v: number) => void;
  onClose?: () => void;
  isMobile?: boolean;
}

export function Sidebar({
  confidence,
  iou,
  onConfidenceChange,
  onIouChange,
  onClose,
  isMobile = false,
}: SidebarProps) {
  return (
    <aside
      className={`glass-card space-y-6 ${
        isMobile ? 'fixed inset-y-0 left-0 z-50 w-72 p-6 overflow-y-auto' : 'w-72 shrink-0'
      }`}
    >
      {isMobile && onClose && (
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white"
          aria-label="Close"
        >
          ×
        </button>
      )}
      <h2 className="text-lg font-semibold flex items-center gap-2">
        <Sliders className="w-5 h-5 text-indigo-400" /> Configuração
      </h2>

      <div>
        <label className="block text-sm text-gray-400 mb-2">Confidence: {confidence.toFixed(2)}</label>
        <input
          type="range"
          min="0.1"
          max="0.9"
          step="0.05"
          value={confidence}
          onChange={(e) => onConfidenceChange(parseFloat(e.target.value))}
          className="w-full accent-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm text-gray-400 mb-2">IoU: {iou.toFixed(2)}</label>
        <input
          type="range"
          min="0.1"
          max="0.9"
          step="0.05"
          value={iou}
          onChange={(e) => onIouChange(parseFloat(e.target.value))}
          className="w-full accent-indigo-500"
        />
      </div>

      <div className="pt-4 border-t border-white/10">
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-2">
          <Cpu className="w-4 h-4" />
          <span className="font-medium text-gray-300">YOLOv8 Engine</span>
        </div>
        <p className="text-xs text-gray-500">
          Modelo fine-tuned para diagramas AWS/Azure e detecção STRIDE. Os parâmetros acima serão
          usados quando o modelo YOLO estiver disponível.
        </p>
      </div>
    </aside>
  );
}
