import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { milestones as api, projects as projectApi } from "@/command-client";
import { isCommandError, type CommandError } from "@/command-client";
import type { Milestone, MilestoneStatus } from "@/contracts";
import { Dialog } from "@/components/dialogs/Dialog";
import { ConfirmDialog } from "@/components/dialogs/ConfirmDialog";
import { useInvalidate } from "@/hooks/useInvalidate";
import { weekKeyForDate } from "@/utils/week";
import { MilestoneForm, type MilestoneFormValues } from "./MilestoneForm";

const STATUSES: MilestoneStatus[] = ["backlog", "planned", "doing", "done", "cancelled"];

/** Sort cycle on the Milestone heading: none → ascending → descending → none. */
type SortMode = "none" | "asc" | "desc";
const NEXT_SORT: Record<SortMode, SortMode> = { none: "asc", asc: "desc", desc: "none" };
const SORT_INDICATOR: Record<SortMode, string> = { none: "", asc: " ▲", desc: " ▼" };

export function MilestonesView() {
  const [projectId, setProjectId] = useState<number | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [editing, setEditing] = useState<Milestone | "new" | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<Milestone | null>(null);
  const [bulkStatus, setBulkStatus] = useState<MilestoneStatus>("planned");
  const [sort, setSort] = useState<SortMode>("none");
  const [formError, setFormError] = useState<CommandError | null>(null);
  const { afterMilestoneMutation } = useInvalidate();

  const projectsQuery = useQuery({
    queryKey: ["projects", "all"],
    queryFn: () => projectApi.list(),
  });
  const milestonesQuery = useQuery({
    queryKey: ["milestones", projectId],
    queryFn: () => api.forProject(projectId!),
    enabled: projectId != null,
  });

  const createMut = useMutation({
    mutationFn: (v: MilestoneFormValues) =>
      api.create({ project_id: projectId!, ...v, sort_order: 0 }),
    onSuccess: () => {
      setEditing(null);
      setFormError(null);
      return afterMilestoneMutation();
    },
    onError: (err) => setFormError(isCommandError(err) ? err : null),
  });
  const updateMut = useMutation({
    mutationFn: ({ id, v }: { id: number; v: MilestoneFormValues }) => api.update(id, v),
    onSuccess: () => {
      setEditing(null);
      setFormError(null);
      return afterMilestoneMutation();
    },
    onError: (err) => setFormError(isCommandError(err) ? err : null),
  });
  const statusMut = useMutation({
    mutationFn: ({ id, status }: { id: number; status: MilestoneStatus }) =>
      api.setStatus(id, status),
    onSuccess: afterMilestoneMutation,
  });
  const deleteMut = useMutation({
    mutationFn: (id: number) => api.remove(id),
    onSuccess: () => {
      setSelectedId(null);
      return afterMilestoneMutation();
    },
  });

  // "none" keeps the server's sort_order, which is the authored sequence.
  const rows = useMemo(() => {
    const list = milestonesQuery.data?.milestones ?? [];
    if (sort === "none") return list;
    const sorted = [...list].sort((a, b) =>
      a.description.localeCompare(b.description, undefined, { sensitivity: "base" }),
    );
    return sort === "desc" ? sorted.reverse() : sorted;
  }, [milestonesQuery.data, sort]);

  const selected = rows.find((m) => m.id === selectedId) ?? null;

  return (
    <section aria-label="Milestones">
      <h2>Milestones</h2>

      <div className="toolbar">
        <label htmlFor="ms-project">Project</label>
        <select
          id="ms-project"
          value={projectId ?? ""}
          onChange={(e) => {
            setProjectId(e.target.value ? Number(e.target.value) : null);
            setSelectedId(null);
          }}
        >
          <option value="">Select a project…</option>
          {projectsQuery.data?.projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <span className="spacer" />
        <button
          className="primary"
          disabled={projectId == null}
          onClick={() => {
            setFormError(null);
            setEditing("new");
          }}
        >
          New Milestone
        </button>
      </div>

      {projectId != null && (
        <>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>
                    <button
                      type="button"
                      className="sort-btn"
                      aria-label={`Sort by milestone (${sort})`}
                      onClick={() => setSort(NEXT_SORT[sort])}
                    >
                      Milestone{SORT_INDICATOR[sort]}
                    </button>
                  </th>
                  <th>Target</th>
                  <th>Week</th>
                  <th>Total Min</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((m) => (
                  <tr
                    key={m.id}
                    className="row-clickable"
                    aria-selected={m.id === selectedId}
                    onClick={() => setSelectedId(m.id)}
                    onDoubleClick={() => {
                      setFormError(null);
                      setEditing(m);
                    }}
                  >
                    <td>{m.description}</td>
                    <td>{m.target_date ?? ""}</td>
                    <td>{(m.target_date && weekKeyForDate(m.target_date)) || ""}</td>
                    <td>{m.total_session_minutes || ""}</td>
                    <td className={`status-${m.status}`}>{m.status}</td>
                  </tr>
                ))}
                {rows.length === 0 && (
                  <tr>
                    <td colSpan={5}>No milestones for this project.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="action-bar">
            <label htmlFor="ms-bulk-status">Set Status:</label>
            <select
              id="ms-bulk-status"
              value={bulkStatus}
              onChange={(e) => setBulkStatus(e.target.value as MilestoneStatus)}
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            <button
              disabled={!selected}
              onClick={() =>
                selected && statusMut.mutate({ id: selected.id, status: bulkStatus })
              }
            >
              Apply
            </button>
            <button disabled={!selected} onClick={() => selected && setEditing(selected)}>
              Edit
            </button>
            <button
              className="danger"
              disabled={!selected}
              onClick={() => selected && setConfirmDelete(selected)}
            >
              Delete
            </button>
          </div>
        </>
      )}

      {editing === "new" && (
        <Dialog title="New Milestone" onClose={() => setEditing(null)}>
          <MilestoneForm
            submitLabel="Save"
            error={formError?.message ?? null}
            onCancel={() => setEditing(null)}
            onSubmit={(v) => createMut.mutate(v)}
          />
        </Dialog>
      )}

      {editing && editing !== "new" && (
        <Dialog title="Edit Milestone" onClose={() => setEditing(null)}>
          <MilestoneForm
            initial={editing}
            submitLabel="Save"
            error={formError?.message ?? null}
            onCancel={() => setEditing(null)}
            onSubmit={(v) => updateMut.mutate({ id: editing.id, v })}
          />
        </Dialog>
      )}

      {confirmDelete && (
        <ConfirmDialog
          title="Delete milestone"
          message={`Delete "${confirmDelete.description}"? This cannot be undone.`}
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
