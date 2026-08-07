import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ProjectForm } from "./ProjectForm";

describe("ProjectForm", () => {
  it("retains entered values after a validation error", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockRejectedValue({
      code: "VALIDATION_ERROR",
      message: "Name is invalid.",
      field_errors: { name: ["must not be empty"] },
    });

    render(
      <ProjectForm submitLabel="Create" onSubmit={onSubmit} onCancel={() => {}} />,
    );

    const nameInput = screen.getByLabelText("Name") as HTMLInputElement;
    await user.type(nameInput, "My Draft");
    await user.click(screen.getByRole("button", { name: "Create" }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalled());
    // Value is preserved and the field-level error is shown.
    expect(nameInput.value).toBe("My Draft");
    expect(screen.getByText("Name is invalid.")).toBeInTheDocument();
    expect(screen.getByText("must not be empty")).toBeInTheDocument();
  });

  it("submits entered values on success", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <ProjectForm submitLabel="Create" onSubmit={onSubmit} onCancel={() => {}} />,
    );
    await user.type(screen.getByLabelText("Name"), "Ok Project");
    await user.click(screen.getByRole("button", { name: "Create" }));
    await waitFor(() =>
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ name: "Ok Project", priority: 3, status: "active" }),
      ),
    );
  });
});
