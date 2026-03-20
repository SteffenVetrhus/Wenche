<script lang="ts">
	import { config, formatNOK } from '$lib/store';
	import { api } from '$lib/api';
	import { get } from 'svelte/store';

	let saving = $state(false);
	let message = $state<{ type: string; text: string } | null>(null);
	let showForegaaende = $state(false);

	const sumDriftsinntekter = $derived(
		$config.resultat.salgsinntekter + $config.resultat.andre_driftsinntekter
	);
	const sumDriftskostnader = $derived(
		$config.resultat.loennskostnader +
			$config.resultat.avskrivninger +
			$config.resultat.andre_driftskostnader
	);
	const driftsresultat = $derived(sumDriftsinntekter - sumDriftskostnader);
	const resultatFoerSkatt = $derived(
		driftsresultat +
			$config.resultat.utbytte_fra_datterselskap +
			$config.resultat.andre_finansinntekter -
			$config.resultat.rentekostnader -
			$config.resultat.andre_finanskostnader
	);

	const sumAnleggsmidler = $derived(
		$config.balanse.aksjer_i_datterselskap +
			$config.balanse.andre_aksjer +
			$config.balanse.langsiktige_fordringer
	);
	const sumOmloepmidler = $derived(
		$config.balanse.kortsiktige_fordringer + $config.balanse.bankinnskudd
	);
	const sumEiendeler = $derived(sumAnleggsmidler + sumOmloepmidler);

	const sumEgenkapital = $derived(
		$config.balanse.ek_aksjekapital +
			$config.balanse.overkursfond +
			$config.balanse.annen_egenkapital
	);
	const sumLangsiktigGjeld = $derived(
		$config.balanse.laan_fra_aksjonaer + $config.balanse.andre_langsiktige_laan
	);
	const sumKortsiktigGjeld = $derived(
		$config.balanse.leverandoergjeld +
			$config.balanse.skyldige_offentlige_avgifter +
			$config.balanse.annen_kortsiktig_gjeld
	);
	const sumEkOgGjeld = $derived(sumEgenkapital + sumLangsiktigGjeld + sumKortsiktigGjeld);
	const differanse = $derived(sumEiendeler - sumEkOgGjeld);

	async function lagre() {
		saving = true;
		message = null;
		try {
			await api.saveConfig(get(config));
			message = { type: 'success', text: 'Regnskapstall lagret.' };
		} catch (e: any) {
			message = { type: 'error', text: e.message };
		}
		saving = false;
	}
</script>

<div class="page-header">
	<h2>Regnskap og balanse</h2>
	<p class="caption">Tall fra resultatregnskapet og balansen.</p>
</div>

<!-- Resultatregnskap -->
<div class="card">
	<div class="card-title">Resultatregnskap</div>
	<div class="form-grid">
		<div class="form-group">
			<label for="salg">Salgsinntekter</label>
			<input id="salg" type="number" bind:value={$config.resultat.salgsinntekter} />
		</div>
		<div class="form-group">
			<label for="andreDrift">Andre driftsinntekter</label>
			<input id="andreDrift" type="number" bind:value={$config.resultat.andre_driftsinntekter} />
		</div>
		<div class="form-group">
			<label for="lonn">Lønnskostnader</label>
			<input id="lonn" type="number" bind:value={$config.resultat.loennskostnader} />
		</div>
		<div class="form-group">
			<label for="avskr">Avskrivninger</label>
			<input id="avskr" type="number" bind:value={$config.resultat.avskrivninger} />
		</div>
		<div class="form-group">
			<label for="andreDK">Andre driftskostnader</label>
			<input id="andreDK" type="number" bind:value={$config.resultat.andre_driftskostnader} />
		</div>
		<div class="form-group">
			<label for="utbytte">Utbytte fra datterselskap</label>
			<input id="utbytte" type="number" bind:value={$config.resultat.utbytte_fra_datterselskap} />
		</div>
		<div class="form-group">
			<label for="andreFI">Andre finansinntekter</label>
			<input id="andreFI" type="number" bind:value={$config.resultat.andre_finansinntekter} />
		</div>
		<div class="form-group">
			<label for="rente">Rentekostnader</label>
			<input id="rente" type="number" bind:value={$config.resultat.rentekostnader} />
		</div>
		<div class="form-group">
			<label for="andreFK">Andre finanskostnader</label>
			<input id="andreFK" type="number" bind:value={$config.resultat.andre_finanskostnader} />
		</div>
	</div>
	<div style="display: flex; gap: var(--space-xl); margin-top: var(--space-lg)">
		<div class="metric">
			<div class="metric-label">Driftsresultat</div>
			<div class="metric-value" class:negative={driftsresultat < 0}>{formatNOK(driftsresultat)}</div>
		</div>
		<div class="metric">
			<div class="metric-label">Resultat før skatt</div>
			<div class="metric-value" class:negative={resultatFoerSkatt < 0}>{formatNOK(resultatFoerSkatt)}</div>
		</div>
	</div>
</div>

<!-- Balanse -->
<div class="card">
	<div class="card-title">Balanse</div>
	<div class="form-grid">
		<div>
			<h4 style="margin-bottom: var(--space-md)">Eiendeler</h4>
			<div class="form-group" style="margin-bottom: var(--space-md)">
				<label for="aksjeDatter">Aksjer i datterselskap</label>
				<input id="aksjeDatter" type="number" bind:value={$config.balanse.aksjer_i_datterselskap} />
			</div>
			<div class="form-group" style="margin-bottom: var(--space-md)">
				<label for="andreAksjer">Andre aksjer</label>
				<input id="andreAksjer" type="number" bind:value={$config.balanse.andre_aksjer} />
			</div>
			<div class="form-group" style="margin-bottom: var(--space-md)">
				<label for="langFord">Langsiktige fordringer</label>
				<input id="langFord" type="number" bind:value={$config.balanse.langsiktige_fordringer} />
			</div>
			<div class="form-group" style="margin-bottom: var(--space-md)">
				<label for="kortFord">Kortsiktige fordringer</label>
				<input id="kortFord" type="number" bind:value={$config.balanse.kortsiktige_fordringer} />
			</div>
			<div class="form-group" style="margin-bottom: var(--space-md)">
				<label for="bank">Bankinnskudd</label>
				<input id="bank" type="number" bind:value={$config.balanse.bankinnskudd} />
			</div>
			<div class="metric">
				<div class="metric-label">Sum eiendeler</div>
				<div class="metric-value">{formatNOK(sumEiendeler)}</div>
			</div>
		</div>
		<div>
			<h4 style="margin-bottom: var(--space-md)">Egenkapital og gjeld</h4>
			<div class="form-group" style="margin-bottom: var(--space-md)">
				<label for="ekAksje">Aksjekapital</label>
				<input id="ekAksje" type="number" bind:value={$config.balanse.ek_aksjekapital} />
			</div>
			<div class="form-group" style="margin-bottom: var(--space-md)">
				<label for="overkurs">Overkursfond</label>
				<input id="overkurs" type="number" bind:value={$config.balanse.overkursfond} />
			</div>
			<div class="form-group" style="margin-bottom: var(--space-md)">
				<label for="annenEK">Annen egenkapital</label>
				<input id="annenEK" type="number" bind:value={$config.balanse.annen_egenkapital} />
			</div>
			<div class="form-group" style="margin-bottom: var(--space-md)">
				<label for="laanAksj">Lån fra aksjonær</label>
				<input id="laanAksj" type="number" bind:value={$config.balanse.laan_fra_aksjonaer} />
			</div>
			<div class="form-group" style="margin-bottom: var(--space-md)">
				<label for="andreLang">Andre langsiktige lån</label>
				<input id="andreLang" type="number" bind:value={$config.balanse.andre_langsiktige_laan} />
			</div>
			<div class="form-group" style="margin-bottom: var(--space-md)">
				<label for="levgjeld">Leverandørgjeld</label>
				<input id="levgjeld" type="number" bind:value={$config.balanse.leverandoergjeld} />
			</div>
			<div class="form-group" style="margin-bottom: var(--space-md)">
				<label for="offentlig">Skyldige offentlige avgifter</label>
				<input id="offentlig" type="number" bind:value={$config.balanse.skyldige_offentlige_avgifter} />
			</div>
			<div class="form-group" style="margin-bottom: var(--space-md)">
				<label for="annenKort">Annen kortsiktig gjeld</label>
				<input id="annenKort" type="number" bind:value={$config.balanse.annen_kortsiktig_gjeld} />
			</div>
			<div class="metric">
				<div class="metric-label">Sum egenkapital og gjeld</div>
				<div class="metric-value">{formatNOK(sumEkOgGjeld)}</div>
			</div>
		</div>
	</div>

	{#if differanse === 0}
		<div class="alert alert-success" style="margin-top: var(--space-lg)">Balansen stemmer.</div>
	{:else}
		<div class="alert alert-error" style="margin-top: var(--space-lg)">
			Balansen stemmer ikke. Differanse: {formatNOK(differanse)}
		</div>
	{/if}
</div>

<!-- Foregående år -->
<details class="collapsible">
	<summary>Sammenligningstall — foregående år</summary>
	<div class="collapsible-content">
		<div class="card">
			<div class="card-title">Resultatregnskap (foregående)</div>
			<div class="form-grid">
				<div class="form-group">
					<label for="fSalg">Salgsinntekter</label>
					<input id="fSalg" type="number" bind:value={$config.foregaaende_resultat.salgsinntekter} />
				</div>
				<div class="form-group">
					<label for="fAndreDI">Andre driftsinntekter</label>
					<input id="fAndreDI" type="number" bind:value={$config.foregaaende_resultat.andre_driftsinntekter} />
				</div>
				<div class="form-group">
					<label for="fLonn">Lønnskostnader</label>
					<input id="fLonn" type="number" bind:value={$config.foregaaende_resultat.loennskostnader} />
				</div>
				<div class="form-group">
					<label for="fAvskr">Avskrivninger</label>
					<input id="fAvskr" type="number" bind:value={$config.foregaaende_resultat.avskrivninger} />
				</div>
				<div class="form-group">
					<label for="fAndreDK">Andre driftskostnader</label>
					<input id="fAndreDK" type="number" bind:value={$config.foregaaende_resultat.andre_driftskostnader} />
				</div>
				<div class="form-group">
					<label for="fUtbytte">Utbytte fra datterselskap</label>
					<input id="fUtbytte" type="number" bind:value={$config.foregaaende_resultat.utbytte_fra_datterselskap} />
				</div>
				<div class="form-group">
					<label for="fAndreFI">Andre finansinntekter</label>
					<input id="fAndreFI" type="number" bind:value={$config.foregaaende_resultat.andre_finansinntekter} />
				</div>
				<div class="form-group">
					<label for="fRente">Rentekostnader</label>
					<input id="fRente" type="number" bind:value={$config.foregaaende_resultat.rentekostnader} />
				</div>
				<div class="form-group">
					<label for="fAndreFK">Andre finanskostnader</label>
					<input id="fAndreFK" type="number" bind:value={$config.foregaaende_resultat.andre_finanskostnader} />
				</div>
			</div>
		</div>
		<div class="card">
			<div class="card-title">Balanse (foregående)</div>
			<div class="form-grid">
				<div class="form-group">
					<label for="fAksjeDatter">Aksjer i datterselskap</label>
					<input id="fAksjeDatter" type="number" bind:value={$config.foregaaende_balanse.aksjer_i_datterselskap} />
				</div>
				<div class="form-group">
					<label for="fAndreAksjer">Andre aksjer</label>
					<input id="fAndreAksjer" type="number" bind:value={$config.foregaaende_balanse.andre_aksjer} />
				</div>
				<div class="form-group">
					<label for="fLangFord">Langsiktige fordringer</label>
					<input id="fLangFord" type="number" bind:value={$config.foregaaende_balanse.langsiktige_fordringer} />
				</div>
				<div class="form-group">
					<label for="fKortFord">Kortsiktige fordringer</label>
					<input id="fKortFord" type="number" bind:value={$config.foregaaende_balanse.kortsiktige_fordringer} />
				</div>
				<div class="form-group">
					<label for="fBank">Bankinnskudd</label>
					<input id="fBank" type="number" bind:value={$config.foregaaende_balanse.bankinnskudd} />
				</div>
				<div class="form-group">
					<label for="fEkAksje">Aksjekapital</label>
					<input id="fEkAksje" type="number" bind:value={$config.foregaaende_balanse.ek_aksjekapital} />
				</div>
				<div class="form-group">
					<label for="fOverkurs">Overkursfond</label>
					<input id="fOverkurs" type="number" bind:value={$config.foregaaende_balanse.overkursfond} />
				</div>
				<div class="form-group">
					<label for="fAnnenEK">Annen egenkapital</label>
					<input id="fAnnenEK" type="number" bind:value={$config.foregaaende_balanse.annen_egenkapital} />
				</div>
				<div class="form-group">
					<label for="fLaanAksj">Lån fra aksjonær</label>
					<input id="fLaanAksj" type="number" bind:value={$config.foregaaende_balanse.laan_fra_aksjonaer} />
				</div>
				<div class="form-group">
					<label for="fAndreLang">Andre langsiktige lån</label>
					<input id="fAndreLang" type="number" bind:value={$config.foregaaende_balanse.andre_langsiktige_laan} />
				</div>
				<div class="form-group">
					<label for="fLevgjeld">Leverandørgjeld</label>
					<input id="fLevgjeld" type="number" bind:value={$config.foregaaende_balanse.leverandoergjeld} />
				</div>
				<div class="form-group">
					<label for="fOffentlig">Skyldige offentlige avgifter</label>
					<input id="fOffentlig" type="number" bind:value={$config.foregaaende_balanse.skyldige_offentlige_avgifter} />
				</div>
				<div class="form-group">
					<label for="fAnnenKort">Annen kortsiktig gjeld</label>
					<input id="fAnnenKort" type="number" bind:value={$config.foregaaende_balanse.annen_kortsiktig_gjeld} />
				</div>
			</div>
		</div>
	</div>
</details>

{#if message}
	<div class="alert alert-{message.type}" style="margin-top: var(--space-lg)">{message.text}</div>
{/if}

<div style="margin-top: var(--space-lg)">
	<button class="btn btn-primary" onclick={lagre} disabled={saving}>
		{#if saving}<span class="spinner"></span>{/if}
		Lagre regnskapstall
	</button>
</div>
