// dashboard-state.svelte.ts
// Demonstrates the factory function pattern for extracting logic from UI.
// Colocated next to the +page.svelte that uses it.
//
// Usage in +page.svelte:
//   let { data } = $props();
//   const dashboard = createDashboardState(() => data);

interface DashboardItem {
	id: string;
	label: string;
	value: number;
	date: string;
	category: string;
}

interface DashboardData {
	items: DashboardItem[];
	summary: { total: number; average: number };
}

// Accept a getter function for reactive props — ensures the factory
// tracks changes when the parent's data prop updates.
export function createDashboardState(getData: () => DashboardData) {
	let loading = $state(false);
	let error = $state<string | null>(null);

	// Filtering
	let searchQuery = $state('');
	let selectedCategory = $state<string | null>(null);

	// Sorting
	let sortField = $state<'date' | 'value' | 'label'>('date');
	let sortDirection = $state<'asc' | 'desc'>('desc');

	// Derived: filtered + sorted items
	let filteredItems = $derived.by(() => {
		let items = getData().items;

		if (searchQuery) {
			const q = searchQuery.toLowerCase();
			items = items.filter((i) => i.label.toLowerCase().includes(q));
		}

		if (selectedCategory) {
			items = items.filter((i) => i.category === selectedCategory);
		}

		return items.toSorted((a, b) => {
			const cmp = a[sortField] > b[sortField] ? 1 : -1;
			return sortDirection === 'asc' ? cmp : -cmp;
		});
	});

	// Derived: unique categories for filter dropdown
	let categories = $derived([...new Set(getData().items.map((i: DashboardItem) => i.category))].sort());

	// Derived: summary of filtered data
	let filteredSummary = $derived({
		count: filteredItems.length,
		total: filteredItems.reduce((sum, i) => sum + i.value, 0),
		average: filteredItems.length ? filteredItems.reduce((sum, i) => sum + i.value, 0) / filteredItems.length : 0
	});

	// When data comes from a getter (page load data), refresh by invalidating
	// the SvelteKit load function rather than fetching directly.
	// For standalone fetch patterns, use internal $state instead of a getter.

	function toggleSort(field: typeof sortField) {
		if (sortField === field) {
			sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
		} else {
			sortField = field;
			sortDirection = 'asc';
		}
	}

	function clearFilters() {
		searchQuery = '';
		selectedCategory = null;
	}

	return {
		// State (read-only via getters)
		get loading() { return loading; },
		get error() { return error; },
		get filteredItems() { return filteredItems; },
		get categories() { return categories; },
		get filteredSummary() { return filteredSummary; },
		get sortField() { return sortField; },
		get sortDirection() { return sortDirection; },

		// State (read-write)
		get searchQuery() { return searchQuery; },
		set searchQuery(v) { searchQuery = v; },
		get selectedCategory() { return selectedCategory; },
		set selectedCategory(v) { selectedCategory = v; },

		// Actions
		toggleSort,
		clearFilters,
	};
}
