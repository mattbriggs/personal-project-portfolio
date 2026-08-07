# End-to-end tests

Cross-process tests that drive the packaged (or dev) Tauri app. These require a
built desktop app and a WebDriver-capable runner (WebdriverIO + `tauri-driver`),
which need a Rust ≥ 1.85 toolchain and macOS WebKit libraries.

## Required workflow (SRS §7.7)

1. Launch the app; confirm the sidecar reaches **ready**.
2. Create an active project.
3. Add a milestone.
4. Add a planned session for the selected week.
5. Verify weekly budget and dashboard planned count.
6. Mark the session **done**.
7. Mark the milestone **done**.
8. Verify score recomputation.
9. Add Markdown plan content with a Mermaid block; verify preview.
10. Save a weekly review.
11. Restart the app; verify persisted data remains.

## Additional cases

- Invalid form retains entered values.
- Delete requires confirmation.
- Sidecar startup failure / runtime termination shows the degraded UI.
- Offline operation (including Mermaid preview) works.
- An existing Tkinter database opens without manual conversion.

The backend half of this workflow is already covered in-process by
`backend/tests/contract/test_workflow_api.py`. The E2E harness adds the Tauri
shell and renderer once the desktop build is available.
