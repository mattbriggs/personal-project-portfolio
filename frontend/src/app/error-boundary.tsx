import { Component, type ErrorInfo, type ReactNode } from "react";

interface State {
  error: Error | null;
}

// Global error boundary: catches render errors and shows a safe fallback with
// no stack trace, keeping the app usable.
export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // eslint-disable-next-line no-console
    console.error("Render error:", error.message, info.componentStack);
  }

  render(): ReactNode {
    if (this.state.error) {
      return (
        <div className="main-view" role="alert">
          <h2>Something went wrong</h2>
          <p>The view failed to render. Try reloading the window.</p>
          <button className="primary" onClick={() => this.setState({ error: null })}>
            Dismiss
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
