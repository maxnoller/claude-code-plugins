// src/routes/dashboard/+page.server.ts
// 
// Example of a SvelteKit server-side page with load function and form actions.
// In a real SvelteKit project, types are auto-generated from the route structure.

import { error, fail, redirect } from '@sveltejs/kit';
import { db } from '$lib/server/db';

// Define types inline for this example (in real SvelteKit these come from ./$types)
interface Locals {
    user?: {
        id: string;
        name: string;
        email: string;
    };
}

// Server-only load function
export const load = async ({ locals, depends }: { locals: Locals; depends: (dep: string) => void }) => {
    // Authentication check
    if (!locals.user) {
        redirect(303, '/login');
    }

    // Mark as dependent on user data (for invalidation)
    depends('app:user');

    // Parallel data loading
    const [stats, recentActivity] = await Promise.all([
        db.stats.findUnique({ where: { userId: locals.user.id } }),
        db.activity.findMany({
            where: { userId: locals.user.id },
            take: 10,
            orderBy: { createdAt: 'desc' }
        })
    ]);

    return {
        user: {
            id: locals.user.id,
            name: locals.user.name,
            email: locals.user.email
        },
        stats,
        recentActivity
    };
};

interface Cookies {
    delete: (name: string, options: { path: string }) => void;
}

// Form actions
export const actions = {
    updateProfile: async ({ request, locals }: { request: Request; locals: Locals }) => {
        if (!locals.user) {
            error(401, 'Unauthorized');
        }

        const data = await request.formData();
        const name = data.get('name') as string;

        if (!name?.trim()) {
            return fail(400, { name, error: 'Name is required' });
        }

        await db.users.update({
            where: { id: locals.user.id },
            data: { name: name.trim() }
        });

        return { success: true };
    },

    logout: async ({ cookies }: { cookies: Cookies }) => {
        cookies.delete('session', { path: '/' });
        redirect(303, '/login');
    }
};
