"""Tester for Brreg Enhetsregister-klienten."""

import pytest

from wenche.brreg_client import (
    BrregClient,
    BrregEnhet,
    _formater_adresse,
    _hent_roller,
    _parse_enhet,
)


# ---------------------------------------------------------------------------
# Eksempeldata (basert på reelt API-svar)
# ---------------------------------------------------------------------------

ENHET_JSON = {
    "organisasjonsnummer": "974760673",
    "navn": "REGISTERENHETEN I BRØNNØYSUND",
    "organisasjonsform": {
        "kode": "ORGL",
        "beskrivelse": "Organisasjonsledd",
    },
    "forretningsadresse": {
        "land": "Norge",
        "landkode": "NO",
        "postnummer": "8900",
        "poststed": "BRØNNØYSUND",
        "adresse": ["Havnegata 48"],
        "kommune": "BRØNNØY",
        "kommunenummer": "1813",
    },
    "postadresse": {
        "land": "Norge",
        "landkode": "NO",
        "postnummer": "8910",
        "poststed": "BRØNNØYSUND",
        "adresse": ["Postboks 900"],
        "kommune": "BRØNNØY",
        "kommunenummer": "1813",
    },
    "registreringsdatoEnhetsregisteret": "1995-08-09",
    "naeringskode1": {
        "kode": "84.110",
        "beskrivelse": "Generell offentlig administrasjon",
    },
    "antallAnsatte": 481,
    "konkurs": False,
    "underAvvikling": False,
    "hjemmeside": "www.brreg.no",
    "epostadresse": "firmapost@brreg.no",
}

ROLLER_JSON = {
    "rollegrupper": [
        {
            "type": {"kode": "DAGL", "beskrivelse": "Daglig leder/ adm.direktør"},
            "roller": [
                {
                    "type": {"kode": "DAGL", "beskrivelse": "Daglig leder/ adm.direktør"},
                    "person": {
                        "fodselsdato": "1970-01-01",
                        "navn": {"fornavn": "Lars", "etternavn": "Pansen"},
                    },
                    "fratraadt": False,
                },
            ],
        },
        {
            "type": {"kode": "STYR", "beskrivelse": "Styre"},
            "roller": [
                {
                    "type": {"kode": "LEDE", "beskrivelse": "Styrets leder"},
                    "person": {
                        "fodselsdato": "1965-05-15",
                        "navn": {"fornavn": "Kari", "etternavn": "Nordmann"},
                    },
                    "fratraadt": False,
                },
                {
                    "type": {"kode": "MEDL", "beskrivelse": "Styremedlem"},
                    "person": {
                        "fodselsdato": "1980-03-20",
                        "navn": {"fornavn": "Per", "etternavn": "Hansen"},
                    },
                    "fratraadt": False,
                },
            ],
        },
    ]
}


# ---------------------------------------------------------------------------
# Tester for adresseformatering
# ---------------------------------------------------------------------------

class TestFormaterAdresse:
    def test_full_adresse(self):
        adresse = {
            "adresse": ["Havnegata 48"],
            "postnummer": "8900",
            "poststed": "BRØNNØYSUND",
        }
        assert _formater_adresse(adresse) == "Havnegata 48, 8900 BRØNNØYSUND"

    def test_tom_adresse(self):
        assert _formater_adresse({}) == ""
        assert _formater_adresse(None) == ""

    def test_flere_adresselinjer(self):
        adresse = {
            "adresse": ["c/o Firma AS", "Storgata 1"],
            "postnummer": "0001",
            "poststed": "OSLO",
        }
        assert _formater_adresse(adresse) == "c/o Firma AS, Storgata 1, 0001 OSLO"

    def test_kun_poststed(self):
        adresse = {"postnummer": "0001", "poststed": "OSLO"}
        assert _formater_adresse(adresse) == "0001 OSLO"


# ---------------------------------------------------------------------------
# Tester for parsing av enhetsdata
# ---------------------------------------------------------------------------

class TestParseEnhet:
    def test_parser_alle_felter(self):
        enhet = _parse_enhet(ENHET_JSON)

        assert enhet.organisasjonsnummer == "974760673"
        assert enhet.navn == "REGISTERENHETEN I BRØNNØYSUND"
        assert enhet.organisasjonsform == "Organisasjonsledd"
        assert enhet.forretningsadresse == "Havnegata 48, 8900 BRØNNØYSUND"
        assert enhet.postadresse == "Postboks 900, 8910 BRØNNØYSUND"
        assert enhet.registreringsdato == "1995-08-09"
        assert enhet.naeringskode == "84.110 Generell offentlig administrasjon"
        assert enhet.antall_ansatte == 481
        assert enhet.konkurs is False
        assert enhet.under_avvikling is False
        assert enhet.hjemmeside == "www.brreg.no"
        assert enhet.epostadresse == "firmapost@brreg.no"

    def test_minimalt_svar(self):
        data = {"organisasjonsnummer": "999999999", "navn": "Test AS"}
        enhet = _parse_enhet(data)

        assert enhet.organisasjonsnummer == "999999999"
        assert enhet.navn == "Test AS"
        assert enhet.forretningsadresse == ""
        assert enhet.naeringskode == ""
        assert enhet.antall_ansatte == 0


# ---------------------------------------------------------------------------
# Tester for roller
# ---------------------------------------------------------------------------

class TestHentRoller:
    def test_finner_daglig_leder_og_styreleder(self):
        enhet = BrregEnhet(organisasjonsnummer="123456789", navn="Test")
        _hent_roller(ROLLER_JSON, enhet)

        assert enhet.daglig_leder == "Lars Pansen"
        assert enhet.styreleder == "Kari Nordmann"

    def test_fratraadt_ignoreres(self):
        data = {
            "rollegrupper": [
                {
                    "type": {"kode": "DAGL"},
                    "roller": [
                        {
                            "type": {"kode": "DAGL"},
                            "person": {"navn": {"fornavn": "Gammel", "etternavn": "Leder"}},
                            "fratraadt": True,
                        },
                    ],
                },
            ]
        }
        enhet = BrregEnhet(organisasjonsnummer="123456789", navn="Test")
        _hent_roller(data, enhet)

        assert enhet.daglig_leder == ""

    def test_tomme_rollegrupper(self):
        enhet = BrregEnhet(organisasjonsnummer="123456789", navn="Test")
        _hent_roller({"rollegrupper": []}, enhet)

        assert enhet.daglig_leder == ""
        assert enhet.styreleder == ""


# ---------------------------------------------------------------------------
# Tester for validering
# ---------------------------------------------------------------------------

class TestBrregClientValidering:
    def test_ugyldig_org_nummer_bokstaver(self):
        with BrregClient() as klient:
            with pytest.raises(ValueError, match="Ugyldig organisasjonsnummer"):
                klient.hent_enhet("abc")

    def test_ugyldig_org_nummer_for_kort(self):
        with BrregClient() as klient:
            with pytest.raises(ValueError, match="9 siffer"):
                klient.hent_enhet("12345")

    def test_ugyldig_org_nummer_for_langt(self):
        with BrregClient() as klient:
            with pytest.raises(ValueError, match="9 siffer"):
                klient.hent_enhet("1234567890")

    def test_mellomrom_i_org_nummer_fjernes(self):
        """Org.nr. med mellomrom skal fungere (mellomrom fjernes)."""
        with BrregClient() as klient:
            with pytest.raises(ValueError, match="9 siffer"):
                klient.hent_enhet("123 456")  # Bare 6 siffer etter fjerning
