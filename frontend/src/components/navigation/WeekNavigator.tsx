import { useState } from "react";
import { useWorkspace } from "@/state/workspace";
import { currentWeekKey, weekInfo, weekRange } from "@/utils/week";

// Left-rail week navigator: shows 12 past weeks, the current week, and >=4
// future weeks; "Load more" adds 4 future weeks per request (SRS §5.6).
const PAST = 12;
const INITIAL_FUTURE = 4;
const FUTURE_STEP = 4;

export function WeekNavigator() {
  const { selectedWeek, setSelectedWeek } = useWorkspace();
  const [future, setFuture] = useState(INITIAL_FUTURE);
  const current = currentWeekKey();
  const keys = weekRange(current, PAST, future);

  return (
    <nav className="week-rail" aria-label="Week navigator">
      <h2 style={{ fontSize: 12, textTransform: "uppercase", color: "var(--muted)" }}>
        Weeks
      </h2>
      <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
        {keys.map((key) => {
          const info = weekInfo(key);
          const isCurrent = key === selectedWeek;
          return (
            <li key={key}>
              <button
                type="button"
                className="week-item"
                aria-current={isCurrent}
                onClick={() => setSelectedWeek(key)}
              >
                <span>
                  {info.year}.W{info.week}
                  {key === current ? " (now)" : ""}
                </span>
                <span className="range">{info.label}</span>
              </button>
            </li>
          );
        })}
      </ul>
      <button
        type="button"
        onClick={() => setFuture((f) => f + FUTURE_STEP)}
        style={{ marginTop: 8 }}
      >
        Load more weeks
      </button>
    </nav>
  );
}
