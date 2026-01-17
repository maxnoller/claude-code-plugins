// src/hooks.server.ts
import type { Handle, HandleFetch, HandleServerError } from '@sveltejs/kit';
import { db } from '$lib/server/db';

// Authentication middleware
const auth: Handle = async ({ event, resolve }) => {
    const sessionId = event.cookies.get('session');

    if (sessionId) {
        const session = await db.sessions.findUnique({
            where: { id: sessionId },
            include: { user: true }
        });

        if (session && session.expiresAt > new Date()) {
            event.locals.user = session.user;
        } else {
            // Clear expired session
            event.cookies.delete('session', { path: '/' });
        }
    }

    return resolve(event);
};

// Route protection middleware
const protect: Handle = async ({ event, resolve }) => {
    const protectedPaths = ['/dashboard', '/admin', '/settings'];
    const isProtected = protectedPaths.some(p =>
        event.url.pathname.startsWith(p)
    );

    if (isProtected && !event.locals.user) {
        return new Response(null, {
            status: 303,
            headers: { Location: '/login' }
        });
    }

    // Admin routes
    if (event.url.pathname.startsWith('/admin')) {
        if (!event.locals.user?.isAdmin) {
            return new Response('Forbidden', { status: 403 });
        }
    }

    return resolve(event);
};

// Logging middleware
const logger: Handle = async ({ event, resolve }) => {
    const start = Date.now();
    const response = await resolve(event);
    const duration = Date.now() - start;

    console.log(`${event.request.method} ${event.url.pathname} - ${response.status} (${duration}ms)`);

    return response;
};

// Helper to compose multiple handles (simplified version of sequence)
function sequence(...handlers: Handle[]): Handle {
    return async ({ event, resolve }) => {
        let currentResolve = resolve;
        for (let i = handlers.length - 1; i >= 0; i--) {
            const handler = handlers[i];
            const nextResolve = currentResolve;
            currentResolve = (event) => handler({ event, resolve: nextResolve });
        }
        return currentResolve(event);
    };
}

// Combine handles
export const handle = sequence(auth, protect, logger);

// Modify internal fetch requests
export const handleFetch: HandleFetch = async ({ request, fetch, event }) => {
    // Add auth header to internal API calls
    if (request.url.startsWith('http://localhost')) {
        request = new Request(request, {
            headers: {
                ...Object.fromEntries(request.headers),
                'X-User-Id': event.locals.user?.id ?? ''
            }
        });
    }

    return fetch(request);
};

// Global error handling
export const handleError: HandleServerError = async ({ error, event, status, message }) => {
    const errorId = crypto.randomUUID();

    // Log error details
    console.error(`Error ${errorId}:`, {
        status,
        message,
        path: event.url.pathname,
        error
    });

    // Return safe error to client
    return {
        message: status === 404 ? 'Page not found' : 'An unexpected error occurred',
        errorId
    };
};
