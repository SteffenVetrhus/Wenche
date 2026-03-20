import type { Handle } from '@sveltejs/kit';

const API_BACKEND = process.env.API_URL ?? 'http://localhost:8000';

export const handle: Handle = async ({ event, resolve }) => {
	if (event.url.pathname.startsWith('/api')) {
		const target = `${API_BACKEND}${event.url.pathname}${event.url.search}`;
		const res = await fetch(target, {
			method: event.request.method,
			headers: event.request.headers,
			body: event.request.method !== 'GET' ? await event.request.text() : undefined,
			// @ts-expect-error duplex needed for streaming body
			duplex: 'half'
		});

		return new Response(res.body, {
			status: res.status,
			statusText: res.statusText,
			headers: res.headers
		});
	}

	return resolve(event);
};
