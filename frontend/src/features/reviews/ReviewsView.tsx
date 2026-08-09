import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { reviews as api } from "@/command-client";
import type { WeeklyReview } from "@/contracts";
import { useInvalidate } from "@/hooks/useInvalidate";
import { useWorkspace } from "@/state/workspace";
import { ExpandEditor } from "./ExpandEditor";

const TEXT_FIELDS: { key: keyof WeeklyReview; label: string }[] = [
  { key: "what_moved", label: "What moved" },
  { key: "what_stalled", label: "What stalled" },
  { key: "signals", label: "Signals" },
  { key: "decision_next_week", label: "Decision next week" },
  { key: "primary_focus", label: "Primary focus" },
  { key: "project_to_deprioritize", label: "Project to deprioritize" },
  { key: "risk_to_watch", label: "Risk to watch" },
  { key: "first_session_target", label: "First session target" },
];

export function ReviewsView() {
  const { selectedWeek } = useWorkspace();
  const { afterReviewMutation } = useInvalidate();
  const [draft, setDraft] = useState<WeeklyReview | null>(null);
  const [expanded, setExpanded] = useState<(typeof TEXT_FIELDS)[number] | null>(null);

  const reviewQuery = useQuery({
    queryKey: ["review", selectedWeek],
    queryFn: () => api.getOrCreate(selectedWeek),
  });
  const historyQuery = useQuery({
    queryKey: ["reviews"],
    queryFn: () => api.list(),
  });

  useEffect(() => {
    if (reviewQuery.data) setDraft(reviewQuery.data);
  }, [reviewQuery.data]);

  const saveMut = useMutation({
    mutationFn: (r: WeeklyReview) =>
      api.save(selectedWeek, {
        hours_invested: r.hours_invested,
        sessions_completed: r.sessions_completed,
        what_moved: r.what_moved,
        what_stalled: r.what_stalled,
        signals: r.signals,
        decision_next_week: r.decision_next_week,
        primary_focus: r.primary_focus,
        project_to_deprioritize: r.project_to_deprioritize,
        risk_to_watch: r.risk_to_watch,
        first_session_target: r.first_session_target,
        written_to_repo: r.written_to_repo,
      }),
    onSuccess: afterReviewMutation,
  });

  if (!draft) return <p>Loading review…</p>;

  const set = <K extends keyof WeeklyReview>(key: K, value: WeeklyReview[K]) =>
    setDraft({ ...draft, [key]: value });

  return (
    <section aria-label="Weekly review">
      <h2>Weekly review</h2>
      <p className="view-sub">
        {selectedWeek} · {draft.date_from} to {draft.date_to}
        {draft.id === 0 && " (not yet saved)"}
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          saveMut.mutate(draft);
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "var(--space-4)",
            maxWidth: 480,
          }}
        >
          <div className="field">
            <label htmlFor="r-hours">Hours invested</label>
            <input
              id="r-hours"
              type="number"
              step="0.5"
              value={draft.hours_invested}
              onChange={(e) => set("hours_invested", Number(e.target.value))}
            />
          </div>
          <div className="field">
            <label htmlFor="r-sessions">Sessions completed</label>
            <input
              id="r-sessions"
              type="number"
              value={draft.sessions_completed}
              onChange={(e) => set("sessions_completed", Number(e.target.value))}
            />
          </div>
        </div>
        {TEXT_FIELDS.map((f) => (
          <div className="field" key={f.key}>
            <div className="field-row" style={{ alignItems: "baseline" }}>
              <label htmlFor={`r-${f.key}`} style={{ marginBottom: 0 }}>
                {f.label}
              </label>
              <span className="spacer" />
              <button
                type="button"
                className="btn btn-ghost"
                aria-label={`Expand ${f.label}`}
                title={`Expand ${f.label}`}
                onClick={() => setExpanded(f)}
              >
                ⤢
              </button>
            </div>
            <textarea
              id={`r-${f.key}`}
              rows={3}
              value={String(draft[f.key] ?? "")}
              onChange={(e) => set(f.key, e.target.value as never)}
            />
          </div>
        ))}
        <div className="field" style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
          <input
            id="r-written"
            type="checkbox"
            checked={draft.written_to_repo}
            onChange={(e) => set("written_to_repo", e.target.checked)}
          />
          <label htmlFor="r-written" style={{ margin: 0 }}>
            Written to repository
          </label>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 8 }}>
          <button type="submit" className="btn btn-primary" disabled={saveMut.isPending}>
            Save review
          </button>
          {saveMut.isSuccess && <span role="status">Saved.</span>}
        </div>
      </form>

      <h3 style={{ marginTop: 32 }}>History</h3>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {historyQuery.data?.reviews.map((r) => (
          <p key={r.week_key} style={{ margin: 0, fontSize: 13 }}>
            {r.week_key} — {r.hours_invested}h, {r.sessions_completed} sessions
          </p>
        ))}
      </div>

      {expanded && draft && (
        <ExpandEditor
          label={expanded.label}
          value={String(draft[expanded.key] ?? "")}
          onCancel={() => setExpanded(null)}
          onDone={(value) => {
            set(expanded.key, value as never);
            setExpanded(null);
          }}
        />
      )}
    </section>
  );
}
