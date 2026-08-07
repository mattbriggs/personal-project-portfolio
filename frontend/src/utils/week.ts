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

/**
 * ISO week number for a date (week containing the first Thursday).
 *
 * *date* is read as a UTC calendar date, matching {@link mondayOf} and the
 * UTC-based dates in {@link WeekInfo}. To go from a local wall-clock instant
 * (such as `new Date()`) use {@link utcCalendarDay} first.
 */
export function isoWeek(date: Date): { year: number; week: number } {
  const d = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
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

/**
 * The calendar day *instant* falls on in local time, as a UTC-midnight date.
 *
 * The backend keys weeks off a naive local `date`, so the renderer resolves
 * "which day is it" locally and only then hands the result to the UTC-based
 * helpers here.
 */
function utcCalendarDay(instant: Date): Date {
  return new Date(Date.UTC(instant.getFullYear(), instant.getMonth(), instant.getDate()));
}

/** Current week key. */
export function currentWeekKey(now: Date = new Date()): string {
  const { year, week } = isoWeek(utcCalendarDay(now));
  return `${year}.${week}`;
}

/**
 * Week key for a `YYYY-MM-DD` calendar date, or `null` when unparseable.
 *
 * The string is read as a plain calendar date with no timezone applied, so a
 * milestone's target date lands in the same week the backend assigns it.
 */
export function weekKeyForDate(iso: string): string | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso.trim());
  if (!match) return null;
  const [, y, m, d] = match;
  const date = new Date(Date.UTC(Number(y), Number(m) - 1, Number(d)));
  if (
    date.getUTCFullYear() !== Number(y) ||
    date.getUTCMonth() !== Number(m) - 1 ||
    date.getUTCDate() !== Number(d)
  ) {
    return null; // rolled over, e.g. 2026-02-30
  }
  const { year, week } = isoWeek(date);
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
