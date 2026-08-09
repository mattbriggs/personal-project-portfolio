import { Dialog } from "./Dialog";

// Confirmation gate for destructive actions (delete/archive). Backend
// authorization does not depend on this — it is purely a UI safeguard.
interface ConfirmDialogProps {
  title: string;
  message: string;
  confirmLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  title,
  message,
  confirmLabel = "Confirm",
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  return (
    <Dialog title={title} onClose={onCancel}>
      <p className="dialog-body">{message}</p>
      <div className="dialog-actions">
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button type="button" className="btn btn-primary" onClick={onConfirm}>
          {confirmLabel}
        </button>
      </div>
    </Dialog>
  );
}
