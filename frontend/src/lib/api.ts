async function request<T>(path: string, opts?: RequestInit): Promise<T> {
	const res = await fetch(path, {
		headers: { 'Content-Type': 'application/json' },
		...opts
	});
	if (!res.ok) {
		const body = await res.json().catch(() => ({ detail: res.statusText }));
		throw new Error(Array.isArray(body.detail) ? body.detail.join('\n') : body.detail);
	}
	return res.json();
}

export const api = {
	getConfig: () => request<FullKonfig>('/api/config'),
	saveConfig: (data: FullKonfig) => request('/api/config', { method: 'POST', body: JSON.stringify(data) }),
	getStatus: () => request<KonfigStatus[]>('/api/status'),
	saveEnv: (data: EnvKonfig) => request('/api/env', { method: 'POST', body: JSON.stringify(data) }),
	testConnection: () => request<{ ok: boolean; melding: string }>('/api/test-connection', { method: 'POST' }),
	registerSystem: () => request('/api/register-system', { method: 'POST' }),
	createSystemUser: () => request<{ ok: boolean; status: string; confirmUrl: string }>('/api/create-system-user', { method: 'POST' }),
	systemUserStatus: () => request<{ status: string }>('/api/system-user-status'),
	generateSkattemelding: (data: FullKonfig) => request<{ tekst: string }>('/api/generate/skattemelding', { method: 'POST', body: JSON.stringify(data) }),
	generateAarsregnskap: (data: FullKonfig) => request<{ hovedskjema: string; underskjema: string }>('/api/generate/aarsregnskap', { method: 'POST', body: JSON.stringify(data) }),
	generateAksjonaerregister: (data: FullKonfig) => request<{ hovedskjema: string; underskjemaer: { navn: string; xml: string }[] }>('/api/generate/aksjonaerregister', { method: 'POST', body: JSON.stringify(data) }),
	sendAarsregnskap: (data: FullKonfig, env: string) => request<{ ok: boolean; sign_url: string }>('/api/send/aarsregnskap', { method: 'POST', body: JSON.stringify({ ...data, env }) }),
	sendAksjonaerregister: (data: FullKonfig, env: string) => request<{ ok: boolean; forsendelse_id: string }>('/api/send/aksjonaerregister', { method: 'POST', body: JSON.stringify({ ...data, env }) }),
	hentSelskap: (orgNummer: string) => request<BrregEnhetData>(`/api/brreg/${orgNummer}`)
};

export interface KonfigStatus {
	ok: boolean;
	tittel: string;
	detalj: string;
}

export interface EnvKonfig {
	client_id: string;
	kid: string;
	org_nummer: string;
	env: string;
}

export interface SelskapData {
	navn: string;
	org_nummer: string;
	daglig_leder: string;
	styreleder: string;
	forretningsadresse: string;
	stiftelsesaar: number;
	aksjekapital: number;
	kontakt_epost: string;
}

export interface ResultatData {
	salgsinntekter: number;
	andre_driftsinntekter: number;
	loennskostnader: number;
	avskrivninger: number;
	andre_driftskostnader: number;
	utbytte_fra_datterselskap: number;
	andre_finansinntekter: number;
	rentekostnader: number;
	andre_finanskostnader: number;
}

export interface BalanseData {
	aksjer_i_datterselskap: number;
	andre_aksjer: number;
	langsiktige_fordringer: number;
	kortsiktige_fordringer: number;
	bankinnskudd: number;
	ek_aksjekapital: number;
	overkursfond: number;
	annen_egenkapital: number;
	laan_fra_aksjonaer: number;
	andre_langsiktige_laan: number;
	leverandoergjeld: number;
	skyldige_offentlige_avgifter: number;
	annen_kortsiktig_gjeld: number;
}

export interface AksjonaerData {
	navn: string;
	fodselsnummer: string;
	antall_aksjer: number;
	aksjeklasse: string;
	utbytte_utbetalt: number;
	innbetalt_kapital_per_aksje: number;
}

export interface SkattemeldingData {
	underskudd: number;
	fritaksmetoden: boolean;
	eierandel_datterselskap: number;
}

export interface BrregEnhetData {
	navn: string;
	org_nummer: string;
	organisasjonsform: string;
	forretningsadresse: string;
	daglig_leder: string;
	styreleder: string;
	stiftelsesaar: number;
	epostadresse: string;
	hjemmeside: string;
	naeringskode: string;
	konkurs: boolean;
	under_avvikling: boolean;
}

export interface FullKonfig {
	selskap: SelskapData;
	regnskapsaar: number;
	resultat: ResultatData;
	balanse: BalanseData;
	foregaaende_resultat: ResultatData;
	foregaaende_balanse: BalanseData;
	skattemelding: SkattemeldingData;
	aksjonaerer: AksjonaerData[];
}
