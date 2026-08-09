import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { milestones as milestoneApi } from "@/command-client";
import type { Project, Session, SessionStatus } from "@/contracts";

const STATUSES: SessionStatus[] = ["backlog", "planned", "doing", "done", "cancelled"];

export interface SessionFormValues {
  project_id: number;
  milestone_id: number | null;
  scheduled_date: string;
  duration_minutes: number;
  status: SessionStatus;
  description: string;
  notes: string;
}

interface SessionFormProps {
  projects: Project[];
  /** Existing session for edit mode; omitted for create mode. */
  initial?: Session;
  /** Default duration from settings, used for new sessions. */
  defaultDuration: number;
  /** Date pre-filled for a new session, normally the selected week's Monday. */
  defaultDate: string;
  submitLabel: string;
  error?: string | null;
  onSubmit: (values: SessionFormValues) => void;
  onCancel: () => void;
}

/**
 * Create/edit form for a session, matching the fields of the Tkinter
 * `_SessionDialog`: project, milestone, session name, date, status, duration,
 * and free-text notes.
 */
export function SessionForm({
  projects,
  initial,
  defaultDuration,
  defaultDate,
  submitLabel,
  error,
  onSubmit,
  onCancel,
}: SessionFormProps) {
  const [projectId, setProjectId] = useState<number | "">(
    initial?.project_id ?? projects[0]?.id ?? "",
  );
  const [milestoneId, setMilestoneId] = useState<number | "">(initial?.milestone_id ?? "");
  const [description, setDescription] = useState(initial?.description ?? "");
  const [date, setDate] = useState(initial?.scheduled_date ?? defaultDate);
  const [status, setStatus] = useState<SessionStatus>(initial?.status ?? "backlog");
  const [duration, setDuration] = useState<number>(
    initial?.duration_minutes ?? defaultDuration,
  );
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [localError, setLocalError] = useState<string | null>(null);

  // Milestone choices follow the selected project, as in the Tkinter dialog.
  const milestonesQuery = useQuery({
    queryKey: ["milestones", projectId],
    queryFn: () => milestoneApi.forProject(Number(projectId)),
    enabled: projectId !== "",
  });

  // Clear a milestone that belongs to a project the user just switched away from.
  useEffect(() => {
    if (milestoneId === "") return;
    const available = milestonesQuery.data?.milestones;
    if (available && !available.some((m) => m.id === milestoneId)) {
      setMilestoneId("");
    }
  }, [milestonesQuery.data, milestoneId]);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (projectId === "") {
      setLocalError("Please select a project.");
      return;
    }
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || Number.isNaN(Date.parse(date))) {
      setLocalError("Date must be YYYY-MM-DD.");
      return;
    }
    setLocalError(null);
    onSubmit({
      project_id: Number(projectId),
      milestone_id: milestoneId === "" ? null : Number(milestoneId),
      scheduled_date: date,
      duration_minutes: duration,
      status,
      description: description.trim(),
      notes: notes.trim(),
    });
  }

  const shownError = localError ?? error;

  return (
    <form onSubmit={submit}>
      {shownError && (
        <p className="field-error" role="alert">
          {shownError}
        </p>
      )}

      <div className="field">
        <label htmlFor="sf-project">Project</label>
        <select
          id="sf-project"
          value={projectId}
          onChange={(e) => setProjectId(e.target.value ? Number(e.target.value) : "")}
        >
          <option value="">Select…</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label htmlFor="sf-milestone">Milestone</label>
        <select
          id="sf-milestone"
          value={milestoneId}
          onChange={(e) => setMilestoneId(e.target.value ? Number(e.target.value) : "")}
        >
          <option value="">— none —</option>
          {milestonesQuery.data?.milestones.map((m) => (
            <option key={m.id} value={m.id}>
              {m.description}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label htmlFor="sf-name">Session</label>
        <input
          id="sf-name"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      <div className="field">
        <label htmlFor="sf-date">Date</label>
        <div className="field-row">
          <input
            id="sf-date"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setDate(new Date().toLocaleDateString("en-CA"))}
          >
            Today
          </button>
        </div>
      </div>

      <div className="field">
        <label htmlFor="sf-status">Status</label>
        <div className="field-row">
          <select
            id="sf-status"
            value={status}
            onChange={(e) => setStatus(e.target.value as SessionStatus)}
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          <label htmlFor="sf-duration" className="field-hint">
            Min
          </label>
          <input
            id="sf-duration"
            type="number"
            min={15}
            max={480}
            step={15}
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
          />
        </div>
      </div>

      <div className="field">
        <label htmlFor="sf-notes">Description</label>
        <textarea
          id="sf-notes"
          rows={5}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>

      <div className="dialog-actions">
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary">
          {submitLabel}
        </button>
      </div>
    </form>
  );
}
