import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";
import DOMPurify from "dompurify";

// Renders a single fenced ```mermaid block. On a parse error the raw source is
// preserved and an explicit error message is shown (SRS §5.10 / §5.15). Mermaid
// is bundled — no CDN dependency.
mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });

let counter = 0;

export function MermaidBlock({ code }: { code: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const id = `mermaid-${counter++}`;
    mermaid
      .render(id, code)
      .then(({ svg }) => {
        if (cancelled || !ref.current) return;
        ref.current.innerHTML = DOMPurify.sanitize(svg, {
          USE_PROFILES: { svg: true, svgFilters: true },
        });
        setError(null);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      });
    return () => {
      cancelled = true;
    };
  }, [code]);

  if (error) {
    return (
      <div role="alert" className="field-error">
        <p>Diagram could not be rendered: {error}</p>
        <pre>{code}</pre>
      </div>
    );
  }
  return <div className="mermaid" ref={ref} aria-label="Mermaid diagram" />;
}
