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
    <div style={{ minWidth: 640 }}>
      <div role="group" aria-label="Preview mode" style={{ marginBottom: 8 }}>
        {(["edit", "preview", "split"] as Mode[]).map((m) => (
          <button key={m} aria-current={mode === m} className="tab-btn" onClick={() => setMode(m)}>
            {m}
          </button>
        ))}
      </div>

      {saveError && (
        <p className="field-error" role="alert">
          {saveError} — your draft has been kept.
        </p>
      )}
      {saved && <p role="status">Plan saved.</p>}

      <div style={{ display: "flex", gap: 12 }}>
        {(mode === "edit" || mode === "split") && (
          <textarea
            aria-label="Plan Markdown"
            style={{ flex: 1, minHeight: 320, fontFamily: "monospace" }}
            value={draft}
            readOnly={readOnly}
            onChange={(e) => {
              setDraft(e.target.value);
              setSaved(false);
            }}
          />
        )}
        {(mode === "preview" || mode === "split") && (
          <div style={{ flex: 1, borderLeft: "1px solid var(--border)", paddingLeft: 12 }}>
            <PlanPreview content={draft} />
          </div>
        )}
      </div>

      <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 12 }}>
        <button onClick={onClose}>Close</button>
        {!readOnly && (
          <button
            className="primary"
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
