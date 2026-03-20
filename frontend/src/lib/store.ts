import { writable } from 'svelte/store';
import type { FullKonfig } from './api';

const defaultConfig: FullKonfig = {
	selskap: {
		navn: 'Mitt Holding AS',
		org_nummer: '123456789',
		daglig_leder: 'Ola Nordmann',
		styreleder: 'Ola Nordmann',
		forretningsadresse: 'Gateveien 1, 0001 Oslo',
		stiftelsesaar: 2020,
		aksjekapital: 30000,
		kontakt_epost: ''
	},
	regnskapsaar: 2025,
	resultat: {
		salgsinntekter: 0,
		andre_driftsinntekter: 0,
		loennskostnader: 0,
		avskrivninger: 0,
		andre_driftskostnader: 5500,
		utbytte_fra_datterselskap: 0,
		andre_finansinntekter: 0,
		rentekostnader: 0,
		andre_finanskostnader: 0
	},
	balanse: {
		aksjer_i_datterselskap: 100000,
		andre_aksjer: 0,
		langsiktige_fordringer: 0,
		kortsiktige_fordringer: 0,
		bankinnskudd: 1200,
		ek_aksjekapital: 30000,
		overkursfond: 0,
		annen_egenkapital: -34300,
		laan_fra_aksjonaer: 105500,
		andre_langsiktige_laan: 0,
		leverandoergjeld: 0,
		skyldige_offentlige_avgifter: 0,
		annen_kortsiktig_gjeld: 0
	},
	foregaaende_resultat: {
		salgsinntekter: 0,
		andre_driftsinntekter: 0,
		loennskostnader: 0,
		avskrivninger: 0,
		andre_driftskostnader: 0,
		utbytte_fra_datterselskap: 0,
		andre_finansinntekter: 0,
		rentekostnader: 0,
		andre_finanskostnader: 0
	},
	foregaaende_balanse: {
		aksjer_i_datterselskap: 0,
		andre_aksjer: 0,
		langsiktige_fordringer: 0,
		kortsiktige_fordringer: 0,
		bankinnskudd: 0,
		ek_aksjekapital: 0,
		overkursfond: 0,
		annen_egenkapital: 0,
		laan_fra_aksjonaer: 0,
		andre_langsiktige_laan: 0,
		leverandoergjeld: 0,
		skyldige_offentlige_avgifter: 0,
		annen_kortsiktig_gjeld: 0
	},
	skattemelding: {
		underskudd: 0,
		fritaksmetoden: false,
		eierandel_datterselskap: 100
	},
	aksjonaerer: []
};

export const config = writable<FullKonfig>(structuredClone(defaultConfig));
export const configLoaded = writable(false);

export function formatNOK(n: number): string {
	return n.toLocaleString('nb-NO') + ' kr';
}
