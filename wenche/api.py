"""
Wenche — REST API (FastAPI).

Eksponerer eksisterende logikk som JSON-endepunkter
for SvelteKit-grensesnittet.
"""

import os
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from wenche import aarsregnskap as ar_modul
from wenche import aksjonaerregister as akr_modul
from wenche import auth, skattemelding as sm_modul, systembruker
from wenche.altinn_client import AltinnClient
from wenche.brg_xml import generer_hovedskjema, generer_underskjema
from wenche.models import (
    Aarsregnskap,
    Aksjonaer,
    Aksjonaerregisteroppgave,
    Anleggsmidler,
    Balanse,
    Driftsinntekter,
    Driftskostnader,
    Egenkapital,
    EgenkapitalOgGjeld,
    Eiendeler,
    Finansposter,
    KortsiktigGjeld,
    LangsiktigGjeld,
    Omloepmidler,
    Resultatregnskap,
    Selskap,
    SkattemeldingKonfig,
)
from wenche.skd_client import SkdAksjonaerClient

CONFIG_FIL = Path("config.yaml")

_WENCHE_DIR = Path.home() / ".wenche"
_REQUEST_ID_FIL = _WENCHE_DIR / "systembruker_request_id.txt"


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Wenche API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic-modeller for request/response
# ---------------------------------------------------------------------------


class EnvKonfig(BaseModel):
    client_id: str = ""
    kid: str = ""
    org_nummer: str = ""
    env: str = "prod"


class KonfigStatus(BaseModel):
    ok: bool
    tittel: str
    detalj: str


class SelskapData(BaseModel):
    navn: str = "Mitt Holding AS"
    org_nummer: str = "123456789"
    daglig_leder: str = "Ola Nordmann"
    styreleder: str = "Ola Nordmann"
    forretningsadresse: str = "Gateveien 1, 0001 Oslo"
    stiftelsesaar: int = 2020
    aksjekapital: int = 30000
    kontakt_epost: str = ""


class ResultatData(BaseModel):
    salgsinntekter: int = 0
    andre_driftsinntekter: int = 0
    loennskostnader: int = 0
    avskrivninger: int = 0
    andre_driftskostnader: int = 5500
    utbytte_fra_datterselskap: int = 0
    andre_finansinntekter: int = 0
    rentekostnader: int = 0
    andre_finanskostnader: int = 0


class BalanseData(BaseModel):
    aksjer_i_datterselskap: int = 100000
    andre_aksjer: int = 0
    langsiktige_fordringer: int = 0
    kortsiktige_fordringer: int = 0
    bankinnskudd: int = 1200
    ek_aksjekapital: int = 30000
    overkursfond: int = 0
    annen_egenkapital: int = -34300
    laan_fra_aksjonaer: int = 105500
    andre_langsiktige_laan: int = 0
    leverandoergjeld: int = 0
    skyldige_offentlige_avgifter: int = 0
    annen_kortsiktig_gjeld: int = 0


class AksjonaerData(BaseModel):
    navn: str = ""
    fodselsnummer: str = ""
    antall_aksjer: int = 1
    aksjeklasse: str = "ordinære"
    utbytte_utbetalt: int = 0
    innbetalt_kapital_per_aksje: int = 0


class SkattemeldingData(BaseModel):
    underskudd: int = 0
    fritaksmetoden: bool = False
    eierandel_datterselskap: int = 100


class FullKonfig(BaseModel):
    selskap: SelskapData = SelskapData()
    regnskapsaar: int = 2025
    resultat: ResultatData = ResultatData()
    balanse: BalanseData = BalanseData()
    foregaaende_resultat: ResultatData = ResultatData()
    foregaaende_balanse: BalanseData = BalanseData()
    skattemelding: SkattemeldingData = SkattemeldingData()
    aksjonaerer: list[AksjonaerData] = []


class SendRequest(BaseModel):
    env: str = "test"


# ---------------------------------------------------------------------------
# Hjelpefunksjoner
# ---------------------------------------------------------------------------


def _les_config() -> dict[str, Any]:
    if CONFIG_FIL.exists():
        with open(CONFIG_FIL, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def _konfig_til_full(cfg: dict) -> FullKonfig:
    """Konverterer config.yaml-dict til FullKonfig."""
    s = cfg.get("selskap", {})
    rr = cfg.get("resultatregnskap", {})
    b = cfg.get("balanse", {})
    fa = cfg.get("foregaaende_aar", {})
    frr = fa.get("resultatregnskap", {})
    fb = fa.get("balanse", {})
    sm = cfg.get("skattemelding", {})

    di = rr.get("driftsinntekter", {})
    dk = rr.get("driftskostnader", {})
    fp = rr.get("finansposter", {})
    anl = b.get("eiendeler", {}).get("anleggsmidler", {})
    oml = b.get("eiendeler", {}).get("omloepmidler", {})
    ek = b.get("egenkapital_og_gjeld", {}).get("egenkapital", {})
    lg = b.get("egenkapital_og_gjeld", {}).get("langsiktig_gjeld", {})
    kg = b.get("egenkapital_og_gjeld", {}).get("kortsiktig_gjeld", {})

    fdi = frr.get("driftsinntekter", {})
    fdk = frr.get("driftskostnader", {})
    ffp = frr.get("finansposter", {})
    fanl = fb.get("eiendeler", {}).get("anleggsmidler", {})
    foml = fb.get("eiendeler", {}).get("omloepmidler", {})
    fek = fb.get("egenkapital_og_gjeld", {}).get("egenkapital", {})
    flg = fb.get("egenkapital_og_gjeld", {}).get("langsiktig_gjeld", {})
    fkg = fb.get("egenkapital_og_gjeld", {}).get("kortsiktig_gjeld", {})

    aksjonaerer_raw = cfg.get("aksjonaerer", [])

    return FullKonfig(
        selskap=SelskapData(
            navn=s.get("navn", "Mitt Holding AS"),
            org_nummer=str(s.get("org_nummer", "123456789")),
            daglig_leder=s.get("daglig_leder", "Ola Nordmann"),
            styreleder=s.get("styreleder", "Ola Nordmann"),
            forretningsadresse=s.get("forretningsadresse", "Gateveien 1, 0001 Oslo"),
            stiftelsesaar=int(s.get("stiftelsesaar", 2020)),
            aksjekapital=int(s.get("aksjekapital", 30000)),
            kontakt_epost=s.get("kontakt_epost", ""),
        ),
        regnskapsaar=int(cfg.get("regnskapsaar", 2025)),
        resultat=ResultatData(
            salgsinntekter=int(di.get("salgsinntekter", 0)),
            andre_driftsinntekter=int(di.get("andre_driftsinntekter", 0)),
            loennskostnader=int(dk.get("loennskostnader", 0)),
            avskrivninger=int(dk.get("avskrivninger", 0)),
            andre_driftskostnader=int(dk.get("andre_driftskostnader", 5500)),
            utbytte_fra_datterselskap=int(fp.get("utbytte_fra_datterselskap", 0)),
            andre_finansinntekter=int(fp.get("andre_finansinntekter", 0)),
            rentekostnader=int(fp.get("rentekostnader", 0)),
            andre_finanskostnader=int(fp.get("andre_finanskostnader", 0)),
        ),
        balanse=BalanseData(
            aksjer_i_datterselskap=int(anl.get("aksjer_i_datterselskap", 100000)),
            andre_aksjer=int(anl.get("andre_aksjer", 0)),
            langsiktige_fordringer=int(anl.get("langsiktige_fordringer", 0)),
            kortsiktige_fordringer=int(oml.get("kortsiktige_fordringer", 0)),
            bankinnskudd=int(oml.get("bankinnskudd", 1200)),
            ek_aksjekapital=int(ek.get("aksjekapital", 30000)),
            overkursfond=int(ek.get("overkursfond", 0)),
            annen_egenkapital=int(ek.get("annen_egenkapital", -34300)),
            laan_fra_aksjonaer=int(lg.get("laan_fra_aksjonaer", 105500)),
            andre_langsiktige_laan=int(lg.get("andre_langsiktige_laan", 0)),
            leverandoergjeld=int(kg.get("leverandoergjeld", 0)),
            skyldige_offentlige_avgifter=int(kg.get("skyldige_offentlige_avgifter", 0)),
            annen_kortsiktig_gjeld=int(kg.get("annen_kortsiktig_gjeld", 0)),
        ),
        foregaaende_resultat=ResultatData(
            salgsinntekter=int(fdi.get("salgsinntekter", 0)),
            andre_driftsinntekter=int(fdi.get("andre_driftsinntekter", 0)),
            loennskostnader=int(fdk.get("loennskostnader", 0)),
            avskrivninger=int(fdk.get("avskrivninger", 0)),
            andre_driftskostnader=int(fdk.get("andre_driftskostnader", 0)),
            utbytte_fra_datterselskap=int(ffp.get("utbytte_fra_datterselskap", 0)),
            andre_finansinntekter=int(ffp.get("andre_finansinntekter", 0)),
            rentekostnader=int(ffp.get("rentekostnader", 0)),
            andre_finanskostnader=int(ffp.get("andre_finanskostnader", 0)),
        ),
        foregaaende_balanse=BalanseData(
            aksjer_i_datterselskap=int(fanl.get("aksjer_i_datterselskap", 0)),
            andre_aksjer=int(fanl.get("andre_aksjer", 0)),
            langsiktige_fordringer=int(fanl.get("langsiktige_fordringer", 0)),
            kortsiktige_fordringer=int(foml.get("kortsiktige_fordringer", 0)),
            bankinnskudd=int(foml.get("bankinnskudd", 0)),
            ek_aksjekapital=int(fek.get("aksjekapital", 0)),
            overkursfond=int(fek.get("overkursfond", 0)),
            annen_egenkapital=int(fek.get("annen_egenkapital", 0)),
            laan_fra_aksjonaer=int(flg.get("laan_fra_aksjonaer", 0)),
            andre_langsiktige_laan=int(flg.get("andre_langsiktige_laan", 0)),
            leverandoergjeld=int(fkg.get("leverandoergjeld", 0)),
            skyldige_offentlige_avgifter=int(fkg.get("skyldige_offentlige_avgifter", 0)),
            annen_kortsiktig_gjeld=int(fkg.get("annen_kortsiktig_gjeld", 0)),
        ),
        skattemelding=SkattemeldingData(
            underskudd=int(sm.get("underskudd_til_fremfoering", 0)),
            fritaksmetoden=bool(sm.get("anvend_fritaksmetoden", False)),
            eierandel_datterselskap=int(sm.get("eierandel_datterselskap", 100)),
        ),
        aksjonaerer=[
            AksjonaerData(
                navn=a.get("navn", ""),
                fodselsnummer=str(a.get("fodselsnummer", "")),
                antall_aksjer=int(a.get("antall_aksjer", 1)),
                aksjeklasse=a.get("aksjeklasse", "ordinære"),
                utbytte_utbetalt=int(a.get("utbytte_utbetalt", 0)),
                innbetalt_kapital_per_aksje=int(a.get("innbetalt_kapital_per_aksje", 0)),
            )
            for a in aksjonaerer_raw
        ],
    )


def _full_til_yaml(data: FullKonfig) -> dict:
    """Konverterer FullKonfig til config.yaml-format."""
    return {
        "selskap": {
            "navn": data.selskap.navn,
            "org_nummer": data.selskap.org_nummer,
            "daglig_leder": data.selskap.daglig_leder,
            "styreleder": data.selskap.styreleder,
            "forretningsadresse": data.selskap.forretningsadresse,
            "stiftelsesaar": data.selskap.stiftelsesaar,
            "aksjekapital": data.selskap.aksjekapital,
            "kontakt_epost": data.selskap.kontakt_epost,
        },
        "regnskapsaar": data.regnskapsaar,
        "resultatregnskap": {
            "driftsinntekter": {
                "salgsinntekter": data.resultat.salgsinntekter,
                "andre_driftsinntekter": data.resultat.andre_driftsinntekter,
            },
            "driftskostnader": {
                "loennskostnader": data.resultat.loennskostnader,
                "avskrivninger": data.resultat.avskrivninger,
                "andre_driftskostnader": data.resultat.andre_driftskostnader,
            },
            "finansposter": {
                "utbytte_fra_datterselskap": data.resultat.utbytte_fra_datterselskap,
                "andre_finansinntekter": data.resultat.andre_finansinntekter,
                "rentekostnader": data.resultat.rentekostnader,
                "andre_finanskostnader": data.resultat.andre_finanskostnader,
            },
        },
        "balanse": {
            "eiendeler": {
                "anleggsmidler": {
                    "aksjer_i_datterselskap": data.balanse.aksjer_i_datterselskap,
                    "andre_aksjer": data.balanse.andre_aksjer,
                    "langsiktige_fordringer": data.balanse.langsiktige_fordringer,
                },
                "omloepmidler": {
                    "kortsiktige_fordringer": data.balanse.kortsiktige_fordringer,
                    "bankinnskudd": data.balanse.bankinnskudd,
                },
            },
            "egenkapital_og_gjeld": {
                "egenkapital": {
                    "aksjekapital": data.balanse.ek_aksjekapital,
                    "overkursfond": data.balanse.overkursfond,
                    "annen_egenkapital": data.balanse.annen_egenkapital,
                },
                "langsiktig_gjeld": {
                    "laan_fra_aksjonaer": data.balanse.laan_fra_aksjonaer,
                    "andre_langsiktige_laan": data.balanse.andre_langsiktige_laan,
                },
                "kortsiktig_gjeld": {
                    "leverandoergjeld": data.balanse.leverandoergjeld,
                    "skyldige_offentlige_avgifter": data.balanse.skyldige_offentlige_avgifter,
                    "annen_kortsiktig_gjeld": data.balanse.annen_kortsiktig_gjeld,
                },
            },
        },
        "foregaaende_aar": {
            "resultatregnskap": {
                "driftsinntekter": {
                    "salgsinntekter": data.foregaaende_resultat.salgsinntekter,
                    "andre_driftsinntekter": data.foregaaende_resultat.andre_driftsinntekter,
                },
                "driftskostnader": {
                    "loennskostnader": data.foregaaende_resultat.loennskostnader,
                    "avskrivninger": data.foregaaende_resultat.avskrivninger,
                    "andre_driftskostnader": data.foregaaende_resultat.andre_driftskostnader,
                },
                "finansposter": {
                    "utbytte_fra_datterselskap": data.foregaaende_resultat.utbytte_fra_datterselskap,
                    "andre_finansinntekter": data.foregaaende_resultat.andre_finansinntekter,
                    "rentekostnader": data.foregaaende_resultat.rentekostnader,
                    "andre_finanskostnader": data.foregaaende_resultat.andre_finanskostnader,
                },
            },
            "balanse": {
                "eiendeler": {
                    "anleggsmidler": {
                        "aksjer_i_datterselskap": data.foregaaende_balanse.aksjer_i_datterselskap,
                        "andre_aksjer": data.foregaaende_balanse.andre_aksjer,
                        "langsiktige_fordringer": data.foregaaende_balanse.langsiktige_fordringer,
                    },
                    "omloepmidler": {
                        "kortsiktige_fordringer": data.foregaaende_balanse.kortsiktige_fordringer,
                        "bankinnskudd": data.foregaaende_balanse.bankinnskudd,
                    },
                },
                "egenkapital_og_gjeld": {
                    "egenkapital": {
                        "aksjekapital": data.foregaaende_balanse.ek_aksjekapital,
                        "overkursfond": data.foregaaende_balanse.overkursfond,
                        "annen_egenkapital": data.foregaaende_balanse.annen_egenkapital,
                    },
                    "langsiktig_gjeld": {
                        "laan_fra_aksjonaer": data.foregaaende_balanse.laan_fra_aksjonaer,
                        "andre_langsiktige_laan": data.foregaaende_balanse.andre_langsiktige_laan,
                    },
                    "kortsiktig_gjeld": {
                        "leverandoergjeld": data.foregaaende_balanse.leverandoergjeld,
                        "skyldige_offentlige_avgifter": data.foregaaende_balanse.skyldige_offentlige_avgifter,
                        "annen_kortsiktig_gjeld": data.foregaaende_balanse.annen_kortsiktig_gjeld,
                    },
                },
            },
        },
        "skattemelding": {
            "underskudd_til_fremfoering": data.skattemelding.underskudd,
            "anvend_fritaksmetoden": data.skattemelding.fritaksmetoden,
            "eierandel_datterselskap": data.skattemelding.eierandel_datterselskap,
        },
        "aksjonaerer": [
            {
                "navn": a.navn,
                "fodselsnummer": a.fodselsnummer,
                "antall_aksjer": a.antall_aksjer,
                "aksjeklasse": a.aksjeklasse,
                "utbytte_utbetalt": a.utbytte_utbetalt,
                "innbetalt_kapital_per_aksje": a.innbetalt_kapital_per_aksje,
            }
            for a in data.aksjonaerer
        ],
    }


def _bygg_regnskap(data: FullKonfig) -> Aarsregnskap:
    """Bygger et Aarsregnskap-objekt fra FullKonfig."""
    utbytte = sum(a.utbytte_utbetalt for a in data.aksjonaerer)

    def _resultat(r: ResultatData) -> Resultatregnskap:
        return Resultatregnskap(
            driftsinntekter=Driftsinntekter(r.salgsinntekter, r.andre_driftsinntekter),
            driftskostnader=Driftskostnader(r.loennskostnader, r.avskrivninger, r.andre_driftskostnader),
            finansposter=Finansposter(r.utbytte_fra_datterselskap, r.andre_finansinntekter, r.rentekostnader, r.andre_finanskostnader),
        )

    def _balanse(b: BalanseData) -> Balanse:
        return Balanse(
            eiendeler=Eiendeler(
                anleggsmidler=Anleggsmidler(b.aksjer_i_datterselskap, b.andre_aksjer, b.langsiktige_fordringer),
                omloepmidler=Omloepmidler(b.kortsiktige_fordringer, b.bankinnskudd),
            ),
            egenkapital_og_gjeld=EgenkapitalOgGjeld(
                egenkapital=Egenkapital(b.ek_aksjekapital, b.overkursfond, b.annen_egenkapital),
                langsiktig_gjeld=LangsiktigGjeld(b.laan_fra_aksjonaer, b.andre_langsiktige_laan),
                kortsiktig_gjeld=KortsiktigGjeld(b.leverandoergjeld, b.skyldige_offentlige_avgifter, b.annen_kortsiktig_gjeld),
            ),
        )

    return Aarsregnskap(
        utbytte_utbetalt=utbytte,
        selskap=Selskap(
            data.selskap.navn, data.selskap.org_nummer, data.selskap.daglig_leder,
            data.selskap.styreleder, data.selskap.forretningsadresse,
            data.selskap.stiftelsesaar, data.selskap.aksjekapital, data.selskap.kontakt_epost,
        ),
        regnskapsaar=data.regnskapsaar,
        resultatregnskap=_resultat(data.resultat),
        balanse=_balanse(data.balanse),
        foregaaende_aar_resultat=_resultat(data.foregaaende_resultat),
        foregaaende_aar_balanse=_balanse(data.foregaaende_balanse),
    )


# ---------------------------------------------------------------------------
# Endepunkter
# ---------------------------------------------------------------------------


@app.get("/api/config")
def hent_config() -> FullKonfig:
    cfg = _les_config()
    return _konfig_til_full(cfg)


@app.post("/api/config")
def lagre_config(data: FullKonfig):
    yaml_data = _full_til_yaml(data)
    with open(CONFIG_FIL, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False)
    return {"ok": True}


@app.get("/api/status")
def sjekk_status() -> list[KonfigStatus]:
    resultater = []

    client_id = os.getenv("MASKINPORTEN_CLIENT_ID")
    resultater.append(KonfigStatus(
        ok=bool(client_id),
        tittel="MASKINPORTEN_CLIENT_ID",
        detalj="Satt" if client_id else "Mangler — legg til i .env-filen",
    ))

    kid = os.getenv("MASKINPORTEN_KID")
    resultater.append(KonfigStatus(
        ok=bool(kid),
        tittel="MASKINPORTEN_KID",
        detalj="Satt" if kid else "Mangler — legg til i .env-filen",
    ))

    orgnr = os.getenv("ORG_NUMMER")
    resultater.append(KonfigStatus(
        ok=bool(orgnr),
        tittel="ORG_NUMMER",
        detalj="Satt" if orgnr else "Mangler — legg til i .env-filen",
    ))

    nokkel_sti = os.getenv("MASKINPORTEN_PRIVAT_NOKKEL", "maskinporten_privat.pem")
    nokkel_ok = Path(nokkel_sti).exists()
    resultater.append(KonfigStatus(
        ok=nokkel_ok,
        tittel="Privat nøkkel",
        detalj=f"Funnet: {nokkel_sti}" if nokkel_ok else f"Finner ikke: {nokkel_sti}",
    ))

    env = os.getenv("WENCHE_ENV", "prod")
    resultater.append(KonfigStatus(
        ok=True,
        tittel="Miljø",
        detalj=f"{'Testmiljø (tt02)' if env == 'test' else 'Produksjon'}",
    ))

    return resultater


@app.post("/api/env")
def lagre_env(data: EnvKonfig):
    from dotenv import set_key
    dot_env = Path(".env")
    dot_env.touch(exist_ok=True)

    if data.client_id:
        set_key(str(dot_env), "MASKINPORTEN_CLIENT_ID", data.client_id)
        os.environ["MASKINPORTEN_CLIENT_ID"] = data.client_id
    if data.kid:
        set_key(str(dot_env), "MASKINPORTEN_KID", data.kid)
        os.environ["MASKINPORTEN_KID"] = data.kid
    if data.org_nummer:
        set_key(str(dot_env), "ORG_NUMMER", data.org_nummer)
        os.environ["ORG_NUMMER"] = data.org_nummer

    set_key(str(dot_env), "WENCHE_ENV", data.env)
    os.environ["WENCHE_ENV"] = data.env

    return {"ok": True}


@app.post("/api/test-connection")
def test_tilkobling():
    try:
        auth.login()
        return {"ok": True, "melding": "Tilkobling OK"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/register-system")
def registrer_system():
    try:
        token = auth.login_admin()
        orgnr = os.getenv("ORG_NUMMER")
        client_id = os.getenv("MASKINPORTEN_CLIENT_ID")
        svar = systembruker.registrer_system(token, orgnr, client_id)
        return {"ok": True, "oppdatert": svar.get("oppdatert", False)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/create-system-user")
def opprett_systembruker():
    try:
        token = auth.login_admin()
        orgnr = os.getenv("ORG_NUMMER")
        svar = systembruker.opprett_forespørsel(token, orgnr, orgnr)
        request_id = svar.get("id", "")
        if request_id:
            _WENCHE_DIR.mkdir(exist_ok=True)
            _REQUEST_ID_FIL.write_text(request_id, encoding="utf-8")
        return {
            "ok": True,
            "status": svar.get("status"),
            "confirmUrl": svar.get("confirmUrl"),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/system-user-status")
def sjekk_systembruker_status():
    if not _REQUEST_ID_FIL.exists():
        raise HTTPException(status_code=404, detail="Ingen forespørsel funnet")
    request_id = _REQUEST_ID_FIL.read_text(encoding="utf-8").strip()
    try:
        token = auth.login_admin()
        svar = systembruker.hent_forespørsel_status(token, request_id)
        return {"status": svar.get("status", "ukjent")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/generate/skattemelding")
def generer_skattemelding(data: FullKonfig):
    regnskap = _bygg_regnskap(data)
    konfig = SkattemeldingKonfig(
        underskudd_til_fremfoering=data.skattemelding.underskudd,
        anvend_fritaksmetoden=data.skattemelding.fritaksmetoden,
        eierandel_datterselskap=data.skattemelding.eierandel_datterselskap,
    )
    tekst = sm_modul.generer(regnskap, konfig)
    return {"tekst": tekst}


@app.post("/api/generate/aarsregnskap")
def generer_aarsregnskap(data: FullKonfig):
    regnskap = _bygg_regnskap(data)
    feil = ar_modul.valider(regnskap)
    if feil:
        raise HTTPException(status_code=422, detail=feil)
    return {
        "hovedskjema": generer_hovedskjema(regnskap),
        "underskjema": generer_underskjema(regnskap),
    }


@app.post("/api/generate/aksjonaerregister")
def generer_aksjonaerregister(data: FullKonfig):
    regnskap = _bygg_regnskap(data)
    aksjonaerer = [
        Aksjonaer(a.navn, a.fodselsnummer, a.antall_aksjer, a.aksjeklasse,
                  a.utbytte_utbetalt, a.innbetalt_kapital_per_aksje)
        for a in data.aksjonaerer
    ]
    oppgave = Aksjonaerregisteroppgave(regnskap.selskap, data.regnskapsaar, aksjonaerer)
    feil = akr_modul.valider(oppgave)
    if feil:
        raise HTTPException(status_code=422, detail=feil)
    result = {
        "hovedskjema": akr_modul.generer_hovedskjema_xml(oppgave),
        "underskjemaer": [
            {"navn": a.navn, "xml": akr_modul.generer_underskjema_xml(a, oppgave)}
            for a in oppgave.aksjonaerer
        ],
    }
    return result


@app.post("/api/send/aarsregnskap")
def send_aarsregnskap(data: FullKonfig, req: SendRequest = SendRequest()):
    regnskap = _bygg_regnskap(data)
    feil = ar_modul.valider(regnskap)
    if feil:
        raise HTTPException(status_code=422, detail=feil)
    try:
        token = auth.get_altinn_token()
        with AltinnClient(token, env=req.env) as klient:
            sign_url = ar_modul.send_inn(regnskap, klient)
        return {"ok": True, "sign_url": sign_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/send/aksjonaerregister")
def send_aksjonaerregister(data: FullKonfig, req: SendRequest = SendRequest()):
    regnskap = _bygg_regnskap(data)
    aksjonaerer = [
        Aksjonaer(a.navn, a.fodselsnummer, a.antall_aksjer, a.aksjeklasse,
                  a.utbytte_utbetalt, a.innbetalt_kapital_per_aksje)
        for a in data.aksjonaerer
    ]
    oppgave = Aksjonaerregisteroppgave(regnskap.selskap, data.regnskapsaar, aksjonaerer)
    feil = akr_modul.valider(oppgave)
    if feil:
        raise HTTPException(status_code=422, detail=feil)
    try:
        skd_token = auth.get_skd_aksjonaer_token()
        with SkdAksjonaerClient(skd_token, env=req.env) as klient:
            svar = akr_modul.send_inn(oppgave, klient)
        return {"ok": True, "forsendelse_id": svar.get("forsendelseId") if svar else None}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
