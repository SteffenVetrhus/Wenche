"""
Wenche — kommandolinjegrensesnitt.

Bruk:
  wenche ui
  wenche login
  wenche logout
  wenche send-aarsregnskap [--config config.yaml] [--dry-run]
  wenche send-aksjonaerregister [--config config.yaml] [--dry-run]
  wenche generer-skattemelding [--config config.yaml] [--ut skattemelding.txt]
  wenche send-skattemelding
"""

import click

from wenche import __version__
from wenche import auth, aarsregnskap, aksjonaerregister, skattemelding, systembruker
from wenche.altinn_client import AltinnClient
from wenche.brreg_client import BrregClient
from wenche.skd_client import SkdAksjonaerClient


@click.group()
@click.version_option(__version__, prog_name="Wenche")
def main():
    """Wenche — enkel innsending til Altinn for holdingselskaper."""
    pass


# ---------------------------------------------------------------------------
# Autentisering
# ---------------------------------------------------------------------------

@main.command()
@click.option("--legacy", is_flag=True, help="Start det gamle Streamlit-grensesnittet.")
def ui(legacy: bool):
    """Start webgrensesnitt i nettleseren."""
    import subprocess
    import sys
    from pathlib import Path

    if legacy:
        app = Path(__file__).parent / "ui.py"
        try:
            subprocess.run(
                [sys.executable, "-m", "streamlit", "run", str(app)], check=True
            )
        except FileNotFoundError:
            click.echo(
                "Streamlit er ikke installert. Kjør:\n  pip install wenche[ui]", err=True
            )
            raise SystemExit(1)
        return

    # Start FastAPI backend + SvelteKit dev server
    frontend_dir = Path(__file__).parent.parent / "frontend"
    if not frontend_dir.exists():
        click.echo(
            f"Frontend-mappen finnes ikke: {frontend_dir}\n"
            "Kjør 'cd frontend && npm install' for å sette opp.",
            err=True,
        )
        raise SystemExit(1)

    import signal

    click.echo("Starter Wenche...")
    click.echo("  API:      http://localhost:8000")
    click.echo("  Frontend: http://localhost:5173")
    click.echo()

    api_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "wenche.api:app", "--port", "8000", "--reload"],
    )
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev", "--", "--open"],
        cwd=str(frontend_dir),
    )

    def shutdown(sig, frame):
        api_proc.terminate()
        frontend_proc.terminate()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        api_proc.wait()
    finally:
        api_proc.terminate()
        frontend_proc.terminate()


@main.command()
def login():
    """Autentiser mot Maskinporten med RSA-nøkkel."""
    auth.login()


@main.command()
def logout():
    """Logg ut og slett lagret token."""
    auth.logout()


@main.command("registrer-system")
def registrer_system():
    """Registrer Wenche i Altinns systemregister (kjøres én gang per miljø)."""
    import os
    client_id = os.getenv("MASKINPORTEN_CLIENT_ID")
    org_nummer = os.getenv("ORG_NUMMER")
    if not client_id or not org_nummer:
        click.echo(
            "Feil: MASKINPORTEN_CLIENT_ID og ORG_NUMMER må være satt i .env.", err=True
        )
        raise SystemExit(1)

    click.echo("Henter Maskinporten admin-token...")
    token = auth.login_admin()
    sid = systembruker.system_id(org_nummer)
    click.echo(f"Registrerer system '{sid}' i Altinn...")
    try:
        svar = systembruker.registrer_system(token, org_nummer, client_id)
        if svar.get("oppdatert"):
            click.echo(f"System '{sid}' oppdatert i Altinn.")
        else:
            click.echo(f"System registrert: {svar}")
    except Exception as e:
        click.echo(f"Feil ved registrering: {e}", err=True)
        raise SystemExit(1)


@main.command("opprett-systembruker")
@click.option(
    "--org",
    default=None,
    help="Org.nr. for systembrukeren. Standard: ORG_NUMMER fra .env. "
         "I SKDs testmiljø skal dette være et syntetisk org.nr. fra Tenor.",
)
def opprett_systembruker(org: str | None):
    """Opprett systembrukerforespørsel og få godkjenningslenke."""
    import os
    vendor_orgnr = os.getenv("ORG_NUMMER")
    if not vendor_orgnr:
        click.echo("Feil: ORG_NUMMER må være satt i .env.", err=True)
        raise SystemExit(1)
    org_nummer = org or vendor_orgnr

    click.echo("Henter Maskinporten admin-token...")
    token = auth.login_admin()
    click.echo(f"Oppretter systembrukerforespørsel for {org_nummer}...")
    try:
        svar = systembruker.opprett_forespørsel(token, vendor_orgnr, org_nummer)
        click.echo(f"\nForespørsel opprettet (ID: {svar['id']})")
        click.echo(f"Status: {svar['status']}")
        click.echo(f"\nGodkjenn her:\n  {svar['confirmUrl']}")
    except Exception as e:
        click.echo(f"Feil ved oppretting av systembruker: {e}", err=True)
        raise SystemExit(1)



# ---------------------------------------------------------------------------
# Oppslag i Enhetsregisteret
# ---------------------------------------------------------------------------

@main.command("hent-selskap")
@click.argument("org_nummer")
def hent_selskap(org_nummer: str):
    """Hent selskapsinformasjon fra Brønnøysundregistrene."""
    with BrregClient() as klient:
        try:
            enhet = klient.hent_enhet(org_nummer)
        except ValueError as e:
            click.echo(f"Feil: {e}", err=True)
            raise SystemExit(1)
        except Exception as e:
            click.echo(f"Kunne ikke hente selskap: {e}", err=True)
            raise SystemExit(1)

    click.echo(f"Navn:                {enhet.navn}")
    click.echo(f"Org.nr.:             {enhet.organisasjonsnummer}")
    click.echo(f"Organisasjonsform:   {enhet.organisasjonsform}")
    click.echo(f"Forretningsadresse:  {enhet.forretningsadresse}")
    if enhet.daglig_leder:
        click.echo(f"Daglig leder:        {enhet.daglig_leder}")
    if enhet.styreleder:
        click.echo(f"Styreleder:          {enhet.styreleder}")
    if enhet.stiftelsesdato:
        click.echo(f"Stiftelsesdato:      {enhet.stiftelsesdato}")
    elif enhet.registreringsdato:
        click.echo(f"Registreringsdato:   {enhet.registreringsdato}")
    if enhet.naeringskode:
        click.echo(f"Næringskode:         {enhet.naeringskode}")
    if enhet.epostadresse:
        click.echo(f"E-post:              {enhet.epostadresse}")
    if enhet.hjemmeside:
        click.echo(f"Hjemmeside:          {enhet.hjemmeside}")
    if enhet.konkurs:
        click.echo("ADVARSEL: Selskapet er registrert som konkurs!")
    if enhet.under_avvikling:
        click.echo("ADVARSEL: Selskapet er under avvikling!")


# ---------------------------------------------------------------------------
# Årsregnskap
# ---------------------------------------------------------------------------

@main.command("send-aarsregnskap")
@click.option(
    "--config",
    "config_fil",
    default="config.yaml",
    show_default=True,
    help="Sti til konfigurasjonsfilen.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Generer og valider dokument uten å sende til Altinn.",
)
def send_aarsregnskap(config_fil: str, dry_run: bool):
    """Send inn årsregnskap til Brønnøysundregistrene."""
    click.echo(f"Leser konfigurasjon fra {config_fil}...")
    try:
        regnskap = aarsregnskap.les_config(config_fil)
    except FileNotFoundError:
        click.echo(
            f"Feil: finner ikke {config_fil}.\n"
            "Kopier config.example.yaml til config.yaml og fyll inn dine verdier.",
            err=True,
        )
        raise SystemExit(1)

    click.echo(
        f"Aarsregnskap {regnskap.regnskapsaar} for {regnskap.selskap.navn} "
        f"({regnskap.selskap.org_nummer})"
    )

    if dry_run:
        aarsregnskap.send_inn(regnskap, klient=None, dry_run=True)
        return

    token = auth.get_altinn_token()
    with AltinnClient(token) as klient:
        aarsregnskap.send_inn(regnskap, klient)


# ---------------------------------------------------------------------------
# Aksjonærregisteroppgave
# ---------------------------------------------------------------------------

@main.command("send-aksjonaerregister")
@click.option(
    "--config",
    "config_fil",
    default="config.yaml",
    show_default=True,
    help="Sti til konfigurasjonsfilen.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Generer og valider XML lokalt uten å sende til SKD.",
)
def send_aksjonaerregister(config_fil: str, dry_run: bool):
    """Send inn aksjonærregisteroppgave (RF-1086) til Skatteetaten."""
    import os
    click.echo(f"Leser konfigurasjon fra {config_fil}...")
    try:
        oppgave = aksjonaerregister.les_config(config_fil)
    except FileNotFoundError:
        click.echo(
            f"Feil: finner ikke {config_fil}.\n"
            "Kopier config.example.yaml til config.yaml og fyll inn dine verdier.",
            err=True,
        )
        raise SystemExit(1)

    click.echo(
        f"Aksjonaerregisteroppgave {oppgave.regnskapsaar} for {oppgave.selskap.navn} "
        f"({oppgave.selskap.org_nummer}) — "
        f"{len(oppgave.aksjonaerer)} aksjonaer(er)"
    )

    if dry_run:
        aksjonaerregister.send_inn(oppgave, klient=None, dry_run=True)
        return

    click.echo("Henter Maskinporten-token med SKD-scope...")
    token = auth.get_skd_aksjonaer_token()
    env = os.getenv("WENCHE_ENV", "prod")
    with SkdAksjonaerClient(token, env=env) as klient:
        svar = aksjonaerregister.send_inn(oppgave, klient)
    if svar:
        click.echo(f"\nForsendelse-ID: {svar.get('forsendelseId')}")
        click.echo(f"Dialog-ID:      {svar.get('dialogId')}")


# ---------------------------------------------------------------------------
# Skattemelding
# ---------------------------------------------------------------------------

@main.command("generer-skattemelding")
@click.option(
    "--config",
    "config_fil",
    default="config.yaml",
    show_default=True,
    help="Sti til konfigurasjonsfilen.",
)
@click.option(
    "--ut",
    "ut_fil",
    default=None,
    help="Lagre sammendrag til fil i stedet for å skrive til skjermen.",
)
def generer_skattemelding(config_fil: str, ut_fil: str | None):
    """Generer ferdig utfylt RF-1167 og RF-1028 fra config.yaml."""
    click.echo(f"Leser konfigurasjon fra {config_fil}...")
    try:
        regnskap, konfig = skattemelding.les_config(config_fil)
    except FileNotFoundError:
        click.echo(
            f"Feil: finner ikke {config_fil}.\n"
            "Kopier config.example.yaml til config.yaml og fyll inn dine verdier.",
            err=True,
        )
        raise SystemExit(1)

    tekst = skattemelding.generer(regnskap, konfig)

    if ut_fil:
        from pathlib import Path
        Path(ut_fil).write_text(tekst, encoding="utf-8")
        click.echo(f"Skattemelding lagret til {ut_fil}")
    else:
        click.echo(tekst)


@main.command("send-skattemelding")
def send_skattemelding():
    """Send inn skattemelding for AS (ikke implementert ennå)."""
    click.echo(
        "Innsending via API krever registrering som systemleverandør hos Skatteetaten.\n"
        "Bruk 'wenche generer-skattemelding' for å generere et ferdig utfylt sammendrag\n"
        "som du kan sende inn manuelt på https://www.skatteetaten.no/"
    )
    raise SystemExit(1)
