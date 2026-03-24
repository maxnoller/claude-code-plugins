// src/lib/auth-form.remote.ts
// Login/register form with progressive enhancement
// Demonstrates: form(), field API, multiple submit buttons, sensitive fields

import { form, getRequestEvent } from '$app/server';
import { redirect, invalid } from '@sveltejs/kit';
import * as v from 'valibot';
import * as auth from '$lib/server/auth';

export const loginOrRegister = form(
	v.object({
		email: v.pipe(v.string(), v.email('Please enter a valid email')),
		_password: v.pipe(v.string(), v.minLength(8, 'At least 8 characters')),
		action: v.picklist(['login', 'register'])
	}),
	async ({ email, _password, action }, issue) => {
		if (action === 'register') {
			const existing = await auth.findByEmail(email);
			if (existing) {
				invalid(issue.email('An account with this email already exists'));
			}
			await auth.createUser(email, _password);
		}

		const user = await auth.authenticate(email, _password);
		if (!user) {
			invalid(issue.email('Invalid email or password'));
		}

		const { cookies } = getRequestEvent();
		const session = await auth.createSession(user.id);
		cookies.set('session', session.id, {
			path: '/',
			httpOnly: true,
			secure: true,
			sameSite: 'lax',
			maxAge: 60 * 60 * 24 * 7
		});

		redirect(303, '/dashboard');
	}
);

// Usage in component:
//
// <form {...loginOrRegister}>
//   <input {...loginOrRegister.fields.email.as('email')} />
//   {#each loginOrRegister.fields.email.issues() as issue}
//     <span class="error">{issue.message}</span>
//   {/each}
//
//   <input {...loginOrRegister.fields._password.as('password')} />
//   {#each loginOrRegister.fields._password.issues() as issue}
//     <span class="error">{issue.message}</span>
//   {/each}
//
//   <button {...loginOrRegister.fields.action.as('submit', 'login')}>
//     Login
//   </button>
//   <button {...loginOrRegister.fields.action.as('submit', 'register')}>
//     Register
//   </button>
// </form>
