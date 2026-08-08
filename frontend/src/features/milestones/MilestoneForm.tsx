import { useState } from "react";
import type { Milestone, MilestoneStatus } from "@/contracts";
import { weekKeyForDate } from "@/utils/week";

const STATUSES: MilestoneStatus[] = ["backlog", "planned", "doing", "done", "cancelled"];

export interface MilestoneFormValues {
  description: string;
  status: MilestoneStatus;
  target_date: string | null;
  notes: string;
}

interface MilestoneFormProps {
  /** Existing milestone for edit mode; omitted for create mode. */
  initial?: Milestone;
  submitLabel: string;
  error?: string | null;
  onSubmit: (values: MilestoneFormValues) => void;
  onCancel: () => void;
}

/**
 * Create/edit form for a milestone, matching the fields of the Tkinter
 * `_MilestoneDialog`: description, target date, status, the read-only week and
 * total-minutes readouts, and free-text notes.
 */
export function MilestoneForm({
  initial,
  submitLabel,
  error,
  onSubmit,
  onCancel,
}: MilestoneFormProps) {
  const [description, setDescription] = useState(initial?.description ?? "");
  const [target, setTarget] = useState(initial?.target_date ?? "");
  const [status, setStatus] = useState<MilestoneStatus>(initial?.status ?? "backlog");
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [localError, setLocalError] = useState<string | null>(null);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!description.trim()) {
      setLocalError("Milestone description is required.");
      return;
    }
    if (target && weekKeyForDate(target) === null) {
      setLocalError("Target must be YYYY-MM-DD.");
      return;
    }
    setLocalError(null);
    onSubmit({
      description: description.trim(),
      status,
      target_date: target ? target : null,
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
        <label htmlFor="mf-name">Milestone</label>
        <input
          id="mf-name"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      <div className="field">
        <label htmlFor="mf-target">Target</label>
        <div className="field-row">
          <input
            id="mf-target"
            type="date"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
          />
          <button
            type="button"
            onClick={() => setTarget(new Date().toLocaleDateString("en-CA"))}
          >
            Today
          </button>
          <button type="button" onClick={() => setTarget("")}>
            Clear
          </button>
        </div>
      </div>

      <div className="field">
        <label htmlFor="mf-status">Status</label>
        <select
          id="mf-status"
          value={status}
          onChange={(e) => setStatus(e.target.value as MilestoneStatus)}
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      <p className="field-hint">
        Week: {(target && weekKeyForDate(target)) || "—"}
        {"    "}Total Min: {initial?.total_session_minutes || "—"}
      </p>

      <div className="field">
        <label htmlFor="mf-notes">Description</label>
        <textarea
          id="mf-notes"
          rows={5}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>

      <div className="dialog-actions">
        <button type="submit" className="primary">
          {submitLabel}
        </button>
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
}
