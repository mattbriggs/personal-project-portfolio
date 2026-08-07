import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { settings as api } from "@/command-client";
import type { Settings } from "@/contracts";
import { isCommandError, type CommandError } from "@/command-client";
import { useInvalidate } from "@/hooks/useInvalidate";

export function SettingsView() {
  const { afterSettingsMutation } = useInvalidate();
  const [draft, setDraft] = useState<Settings | null>(null);
  const [error, setError] = useState<CommandError | null>(null);

  const query = useQuery({ queryKey: ["settings"], queryFn: () => api.get() });
  useEffect(() => {
    if (query.data) setDraft(query.data);
  }, [query.data]);

  const saveMut = useMutation({
    mutationFn: (s: Settings) =>
      api.update({
        log_level: s.log_level,
        theme: s.theme,
        default_duration_minutes: s.default_duration_minutes,
        weekly_budget_hours: s.weekly_budget_hours,
        database_path: s.database_path,
      }),
    onSuccess: (updated) => {
      setDraft(updated);
      setError(null);
      return afterSettingsMutation();
    },
    // Form values are kept on error so the user does not lose edits.
    onError: (err) => setError(isCommandError(err) ? err : null),
  });

  if (!draft) return <p>Loading settings…</p>;

  const restartRequired =
    draft.active_database_path !== "" &&
    draft.resolved_database_path !== draft.active_database_path;

  return (
    <section aria-label="Settings">
      <h2>Settings</h2>
      {error && (
        <p className="field-error" role="alert">
          {error.message} — settings were not saved.
        </p>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          saveMut.mutate(draft);
        }}
      >
        <div className="field">
          <label htmlFor="set-log">Log level</label>
          <select
            id="set-log"
            value={draft.log_level}
            onChange={(e) => setDraft({ ...draft, log_level: e.target.value })}
          >
            {["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"].map((l) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="set-theme">Theme</label>
          <select
            id="set-theme"
            value={draft.theme}
            onChange={(e) => setDraft({ ...draft, theme: e.target.value })}
          >
            <option value="light">light</option>
            <option value="dark">dark</option>
          </select>
        </div>
        <div className="field">
          <label htmlFor="set-dur">Default session duration (15–480)</label>
          <input
            id="set-dur"
            type="number"
            min={15}
            max={480}
            value={draft.default_duration_minutes}
            onChange={(e) =>
              setDraft({ ...draft, default_duration_minutes: Number(e.target.value) })
            }
          />
        </div>
        <div className="field">
          <label htmlFor="set-budget">Weekly budget hours (1–100)</label>
          <input
            id="set-budget"
            type="number"
            min={1}
            max={100}
            value={draft.weekly_budget_hours}
            onChange={(e) =>
              setDraft({ ...draft, weekly_budget_hours: Number(e.target.value) })
            }
          />
        </div>
        <div className="field">
          <label htmlFor="set-db">Database path</label>
          <input
            id="set-db"
            value={draft.database_path}
            onChange={(e) => setDraft({ ...draft, database_path: e.target.value })}
          />
          <small>Resolved: {draft.resolved_database_path}</small>
          <small>Currently active: {draft.active_database_path || "(in-memory)"}</small>
        </div>

        {restartRequired && (
          <p role="alert" className="field-error">
            The database path change will take effect after a restart. The app is still
            using <code>{draft.active_database_path}</code>.
          </p>
        )}

        <button type="submit" className="primary" disabled={saveMut.isPending}>
          Save settings
        </button>
        {saveMut.isSuccess && <span role="status"> Saved.</span>}
      </form>
    </section>
  );
}
