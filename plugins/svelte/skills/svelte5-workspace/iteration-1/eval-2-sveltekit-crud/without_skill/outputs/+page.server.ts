import type { Actions, PageServerLoad } from './$types';
import { fail } from '@sveltejs/kit';
import { db } from '$lib/server/db';

export const load: PageServerLoad = async () => {
	const posts = await db.post.findMany({
		orderBy: { createdAt: 'desc' }
	});

	return { posts };
};

export const actions: Actions = {
	create: async ({ request }) => {
		const formData = await request.formData();
		const title = formData.get('title');
		const content = formData.get('content');

		if (!title || typeof title !== 'string' || title.trim().length === 0) {
			return fail(400, { error: 'Title is required', title, content });
		}

		if (!content || typeof content !== 'string' || content.trim().length === 0) {
			return fail(400, { error: 'Content is required', title, content });
		}

		await db.post.create({
			data: {
				title: title.trim(),
				content: content.trim()
			}
		});

		return { success: true };
	},

	delete: async ({ request }) => {
		const formData = await request.formData();
		const id = formData.get('id');

		if (!id || typeof id !== 'string') {
			return fail(400, { error: 'Post ID is required' });
		}

		try {
			await db.post.delete({ where: { id } });
		} catch {
			return fail(404, { error: 'Post not found' });
		}

		return { success: true };
	}
};
