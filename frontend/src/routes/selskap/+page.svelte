<script lang="ts">
	import { config } from '$lib/store';
	import { api } from '$lib/api';
	import { get } from 'svelte/store';

	let saving = $state(false);
	let message = $state<{ type: string; text: string } | null>(null);

	async function lagre() {
		saving = true;
		message = null;
		try {
			await api.saveConfig(get(config));
			message = { type: 'success', text: 'Selskapsopplysninger lagret.' };
		} catch (e: any) {
			message = { type: 'error', text: e.message };
		}
		saving = false;
	}
</script>

<div class="page-header">
	<h2>Selskap</h2>
	<p class="caption">Grunnleggende informasjon om selskapet.</p>
</div>

<div class="card">
	<div class="card-title">Selskapsinformasjon</div>
	<div class="form-grid">
		<div class="form-group">
			<label for="navn">Selskapsnavn</label>
			<input id="navn" type="text" bind:value={$config.selskap.navn} />
		</div>
		<div class="form-group">
			<label for="orgnr">Organisasjonsnummer</label>
			<input id="orgnr" type="text" bind:value={$config.selskap.org_nummer} placeholder="9 siffer" />
		</div>
		<div class="form-group">
			<label for="dagligleder">Daglig leder</label>
			<input id="dagligleder" type="text" bind:value={$config.selskap.daglig_leder} />
		</div>
		<div class="form-group">
			<label for="styreleder">Styreleder</label>
			<input id="styreleder" type="text" bind:value={$config.selskap.styreleder} />
		</div>
		<div class="form-group full-width">
			<label for="adresse">Forretningsadresse</label>
			<input id="adresse" type="text" bind:value={$config.selskap.forretningsadresse} />
		</div>
		<div class="form-group">
			<label for="stiftaar">Stiftelsesår</label>
			<input id="stiftaar" type="number" bind:value={$config.selskap.stiftelsesaar} />
		</div>
		<div class="form-group">
			<label for="aksjekapital">Aksjekapital (NOK)</label>
			<input id="aksjekapital" type="number" bind:value={$config.selskap.aksjekapital} />
		</div>
		<div class="form-group">
			<label for="epost">Kontakt-e-post</label>
			<input id="epost" type="email" bind:value={$config.selskap.kontakt_epost} placeholder="Påkrevd for RF-1086" />
		</div>
		<div class="form-group">
			<label for="regaar">Regnskapsår</label>
			<input id="regaar" type="number" bind:value={$config.regnskapsaar} />
		</div>
	</div>
</div>

{#if message}
	<div class="alert alert-{message.type}">{message.text}</div>
{/if}

<button class="btn btn-primary" onclick={lagre} disabled={saving}>
	{#if saving}<span class="spinner"></span>{/if}
	Lagre
</button>
