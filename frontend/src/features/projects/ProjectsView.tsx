import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { projects as api } from "@/command-client";
import type { Project, ProjectStatus } from "@/contracts";
import { Dialog } from "@/components/dialogs/Dialog";
import { ConfirmDialog } from "@/components/dialogs/ConfirmDialog";
import { useInvalidate } from "@/hooks/useInvalidate";
import { ProjectForm, type ProjectFormValues } from "./ProjectForm";
import { PlanEditor } from "@/features/plans/PlanEditor";

type Filter = ProjectStatus | "all";

export function ProjectsView() {
  const [filter, setFilter] = useState<Filter>("active");
  const [editing, setEditing] = useState<Project | "new" | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<Project | null>(null);
  const [planFor, setPlanFor] = useState<Project | null>(null);
  const { afterProjectMutation } = useInvalidate();

  const { data, isLoading } = useQuery({
    queryKey: ["projects", filter],
    queryFn: () => api.list(filter === "all" ? undefined : filter),
  });

  const createMut = useMutation({
    mutationFn: (v: ProjectFormValues) => api.create(v),
    onSuccess: afterProjectMutation,
  });
  const updateMut = useMutation({
    mutationFn: ({ id, v }: { id: number; v: ProjectFormValues }) =>
      api.update(id, v),
    onSuccess: afterProjectMutation,
  });
  const archiveMut = useMutation({
    mutationFn: (id: number) => api.archive(id),
    onSuccess: afterProjectMutation,
  });
  const deleteMut = useMutation({
    mutationFn: (id: number) => api.remove(id),
    onSuccess: afterProjectMutation,
  });

  const filters: Filter[] = ["active", "backlog", "archive", "all"];

  return (
    <section aria-label="Projects">
      <h2>Projects</h2>
      <div role="group" aria-label="Project filters" style={{ marginBottom: 12 }}>
        {filters.map((f) => (
          <button
            key={f}
            aria-current={filter === f}
            className="tab-btn"
            onClick={() => setFilter(f)}
          >
            {f[0].toUpperCase() + f.slice(1)}
          </button>
        ))}
        <button className="primary" onClick={() => setEditing("new")}>
          New project
        </button>
      </div>

      {isLoading ? (
        <p>Loading…</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {data?.projects.map((p) => {
              const archived = p.status === "archive";
              return (
                <tr key={p.id}>
                  <td>{p.name}</td>
                  <td>{p.status}</td>
                  <td>{p.priority}</td>
                  <td>
                    <button onClick={() => setPlanFor(p)}>Plan</button>{" "}
                    <button onClick={() => setEditing(p)} disabled={archived}>
                      {archived ? "View" : "Edit"}
                    </button>{" "}
                    {!archived && (
                      <button onClick={() => archiveMut.mutate(p.id)}>Archive</button>
                    )}{" "}
                    <button className="danger" onClick={() => setConfirmDelete(p)}>
                      Delete
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      {editing === "new" && (
        <Dialog title="New project" onClose={() => setEditing(null)}>
          <ProjectForm
            submitLabel="Create"
            onCancel={() => setEditing(null)}
            onSubmit={async (v) => {
              await createMut.mutateAsync(v);
              setEditing(null);
            }}
          />
        </Dialog>
      )}

      {editing && editing !== "new" && (
        <Dialog
          title={editing.status === "archive" ? "Project (read-only)" : "Edit project"}
          onClose={() => setEditing(null)}
        >
          {editing.status === "archive" ? (
            <div>
              <p>
                <strong>{editing.name}</strong> is archived and read-only.
              </p>
              <p>{editing.description}</p>
              <button onClick={() => setEditing(null)}>Close</button>
            </div>
          ) : (
            <ProjectForm
              initial={editing}
              submitLabel="Save"
              onCancel={() => setEditing(null)}
              onSubmit={async (v) => {
                await updateMut.mutateAsync({ id: editing.id, v });
                setEditing(null);
              }}
            />
          )}
        </Dialog>
      )}

      {confirmDelete && (
        <ConfirmDialog
          title="Delete project"
          message={`Permanently delete "${confirmDelete.name}" and all its sessions and milestones? This cannot be undone.`}
          confirmLabel="Delete"
          onCancel={() => setConfirmDelete(null)}
          onConfirm={() => {
            deleteMut.mutate(confirmDelete.id);
            setConfirmDelete(null);
          }}
        />
      )}

      {planFor && (
        <Dialog title={`Plan — ${planFor.name}`} onClose={() => setPlanFor(null)}>
          <PlanEditor
            projectId={planFor.id}
            readOnly={planFor.status === "archive"}
            onClose={() => setPlanFor(null)}
          />
        </Dialog>
      )}
    </section>
  );
}
