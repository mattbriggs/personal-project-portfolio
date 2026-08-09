import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { projects as api } from "@/command-client";
import { isCommandError } from "@/command-client";
import { PlanPreview } from "./PlanPreview";

type Mode = "edit" | "preview" | "split";

// Plan editor with raw Markdown editing, preview, and split modes. The draft is
// preserved after a failed save (SRS §5.10).
export function PlanEditor({
  projectId,
  readOnly,
  onClose,
}: {
  projectId: number;
  readOnly: boolean;
  onClose: () => void;
}) {
  const [mode, setMode] = useState<Mode>("split");
  const [draft, setDraft] = useState<string>("");
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["plan", projectId],
    queryFn: () => api.getPlan(projectId),
  });

  useEffect(() => {
    if (data) setDraft(data.content);
  }, [data]);

  const saveMut = useMutation({
    mutationFn: (content: string) => api.savePlan(projectId, content),
    onSuccess: () => {
      setSaved(true);
      setSaveError(null);
    },
    onError: (err) => {
      // Draft is retained; only surface the error.
      setSaveError(isCommandError(err) ? err.message : "Save failed.");
    },
  });

  if (isLoading) return <p>Loading plan…</p>;

  return (
    <div style={{ minWidth: 640, display: "flex", flexDirection: "column", gap: 12 }}>
      <div className="seg" role="group" aria-label="Preview mode" style={{ alignSelf: "flex-start" }}>
        {(["edit", "preview", "split"] as Mode[]).map((m) => (
          <button
            key={m}
            type="button"
            className="seg-opt"
            aria-pressed={mode === m}
            onClick={() => setMode(m)}
          >
            {m[0].toUpperCase() + m.slice(1)}
          </button>
        ))}
      </div>

      {saveError && (
        <p className="field-error" role="alert">
          {saveError} — your draft has been kept.
        </p>
      )}
      {saved && (
        <p role="status" className="dialog-body">
          Plan saved.
        </p>
      )}

      <div style={{ display: "flex", gap: 16, minHeight: 280 }}>
        {(mode === "edit" || mode === "split") && (
          <textarea
            aria-label="Plan Markdown"
            style={{ flex: 1, minHeight: 280, fontFamily: "monospace", fontSize: 13 }}
            value={draft}
            readOnly={readOnly}
            onChange={(e) => {
              setDraft(e.target.value);
              setSaved(false);
            }}
          />
        )}
        {(mode === "preview" || mode === "split") && (
          <div
            style={{
              flex: 1,
              borderLeft: "2px solid var(--color-divider)",
              paddingLeft: 16,
              overflowY: "auto",
            }}
          >
            <PlanPreview content={draft} />
          </div>
        )}
      </div>

      <div className="dialog-actions">
        <button type="button" className="btn btn-secondary" onClick={onClose}>
          Close
        </button>
        {!readOnly && (
          <button
            className="btn btn-primary"
            disabled={saveMut.isPending}
            onClick={() => saveMut.mutate(draft)}
          >
            Save plan
          </button>
        )}
      </div>
    </div>
  );
}
