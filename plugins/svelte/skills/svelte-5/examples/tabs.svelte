<script lang="ts" module>
	import { getContext, setContext } from 'svelte';

	const TABS_KEY = Symbol('tabs');

	export interface TabsContext {
		activeTab: string;
		setActiveTab: (id: string) => void;
	}

	export function getTabsContext(): TabsContext {
		return getContext(TABS_KEY);
	}
</script>

<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		defaultTab?: string;
		children: Snippet;
	}

	let { defaultTab = '', children }: Props = $props();
	let activeTab = $state(defaultTab);

	function setActiveTab(id: string) {
		activeTab = id;
	}

	setContext(TABS_KEY, {
		get activeTab() { return activeTab },
		setActiveTab
	});
</script>

<div class="tabs">
	{@render children()}
</div>
