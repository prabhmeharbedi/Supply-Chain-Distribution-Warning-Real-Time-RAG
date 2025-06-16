import React from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  AlertTriangle, 
  Shield, 
  Zap,
  Clock,
  Target
} from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: React.ReactNode;
  color: 'blue' | 'red' | 'green' | 'yellow' | 'purple' | 'indigo';
}

const StatCard: React.FC<StatCardProps> = ({ title, value, change, changeType, icon, color }) => {
  const colorClasses = {
    blue: 'bg-primary-100 text-primary-600',
    red: 'bg-error-100 text-error-600',
    green: 'bg-success-100 text-success-600',
    yellow: 'bg-warning-100 text-warning-600',
    purple: 'bg-purple-100 text-purple-600',
    indigo: 'bg-indigo-100 text-indigo-600'
  };

  const valueColorClasses = {
    blue: 'text-primary-600',
    red: 'text-error-600',
    green: 'text-success-600',
    yellow: 'text-warning-600',
    purple: 'text-purple-600',
    indigo: 'text-indigo-600'
  };

  return (
    <div className="bg-white rounded-xl shadow-soft border border-neutral-200 p-6 hover:shadow-medium transition-all duration-200 hover:translate-y-[-2px]">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-neutral-600 mb-1">{title}</p>
          <p className={`text-3xl font-bold ${valueColorClasses[color]}`}>{value}</p>
          {change && (
            <div className="mt-3 flex items-center text-sm">
              {changeType === 'positive' && <TrendingUp className="h-4 w-4 text-success-500 mr-1" />}
              {changeType === 'negative' && <TrendingDown className="h-4 w-4 text-error-500 mr-1" />}
              <span className={`font-medium ${
                changeType === 'positive' ? 'text-success-600' : 
                changeType === 'negative' ? 'text-error-600' : 
                'text-neutral-600'
              }`}>
                {change}
              </span>
              <span className="text-neutral-500 ml-1">vs last period</span>
            </div>
          )}
        </div>
        <div className={`h-14 w-14 rounded-xl flex items-center justify-center ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

interface StatsCardsProps {
  stats: {
    totalAlerts24h: number;
    criticalAlerts: number;
    systemHealth: string;
    averageConfidence: number;
    activeDisruptions: number;
    resolvedToday: number;
  };
}

const StatsCards: React.FC<StatsCardsProps> = ({ stats }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <StatCard
        title="Total Alerts (24h)"
        value={stats.totalAlerts24h}
        change="+12%"
        changeType="positive"
        icon={<Activity className="h-7 w-7" />}
        color="blue"
      />
      
      <StatCard
        title="Critical Alerts"
        value={stats.criticalAlerts}
        change="Requires attention"
        changeType="negative"
        icon={<AlertTriangle className="h-7 w-7" />}
        color="red"
      />
      
      <StatCard
        title="System Health"
        value={stats.systemHealth}
        change="+2%"
        changeType="positive"
        icon={<Shield className="h-7 w-7" />}
        color="green"
      />
      
      <StatCard
        title="ML Confidence"
        value={`${Math.round(stats.averageConfidence)}%`}
        change="+5%"
        changeType="positive"
        icon={<Zap className="h-7 w-7" />}
        color="purple"
      />
      
      <StatCard
        title="Active Disruptions"
        value={stats.activeDisruptions}
        change="-3"
        changeType="positive"
        icon={<Target className="h-7 w-7" />}
        color="yellow"
      />
      
      <StatCard
        title="Resolved Today"
        value={stats.resolvedToday}
        change="+8"
        changeType="positive"
        icon={<Clock className="h-7 w-7" />}
        color="indigo"
      />
    </div>
  );
};

export default StatsCards;