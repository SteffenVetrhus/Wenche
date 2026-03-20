<script lang="ts">
	import { config } from '$lib/store';
	import { api } from '$lib/api';
	import { get } from 'svelte/store';

	let generatingSM = $state(false);
	let generatingAR = $state(false);
	let generatingAKR = $state(false);
	let skattemeldingTekst = $state('');
	let message = $state<{ type: string; text: string } | null>(null);
	let arFiles = $state<{ hovedskjema: string; underskjema: string } | null>(null);
	let akrFiles = $state<{ hovedskjema: string; underskjemaer: { navn: string; xml: string }[] } | null>(null);

	function download(filename: string, content: string, mime = 'application/xml') {
		const blob = new Blob([content], { type: mime });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = filename;
		a.click();
		URL.revokeObjectURL(url);
	}

	async function genererSkattemelding() {
		generatingSM = true;
		message = null;
		try {
			const res = await api.generateSkattemelding(get(config));
			skattemeldingTekst = res.tekst;
		} catch (e: any) {
			message = { type: 'error', text: e.message };
		}
		generatingSM = false;
	}

	async function genererAarsregnskap() {
		generatingAR = true;
		message = null;
		try {
			arFiles = await api.generateAarsregnskap(get(config));
		} catch (e: any) {
			message = { type: 'error', text: e.message };
		}
		generatingAR = false;
	}

	async function genererAksjonaerregister() {
		generatingAKR = true;
		message = null;
		try {
			akrFiles = await api.generateAksjonaerregister(get(config));
		} catch (e: any) {
			message = { type: 'error', text: e.message };
		}
		generatingAKR = false;
	}
</script>

<div class="page-header">
	<h2>Dokumenter</h2>
	<p class="caption">Generer og last ned dokumenter for gjennomgang.</p>
</div>

<!-- Skattemelding settings -->
<div class="card">
	<div class="card-title">Skattemelding-innstillinger</div>
	<div class="form-grid">
		<div class="form-group">
			<label for="underskudd">Fremførbart underskudd (NOK)</label>
			<input id="underskudd" type="number" bind:value={$config.skattemelding.underskudd} min="0" />
		</div>
		<div class="form-group" style="justify-content: flex-end">
			<label class="checkbox-group">
				<input type="checkbox" bind:checked={$config.skattemelding.fritaksmetoden} />
				Anvend fritaksmetoden
			</label>
		</div>
		{#if $config.skattemelding.fritaksmetoden}
			<div class="form-group">
				<label for="eierandel">Eierandel i datterselskap (%)</label>
				<input id="eierandel" type="number" bind:value={$config.skattemelding.eierandel_datterselskap} min="0" max="100" />
			</div>
		{/if}
	</div>
</div>

{#if message}
	<div class="alert alert-{message.type}">{message.text}</div>
{/if}

<div class="divider"></div>

<!-- Generate buttons -->
<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-md)">
	<button class="btn btn-secondary btn-wide" onclick={genererSkattemelding} disabled={generatingSM}>
		{#if generatingSM}<span class="spinner"></span>{/if}
		Skattemelding
	</button>
	<button class="btn btn-secondary btn-wide" onclick={genererAarsregnskap} disabled={generatingAR}>
		{#if generatingAR}<span class="spinner"></span>{/if}
		Årsregnskap
	</button>
	<button class="btn btn-secondary btn-wide" onclick={genererAksjonaerregister} disabled={generatingAKR}>
		{#if generatingAKR}<span class="spinner"></span>{/if}
		Aksjonærregister
	</button>
</div>

<!-- Skattemelding output -->
{#if skattemeldingTekst}
	<div class="card" style="margin-top: var(--space-lg)">
		<div class="card-title">Skattemelding</div>
		<pre style="font-size: 0.8rem; overflow-x: auto; background: var(--frost); padding: var(--space-md); border-radius: var(--radius-sm); line-height: 1.6">{skattemeldingTekst}</pre>
		<div style="margin-top: var(--space-md)">
			<button
				class="download-btn"
				onclick={() => download(`skattemelding_${$config.regnskapsaar}_${$config.selskap.org_nummer}.txt`, skattemeldingTekst, 'text/plain')}
			>
				Last ned .txt
			</button>
		</div>
	</div>
{/if}

<!-- Årsregnskap output -->
{#if arFiles}
	<div class="card" style="margin-top: var(--space-lg)">
		<div class="card-title">Årsregnskap</div>
		<div style="display: flex; gap: var(--space-sm); flex-wrap: wrap">
			<button
				class="download-btn"
				onclick={() => download(`aarsregnskap_${$config.regnskapsaar}_hovedskjema.xml`, arFiles!.hovedskjema)}
			>
				Hovedskjema (XML)
			</button>
			<button
				class="download-btn"
				onclick={() => download(`aarsregnskap_${$config.regnskapsaar}_underskjema.xml`, arFiles!.underskjema)}
			>
				Underskjema (XML)
			</button>
		</div>
	</div>
{/if}

<!-- Aksjonærregister output -->
{#if akrFiles}
	<div class="card" style="margin-top: var(--space-lg)">
		<div class="card-title">Aksjonærregisteroppgave</div>
		<div style="display: flex; gap: var(--space-sm); flex-wrap: wrap">
			<button
				class="download-btn"
				onclick={() => download(`aksjonaerregister_${$config.regnskapsaar}_hovedskjema.xml`, akrFiles!.hovedskjema)}
			>
				Hovedskjema (RF-1086)
			</button>
			{#each akrFiles.underskjemaer as under, i}
				<button
					class="download-btn"
					onclick={() => download(`aksjonaerregister_${$config.regnskapsaar}_underskjema_${i + 1}.xml`, under.xml)}
				>
					Underskjema {i + 1} — {under.navn}
				</button>
			{/each}
		</div>
	</div>
{/if}
