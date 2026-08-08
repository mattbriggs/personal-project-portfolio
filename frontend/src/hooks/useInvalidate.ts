import { useQueryClient } from "@tanstack/react-query";

// Central cache-invalidation rules (SRS §4.9). After a successful mutation,
// call the matching helper to refresh exactly the dependent queries — replacing
// the Tkinter event bus with explicit query invalidation.
export function useInvalidate() {
  const qc = useQueryClient();
  const invalidate = (keys: string[][]) =>
    Promise.all(keys.map((key) => qc.invalidateQueries({ queryKey: key })));

  return {
    afterProjectMutation: () =>
      invalidate([["projects"], ["dashboard"]]),
    afterSessionMutation: () =>
      invalidate([["sessions"], ["dashboard"], ["scores"], ["budget"]]),
    afterMilestoneMutation: () =>
      invalidate([["milestones"], ["dashboard"], ["scores"]]),
    afterReviewMutation: () =>
      invalidate([["reviews"], ["review"]]),
    afterSettingsMutation: () =>
      invalidate([["settings"], ["dashboard"]]),
    afterScoreMutation: () =>
      invalidate([["scores"], ["dashboard"]]),
  };
}
