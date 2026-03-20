<script lang="ts">
	import '../app.css';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { config, configLoaded } from '$lib/store';

	let { children } = $props();

	const steps = [
		{ href: '/oppsett', label: 'Oppsett', step: 1 },
		{ href: '/selskap', label: 'Selskap', step: 2 },
		{ href: '/regnskap', label: 'Regnskap', step: 3 },
		{ href: '/aksjonaerer', label: 'Aksjonaerer', step: 4 },
		{ href: '/dokumenter', label: 'Dokumenter', step: 5 },
		{ href: '/send', label: 'Send inn', step: 6 }
	];

	onMount(async () => {
		try {
			const cfg = await api.getConfig();
			config.set(cfg);
		} catch {
			// API not available, use defaults
		}
		configLoaded.set(true);
	});

	function isActive(href: string): boolean {
		const currentPath = page.url.pathname;
		if (href === '/oppsett') return currentPath === '/' || currentPath === '/oppsett';
		return currentPath.startsWith(href);
	}
</script>

<div class="app-shell">
	<aside class="sidebar">
		<div class="sidebar-logo">
			<h1>Wenche</h1>
			<div class="subtitle">Regnskap og skatt</div>
		</div>
		<nav class="sidebar-nav">
			{#each steps as { href, label, step }}
				<a
					{href}
					class="nav-item"
					class:active={isActive(href)}
				>
					<span class="nav-step">{step}</span>
					{label}
				</a>
			{/each}
		</nav>
	</aside>
	<main class="main-content">
		{@render children()}
	</main>
</div>
