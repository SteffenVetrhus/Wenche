# Oppsett

Wenche bruker Maskinporten for å autentisere deg som konsument overfor Altinn — uten nettleserinnlogging. Du trenger:

1. Et RSA-nøkkelpar (genereres lokalt)
2. En Maskinporten-klient registrert hos Digdir
3. En `.env`-fil med klient-ID og nøkkelinformasjon

!!! note "Webgrensesnittet hjelper deg"
    Har du installert Wenche med UI-støtte? Start `wenche ui` og gå til fanen **Oppsett** — der kan du fylle inn konfigurasjonen direkte i nettleseren uten å redigere filer manuelt.

---

## Steg 1 — Generer RSA-nøkkelpar

Nøklene brukes til å identifisere deg overfor Maskinporten. Den private nøkkelen beholdes lokalt; den offentlige lastes opp til Digdir.

```bash
openssl genrsa -out maskinporten_privat.pem 2048
openssl rsa -in maskinporten_privat.pem -pubout -out maskinporten_offentlig.pem
```

!!! warning "Ikke del den private nøkkelen"
    `maskinporten_privat.pem` skal aldri deles med andre eller legges i git. Filen er lagt til i `.gitignore`.

---

## Steg 2 — Registrer Maskinporten-klient hos Digdir

Registrering er gratis og tar ca. 15 minutter.

### 2a. Søk om tilgang

Gå til [samarbeid.digdir.no](https://samarbeid.digdir.no) og søk om tilgang som **Maskinporten-konsument**. Du vil motta en e-post med bekreftelse og lenke til selvbetjeningsportalen.

### 2b. Opprett integrasjon

Logg inn på [selvbetjeningsportalen.digdir.no](https://selvbetjeningsportalen.digdir.no):

1. Velg **Produksjon** (eller **Test** for testmiljø)
2. Velg **Klienter** → **Maskinporten & KRR**
3. Klikk **Ny integrasjon** og fyll ut:
    - Visningsnavn: `wenche`
    - Access token levetid: `120`
4. Legg til scopes: `altinn:instances.read` og `altinn:instances.write`
5. Kopier **klient-ID** — du trenger den i neste steg

### 2c. Last opp offentlig nøkkel

Under klienten, klikk **Legg til nøkkel** og lim inn innholdet i `maskinporten_offentlig.pem`. Lagre klienten.

Nøkkelen vil vises i listen med en UUID (f.eks. `9bc5078c-...`). Kopier denne UUID-en — dette er din **KID**.

!!! info "Synkroniseringstid"
    Endringer i testmiljøet kan ta noen minutter å synkronisere.

---

## Steg 3 — Konfigurer miljøvariabler

Kopier eksempelfilen:

```bash
cp .env.example .env
```

Åpne `.env` og fyll inn verdiene fra portalen:

```
MASKINPORTEN_CLIENT_ID=din-klient-id-her
MASKINPORTEN_KID=uuid-fra-portalen-her
MASKINPORTEN_PRIVAT_NOKKEL=maskinporten_privat.pem
WENCHE_ENV=prod
```

| Variabel | Hva det er |
|---|---|
| `MASKINPORTEN_CLIENT_ID` | Klient-ID fra selvbetjeningsportalen |
| `MASKINPORTEN_KID` | UUID som portalen tildelte nøkkelen din |
| `MASKINPORTEN_PRIVAT_NOKKEL` | Sti til din private nøkkelfil (standard: `maskinporten_privat.pem`) |
| `WENCHE_ENV` | `prod` for produksjon, `test` for Altinn tt02-testmiljø |

---

## Steg 4 — Fyll ut config.yaml

Kopier eksempelfilen:

```bash
cp config.example.yaml config.yaml
```

Åpne `config.yaml` og fyll inn selskapets opplysninger, regnskapstall og aksjonærdata. Filen er kommentert og selvforklarende. Alle beløp oppgis i hele kroner (NOK).

!!! tip "Webgrensesnittet"
    Bruker du `wenche ui` kan du fylle ut all informasjon om selskapet, regnskapet og aksjonærene direkte i nettleseren — ingen manuell filredigering nødvendig.

---

## Verifiser oppsett

Test at alt er konfigurert riktig:

```bash
wenche login
```

Vellykket utskrift:

```
Autentiserer mot Maskinporten...
Maskinporten-token mottatt. Henter Altinn-token...
Autentisering vellykket.
```

Logg deretter ut igjen:

```bash
wenche logout
```

[Gå videre til bruk →](bruk.md){ .md-button .md-button--primary }
