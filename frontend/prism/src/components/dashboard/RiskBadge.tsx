interface RiskBadgeProps {
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
}

export const RiskBadge = ({ priority }: RiskBadgeProps) => {
  const getBadgeClass = () => {
    switch (priority) {
      case 'HIGH':
        return 'badge-critical';
      case 'MEDIUM':
        return 'badge-warning';
      case 'LOW':
        return 'badge-advisory';
      default:
        return 'badge-info';
    }
  };

  const getLabel = () => {
    switch (priority) {
      case 'HIGH':
        return 'CRITICAL';
      case 'MEDIUM':
        return 'WARNING';
      case 'LOW':
        return 'ADVISORY';
      default:
        return priority;
    }
  };

  return <span className={getBadgeClass()}>{getLabel()}</span>;
};

// Made with Bob
