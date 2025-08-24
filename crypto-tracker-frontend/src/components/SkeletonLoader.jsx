import React from 'react';
import './SkeletonLoader.css';

// Base Skeleton Component
export const Skeleton = ({ 
  width = '100%', 
  height = '20px', 
  borderRadius = '4px',
  className = '',
  style = {} 
}) => (
  <div 
    className={`skeleton ${className}`}
    style={{ 
      width, 
      height, 
      borderRadius,
      ...style 
    }}
    aria-label="Loading..."
  />
);

// Portfolio Card Skeleton
export const PortfolioSkeleton = () => (
  <div className="skeleton-card">
    <div className="skeleton-header">
      <Skeleton width="200px" height="24px" />
      <Skeleton width="80px" height="32px" borderRadius="20px" />
    </div>
    <div className="skeleton-content">
      <div className="skeleton-row">
        <Skeleton width="120px" height="16px" />
        <Skeleton width="150px" height="24px" />
      </div>
      <div className="skeleton-row">
        <Skeleton width="100px" height="16px" />
        <Skeleton width="120px" height="20px" />
      </div>
      <div className="skeleton-row">
        <Skeleton width="140px" height="16px" />
        <Skeleton width="180px" height="20px" />
      </div>
    </div>
  </div>
);

// Chart Skeleton
export const ChartSkeleton = () => (
  <div className="skeleton-card">
    <div className="skeleton-header">
      <Skeleton width="250px" height="24px" />
      <Skeleton width="100px" height="32px" borderRadius="6px" />
    </div>
    <div className="skeleton-chart">
      <div className="skeleton-chart-bars">
        {[...Array(8)].map((_, i) => (
          <Skeleton 
            key={i}
            width="20px" 
            height={`${Math.random() * 100 + 50}px`}
            borderRadius="2px"
          />
        ))}
      </div>
      <div className="skeleton-chart-labels">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} width="60px" height="12px" />
        ))}
      </div>
    </div>
  </div>
);

// Table Skeleton
export const TableSkeleton = ({ rows = 5, columns = 4 }) => (
  <div className="skeleton-table">
    {/* Table Header */}
    <div className="skeleton-table-row skeleton-table-header">
      {[...Array(columns)].map((_, i) => (
        <Skeleton key={i} width="100%" height="20px" />
      ))}
    </div>
    
    {/* Table Rows */}
    {[...Array(rows)].map((_, rowIndex) => (
      <div key={rowIndex} className="skeleton-table-row">
        {[...Array(columns)].map((_, colIndex) => (
          <Skeleton 
            key={colIndex} 
            width={colIndex === 0 ? "80%" : "100%"} 
            height="16px" 
          />
        ))}
      </div>
    ))}
  </div>
);

// Analytics Card Skeleton
export const AnalyticsSkeleton = () => (
  <div className="skeleton-analytics">
    <div className="skeleton-header">
      <Skeleton width="300px" height="28px" />
      <Skeleton width="120px" height="36px" borderRadius="8px" />
    </div>
    
    <div className="skeleton-analytics-grid">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="skeleton-analytics-card">
          <div className="skeleton-card-header">
            <Skeleton width="60px" height="20px" />
            <Skeleton width="120px" height="16px" />
          </div>
          <div className="skeleton-metrics">
            {[...Array(3)].map((_, j) => (
              <div key={j} className="skeleton-metric">
                <Skeleton width="100px" height="14px" />
                <Skeleton width="80px" height="20px" />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Form Skeleton
export const FormSkeleton = () => (
  <div className="skeleton-form">
    <div className="skeleton-form-header">
      <Skeleton width="200px" height="24px" />
    </div>
    
    <div className="skeleton-form-fields">
      <div className="skeleton-form-row">
        <div className="skeleton-form-field">
          <Skeleton width="80px" height="16px" />
          <Skeleton width="100%" height="40px" borderRadius="6px" />
        </div>
        <div className="skeleton-form-field">
          <Skeleton width="100px" height="16px" />
          <Skeleton width="100%" height="40px" borderRadius="6px" />
        </div>
      </div>
      
      <div className="skeleton-form-field">
        <Skeleton width="120px" height="16px" />
        <Skeleton width="100%" height="40px" borderRadius="6px" />
      </div>
      
      <div className="skeleton-form-actions">
        <Skeleton width="80px" height="40px" borderRadius="6px" />
        <Skeleton width="120px" height="40px" borderRadius="6px" />
      </div>
    </div>
  </div>
);

// List Item Skeleton
export const ListItemSkeleton = ({ showAvatar = false }) => (
  <div className="skeleton-list-item">
    {showAvatar && (
      <Skeleton width="40px" height="40px" borderRadius="50%" />
    )}
    <div className="skeleton-list-content">
      <Skeleton width="200px" height="18px" />
      <Skeleton width="150px" height="14px" />
    </div>
    <Skeleton width="60px" height="14px" />
  </div>
);

// Page Skeleton (combines multiple skeletons)
export const PageSkeleton = () => (
  <div className="skeleton-page">
    {/* Header */}
    <div className="skeleton-page-header">
      <Skeleton width="300px" height="32px" />
      <div className="skeleton-header-actions">
        <Skeleton width="40px" height="40px" borderRadius="50%" />
        <Skeleton width="120px" height="40px" borderRadius="20px" />
      </div>
    </div>
    
    {/* Content Grid */}
    <div className="skeleton-page-content">
      <PortfolioSkeleton />
      <ChartSkeleton />
      <div className="skeleton-table-container">
        <TableSkeleton rows={6} columns={5} />
      </div>
    </div>
  </div>
);

export default Skeleton;