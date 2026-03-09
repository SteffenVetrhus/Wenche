"""
Systembruker-flyt for Altinn 3.

Altinn 3 krever at sluttbrukersystemer registrerer seg i systemregisteret
og oppretter en systembruker for hver organisasjon de skal handle på vegne av.

Oppsett (kjøres én gang):
  1. wenche registrer-system   — registrerer Wenche i Altinns systemregister
  2. wenche opprett-systembruker — sender forespørsel til org om godkjenning
  3. Brukeren godkjenner via confirmUrl i nettleseren

Ved innsending bruker wenche login et systembruker-token fra Maskinporten.
"""

import os

import httpx

_BASES = {
    "test": "https://platform.tt02.altinn.no",
    "prod": "https://platform.altinn.no",
}

_SYSTEM_NAVN = "wenche"

# Ressurs-ID for BRG årsregnskap-appen i Altinns ressursregister.
# Verifiseres mot live miljø under tt02-testing.
_BRG_RESSURS = "brg-aarsregnskap-vanlig-202406"


def _base() -> str:
    env = os.getenv("WENCHE_ENV", "prod")
    return _BASES[env]


def system_id(vendor_orgnr: str) -> str:
    """Returnerer system-ID på formatet <orgnr>_wenche."""
    return f"{vendor_orgnr}_{_SYSTEM_NAVN}"


def registrer_system(maskinporten_token: str, vendor_orgnr: str, client_id: str) -> dict:
    """
    Registrerer Wenche i Altinns systemregister.

    Kjøres én gang per miljø (test/prod). Kan kjøres på nytt uten skade
    dersom systemet allerede er registrert (returnerer da feilkode fra Altinn).
    """
    sid = system_id(vendor_orgnr)
    payload = {
        "id": sid,
        "vendor": {
            "authority": "iso6523-actorid-upis",
            "ID": f"0192:{vendor_orgnr}",
        },
        "name": {"nb": "Wenche", "en": "Wenche"},
        "description": {
            "nb": "Enkel innsending av årsregnskap til Brønnøysundregistrene for holdingselskaper.",
            "en": "Simple annual accounts submission to the Register of Business Enterprises.",
        },
        "rights": [
            {
                "resource": [
                    {"id": "urn:altinn:resource", "value": _BRG_RESSURS},
                ]
            }
        ],
        "clientId": [client_id],
        "isVisible": True,
    }
    resp = httpx.post(
        f"{_base()}/authentication/api/v1/systemregister/vendor",
        json=payload,
        headers={
            "Authorization": f"Bearer {maskinporten_token}",
            "Content-Type": "application/json",
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def opprett_forespørsel(
    maskinporten_token: str, vendor_orgnr: str, org_nummer: str
) -> dict:
    """
    Oppretter en systembrukerforespørsel for organisasjonen.

    Returnerer {'id': '<uuid>', 'status': 'New', 'confirmUrl': '...'}.
    Brukeren må gå til confirmUrl og godkjenne i nettleseren.
    """
    sid = system_id(vendor_orgnr)
    payload = {
        "systemId": sid,
        "partyOrgNo": org_nummer,
        "integrationTitle": "Wenche årsregnskap",
        "rights": [
            {
                "resource": [
                    {"id": "urn:altinn:resource", "value": _BRG_RESSURS},
                ]
            }
        ],
    }
    resp = httpx.post(
        f"{_base()}/authentication/api/v1/systemuser/request/vendor",
        json=payload,
        headers={
            "Authorization": f"Bearer {maskinporten_token}",
            "Content-Type": "application/json",
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def hent_forespørsel_status(maskinporten_token: str, request_id: str) -> dict:
    """Henter status for en systembrukerforespørsel."""
    resp = httpx.get(
        f"{_base()}/authentication/api/v1/systemuser/request/vendor/{request_id}",
        headers={"Authorization": f"Bearer {maskinporten_token}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()
