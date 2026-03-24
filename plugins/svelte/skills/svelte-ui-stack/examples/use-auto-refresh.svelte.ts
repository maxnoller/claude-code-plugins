// use-auto-refresh.svelte.ts
// Example of a REUSABLE reactive hook — the right use case for .svelte.ts
// This is shared across multiple pages, not page-local state extraction.
//
// Usage:
//   const refresh = useAutoRefresh(() => invalidate('app:data'), 30_000);
//   // refresh.pause(), refresh.resume(), refresh.isActive

export function useAutoRefresh(callback: () => void, intervalMs = 30_000) {
	let active = $state(true);
	let remaining = $state(intervalMs);

	$effect(() => {
		if (!active) return;

		const id = setInterval(() => {
			remaining -= 1000;
			if (remaining <= 0) {
				callback();
				remaining = intervalMs;
			}
		}, 1000);

		return () => clearInterval(id);
	});

	return {
		get isActive() { return active; },
		get remaining() { return remaining; },
		pause() { active = false; },
		resume() { active = true; remaining = intervalMs; },
		refreshNow() { callback(); remaining = intervalMs; },
	};
}
