import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  sessions as api,
  projects as projectApi,
  settings as settingsApi,
} from "@/command-client";
import type { SessionStatus } from "@/contracts";
import { isCommandError, type CommandError } from "@/command-client";
import { useInvalidate } from "@/hooks/useInvalidate";
import { useWorkspace } from "@/state/workspace";
import { weekInfo } from "@/utils/week";

const STATUSES: SessionStatus[] = ["backlog", "planned", "doing", "done", "cancelled"];

export function SessionsView() {
  const { selectedWeek } = useWorkspace();
  const info = weekInfo(selectedWeek);
  const { afterSessionMutation } = useInvalidate();

  // Form draft state, preserved across validation failures.
  const [projectId, setProjectId] = useState<number | "">("");
  const [date, setDate] = useState(info.monday.toISOString().slice(0, 10));
  const [duration, setDuration] = useState<string>("");
  const [description, setDescription] = useState("");
  const [formError, setFormError] = useState<CommandError | null>(null);

  const projectsQuery = useQuery({
    queryKey: ["projects", "active"],
    queryFn: () => projectApi.list("active"),
  });
  const settingsQuery = useQuery({
    queryKey: ["settings"],
    queryFn: () => settingsApi.get(),
  });
  const sessionsQuery = useQuery({
    queryKey: ["sessions", selectedWeek],
    queryFn: () => api.forWeek(selectedWeek),
  });

  const createMut = useMutation({
    mutationFn: () =>
      api.create({
        project_id: Number(projectId),
        scheduled_date: date,
        duration_minutes: duration ? Number(duration) : null,
        description,
        status: "planned",
      }),
    onSuccess: () => {
      setDescription("");
      setFormError(null);
      return afterSessionMutation();
    },
    onError: (err) => setFormError(isCommandError(err) ? err : null),
  });
  const statusMut = useMutation({
    mutationFn: ({ id, status }: { id: number; status: SessionStatus }) =>
      api.setStatus(id, status),
    onSuccess: afterSessionMutation,
  });

  const budgetMinutes = (settingsQuery.data?.weekly_budget_hours ?? 0) * 60;
  const plannedMinutes =
    sessionsQuery.data?.sessions
      .filter((s) => s.status !== "cancelled" && s.status !== "backlog")
      .reduce((sum, s) => sum + s.duration_minutes, 0) ?? 0;

  return (
    <section aria-label="Sessions">
      <h2>
        Sessions — {selectedWeek} <small>({info.label})</small>
      </h2>

      <p>
        Weekly budget: {(plannedMinutes / 60).toFixed(1)}h planned of{" "}
        {(budgetMinutes / 60).toFixed(1)}h
      </p>

      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Duration</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {sessionsQuery.data?.sessions.map((s) => (
            <tr key={s.id}>
              <td>{s.scheduled_date}</td>
              <td>{s.description}</td>
              <td>{s.duration_minutes}m</td>
              <td>
                <select
                  aria-label={`Status for session ${s.id}`}
                  value={s.status}
                  onChange={(e) =>
                    statusMut.mutate({ id: s.id, status: e.target.value as SessionStatus })
                  }
                >
                  {STATUSES.map((st) => (
                    <option key={st} value={st}>
                      {st}
                    </option>
                  ))}
                </select>
              </td>
            </tr>
          ))}
          {sessionsQuery.data?.sessions.length === 0 && (
            <tr>
              <td colSpan={4}>No sessions this week.</td>
            </tr>
          )}
        </tbody>
      </table>

      <h3>Add session</h3>
      {formError && (
        <p className="field-error" role="alert">
          {formError.message}
        </p>
      )}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          createMut.mutate();
        }}
      >
        <div className="field">
          <label htmlFor="s-project">Project</label>
          <select
            id="s-project"
            value={projectId}
            onChange={(e) => setProjectId(e.target.value ? Number(e.target.value) : "")}
            required
          >
            <option value="">Select…</option>
            {projectsQuery.data?.projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="s-date">Date</label>
          <input
            id="s-date"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="s-duration">Duration (minutes, 15–480; blank = default)</label>
          <input
            id="s-duration"
            type="number"
            min={15}
            max={480}
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            placeholder={String(settingsQuery.data?.default_duration_minutes ?? 90)}
          />
        </div>
        <div className="field">
          <label htmlFor="s-desc">Description</label>
          <input
            id="s-desc"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <button type="submit" className="primary" disabled={!projectId}>
          Add session
        </button>
      </form>
    </section>
  );
}
