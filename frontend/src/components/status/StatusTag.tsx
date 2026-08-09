import type { CSSProperties } from "react";
import type { MilestoneStatus, ProjectStatus, SessionStatus } from "@/contracts";

// Modernist status tags, mirroring WORK_META / PROJECT_META in the design
// prototype: the tag variant carries the color, the label carries the meaning.

type WorkStatus = SessionStatus | MilestoneStatus;

const WORK_META: Record<WorkStatus, { cls: string; label: string; style?: CSSProperties }> = {
  backlog: { cls: "tag tag-neutral", label: "Backlog" },
  planned: { cls: "tag tag-outline", label: "Planned" },
  doing: { cls: "tag tag-accent", label: "Doing" },
  done: { cls: "tag tag-neutral", label: "Done", style: { opacity: 0.65 } },
  cancelled: {
    cls: "tag tag-neutral",
    label: "Cancelled",
    style: { opacity: 0.5, textDecoration: "line-through" },
  },
};

const PROJECT_META: Record<ProjectStatus, { cls: string; label: string }> = {
  active: { cls: "tag tag-accent", label: "Active" },
  backlog: { cls: "tag tag-outline", label: "Backlog" },
  archive: { cls: "tag tag-neutral", label: "Archived" },
};

export function WorkStatusTag({ status }: { status: WorkStatus }) {
  const meta = WORK_META[status];
  return (
    <span className={meta.cls} style={meta.style}>
      {meta.label}
    </span>
  );
}

export function ProjectStatusTag({ status }: { status: ProjectStatus }) {
  const meta = PROJECT_META[status];
  return <span className={meta.cls}>{meta.label}</span>;
}

// Priority 1–5 rendered as filled/empty squares, flush-left in the cell.
export function PriorityDots({ priority }: { priority: number }) {
  return (
    <span className="pri-dots" aria-label={`Priority ${priority} of 5`}>
      {[0, 1, 2, 3, 4].map((i) => (
        <span key={i} className={`pri-dot ${i < priority ? "on" : "off"}`} aria-hidden="true" />
      ))}
    </span>
  );
}
