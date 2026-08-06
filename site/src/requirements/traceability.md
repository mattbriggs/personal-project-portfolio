# Requirement Traceability

Maps representative SRS requirements to their implementation and at least one
automated verification. This is a living document; extend it as requirements are
formally enumerated.

## Security (NFR-SEC)

| Requirement | Implementation | Test |
| --- | --- | --- |
| Per-launch random token | `src-tauri/src/security/token.rs` | `token_has_expected_length_and_entropy` |
| Dynamic loopback port | `src-tauri/src/security/port.rs` | `picks_a_nonzero_loopback_port` |
| Token via env, not argv | `src-tauri/src/sidecar/launcher.rs` | `argv_excludes_token_and_includes_port` |
| Token only in runtime state | `src-tauri/src/app_state.rs` (`SecretString`) | `logging::redact` tests |
| Token never logged | `.../logging.rs`; `infrastructure/logging/filters.py` | `redacts_long_and_short_secrets`; redaction filter |
| Loopback-only bind | `backend/.../cli/sidecar.py` (`HOST=127.0.0.1`) | manual smoke; CLI constant |
| Protected routes reject missing token | `api/middleware/authentication.py` | `test_business_route_requires_token` |
| Protected routes reject invalid token | same | `test_business_route_rejects_wrong_token` |
| Production docs disabled | `api/app.py` | `test_docs_disabled_in_production` |
| Renderer cannot call sidecar directly | Tauri command allowlist | `scripts/verify_no_renderer_http.py` |
| Sanitized unexpected errors | `api/exception_handlers.py` | `_unexpected` handler; contract error tests |

## Sessions (FR-SESS)

| Requirement | Implementation | Test |
| --- | --- | --- |
| Week key derived from date | `domain/week.py`, `SessionService` | `test_create_derives_week_key` |
| Duration bounds 15–480 | `SessionService`, `contracts/sessions.py` | `test_duration_bounds` |
| Default duration applied | `api/routes/sessions.py` | `test_session_default_duration_applied` |
| Entering done sets completed_at | `SessionService.set_status` | `test_entering_done_sets_completed_at` |
| Leaving done clears completed_at | same | `test_leaving_done_clears_completed_at` |
| Reschedule recomputes week key | `SessionService.reschedule_session` | `test_reschedule_recomputes_week_key` |
| Archived project blocks sessions | `SessionService._require_active_project` | `test_archived_project_blocks_session_create` |
| Milestone must belong to project | `SessionService._validate_milestone` | `test_milestone_must_belong_to_project` |

## Projects (FR-PROJ)

| Requirement | Implementation | Test |
| --- | --- | --- |
| Name required, slug generated | `ProjectService.create_project`, `domain/slug.py` | `test_create_generates_slug` |
| Duplicate slug rejected | `ProjectService` (ConflictError) | `test_duplicate_slug_rejected_as_conflict`, `test_duplicate_name_conflicts` |
| Priority 1–5 | `ProjectService`, `contracts/projects.py` | `test_create_rejects_out_of_range_priority` |
| Archived read-only | `ProjectService.update_project` | `test_archived_project_is_read_only`, `test_archived_project_cannot_be_updated` |

## Scoring (FR-SCORE)

| Requirement | Implementation | Test |
| --- | --- | --- |
| 60/40 weighted formula, cap 100 | `domain/scoring.py` | `test_full_session_and_milestone_completion_caps_at_100` |
| Traffic-light boundaries 59/60/79/80 | `domain/scoring.score_to_status` | `test_score_to_status_boundaries` |
| Manual override needs reason | `ScoringService.manual_override` | `test_manual_override_requires_reason` |
| Override blocks recompute | `ScoringService.compute_and_save` | `test_manual_override_blocks_recompute` |
| Portfolio score 0 when none | `ScoringService.portfolio_score` | `test_portfolio_score_zero_when_no_scores` |

## Milestones / Reviews / Dashboard / Settings

| Requirement | Implementation | Test |
| --- | --- | --- |
| Milestone completion date lifecycle | `MilestoneService` | `test_entering_done_sets_completed_date` |
| Deterministic milestone order | `SqliteMilestoneRepository.list_for_project` | `test_listing_is_ordered` |
| Cancelled milestones excluded from score | `SqliteMilestoneRepository.count` | `test_milestone_count_excludes_cancelled` |
| Review get-or-create transient blank | `ReviewService.get_or_create` | `test_get_or_create_returns_transient_blank` |
| Reviews most-recent-first | `SqliteReviewRepository.list_all` | `test_list_orders_most_recent_first` |
| Dashboard aggregate | `DashboardService` | `test_session_status_and_dashboard` |
| Settings bounds + restart-required | `SettingsService`, `contracts/settings.py` | `test_settings_update_reports_no_restart_for_same_path` |

## Database (FR-DB)

| Requirement | Implementation | Test |
| --- | --- | --- |
| Migrations apply v1–v4 | `infrastructure/db/migrations` | `test_fresh_database_applies_all_migrations` |
| Backup before pending migration | `.../migrations/runner.py` | `test_backup_created_before_pending_migration` |
| Legacy DB opens without conversion | migration runner | `test_legacy_v2_database_upgrades_and_preserves_data` |
| Delete cascades | schema FKs | `test_delete_cascades_sessions_and_milestones` |
| One score per project/week | `project_score` UNIQUE | `test_score_one_per_project_week` |

## UI (component tests)

| Requirement | Implementation | Test |
| --- | --- | --- |
| Week nav range + load-more | `components/navigation/WeekNavigator.tsx` | `WeekNavigator.test.tsx` |
| Form retains values on error | `features/projects/ProjectForm.tsx` | `ProjectForm.test.tsx` |
| Non-color status indicator | `components/status/StatusIndicator.tsx` | `StatusIndicator.test.tsx` |
