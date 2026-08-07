import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { WeekNavigator } from "./WeekNavigator";
import { WorkspaceProvider } from "@/state/workspace";

function renderNav() {
  return render(
    <WorkspaceProvider>
      <WeekNavigator />
    </WorkspaceProvider>,
  );
}

describe("WeekNavigator", () => {
  it("shows 12 past + current + 4 future weeks initially (17 items)", () => {
    renderNav();
    const items = screen.getAllByRole("button").filter((b) =>
      b.className.includes("week-item"),
    );
    expect(items).toHaveLength(17);
  });

  it("loads 4 more future weeks per request", async () => {
    const user = userEvent.setup();
    renderNav();
    await user.click(screen.getByRole("button", { name: /load more weeks/i }));
    const items = screen.getAllByRole("button").filter((b) =>
      b.className.includes("week-item"),
    );
    expect(items).toHaveLength(21);
  });

  it("marks a selected week as current", async () => {
    const user = userEvent.setup();
    renderNav();
    const items = screen
      .getAllByRole("button")
      .filter((b) => b.className.includes("week-item"));
    await user.click(items[0]);
    expect(items[0]).toHaveAttribute("aria-current", "true");
  });
});
