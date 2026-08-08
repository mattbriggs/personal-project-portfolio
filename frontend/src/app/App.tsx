import { Providers } from "./providers";
import { ErrorBoundary } from "./error-boundary";
import { AppShell } from "./AppShell";

export function App() {
  return (
    <Providers>
      <ErrorBoundary>
        <AppShell />
      </ErrorBoundary>
    </Providers>
  );
}
