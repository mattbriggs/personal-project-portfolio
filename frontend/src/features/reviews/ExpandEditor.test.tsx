import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ExpandEditor } from "./ExpandEditor";

describe("ExpandEditor", () => {
  it("copies the edited text back only on Done", async () => {
    const onDone = vi.fn();
    const user = userEvent.setup();
    render(
      <ExpandEditor
        label="What moved"
        value="before"
        onDone={onDone}
        onCancel={vi.fn()}
      />,
    );

    const box = screen.getByRole("textbox");
    await user.clear(box);
    await user.type(box, "after");
    await user.click(screen.getByRole("button", { name: "Done" }));

    expect(onDone).toHaveBeenCalledWith("after");
  });

  // The Tkinter popup discards edits on Cancel; the caller keeps its own value.
  it("discards edits on Cancel", async () => {
    const onDone = vi.fn();
    const onCancel = vi.fn();
    const user = userEvent.setup();
    render(
      <ExpandEditor
        label="Signals"
        value="before"
        onDone={onDone}
        onCancel={onCancel}
      />,
    );

    await user.type(screen.getByRole("textbox"), " edited");
    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(onCancel).toHaveBeenCalled();
    expect(onDone).not.toHaveBeenCalled();
  });
});
