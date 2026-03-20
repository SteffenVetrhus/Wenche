<script lang="ts">
	import { config } from '$lib/store';
	import { api, type AksjonaerData } from '$lib/api';
	import { get } from 'svelte/store';

	let saving = $state(false);
	let message = $state<{ type: string; text: string } | null>(null);

	function leggTil() {
		$config.aksjonaerer = [
			...$config.aksjonaerer,
			{
				navn: '',
				fodselsnummer: '',
				antall_aksjer: 1,
				aksjeklasse: 'ordinære',
				utbytte_utbetalt: 0,
				innbetalt_kapital_per_aksje: 0
			}
		];
	}

	function fjern(index: number) {
		$config.aksjonaerer = $config.aksjonaerer.filter((_, i) => i !== index);
	}

	async function lagre() {
		saving = true;
		message = null;
		try {
			await api.saveConfig(get(config));
			message = { type: 'success', text: 'Aksjonærer lagret.' };
		} catch (e: any) {
			message = { type: 'error', text: e.message };
		}
		saving = false;
	}
</script>

<div class="page-header">
	<h2>Aksjonaerer</h2>
	<p class="caption">Opplysninger om aksjonærene i selskapet.</p>
</div>

{#each $config.aksjonaerer as aksjonaer, i}
	<div class="card">
		<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-lg)">
			<div class="card-title" style="margin-bottom: 0">Aksjonær {i + 1}</div>
			<button class="btn btn-ghost" onclick={() => fjern(i)}>Fjern</button>
		</div>
		<div class="form-grid">
			<div class="form-group">
				<label for="a-navn-{i}">Navn</label>
				<input id="a-navn-{i}" type="text" bind:value={aksjonaer.navn} />
			</div>
			<div class="form-group">
				<label for="a-fnr-{i}">Fødselsnummer</label>
				<input id="a-fnr-{i}" type="text" bind:value={aksjonaer.fodselsnummer} placeholder="11 siffer" />
			</div>
			<div class="form-group">
				<label for="a-aksjer-{i}">Antall aksjer</label>
				<input id="a-aksjer-{i}" type="number" bind:value={aksjonaer.antall_aksjer} min="1" />
			</div>
			<div class="form-group">
				<label for="a-klasse-{i}">Aksjeklasse</label>
				<input id="a-klasse-{i}" type="text" bind:value={aksjonaer.aksjeklasse} />
			</div>
			<div class="form-group">
				<label for="a-utbytte-{i}">Utbytte utbetalt (NOK)</label>
				<input id="a-utbytte-{i}" type="number" bind:value={aksjonaer.utbytte_utbetalt} min="0" />
			</div>
			<div class="form-group">
				<label for="a-kap-{i}">Innbetalt kapital per aksje (NOK)</label>
				<input id="a-kap-{i}" type="number" bind:value={aksjonaer.innbetalt_kapital_per_aksje} min="0" />
			</div>
		</div>
	</div>
{/each}

{#if $config.aksjonaerer.length === 0}
	<div class="card">
		<p class="caption" style="text-align: center; padding: var(--space-xl) 0">
			Ingen aksjonærer lagt til ennå.
		</p>
	</div>
{/if}

<div style="display: flex; gap: var(--space-sm); margin-top: var(--space-md)">
	<button class="btn btn-secondary" onclick={leggTil}>
		+ Legg til aksjonær
	</button>
	<button class="btn btn-primary" onclick={lagre} disabled={saving}>
		{#if saving}<span class="spinner"></span>{/if}
		Lagre
	</button>
</div>

{#if message}
	<div class="alert alert-{message.type}" style="margin-top: var(--space-lg)">{message.text}</div>
{/if}
