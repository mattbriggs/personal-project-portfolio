import { useMemo, useState } from "react";
import { useMutation, useQueries, useQuery } from "@tanstack/react-query";
import {
  sessions as api,
  milestones as milestoneApi,
  projects as projectApi,
  settings as settingsApi,
} from "@/command-client";
import type { Session, SessionStatus } from "@/contracts";
import { isCommandError, type CommandError } from "@/command-client";
import { Dialog } from "@/components/dialogs/Dialog";
import { ConfirmDialog } from "@/components/dialogs/ConfirmDialog";
import { WorkStatusTag } from "@/components/status/StatusTag";
import { useInvalidate } from "@/hooks/useInvalidate";
import { useWorkspace } from "@/state/workspace";
import { weekInfo } from "@/utils/week";
import { SessionForm, type SessionFormValues } from "./SessionForm";

const STATUSES: SessionStatus[] = ["backlog", "planned", "doing", "done", "cancelled"];

function hours(minutes: number): string {
  return `${(minutes / 60).toFixed(1)}h`;
}

export function SessionsView() {
  const { selectedWeek } = useWorkspace();
  const info = weekInfo(selectedWeek);
  const { afterSessionMutation } = useInvalidate();

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [editing, setEditing] = useState<Session | "new" | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<Session | null>(null);
  const [bulkStatus, setBulkStatus] = useState<SessionStatus>("planned");
  const [formError, setFormError] = useState<CommandError | null>(null);

  const projectsQuery = useQuery({
    queryKey: ["projects", "all"],
    queryFn: () => projectApi.list(),
  });
  const settingsQuery = useQuery({
    queryKey: ["settings"],
    queryFn: () => settingsApi.get(),
  });
  const sessionsQuery = useQuery({
    queryKey: ["sessions", selectedWeek],
    queryFn: () => api.forWeek(selectedWeek),
  });

  const sessionList = useMemo(
    () => sessionsQuery.data?.sessions ?? [],
    [sessionsQuery.data],
  );
  const projectNames = useMemo(() => {
    const map = new Map<number, string>();
    projectsQuery.data?.projects.forEach((p) => map.set(p.id, p.name));
    return map;
  }, [projectsQuery.data]);

  // The session list carries milestone_id but not its description, so fetch the
  // milestones of exactly the projects present this week to label the column.
  const projectIdsInWeek = useMemo(
    () => [...new Set(sessionList.map((s) => s.project_id))].sort(),
    [sessionList],
  );
  const milestoneQueries = useQueries({
    queries: projectIdsInWeek.map((pid) => ({
      queryKey: ["milestones", pid],
      queryFn: () => milestoneApi.forProject(pid),
    })),
  });
  const milestoneNames = useMemo(() => {
    const map = new Map<number, string>();
    milestoneQueries.forEach((q) =>
      q.data?.milestones.forEach((m) => map.set(m.id, m.description)),
    );
    return map;
  }, [milestoneQueries]);

  const createMut = useMutation({
    mutationFn: (v: SessionFormValues) => api.create(v),
    onSuccess: () => {
      setEditing(null);
      setFormError(null);
      return afterSessionMutation();
    },
    onError: (err) => setFormError(isCommandError(err) ? err : null),
  });
  const updateMut = useMutation({
    mutationFn: ({ id, v }: { id: number; v: SessionFormValues }) => api.update(id, v),
    onSuccess: () => {
      setEditing(null);
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
  const deleteMut = useMutation({
    mutationFn: (id: number) => api.remove(id),
    onSuccess: () => {
      setSelectedId(null);
      return afterSessionMutation();
    },
  });

  // Cancelled sessions are excluded from both totals, matching the Tkinter view.
  const counted = sessionList.filter((s) => s.status !== "cancelled");
  const totalMinutes = counted.reduce((sum, s) => sum + s.duration_minutes, 0);
  const doneMinutes = counted
    .filter((s) => s.status === "done")
    .reduce((sum, s) => sum + s.duration_minutes, 0);
  const budgetMinutes = (settingsQuery.data?.weekly_budget_hours ?? 0) * 60;

  const selected = sessionList.find((s) => s.id === selectedId) ?? null;

  return (
    <section aria-label="Sessions">
      <h2>Sessions</h2>
      <p className="view-sub">
        {selectedWeek} · {info.label}
      </p>

      <div className="toolbar">
        <span className="spacer" />
        <button
          className="btn btn-primary"
          onClick={() => {
            setFormError(null);
            setEditing("new");
          }}
        >
          + New session
        </button>
      </div>

      <div className="table-scroll">
        <table className="table">
          <thead>
            <tr>
              <th>Project</th>
              <th>Milestone</th>
              <th>Date</th>
              <th>Min</th>
              <th>Status</th>
              <th>Session</th>
            </tr>
          </thead>
          <tbody>
            {sessionList.map((s) => (
              <tr
                key={s.id}
                className="row-clickable"
                aria-selected={s.id === selectedId}
                onClick={() => setSelectedId(s.id)}
                onDoubleClick={() => {
                  setFormError(null);
                  setEditing(s);
                }}
              >
                <td>{projectNames.get(s.project_id) ?? `#${s.project_id}`}</td>
                <td>
                  {s.milestone_id
                    ? (milestoneNames.get(s.milestone_id) ?? `#${s.milestone_id}`)
                    : "—"}
                </td>
                <td>{s.scheduled_date}</td>
                <td>{s.duration_minutes}</td>
                <td>
                  <WorkStatusTag status={s.status} />
                </td>
                <td>{s.description || "—"}</td>
              </tr>
            ))}
            {sessionList.length === 0 && (
              <tr>
                <td colSpan={6}>No sessions this week.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="action-bar">
        <label htmlFor="s-bulk-status">Set status</label>
        <select
          id="s-bulk-status"
          className="input-auto"
          value={bulkStatus}
          onChange={(e) => setBulkStatus(e.target.value as SessionStatus)}
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <button
          className="btn btn-secondary"
          disabled={!selected}
          onClick={() => selected && statusMut.mutate({ id: selected.id, status: bulkStatus })}
        >
          Apply
        </button>
        <button
          className="btn btn-secondary"
          disabled={!selected}
          onClick={() => selected && setEditing(selected)}
        >
          Edit
        </button>
        <button
          className="btn btn-ghost"
          disabled={!selected}
          onClick={() => selected && setConfirmDelete(selected)}
        >
          Delete
        </button>
      </div>

      <p
        className="card"
        style={{ display: "inline-flex", flexDirection: "row", gap: 14, fontSize: 13, alignItems: "center" }}
      >
        <span>Planned {hours(totalMinutes)}</span>
        <span>·</span>
        <span>Done {hours(doneMinutes)}</span>
        <span>·</span>
        <span>
          Remaining {hours(Math.max(0, budgetMinutes - doneMinutes))} of {hours(budgetMinutes)} budget
        </span>
      </p>

      {editing === "new" && (
        <Dialog title="New Session" onClose={() => setEditing(null)}>
          <SessionForm
            projects={projectsQuery.data?.projects ?? []}
            defaultDuration={settingsQuery.data?.default_duration_minutes ?? 90}
            defaultDate={info.monday.toISOString().slice(0, 10)}
            submitLabel="Save"
            error={formError?.message ?? null}
            onCancel={() => setEditing(null)}
            onSubmit={(v) => createMut.mutate(v)}
          />
        </Dialog>
      )}

      {editing && editing !== "new" && (
        <Dialog title="Edit Session" onClose={() => setEditing(null)}>
          <SessionForm
            projects={projectsQuery.data?.projects ?? []}
            initial={editing}
            defaultDuration={settingsQuery.data?.default_duration_minutes ?? 90}
            defaultDate={editing.scheduled_date}
            submitLabel="Save"
            error={formError?.message ?? null}
            onCancel={() => setEditing(null)}
            onSubmit={(v) => updateMut.mutate({ id: editing.id, v })}
          />
        </Dialog>
      )}

      {confirmDelete && (
        <ConfirmDialog
          title="Delete session"
          message={`Delete this session? This cannot be undone.`}
          confirmLabel="Delete"
          onCancel={() => setConfirmDelete(null)}
          onConfirm={() => {
            deleteMut.mutate(confirmDelete.id);
            setConfirmDelete(null);
          }}
        />
      )}
    </section>
  );
}
