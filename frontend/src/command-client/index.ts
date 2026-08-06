// Public command-client surface. Feature code imports from here.

export * as health from "./health";
export * as dashboard from "./dashboard";
export * as projects from "./projects";
export * as sessions from "./sessions";
export * as milestones from "./milestones";
export * as reviews from "./reviews";
export * as scores from "./scores";
export * as settings from "./settings";
export { isCommandError, isSidecarDown, toCommandError } from "./errors";
export type { CommandError, ErrorCode } from "./errors";
