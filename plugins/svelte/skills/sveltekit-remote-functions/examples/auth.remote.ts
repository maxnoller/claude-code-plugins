// src/lib/auth.remote.ts
// SvelteKit Remote Functions for Authentication
// 
// NOTE: Remote functions are an experimental SvelteKit feature.
// This example demonstrates the pattern but may not compile without
// the experimental flag: kit.experimental.remoteFunctions = true

// In a real project, these would come from $app/server:
// import { form } from '$app/server';

import { fail, redirect } from '@sveltejs/kit';
import * as v from 'valibot';
import { db } from '$lib/server/database';
import * as auth from '$lib/server/auth';

// Define the login fields schema using valibot
const LoginSchema = v.object({
    email: v.pipe(
        v.string(),
        v.email('Please enter a valid email address')
    ),
    password: v.pipe(
        v.string(),
        v.minLength(8, 'Password must be at least 8 characters')
    )
});

type LoginInput = v.InferOutput<typeof LoginSchema>;

// Type for the form result (simplified for this example)
interface FormResult {
    enhance: (node: HTMLFormElement) => { destroy: () => void };
    pending: boolean;
}

interface Cookies {
    set: (name: string, value: string, options: Record<string, unknown>) => void;
}

// Mock form function for example purposes
// In a real SvelteKit project with remoteFunctions enabled,
// you would use: export const login = form({ ... })
async function handleLogin(
    { email, password }: LoginInput,
    cookies: Cookies
) {
    // Validate input
    const result = v.safeParse(LoginSchema, { email, password });
    if (!result.success) {
        return fail(400, { errors: result.issues });
    }

    // Authenticate user
    const user = await auth.authenticate(email, password);
    if (!user) {
        return fail(401, { message: 'Invalid email or password' });
    }

    // Set session cookie
    const session = await auth.createSession(user.id);
    cookies.set('session', session.id, {
        path: '/',
        httpOnly: true,
        secure: true,
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 7 // 1 week
    });

    // Redirect after successful login
    redirect(303, '/dashboard');
}

export { handleLogin, LoginSchema };

// Example usage in +page.server.ts:
// 
// import { handleLogin, LoginSchema } from '$lib/auth.server';
// import * as v from 'valibot';
// 
// export const actions = {
//   login: async ({ request, cookies }) => {
//     const formData = await request.formData();
//     const email = formData.get('email') as string;
//     const password = formData.get('password') as string;
//     return handleLogin({ email, password }, cookies);
//   }
// };
