import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

// Simulated database — replace with your real DB client (Prisma, Drizzle, etc.)
const db = {
	posts: [
		{ id: '1', title: 'Hello World', content: 'My first blog post', createdAt: new Date('2026-01-15') },
		{ id: '2', title: 'SvelteKit is great', content: 'Form actions are awesome', createdAt: new Date('2026-02-20') }
	],

	findMany() {
		return [...this.posts].sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
	},

	create(data: { title: string; content: string }) {
		const post = {
			id: crypto.randomUUID(),
			title: data.title,
			content: data.content,
			createdAt: new Date()
		};
		this.posts.push(post);
		return post;
	},

	delete(id: string) {
		const index = this.posts.findIndex((p) => p.id === id);
		if (index === -1) return false;
		this.posts.splice(index, 1);
		return true;
	}
};

export { db };

export const load: PageServerLoad = async () => {
	const posts = db.findMany();

	return {
		posts: posts.map((p) => ({
			id: p.id,
			title: p.title,
			content: p.content,
			createdAt: p.createdAt.toISOString()
		}))
	};
};

export const actions: Actions = {
	create: async ({ request }) => {
		const data = await request.formData();
		const title = data.get('title') as string;
		const content = data.get('content') as string;

		if (!title?.trim()) {
			return fail(400, { title, content, error: 'Title is required' });
		}

		if (!content?.trim()) {
			return fail(400, { title, content, error: 'Content is required' });
		}

		db.create({ title: title.trim(), content: content.trim() });

		return { success: true };
	},

	delete: async ({ request }) => {
		const data = await request.formData();
		const id = data.get('id') as string;

		if (!id) {
			return fail(400, { error: 'Post ID is required' });
		}

		const deleted = db.delete(id);

		if (!deleted) {
			return fail(404, { error: 'Post not found' });
		}

		return { success: true };
	}
};
