# Bruk

Wenche kan brukes enten via **kommandolinjen** eller via **webgrensesnittet** (`wenche ui`). Begge gir tilgang til de samme funksjonene.

---

## Skattemelding (frist 31. mai)

Wenche genererer et ferdig utfylt sammendrag av RF-1167 (næringsoppgaven) og RF-1028 (skattemeldingen) basert på tallene i `config.yaml`.

=== "Kommandolinje"

    ```bash
    wenche generer-skattemelding
    ```

    Lagre til fil:

    ```bash
    wenche generer-skattemelding --ut skattemelding.txt
    ```

=== "Webgrensesnitt"

    Gå til fanen **Dokumenter** og klikk **Last ned skattemelding**.

Sammendraget inneholder:

- Alle felt i næringsoppgaven (RF-1167) ferdig utfylt
- Skatteberegning med fritaksmetoden der det er aktuelt
- Beregnet skatt (22 %)
- Fremførbart underskudd hvis selskapet gikk med tap

**Send inn manuelt:**

1. Gå til [skatteetaten.no](https://www.skatteetaten.no/) og logg inn med BankID
2. Åpne skattemeldingen for AS for gjeldende regnskapsår
3. Fyll inn tallene fra sammendraget Wenche har generert
4. Kontroller at Skatteetaten beregner samme skatt
5. Send inn

---

## Årsregnskap (frist 31. juli)

=== "Kommandolinje"

    Test uten innsending (anbefalt første gang):

    ```bash
    wenche send-aarsregnskap --dry-run
    ```

    `--dry-run` lagrer de genererte XML-dokumentene lokalt slik at du kan inspisere dem.

    Send inn:

    ```bash
    wenche login
    wenche send-aarsregnskap
    wenche logout
    ```

=== "Webgrensesnitt"

    Gå til fanen **Send til Altinn** og klikk **Send årsregnskap**.

---

## Aksjonærregisteroppgave (frist 31. januar)

=== "Kommandolinje"

    Test uten innsending:

    ```bash
    wenche send-aksjonaerregister --dry-run
    ```

    Send inn:

    ```bash
    wenche login
    wenche send-aksjonaerregister
    wenche logout
    ```

=== "Webgrensesnitt"

    Gå til fanen **Send til Altinn** og klikk **Send aksjonærregisteroppgave**.

---

## Autentisering

`wenche login` autentiserer mot Maskinporten med din private RSA-nøkkel og lagrer et token lokalt i `~/.wenche/token.json`. Tokenet gjenbrukes automatisk for påfølgende kommandoer i samme sesjon.

```bash
wenche login     # Henter og lagrer token
wenche logout    # Sletter lagret token
```

---

## Alle kommandoer

```
wenche --help

Kommandoer:
  login                    Autentiser mot Maskinporten med RSA-nokkel
  logout                   Logg ut og slett lagret token
  generer-skattemelding    Generer ferdig utfylt RF-1167 og RF-1028 fra config.yaml
  send-aarsregnskap        Send inn arsregnskap til Bronnoysundregistrene
  send-aksjonaerregister   Send inn aksjonaerregisteroppgave (RF-1086)
  ui                       Start webgrensesnittet i nettleseren

Alternativer (send-aarsregnskap og send-aksjonaerregister):
  --config TEXT            Sti til konfigurasjonsfil [standard: config.yaml]
  --dry-run                Generer dokument lokalt uten a sende til Altinn

Alternativer (generer-skattemelding):
  --config TEXT            Sti til konfigurasjonsfil [standard: config.yaml]
  --ut TEXT                Lagre sammendrag til fil
```

---

## Sikkerhet

- `.env` og `config.yaml` skal aldri legges i git (de er lagt til i `.gitignore`)
- Innloggingstokenet lagres i `~/.wenche/token.json` med rettigheter begrenset til din bruker
- Wenche sender aldri data andre steder enn til Maskinporten og Altinn
