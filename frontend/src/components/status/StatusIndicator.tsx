import type { ScoreStatus } from "@/contracts";

// Non-color-only status indicator: pairs a colored dot with a text label and an
// icon glyph so status is perceivable without relying on color alone.
const ICON: Record<ScoreStatus, string> = {
  green: "●",
  yellow: "◐",
  red: "○",
};

const LABEL: Record<ScoreStatus, string> = {
  green: "On track",
  yellow: "At risk",
  red: "Behind",
};

export function StatusIndicator({ status }: { status: ScoreStatus }) {
  return (
    <span aria-label={LABEL[status]} title={LABEL[status]}>
      <span className={`status-dot status-${status}`} aria-hidden="true" />
      <span aria-hidden="true"> {ICON[status]} </span>
      <span>{LABEL[status]}</span>
    </span>
  );
}
