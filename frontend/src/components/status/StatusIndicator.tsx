import type { ScoreStatus } from "@/contracts";

// Non-color-only score indicator, rendered as a Modernist tag: the tag variant
// carries the color, an icon glyph and a text label carry the meaning without
// relying on color alone. Metadata mirrors SCORE_META in the design prototype.
const SCORE_META: Record<ScoreStatus, { cls: string; icon: string; label: string }> = {
  green: { cls: "tag tag-neutral", icon: "●", label: "On track" },
  yellow: { cls: "tag tag-outline", icon: "◐", label: "At risk" },
  red: { cls: "tag tag-accent", icon: "○", label: "Behind" },
};

export function StatusIndicator({ status }: { status: ScoreStatus }) {
  const meta = SCORE_META[status];
  return (
    <span className={meta.cls} aria-label={meta.label} title={meta.label}>
      <span aria-hidden="true">{meta.icon}</span>
      {meta.label}
    </span>
  );
}
