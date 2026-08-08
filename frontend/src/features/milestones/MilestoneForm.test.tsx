import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { Milestone } from "@/contracts";
import { MilestoneForm } from "./MilestoneForm";

const existing: Milestone = {
  id: 7,
  project_id: 1,
  description: "Outline approved",
  status: "planned",
  completed_date: null,
  target_date: "2026-04-08",
  sort_order: 0,
  notes: "some notes",
  total_session_minutes: 120,
  created_at: "",
  updated_at: "",
};

describe("MilestoneForm", () => {
  it("pre-fills every field in edit mode", () => {
    render(
      <MilestoneForm
        initial={existing}
        submitLabel="Save"
        onSubmit={vi.fn()}
        onCancel={vi.fn()}
      />,
    );

    expect(screen.getByLabelText("Milestone")).toHaveValue("Outline approved");
    expect(screen.getByLabelText("Target")).toHaveValue("2026-04-08");
    expect(screen.getByLabelText("Status")).toHaveValue("planned");
    expect(screen.getByLabelText("Description")).toHaveValue("some notes");
  });

  // The Tkinter dialog shows the week derived from the target date, updating live.
  it("shows the week derived from the target date", () => {
    render(
      <MilestoneForm
        initial={existing}
        submitLabel="Save"
        onSubmit={vi.fn()}
        onCancel={vi.fn()}
      />,
    );
    expect(screen.getByText(/Week: 2026\.15/)).toBeInTheDocument();
  });

  it("submits a null target date when cleared", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(
      <MilestoneForm
        initial={existing}
        submitLabel="Save"
        onSubmit={onSubmit}
        onCancel={vi.fn()}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Clear" }));
    await user.click(screen.getByRole("button", { name: "Save" }));

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ target_date: null, description: "Outline approved" }),
    );
  });

  it("rejects an empty description", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<MilestoneForm submitLabel="Save" onSubmit={onSubmit} onCancel={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: "Save" }));

    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent(/required/i);
  });
});
