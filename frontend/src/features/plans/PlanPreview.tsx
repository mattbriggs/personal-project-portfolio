import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { MermaidBlock } from "./MermaidBlock";

// Sanitized Markdown preview with Mermaid support. Fenced ```mermaid blocks are
// rendered as diagrams. react-markdown does NOT render raw HTML unless the
// rehype-raw plugin is added (which it is not), so embedded HTML is escaped —
// there is no injection surface. Mermaid SVG output is separately sanitized with
// DOMPurify inside MermaidBlock.
export function PlanPreview({ content }: { content: string }) {
  return (
    <div aria-label="Plan preview">
      <Markdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ className, children, ...props }) {
            const isMermaid = /language-mermaid/.test(className ?? "");
            const text = String(children).replace(/\n$/, "");
            if (isMermaid) return <MermaidBlock code={text} />;
            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </Markdown>
    </div>
  );
}
