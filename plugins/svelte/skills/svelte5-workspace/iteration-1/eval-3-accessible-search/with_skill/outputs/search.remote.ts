import { query } from '$app/server';
import { db } from '$lib/server/db';

export interface SearchResult {
	id: string;
	title: string;
	description: string;
	url: string;
}

export const search = query(async (term: string): Promise<SearchResult[]> => {
	const trimmed = term.trim();
	if (!trimmed || trimmed.length < 2) return [];

	const results = await db.items.findMany({
		where: {
			OR: [
				{ title: { contains: trimmed, mode: 'insensitive' } },
				{ description: { contains: trimmed, mode: 'insensitive' } }
			]
		},
		take: 20,
		select: { id: true, title: true, description: true, url: true }
	});

	return results;
});
