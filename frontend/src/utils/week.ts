// ISO week-key helpers for the renderer.
//
// These mirror the backend's `YYYY.W` semantics for display and navigation only.
// The backend remains authoritative for any week key persisted with data.

export interface WeekInfo {
  key: string;
  year: number;
  week: number;
  monday: Date;
  sunday: Date;
  label: string;
}

/** ISO week number for a date (week containing the first Thursday). */
export function isoWeek(date: Date): { year: number; week: number } {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const day = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - day);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  const week = Math.ceil(((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7);
  return { year: d.getUTCFullYear(), week };
}

/** Monday (ISO) for a given year/week. */
export function mondayOf(year: number, week: number): Date {
  const jan4 = new Date(Date.UTC(year, 0, 4));
  const jan4Day = jan4.getUTCDay() || 7;
  const week1Monday = new Date(jan4);
  week1Monday.setUTCDate(jan4.getUTCDate() - (jan4Day - 1));
  const monday = new Date(week1Monday);
  monday.setUTCDate(week1Monday.getUTCDate() + (week - 1) * 7);
  return monday;
}

function fmt(d: Date): string {
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  });
}

/** Build a {@link WeekInfo} for a `YYYY.W` key. */
export function weekInfo(key: string): WeekInfo {
  const [yearStr, weekStr] = key.split(".");
  const year = Number(yearStr);
  const week = Number(weekStr);
  const monday = mondayOf(year, week);
  const sunday = new Date(monday);
  sunday.setUTCDate(monday.getUTCDate() + 6);
  return {
    key,
    year,
    week,
    monday,
    sunday,
    label: `${fmt(monday)} – ${fmt(sunday)}, ${sunday.getUTCFullYear()}`,
  };
}

/** Current week key. */
export function currentWeekKey(now: Date = new Date()): string {
  const { year, week } = isoWeek(now);
  return `${year}.${week}`;
}

/** Add (or subtract) whole weeks to a `YYYY.W` key. */
export function addWeeks(key: string, delta: number): string {
  const info = weekInfo(key);
  const shifted = new Date(info.monday);
  shifted.setUTCDate(info.monday.getUTCDate() + delta * 7);
  const { year, week } = isoWeek(shifted);
  return `${year}.${week}`;
}

/**
 * Build a navigable range of week keys: `past` weeks before the current week,
 * the current week, and `future` weeks after it.
 */
export function weekRange(
  currentKey: string,
  past: number,
  future: number,
): string[] {
  const keys: string[] = [];
  for (let i = -past; i <= future; i++) {
    keys.push(addWeeks(currentKey, i));
  }
  return keys;
}
