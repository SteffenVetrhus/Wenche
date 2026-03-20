"""
Klient for Brønnøysundregistrenes Enhetsregister-API.

Henter selskapsinfo (navn, adresse, roller) fra det åpne API-et
slik at brukeren slipper å fylle ut alt manuelt.

API-dokumentasjon: https://data.brreg.no/enhetsregisteret/api/docs/index.html
"""

from dataclasses import dataclass, field
from typing import Optional

import httpx

_BASE_URL = "https://data.brreg.no/enhetsregisteret/api"


@dataclass
class BrregEnhet:
    """Selskapsinformasjon hentet fra Enhetsregisteret."""

    organisasjonsnummer: str
    navn: str
    organisasjonsform: str = ""
    forretningsadresse: str = ""
    postadresse: str = ""
    stiftelsesdato: str = ""
    registreringsdato: str = ""
    naeringskode: str = ""
    antall_ansatte: int = 0
    konkurs: bool = False
    under_avvikling: bool = False
    hjemmeside: str = ""
    epostadresse: str = ""
    daglig_leder: str = ""
    styreleder: str = ""


def _formater_adresse(adresse_obj: dict) -> str:
    """Formater en Brreg-adresse til en lesbar streng."""
    if not adresse_obj:
        return ""
    deler = []
    for linje in adresse_obj.get("adresse", []):
        if linje:
            deler.append(linje)
    postnr = adresse_obj.get("postnummer", "")
    poststed = adresse_obj.get("poststed", "")
    if postnr and poststed:
        deler.append(f"{postnr} {poststed}")
    return ", ".join(deler)


def _parse_enhet(data: dict) -> BrregEnhet:
    """Parser JSON-responsen fra Enhetsregisteret til en BrregEnhet."""
    naeringskode = ""
    if nk := data.get("naeringskode1"):
        naeringskode = f"{nk.get('kode', '')} {nk.get('beskrivelse', '')}".strip()

    orgform = ""
    if of := data.get("organisasjonsform"):
        orgform = of.get("beskrivelse", of.get("kode", ""))

    return BrregEnhet(
        organisasjonsnummer=data["organisasjonsnummer"],
        navn=data["navn"],
        organisasjonsform=orgform,
        forretningsadresse=_formater_adresse(data.get("forretningsadresse", {})),
        postadresse=_formater_adresse(data.get("postadresse", {})),
        stiftelsesdato=data.get("stiftelsesdato", ""),
        registreringsdato=data.get("registreringsdatoEnhetsregisteret", ""),
        naeringskode=naeringskode,
        antall_ansatte=data.get("antallAnsatte", 0),
        konkurs=data.get("konkurs", False),
        under_avvikling=data.get("underAvvikling", False),
        hjemmeside=data.get("hjemmeside", ""),
        epostadresse=data.get("epostadresse", ""),
    )


def _hent_roller(data: dict, enhet: BrregEnhet) -> None:
    """Henter daglig leder og styreleder fra rollegrupper."""
    for gruppe in data.get("rollegrupper", []):
        kode = gruppe.get("type", {}).get("kode", "")
        for rolle in gruppe.get("roller", []):
            if rolle.get("fratraadt"):
                continue
            person = rolle.get("person", {})
            if not person:
                continue
            navn_obj = person.get("navn", {})
            fornavn = navn_obj.get("fornavn", "")
            etternavn = navn_obj.get("etternavn", "")
            fullt_navn = f"{fornavn} {etternavn}".strip()
            if not fullt_navn:
                continue

            rolle_kode = rolle.get("type", {}).get("kode", "")
            if kode == "DAGL" or rolle_kode == "DAGL":
                enhet.daglig_leder = fullt_navn
            if rolle_kode == "LEDE":
                enhet.styreleder = fullt_navn


class BrregClient:
    """Klient for Enhetsregisteret sitt åpne API (ingen autentisering)."""

    def __init__(self, timeout: int = 15):
        self._http = httpx.Client(
            base_url=_BASE_URL,
            headers={"Accept": "application/json"},
            timeout=timeout,
        )

    def hent_enhet(self, org_nummer: str) -> BrregEnhet:
        """
        Henter selskapsinfo fra Enhetsregisteret.

        Raises:
            httpx.HTTPStatusError: Hvis API-kallet feiler (404 = ukjent org.nr.).
            ValueError: Hvis org.nr. har ugyldig format.
        """
        org_nummer = org_nummer.replace(" ", "")
        if not org_nummer.isdigit() or len(org_nummer) != 9:
            raise ValueError(
                f"Ugyldig organisasjonsnummer: {org_nummer!r}. "
                "Må være nøyaktig 9 siffer."
            )

        resp = self._http.get(f"/enheter/{org_nummer}")
        if resp.status_code == 404:
            # Prøv underenheter (avdelinger, filialer)
            resp = self._http.get(f"/underenheter/{org_nummer}")
        if resp.status_code == 404:
            raise ValueError(
                f"Fant ikke organisasjonsnummer {org_nummer} i Enhetsregisteret. "
                "Sjekk at nummeret er riktig."
            )
        resp.raise_for_status()
        enhet = _parse_enhet(resp.json())

        # Hent roller (daglig leder, styreleder) fra eget endepunkt
        try:
            roller_resp = self._http.get(f"/enheter/{org_nummer}/roller")
            roller_resp.raise_for_status()
            _hent_roller(roller_resp.json(), enhet)
        except httpx.HTTPStatusError:
            pass  # Roller er valgfritt — noen enhetstyper har ikke roller

        return enhet

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def hent_enhet(org_nummer: str) -> BrregEnhet:
    """Bekvemmelighetsfunksjon — henter enhet uten å opprette klient manuelt."""
    with BrregClient() as klient:
        return klient.hent_enhet(org_nummer)
