import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { milestones as api, projects as projectApi } from "@/command-client";
import type { MilestoneStatus } from "@/contracts";
import { ConfirmDialog } from "@/components/dialogs/ConfirmDialog";
import { useInvalidate } from "@/hooks/useInvalidate";

const STATUSES: MilestoneStatus[] = ["backlog", "planned", "doing", "done", "cancelled"];

export function MilestonesView() {
  const [projectId, setProjectId] = useState<number | null>(null);
  const [newDesc, setNewDesc] = useState("");
  const [confirmId, setConfirmId] = useState<number | null>(null);
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
    mutationFn: () =>
      api.create({ project_id: projectId!, description: newDesc, sort_order: 0 }),
    onSuccess: () => {
      setNewDesc("");
      return afterMilestoneMutation();
    },
  });
  const statusMut = useMutation({
    mutationFn: ({ id, status }: { id: number; status: MilestoneStatus }) =>
      api.setStatus(id, status),
    onSuccess: afterMilestoneMutation,
  });
  const deleteMut = useMutation({
    mutationFn: (id: number) => api.remove(id),
    onSuccess: afterMilestoneMutation,
  });

  return (
    <section aria-label="Milestones">
      <h2>Milestones</h2>
      <div className="field">
        <label htmlFor="ms-project">Project</label>
        <select
          id="ms-project"
          value={projectId ?? ""}
          onChange={(e) => setProjectId(e.target.value ? Number(e.target.value) : null)}
        >
          <option value="">Select a project…</option>
          {projectsQuery.data?.projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      {projectId != null && (
        <>
          <table>
            <thead>
              <tr>
                <th>Order</th>
                <th>Description</th>
                <th>Status</th>
                <th>Session minutes</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {milestonesQuery.data?.milestones.map((m) => (
                <tr key={m.id}>
                  <td>{m.sort_order}</td>
                  <td>{m.description}</td>
                  <td>
                    <select
                      aria-label={`Status for ${m.description}`}
                      value={m.status}
                      onChange={(e) =>
                        statusMut.mutate({
                          id: m.id,
                          status: e.target.value as MilestoneStatus,
                        })
                      }
                    >
                      {STATUSES.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td>{m.total_session_minutes}</td>
                  <td>
                    <button className="danger" onClick={() => setConfirmId(m.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="field" style={{ marginTop: 12 }}>
            <label htmlFor="ms-new">New milestone</label>
            <input
              id="ms-new"
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              placeholder="Outcome description"
            />
            <button
              className="primary"
              disabled={!newDesc.trim()}
              onClick={() => createMut.mutate()}
            >
              Add milestone
            </button>
          </div>
        </>
      )}

      {confirmId != null && (
        <ConfirmDialog
          title="Delete milestone"
          message="Delete this milestone? This cannot be undone."
          confirmLabel="Delete"
          onCancel={() => setConfirmId(null)}
          onConfirm={() => {
            deleteMut.mutate(confirmId);
            setConfirmId(null);
          }}
        />
      )}
    </section>
  );
}
