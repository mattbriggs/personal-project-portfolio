# Configure Application Settings

Adjust the weekly time budget, default session duration, and other application preferences using the Settings tab.

1.  Click the **Settings** tab.

2.  In the **Weekly budget \(hours\)** spinbox, enter the number of hours you have available for personal projects each week.

    Set this to a number you can reliably achieve, not an aspirational target. The budget is a planning guide, not a quota.

3.  In the **Default session duration \(minutes\)** spinbox, enter your typical session length.

    This value pre-fills the duration field when you create a new session. Valid values are 15 to 480 minutes.

4.  In the **Log level** dropdown, select the logging verbosity.

    -   **ERROR** — logs only application errors \(recommended for daily use\).
    -   **WARNING** — logs errors and warnings.
    -   **INFO** — logs normal application events.
    -   **DEBUG** — logs all events including internal state changes \(for troubleshooting only\).
5.  Click **Save**.

    Settings are applied immediately. Changes to the weekly budget are reflected in the budget bar on the Sessions tab.


Settings are persisted in `~/.portfolio_manager/config.toml`. You can also edit this file directly in a text editor. See [Configuration File Reference](r_config_file.md) for the full list of configuration keys and their valid values.

