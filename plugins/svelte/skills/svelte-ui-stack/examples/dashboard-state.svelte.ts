// dashboard-state.svelte.ts
// Demonstrates the factory function pattern for extracting logic from UI.
// Colocated next to the +page.svelte that uses it.

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

export function createDashboardState(initialData: DashboardData) {
	let data = $state(initialData);
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
		let items = data.items;

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
	let categories = $derived([...new Set(data.items.map((i) => i.category))].sort());

	// Derived: summary of filtered data
	let filteredSummary = $derived({
		count: filteredItems.length,
		total: filteredItems.reduce((sum, i) => sum + i.value, 0),
		average: filteredItems.length ? filteredItems.reduce((sum, i) => sum + i.value, 0) / filteredItems.length : 0
	});

	async function refresh() {
		loading = true;
		error = null;
		try {
			const res = await fetch('/api/dashboard');
			if (!res.ok) throw new Error(`Failed: ${res.status}`);
			data = await res.json();
		} catch (e: unknown) {
			error = e instanceof Error ? e.message : 'Unknown error';
		} finally {
			loading = false;
		}
	}

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
		refresh,
		toggleSort,
		clearFilters,
	};
}
