<script lang="ts">
	import { config } from '$lib/store';
	import { api } from '$lib/api';
	import { get } from 'svelte/store';

	let env = $state('test');
	let sendingAR = $state(false);
	let sendingAKR = $state(false);
	let message = $state<{ type: string; text: string } | null>(null);
	let signUrl = $state('');

	async function sendAarsregnskap() {
		sendingAR = true;
		message = null;
		signUrl = '';
		try {
			const res = await api.sendAarsregnskap(get(config), env);
			signUrl = res.sign_url;
			message = { type: 'success', text: `Årsregnskap lastet opp. Signer i Altinn for å fullføre.` };
		} catch (e: any) {
			message = { type: 'error', text: e.message };
		}
		sendingAR = false;
	}

	async function sendAksjonaerregister() {
		sendingAKR = true;
		message = null;
		try {
			const res = await api.sendAksjonaerregister(get(config), env);
			message = {
				type: 'success',
				text: `Aksjonærregisteroppgave sendt.${res.forsendelse_id ? ` Forsendelse-ID: ${res.forsendelse_id}` : ''}`
			};
		} catch (e: any) {
			message = { type: 'error', text: e.message };
		}
		sendingAKR = false;
	}
</script>

<div class="page-header">
	<h2>Send inn</h2>
	<p class="caption">Send dokumentene til Brønnøysundregistrene og Skatteetaten via Altinn.</p>
</div>

<div class="card">
	<div class="card-title">Miljø</div>
	<div class="radio-group">
		<label class="radio-option">
			<input type="radio" bind:group={env} value="test" />
			<span class="radio-label">Test (tt02)</span>
		</label>
		<label class="radio-option">
			<input type="radio" bind:group={env} value="prod" />
			<span class="radio-label">Produksjon</span>
		</label>
	</div>
	{#if env === 'prod'}
		<div class="alert alert-warning" style="margin-top: var(--space-md)">
			Innsending i produksjonsmiljøet er bindende og kan ikke trekkes tilbake.
		</div>
	{/if}
</div>

{#if message}
	<div class="alert alert-{message.type}">{message.text}</div>
{/if}

{#if signUrl}
	<div class="card">
		<div class="card-title">Signering</div>
		<p style="margin-bottom: var(--space-md)">Logg inn med BankID og signer for å fullføre innsendingen.</p>
		<a href={signUrl} target="_blank" rel="noopener" class="btn btn-primary">
			Signer i Altinn
		</a>
	</div>
{/if}

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md)">
	<div class="card">
		<div class="card-title">Årsregnskap</div>
		<p class="caption" style="margin-bottom: var(--space-lg)">
			Sender årsregnskapet til Brønnøysundregistrene via Altinn.
		</p>
		<button class="btn btn-primary btn-wide" onclick={sendAarsregnskap} disabled={sendingAR}>
			{#if sendingAR}<span class="spinner"></span>{/if}
			Send årsregnskap
		</button>
	</div>

	<div class="card">
		<div class="card-title">Aksjonærregister</div>
		<p class="caption" style="margin-bottom: var(--space-lg)">
			Sender aksjonærregisteroppgaven til Skatteetaten.
		</p>
		<button class="btn btn-primary btn-wide" onclick={sendAksjonaerregister} disabled={sendingAKR}>
			{#if sendingAKR}<span class="spinner"></span>{/if}
			Send aksjonærregister
		</button>
	</div>
</div>
