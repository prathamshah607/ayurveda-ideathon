import React from 'react';
import type { DoshaBreakdown } from '../../api/types';

interface DoshaChartProps {
  breakdown: DoshaBreakdown;
  size?: 'sm' | 'md' | 'lg';
  showLabels?: boolean;
  showPercentages?: boolean;
  className?: string;
}

export function DoshaChart({
  breakdown,
  size = 'md',
  showLabels = true,
  showPercentages = true,
  className = '',
}: DoshaChartProps) {
  const total = breakdown.vata + breakdown.pitta + breakdown.kapha;
  const percentages = {
    vata: Math.round((breakdown.vata / total) * 100),
    pitta: Math.round((breakdown.pitta / total) * 100),
    kapha: Math.round((breakdown.kapha / total) * 100),
  };

  const sizeConfig = {
    sm: { size: 100, stroke: 20 },
    md: { size: 160, stroke: 30 },
    lg: { size: 200, stroke: 40 },
  };

  const config = sizeConfig[size];
  const radius = (config.size - config.stroke) / 2;
  const circumference = 2 * Math.PI * radius;

  // Calculate stroke offsets for pie chart
  const vataLength = (percentages.vata / 100) * circumference;
  const pittaLength = (percentages.pitta / 100) * circumference;
  const kaphaLength = (percentages.kapha / 100) * circumference;

  const vataOffset = 0;
  const pittaOffset = circumference - vataLength;
  const kaphaOffset = circumference - vataLength - pittaLength;

  const doshaColors = {
    vata: '#60A5FA', // Blue - air/ether
    pitta: '#F97316', // Orange - fire/water
    kapha: '#22C55E', // Green - earth/water
  };

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <div className="relative" style={{ width: config.size, height: config.size }}>
        <svg width={config.size} height={config.size} className="-rotate-90">
          {/* Vata */}
          <circle
            cx={config.size / 2}
            cy={config.size / 2}
            r={radius}
            strokeWidth={config.stroke}
            stroke={doshaColors.vata}
            fill="none"
            strokeDasharray={`${vataLength} ${circumference - vataLength}`}
            strokeDashoffset={-vataOffset}
          />
          {/* Pitta */}
          <circle
            cx={config.size / 2}
            cy={config.size / 2}
            r={radius}
            strokeWidth={config.stroke}
            stroke={doshaColors.pitta}
            fill="none"
            strokeDasharray={`${pittaLength} ${circumference - pittaLength}`}
            strokeDashoffset={-vataLength}
          />
          {/* Kapha */}
          <circle
            cx={config.size / 2}
            cy={config.size / 2}
            r={radius}
            strokeWidth={config.stroke}
            stroke={doshaColors.kapha}
            fill="none"
            strokeDasharray={`${kaphaLength} ${circumference - kaphaLength}`}
            strokeDashoffset={-(vataLength + pittaLength)}
          />
        </svg>
      </div>

      {showLabels && (
        <div className="flex justify-center gap-4 mt-4">
          <div className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: doshaColors.vata }}
            />
            <span className="text-sm text-text-secondary">
              Vata {showPercentages && `(${percentages.vata}%)`}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: doshaColors.pitta }}
            />
            <span className="text-sm text-text-secondary">
              Pitta {showPercentages && `(${percentages.pitta}%)`}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: doshaColors.kapha }}
            />
            <span className="text-sm text-text-secondary">
              Kapha {showPercentages && `(${percentages.kapha}%)`}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

interface DoshaBarChartProps {
  breakdown: DoshaBreakdown;
  className?: string;
}

export function DoshaBarChart({ breakdown, className = '' }: DoshaBarChartProps) {
  const total = breakdown.vata + breakdown.pitta + breakdown.kapha;
  const percentages = {
    vata: Math.round((breakdown.vata / total) * 100),
    pitta: Math.round((breakdown.pitta / total) * 100),
    kapha: Math.round((breakdown.kapha / total) * 100),
  };

  const doshas = [
    { name: 'Vata', value: percentages.vata, color: 'bg-blue-400', description: 'Air & Ether' },
    { name: 'Pitta', value: percentages.pitta, color: 'bg-orange-500', description: 'Fire & Water' },
    { name: 'Kapha', value: percentages.kapha, color: 'bg-green-500', description: 'Earth & Water' },
  ];

  return (
    <div className={`space-y-4 ${className}`}>
      {doshas.map((dosha) => (
        <div key={dosha.name}>
          <div className="flex justify-between items-center mb-1">
            <div>
              <span className="font-medium text-text-primary">{dosha.name}</span>
              <span className="text-xs text-text-secondary ml-2">({dosha.description})</span>
            </div>
            <span className="text-sm font-medium text-text-primary">{dosha.value}%</span>
          </div>
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full ${dosha.color} rounded-full transition-all duration-500`}
              style={{ width: `${dosha.value}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
