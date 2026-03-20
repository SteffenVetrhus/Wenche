<script lang="ts">
	import { api, type KonfigStatus } from '$lib/api';

	let clientId = $state('');
	let kid = $state('');
	let orgNummer = $state('');
	let env = $state('prod');
	let statuses = $state<KonfigStatus[]>([]);
	let saving = $state(false);
	let testing = $state(false);
	let registering = $state(false);
	let creatingUser = $state(false);
	let checkingStatus = $state(false);
	let message = $state<{ type: string; text: string } | null>(null);
	let systemMessage = $state<{ type: string; text: string } | null>(null);

	async function loadStatus() {
		try {
			statuses = await api.getStatus();
		} catch { /* API unavailable */ }
	}

	loadStatus();

	const alleOk = $derived(statuses.length > 0 && statuses.every((s) => s.ok));

	async function lagreKonfig() {
		saving = true;
		message = null;
		try {
			await api.saveEnv({ client_id: clientId, kid, org_nummer: orgNummer, env });
			await loadStatus();
			message = { type: 'success', text: 'Konfigurasjon lagret.' };
		} catch (e: any) {
			message = { type: 'error', text: e.message };
		}
		saving = false;
	}

	async function testTilkobling() {
		testing = true;
		message = null;
		try {
			const res = await api.testConnection();
			message = { type: 'success', text: 'Tilkobling OK — Maskinporten og Altinn svarte som forventet.' };
		} catch (e: any) {
			message = { type: 'error', text: e.message };
		}
		testing = false;
	}

	async function registrerSystem() {
		registering = true;
		systemMessage = null;
		try {
			await api.registerSystem();
			systemMessage = { type: 'success', text: 'System registrert i systemregisteret.' };
		} catch (e: any) {
			systemMessage = { type: 'error', text: e.message };
		}
		registering = false;
	}

	async function opprettBruker() {
		creatingUser = true;
		systemMessage = null;
		try {
			const res = await api.createSystemUser();
			systemMessage = {
				type: 'info',
				text: `Forespørsel opprettet (${res.status}). Godkjenn her: ${res.confirmUrl}`
			};
		} catch (e: any) {
			systemMessage = { type: 'error', text: e.message };
		}
		creatingUser = false;
	}

	async function sjekkBrukerStatus() {
		checkingStatus = true;
		systemMessage = null;
		try {
			const res = await api.systemUserStatus();
			if (res.status === 'Accepted') {
				systemMessage = { type: 'success', text: 'Systembruker er godkjent.' };
			} else if (res.status === 'New') {
				systemMessage = { type: 'info', text: 'Forespørselen venter på godkjenning.' };
			} else if (res.status === 'Rejected') {
				systemMessage = { type: 'error', text: 'Forespørselen ble avvist.' };
			} else {
				systemMessage = { type: 'info', text: `Status: ${res.status}` };
			}
		} catch (e: any) {
			systemMessage = { type: 'error', text: e.message };
		}
		checkingStatus = false;
	}
</script>

<div class="page-header">
	<h2>Oppsett</h2>
	<p class="caption">Koble til Maskinporten og test tilkoblingen mot Altinn.</p>
</div>

<div class="card">
	<div class="card-title">Maskinporten-konfigurasjon</div>
	<div class="form-grid">
		<div class="form-group">
			<label for="clientId">Klient-ID</label>
			<input id="clientId" type="text" bind:value={clientId} placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" />
		</div>
		<div class="form-group">
			<label for="kid">Nøkkel-ID</label>
			<input id="kid" type="text" bind:value={kid} placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" />
		</div>
		<div class="form-group">
			<label for="orgNr">Organisasjonsnummer</label>
			<input id="orgNr" type="text" bind:value={orgNummer} placeholder="123456789" />
		</div>
		<div class="form-group">
			<label for="env">Miljø</label>
			<select id="env" bind:value={env}>
				<option value="prod">Produksjon</option>
				<option value="test">Test (tt02)</option>
			</select>
		</div>
	</div>
	<div style="margin-top: var(--space-lg)">
		<button class="btn btn-primary" onclick={lagreKonfig} disabled={saving}>
			{#if saving}<span class="spinner"></span>{/if}
			Lagre konfigurasjon
		</button>
	</div>
</div>

{#if message}
	<div class="alert alert-{message.type}">{message.text}</div>
{/if}

<div class="card">
	<div class="card-title">Status</div>
	{#each statuses as s}
		<div class="status-row">
			<span class="status-dot" class:ok={s.ok} class:fail={!s.ok}></span>
			<span class="status-title">{s.tittel}</span>
			<span class="status-detail">{s.detalj}</span>
		</div>
	{/each}
	{#if statuses.length === 0}
		<p class="caption">Laster status...</p>
	{/if}
</div>

<div class="card">
	<div class="card-title">Tilkoblingstest</div>
	<p class="caption" style="margin-bottom: var(--space-md)">
		Henter et midlertidig token fra Maskinporten og veksler det mot et Altinn-token.
	</p>
	<button class="btn btn-secondary" onclick={testTilkobling} disabled={testing || !alleOk}>
		{#if testing}<span class="spinner"></span>{/if}
		Test tilkobling
	</button>
</div>

<details class="collapsible">
	<summary>Systembruker-oppsett</summary>
	<div class="collapsible-content">
		<div class="card">
			<div style="display: flex; gap: var(--space-sm); flex-wrap: wrap; margin-bottom: var(--space-lg)">
				<button class="btn btn-secondary" onclick={registrerSystem} disabled={registering || !alleOk}>
					{#if registering}<span class="spinner"></span>{/if}
					Registrer system
				</button>
				<button class="btn btn-secondary" onclick={opprettBruker} disabled={creatingUser || !alleOk}>
					{#if creatingUser}<span class="spinner"></span>{/if}
					Opprett systembruker
				</button>
				<button class="btn btn-ghost" onclick={sjekkBrukerStatus} disabled={checkingStatus}>
					{#if checkingStatus}<span class="spinner"></span>{/if}
					Sjekk status
				</button>
			</div>
			{#if systemMessage}
				<div class="alert alert-{systemMessage.type}">{systemMessage.text}</div>
			{/if}
		</div>
	</div>
</details>
