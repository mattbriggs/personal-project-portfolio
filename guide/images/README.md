# Guide Images

This folder contains Mermaid diagram source files (`.mmd`) and the PNG images referenced in
the DITA topics. The PNG files must be generated from the `.mmd` sources before building
the guide.

## Source Files

| Source file             | Referenced PNG               | Topic(s) that use it                     |
|-------------------------|------------------------------|------------------------------------------|
| `portfolio-overview.mmd`| `portfolio-overview.png`     | `c_portfolio_paradigm.dita`              |
| `project-lifecycle.mmd` | `project-lifecycle.png`      | `c_project_lifecycle.dita`               |
| `session-lifecycle.mmd` | `session-lifecycle.png`      | `c_session_paradigm.dita`                |
| `milestone-lifecycle.mmd`| `milestone-lifecycle.png`   | `c_milestone_paradigm.dita`              |
| `scoring-model.mmd`     | `scoring-model.png`          | `c_scoring_model.dita`, `r_scoring_algorithm.dita` |
| `weekly-workflow.mmd`   | `weekly-workflow.png`        | `p_weekly_workflow.dita`                 |
| `app-layout.mmd`        | `app-layout.png`             | `r_ui_reference.dita`                    |

## Generating PNGs

### Using Mermaid CLI (mmdc)

Install the Mermaid CLI globally:

```bash
npm install -g @mermaid-js/mermaid-cli
```

Generate all PNGs from this directory:

```bash
cd guide/images
for f in *.mmd; do
    mmdc -i "$f" -o "${f%.mmd}.png" -b white -w 1200
done
```

### Using the Mermaid Live Editor

1. Open [https://mermaid.live](https://mermaid.live).
2. Paste the contents of the `.mmd` file into the editor.
3. Download the rendered diagram as a PNG.
4. Save it to this folder with the filename shown in the table above.

## Image Dimensions

Recommended output dimensions for DITA PDF rendering:

- Width: 1200px minimum
- Background: white (`-b white` flag for mmdc)
- Scale: 2 for retina displays (`-s 2` flag for mmdc)
