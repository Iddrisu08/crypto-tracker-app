import React from 'react';
import './ErrorBoundary.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      errorId: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { 
      hasError: true,
      errorId: Date.now().toString(36) + Math.random().toString(36).substr(2)
    };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // You could also send error to monitoring service here
    // this.logErrorToService(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null,
      errorId: null 
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      return (
        <div className="error-boundary">
          <div className="error-boundary-content">
            <div className="error-icon">⚠️</div>
            
            <h2 className="error-title">
              {this.props.fallbackTitle || 'Something went wrong'}
            </h2>
            
            <p className="error-message">
              {this.props.fallbackMessage || 
                'We encountered an unexpected error. This has been logged and our team will investigate.'}
            </p>

            <div className="error-actions">
              <button 
                onClick={this.handleRetry}
                className="error-btn error-btn-primary"
              >
                🔄 Try Again
              </button>
              
              <button 
                onClick={this.handleReload}
                className="error-btn error-btn-secondary"
              >
                🔃 Reload Page
              </button>
            </div>

            {/* Show error details in development */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="error-details">
                <summary className="error-details-summary">
                  🐛 Developer Details (Development Only)
                </summary>
                <div className="error-details-content">
                  <div className="error-section">
                    <h4>Error:</h4>
                    <pre className="error-code">
                      {this.state.error && this.state.error.toString()}
                    </pre>
                  </div>
                  
                  <div className="error-section">
                    <h4>Stack Trace:</h4>
                    <pre className="error-code">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </div>
                  
                  <div className="error-section">
                    <h4>Error ID:</h4>
                    <code className="error-id">{this.state.errorId}</code>
                  </div>
                </div>
              </details>
            )}

            {/* Help Section */}
            <div className="error-help">
              <h4>💡 What you can do:</h4>
              <ul>
                <li>Check your internet connection</li>
                <li>Try refreshing the page</li>
                <li>Clear your browser cache</li>
                <li>Contact support if the problem persists</li>
              </ul>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Functional wrapper for easier use with custom props
export const ErrorBoundaryWrapper = ({ 
  children, 
  fallbackTitle, 
  fallbackMessage,
  onError 
}) => (
  <ErrorBoundary 
    fallbackTitle={fallbackTitle}
    fallbackMessage={fallbackMessage}
    onError={onError}
  >
    {children}
  </ErrorBoundary>
);

// Higher-order component for wrapping components with error boundaries
export const withErrorBoundary = (Component, errorBoundaryProps = {}) => {
  const WrappedComponent = (props) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );
  
  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
};

// Lightweight error boundary for specific sections
export const SectionErrorBoundary = ({ children, sectionName }) => (
  <ErrorBoundary 
    fallbackTitle={`${sectionName} Error`}
    fallbackMessage={`There was a problem loading the ${sectionName.toLowerCase()} section. Other parts of the app should still work normally.`}
  >
    {children}
  </ErrorBoundary>
);

export default ErrorBoundary;