import { useState } from "react";
import { Dialog } from "@/components/dialogs/Dialog";

interface ExpandEditorProps {
  label: string;
  value: string;
  onDone: (value: string) => void;
  onCancel: () => void;
}

/**
 * Full-size editor for a single review field, matching the Tkinter expand
 * popup: edits are held locally and only copied back on **Done**, so Cancel
 * (or Escape) discards them.
 */
export function ExpandEditor({ label, value, onDone, onCancel }: ExpandEditorProps) {
  const [draft, setDraft] = useState(value);

  return (
    <Dialog title={label} onClose={onCancel}>
      <textarea
        aria-label={label}
        rows={14}
        style={{ width: "34rem", maxWidth: "80vw" }}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
      />
      <div className="dialog-actions">
        <button type="button" className="primary" onClick={() => onDone(draft)}>
          Done
        </button>
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </Dialog>
  );
}
