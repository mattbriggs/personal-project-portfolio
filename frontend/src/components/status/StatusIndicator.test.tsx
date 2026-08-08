import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatusIndicator } from "./StatusIndicator";

describe("StatusIndicator", () => {
  it("conveys status with text, not color alone", () => {
    render(<StatusIndicator status="green" />);
    expect(screen.getByText("On track")).toBeInTheDocument();
    expect(screen.getByLabelText("On track")).toBeInTheDocument();
  });

  it("labels the red status", () => {
    render(<StatusIndicator status="red" />);
    expect(screen.getByText("Behind")).toBeInTheDocument();
  });
});
