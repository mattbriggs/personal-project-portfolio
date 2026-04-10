# Configuration File Reference

Portfolio Manager stores its configuration in a TOML file at `~/.portfolio_manager/config.toml`. This topic describes all available keys and their default values.

## File Location

```
~/.portfolio_manager/config.toml
```

The file is created automatically on first launch. You can edit it in any text editor. Changes take effect on the next application launch unless noted otherwise.

## Configuration Keys

|Key|Type|Default|Description|
|---|----|-------|-----------|
|`[app] log_level`|String|`"INFO"`|Logging verbosity. Valid values: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`.|
|`[app] theme`|String|`"light"`|UI color theme. Currently only `"light"` is implemented.|
|`[session] default_duration_minutes`|Integer|`90`|Default session duration when creating a new session. Range: 15–480.|
|`[session] weekly_budget_hours`|Integer|`12`|Weekly time budget in hours. Range: 1–100.|
|`[database] path`|String|`"~/.portfolio_manager/portfolio.db"`|Path to the SQLite database file. Changing this value requires a restart. The directory must exist and be writable.|

## Default Configuration File

```
[app]
log_level = "INFO"
theme = "light"

[session]
default_duration_minutes = 90
weekly_budget_hours = 12

[database]
path = "~/.portfolio_manager/portfolio.db"
```

## Data File Locations

|File or Directory|Purpose|
|-----------------|-------|
|`~/.portfolio_manager/config.toml`|Application configuration.|
|`~/.portfolio_manager/portfolio.db`|SQLite database containing all projects, sessions, milestones, scores, and reviews.|
|`~/.portfolio_manager/portfolio.db.bak`|Backup of the database created before schema migrations.|
|`~/.portfolio_manager/logs/`|Application log files \(rotating\).|

