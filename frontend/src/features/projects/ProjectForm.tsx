import { useState } from "react";
import type { Project, ProjectStatus } from "@/contracts";
import { isCommandError, type CommandError } from "@/command-client";

export interface ProjectFormValues {
  name: string;
  status: ProjectStatus;
  priority: number;
  description: string;
}

interface ProjectFormProps {
  initial?: Partial<Project>;
  submitLabel: string;
  onSubmit: (values: ProjectFormValues) => Promise<void>;
  onCancel: () => void;
}

// Form draft state is kept locally and preserved across validation failures:
// on error, field messages are shown but the entered values remain.
export function ProjectForm({ initial, submitLabel, onSubmit, onCancel }: ProjectFormProps) {
  const [values, setValues] = useState<ProjectFormValues>({
    name: initial?.name ?? "",
    status: initial?.status ?? "active",
    priority: initial?.priority ?? 3,
    description: initial?.description ?? "",
  });
  const [error, setError] = useState<CommandError | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await onSubmit(values);
    } catch (err) {
      // Values are intentionally NOT reset — the user keeps their input.
      setError(isCommandError(err) ? err : null);
    } finally {
      setBusy(false);
    }
  }

  const fieldError = (field: string) => error?.field_errors?.[field]?.join(", ");

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <p className="field-error" role="alert">
          {error.message}
        </p>
      )}
      <div className="field">
        <label htmlFor="pf-name">Name</label>
        <input
          id="pf-name"
          value={values.name}
          onChange={(e) => setValues({ ...values, name: e.target.value })}
        />
        {fieldError("name") && <span className="field-error">{fieldError("name")}</span>}
      </div>
      <div className="field">
        <label htmlFor="pf-status">Status</label>
        <select
          id="pf-status"
          value={values.status}
          onChange={(e) =>
            setValues({ ...values, status: e.target.value as ProjectStatus })
          }
        >
          <option value="active">Active</option>
          <option value="backlog">Backlog</option>
          <option value="archive">Archive</option>
        </select>
      </div>
      <div className="field">
        <label htmlFor="pf-priority">Priority (1–5)</label>
        <input
          id="pf-priority"
          type="number"
          min={1}
          max={5}
          value={values.priority}
          onChange={(e) => setValues({ ...values, priority: Number(e.target.value) })}
        />
        {fieldError("priority") && (
          <span className="field-error">{fieldError("priority")}</span>
        )}
      </div>
      <div className="field">
        <label htmlFor="pf-desc">Description</label>
        <textarea
          id="pf-desc"
          value={values.description}
          onChange={(e) => setValues({ ...values, description: e.target.value })}
        />
      </div>
      <div className="dialog-actions">
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={busy}>
          {submitLabel}
        </button>
      </div>
    </form>
  );
}
