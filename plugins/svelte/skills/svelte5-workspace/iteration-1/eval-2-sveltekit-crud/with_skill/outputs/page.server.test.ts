import { describe, expect, it, beforeEach } from 'vitest';
import { load, actions, db } from './+page.server';

// Helper to create a mock Request with FormData
function createFormRequest(data: Record<string, string>): Request {
	const formData = new FormData();
	for (const [key, value] of Object.entries(data)) {
		formData.append(key, value);
	}
	return new Request('http://localhost', { method: 'POST', body: formData });
}

describe('Blog posts load function', () => {
	beforeEach(() => {
		// Reset DB to known state
		db.posts = [
			{ id: '1', title: 'First Post', content: 'First content', createdAt: new Date('2026-01-01') },
			{ id: '2', title: 'Second Post', content: 'Second content', createdAt: new Date('2026-02-01') }
		];
	});

	it('returns posts sorted by date descending', async () => {
		const result = await load({} as any);

		expect(result.posts).toHaveLength(2);
		expect(result.posts[0].title).toBe('Second Post');
		expect(result.posts[1].title).toBe('First Post');
	});

	it('returns posts with serialized date strings', async () => {
		const result = await load({} as any);

		for (const post of result.posts) {
			expect(typeof post.createdAt).toBe('string');
			expect(() => new Date(post.createdAt)).not.toThrow();
		}
	});

	it('returns only safe fields (id, title, content, createdAt)', async () => {
		const result = await load({} as any);
		const post = result.posts[0];

		expect(Object.keys(post).sort()).toEqual(['content', 'createdAt', 'id', 'title']);
	});

	it('returns empty array when no posts exist', async () => {
		db.posts = [];
		const result = await load({} as any);

		expect(result.posts).toEqual([]);
	});
});

describe('Blog posts create action', () => {
	beforeEach(() => {
		db.posts = [];
	});

	it('creates a post with valid data', async () => {
		const request = createFormRequest({ title: 'New Post', content: 'Some content' });
		const result = await actions.create({ request } as any);

		expect(result).toEqual({ success: true });
		expect(db.posts).toHaveLength(1);
		expect(db.posts[0].title).toBe('New Post');
		expect(db.posts[0].content).toBe('Some content');
	});

	it('trims whitespace from title and content', async () => {
		const request = createFormRequest({ title: '  Trimmed  ', content: '  Clean  ' });
		await actions.create({ request } as any);

		expect(db.posts[0].title).toBe('Trimmed');
		expect(db.posts[0].content).toBe('Clean');
	});

	it('fails with 400 when title is missing', async () => {
		const request = createFormRequest({ title: '', content: 'Some content' });
		const result = await actions.create({ request } as any);

		expect(result?.status).toBe(400);
		expect(result?.data?.error).toBe('Title is required');
		expect(db.posts).toHaveLength(0);
	});

	it('fails with 400 when content is missing', async () => {
		const request = createFormRequest({ title: 'Title', content: '' });
		const result = await actions.create({ request } as any);

		expect(result?.status).toBe(400);
		expect(result?.data?.error).toBe('Content is required');
		expect(db.posts).toHaveLength(0);
	});

	it('fails with 400 when title is only whitespace', async () => {
		const request = createFormRequest({ title: '   ', content: 'Content' });
		const result = await actions.create({ request } as any);

		expect(result?.status).toBe(400);
		expect(result?.data?.error).toBe('Title is required');
	});
});

describe('Blog posts delete action', () => {
	beforeEach(() => {
		db.posts = [
			{ id: 'abc', title: 'To Delete', content: 'Will be removed', createdAt: new Date() }
		];
	});

	it('deletes an existing post', async () => {
		const request = createFormRequest({ id: 'abc' });
		const result = await actions.delete({ request } as any);

		expect(result).toEqual({ success: true });
		expect(db.posts).toHaveLength(0);
	});

	it('fails with 400 when id is missing', async () => {
		const request = createFormRequest({});
		const result = await actions.delete({ request } as any);

		expect(result?.status).toBe(400);
		expect(result?.data?.error).toBe('Post ID is required');
	});

	it('fails with 404 when post does not exist', async () => {
		const request = createFormRequest({ id: 'nonexistent' });
		const result = await actions.delete({ request } as any);

		expect(result?.status).toBe(404);
		expect(result?.data?.error).toBe('Post not found');
	});
});
