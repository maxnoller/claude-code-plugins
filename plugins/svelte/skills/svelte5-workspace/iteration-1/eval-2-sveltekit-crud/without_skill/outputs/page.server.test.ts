import { describe, it, expect, vi, beforeEach } from 'vitest';
import { load } from './+page.server';

const mockPosts = [
	{
		id: '1',
		title: 'First Post',
		content: 'Hello world',
		createdAt: new Date('2025-01-15')
	},
	{
		id: '2',
		title: 'Second Post',
		content: 'Another post',
		createdAt: new Date('2025-01-10')
	}
];

vi.mock('$lib/server/db', () => ({
	db: {
		post: {
			findMany: vi.fn(),
			create: vi.fn(),
			delete: vi.fn()
		}
	}
}));

import { db } from '$lib/server/db';

describe('Blog posts load function', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('returns posts from the database', async () => {
		vi.mocked(db.post.findMany).mockResolvedValue(mockPosts);

		const result = await load({} as any);

		expect(result).toEqual({ posts: mockPosts });
		expect(db.post.findMany).toHaveBeenCalledWith({
			orderBy: { createdAt: 'desc' }
		});
	});

	it('returns an empty array when there are no posts', async () => {
		vi.mocked(db.post.findMany).mockResolvedValue([]);

		const result = await load({} as any);

		expect(result).toEqual({ posts: [] });
	});

	it('orders posts by createdAt descending', async () => {
		vi.mocked(db.post.findMany).mockResolvedValue(mockPosts);

		await load({} as any);

		expect(db.post.findMany).toHaveBeenCalledWith({
			orderBy: { createdAt: 'desc' }
		});
	});
});
