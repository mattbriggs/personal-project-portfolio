import { describe, expect, it } from "vitest";
import { addWeeks, currentWeekKey, weekInfo, weekRange } from "./week";

describe("week utils", () => {
  it("computes the ISO date range for a key", () => {
    const info = weekInfo("2026.15");
    expect(info.monday.toISOString().slice(0, 10)).toBe("2026-04-06");
    expect(info.sunday.toISOString().slice(0, 10)).toBe("2026-04-12");
  });

  it("adds and subtracts whole weeks", () => {
    expect(addWeeks("2026.15", 1)).toBe("2026.16");
    expect(addWeeks("2026.1", -1)).toBe("2025.52");
  });

  it("builds a range of 12 past + current + 4 future = 17 weeks", () => {
    const keys = weekRange("2026.20", 12, 4);
    expect(keys).toHaveLength(17);
    expect(keys[12]).toBe("2026.20");
  });

  it("returns a valid current week key", () => {
    expect(currentWeekKey(new Date("2026-04-07T12:00:00Z"))).toBe("2026.15");
  });
});
