import { query } from '$lib/server/remote';

export interface SearchResult {
	id: string;
	title: string;
	description: string;
	url: string;
}

export const search = query(async (term: string): Promise<SearchResult[]> => {
	if (!term.trim()) {
		return [];
	}

	// Simulate server-side search (replace with real DB/API call)
	const allItems: SearchResult[] = [
		{ id: '1', title: 'Getting Started Guide', description: 'Learn the basics of the platform', url: '/docs/getting-started' },
		{ id: '2', title: 'API Reference', description: 'Complete API documentation', url: '/docs/api' },
		{ id: '3', title: 'Component Library', description: 'Browse available UI components', url: '/docs/components' },
		{ id: '4', title: 'Configuration Options', description: 'Configure your application settings', url: '/docs/config' },
		{ id: '5', title: 'Deployment Guide', description: 'Deploy your app to production', url: '/docs/deployment' },
	];

	const normalized = term.toLowerCase();
	return allItems.filter(
		(item) =>
			item.title.toLowerCase().includes(normalized) ||
			item.description.toLowerCase().includes(normalized)
	);
});
