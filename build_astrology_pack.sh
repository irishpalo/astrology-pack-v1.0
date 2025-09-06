#!/usr/bin/env bash
# build_astrology_pack.sh
# Creates: astrology-pack-<VERSION>/ + astrology-pack-<VERSION>.zip
# Files: astrology_keywords_pack.md, openai_completions.yaml, privacy.md, push_to_github_pages.sh, README.md

set -euo pipefail

# ----- config -----
VERSION="${VERSION:-v1.0}"           # override: VERSION=v1.1 ./build_astrology_pack.sh
PKG="astrology-pack-$VERSION"
ZIP="$PKG.zip"

# reset output
rm -rf "$PKG" "$ZIP"
mkdir -p "$PKG"

# 1) Knowledge file
cat > "$PKG/astrology_keywords_pack.md" <<'MD'
---
title: Astrology Keywords Pack
version: 1.0
last_updated: 2025-09-02
---

# ASTROLOGY KEYWORDS PACK

> **Usage notes (internal guidance):**  
> • These tables are reference material for interpretation.  
> • Do **not** echo the lists verbatim to the user; translate them into everyday language.  
> • Use them to *inform* tone and content (clarity, concreteness, South African spelling).

## Contents
- [PLANETS](#planets)
- [SIGNS](#signs)
  - [Polarity](#polarity)
  - [Modality](#modality)
  - [Elements](#elements)
  - [Adjectives](#adjectives)
- [BOUNDS (TERMS)](#bounds-terms)
- [HOUSES](#houses)
- [ASPECTS](#aspects)

---

# PLANETS

## Sun
leadership [political]; authority [sovereign]; decision-making; public matters; action; crowd leadership; father; mentorship; friendship [supportive bond]; celebrity; honour [visibility]; high office; headship of state; gold; wheat; barley; head; right eye; heart; breath [vital]; nerves

## Moon
assembly; family; boat; travel; journey; wandering; elder sibling; mother; conception; care; household; possession [domestic]; nautical role; domestic role; mobility; indirect approach; silver; glass; left eye; stomach; breasts; breath [bodily]; spleen; membranes; marrow; fluid retention [historical: dropsy]

## Saturn
pettiness; malice; envy; anxiety; solitude; deceit [concealed]; dissembling; austerity; poverty; black clothing; persistence; misery; seafaring [labour]; waterfront trade; hired labour; tax collection; farming; gardening; guardianship; property management; foster fatherhood; celibacy; widowhood; orphanhood; childlessness; reputation [austere]; rank [restrictive]; authority [coercive]; secrecy; restraint; imprisonment [restraint]; sorrow; accusation; exposure; violence [cold, slow]; violent death [constraint]; depression; sluggishness; inertia; obstacle; punishment; reversal; lust [corrupt]; depravity; possession [restrictive]; lead; wood; stone; legs; knees; tendons; bladder; kidneys; hidden organs; fluid retention [historical: dropsy]; gout; cough; dysentery; tumours; convulsions; phlegm; bodily fluids

## Jupiter
childbearing; childbirth; marriage [legitimate]; alliance; knowledge; affection; friendship [elite]; abundance; generosity; profit; justice; authority [civic]; government; honour [benefic]; sacred leadership; arbitration; trust; inheritance; brotherhood; fellowship; adoption; confirmation of good; relief of harm; release; freedom; wealth; stewardship; responsibility; tin; thighs; feet; semen; womb; liver; right side

## Mars
violence [hot, sudden]; war; theft; violent theft; scream; arrogance; infidelity; seizure of goods; banishment; exile; estrangement; imprisonment [violent]; rape; abortion; sexuality; marriage [conflictual]; loss; falsehood; hopelessness; piracy; looting; separation [friends]; anger; conflict; abuse [verbal]; hatred; lawsuit; murder [violent]; wounds; bloodshed; torture; perjury; deception [active]; criminality; masculinity; hunting; pursuit; leadership [military]; military service; officers; soldiers; rulership [forceful]; fall; apoplexy; abruptness; iron; wine; legumes; head; buttocks; genitals; blood; seminal passages; bile; faeces; back; fever; ulcers; eruptions; inflammations; ocular weakness

## Venus
sexual desire; romantic attachment; motherhood [nurturing]; nursing; priesthood; charity; ornament [luxury]; crown; joy; friendship [affectionate]; companionship; reconciliation; marriage [harmonious]; pleasant sound; music-making; sweet singing; beauty; order; clothing; adornment; female assistance; reputation [favourable]; refined art; painting; colour mixing; embroidery; dyeing [purple]; fragrance-making; stone work; ivory work; gold thread; gold ornamentation; haircutting; trade [ornamental]; market oversight; nourishment; pleasure; acquisition [ornamental]; precious stones; adornment [multicoloured]; olive; aquatic animals; neck; face; lips; nose; front body; sexual parts; lungs

## Mercury
education; writing; debate; speech; oratory; brotherhood; interpretation; heraldry; number; calculation; geometry; commerce; youth; play; theft; community; message; letter; service; profit; discovery; obedience; contest; wrestling; declamation; certification; sealing; weighing; suspense; testing; hearing; versatility; critical thought; judgement; sibling [younger]; younger child; market; banking; public service; temple service; authority [administrative]; leasing; labour contract; rhythmic performance; administration; body-guarding; robe [sacred]; pomp [ceremonial]; fortune [irregular]; distraction; building; modelling; sculpture; medicine; teaching; law; oratory [forensic]; philosophy; architecture; music; divination; sacrifice; augury; dream interpretation; weaving; astrology; performance; acting; public office; copper; coinage; exchange; hand; shoulder; finger; joint; belly; intestine; tongue; windpipe

---

# SIGNS

## Polarity
- **Masculine:** outward; expressive; energetic; initiating; hastening; projective  
- **Feminine:** inward; receptive; containing; enduring; delaying; resistant

## Modality
- **Cardinal:** initiating; changing; reversing; instigating  
- **Fixed:** stabilising; preserving; firm; completing  
- **Mutable:** adaptable; flexible; fluctuating; adjusting

## Elements
- **Fire:** imperative; commanding; urgent; igniting; liberating  
- **Earth:** declarative; tangible; practical; necessary; enduring  
- **Air:** optative; potential; multiple; connecting; transmitting  
- **Water:** subjunctive; contingent; receptive; shaping; binding

## Adjectives
- **Aries:** assertive; vigorous; pioneering; rash; combative; volatile  
- **Taurus:** steadfast; patient; resourceful; obstinate; indulgent; inflexible  
- **Gemini:** versatile; articulate; curious; restless; evasive; capricious  
- **Cancer:** protective; nurturing; enclosing; possessive; moody; defensive  
- **Leo:** confident; generous; authoritative; arrogant; overbearing; pretentious  
- **Virgo:** diligent; analytical; meticulous; fussy; nitpicking; censorious  
- **Libra:** balanced; tactful; gracious; indecisive; vacillating; appeasing  
- **Scorpio:** perceptive; resilient; strategic; obsessive; secretive; vengeful  
- **Sagittarius:** adventurous; principled; candid; reckless; dogmatic; extravagant  
- **Capricorn:** disciplined; prudent; persevering; rigid; severe; pessimistic  
- **Aquarius:** innovative; impartial; progressive; erratic; aloof; contrary  
- **Pisces:** compassionate; imaginative; receptive; dissolving; dispersed; ineffectual

---

# BOUNDS (TERMS)

### Aries (Cardinal Fire — beginnings, forceful action, combat, injury)
- **1°–6° Jupiter:** adventurers; judges; military commanders; trophies; expansion of rank; athletic honours  
- **7°–12° Venus:** tailors; wool-workers; jewellers; ornaments; garments; adornments; sociability  
- **12°–20° Mercury:** mechanics; locksmiths; couriers; messengers; vehicle operators; disputes; strikes  
- **20°–25° Mars:** soldiers; surgeons; firemen; sharp weapons; firearms; wounds; accidents  
- **25°–30° Saturn:** exiles; prisoners; robbers; pirates; fractures; chronic injuries; harsh poverty

### Taurus (Fixed Earth — stability, agriculture, food, indulgence)
- **1°–8° Venus:** farmers; gardeners; dairy workers; vintners; melodic musicians; indulgence in property  
- **8°–14° Mercury:** merchants; brokers; accountants; market dealers; fraudulent clerks; deceptive contracts  
- **14°–22° Jupiter:** landowners; bankers; treasuries; granaries; patrons; stability of wealth  
- **22°–27° Saturn:** miners; brick-makers; stonemasons; impoverished labourers; stagnant institutions  
- **27°–30° Mars:** butchers; slaughterhouse workers; woodcutters; knives; cruelty; temple desecrators

### Gemini (Mutable Air — communication, trade, trickery, restlessness)
- **1°–6° Mercury:** scribes; translators; writers; clerks; messengers; books; letters; short journeys  
- **6°–12° Jupiter:** diplomats; journalists; publishers; teachers; libraries; eloquent orators  
- **12°–17° Venus:** comedians; singers; poets; actors; stage performers; playful games  
- **17°–24° Mars:** thieves; fraudsters; vagrants; soldiers in exile; quarrels; bloody conflicts  
- **24°–30° Saturn:** auditors; bookkeepers; administrators; record-keepers; secretaries; archival authorities

### Cancer (Cardinal Water — nurture, family, domestic life, instability)
- **1°–7° Mars:** sailors; soldiers by water; defenders; quarrels; emotional instability; poor families  
- **7°–13° Venus:** mothers; homemakers; kitchens; dairy workers; hostesses; musicians; unstable unions  
- **13°–19° Mercury:** tax collectors; notaries; family record-keepers; administrators; visible public figures  
- **19°–26° Jupiter:** patriarchs; matriarchs; grandparents; judges; inheritance; family guardianship; domestic protection  
- **26°–30° Saturn:** widows; orphans; convalescents; laundresses; hunger; destitution; dependence

### Leo (Fixed Fire — leadership, visibility, pride, command)
- **1°–6° Jupiter:** kings; rulers; crowns; gold; public honours; victory arches; prestigious athletes  
- **6°–11° Venus:** entertainers; actors; ornaments; jewellery; banquet organisers; lovers of beauty  
- **11°–18° Saturn:** priests; ascetics; scholars; occult researchers; chroniclers; barren households  
- **18°–24° Mercury:** orators; dramatists; rhetoricians; performers; public instructors; long-lived teachers  
- **24°–30° Mars:** tyrants; oppressive commanders; wounded soldiers; outlaws; sports injuries; dishonour

### Virgo (Mutable Earth — analysis, refinement, practical detail, service)
- **1°–7° Mercury:** scribes; accountants; administrators; archivists; scholars; critical analysts  
- **7°–17° Venus:** lovers; scandalous unions; cosmetics; fashions; entertainers  
- **17°–21° Jupiter:** farmers; gardeners; orchardists; granaries; dietary regulation; trusteeship  
- **21°–28° Mars:** criminals; rioters; demagogues; hired men; prowlers; counterfeiters  
- **28°–30° Saturn:** chronic invalids; misanthropes; deceivers; short-lived workers; barren households

### Libra (Cardinal Air — balance, relationships, social order)
- **1°–6° Saturn:** judges; magistrates; contracts; critics; failed marriages; miscarriages  
- **6°–11° Mercury:** negotiators; merchants; accountants; scribes; orators; market exchanges  
- **11°–19° Jupiter:** wealthy merchants; misers; austere lifestyles; childless households; censurers  
- **19°–26° Venus:** artists; sculptors; fashion designers; musicians; wedding organisers; harmonious unions  
- **26°–30° Mars:** military leaders; warriors; quarrels; lawsuits; broken alliances; family enmities

### Scorpio (Fixed Water — secrecy, intensity, transformation, violence)
- **1°–7° Mars:** soldiers; generals; explorers; surgeons; quarrelsome leaders; campaigners abroad  
- **7°–11° Venus:** spouses; favoured officials; benefactors; noblewomen; honoured companions  
- **11°–19° Mercury:** spies; investigators; rhetoricians; plotters; military scribes; disputants  
- **19°–24° Jupiter:** priests; reformers; judges; sacred officials; generous leaders; wealthy patrons  
- **24°–30° Saturn:** poisoners; traitors; prisoners; widowers; outcasts; embittered loners

### Sagittarius (Mutable Fire — expansion, philosophy, journeys, law)
- **0°–12° Jupiter:** judges; professors; philosophers; explorers; athletes; teachers with large families but little wealth  
- **12°–17° Venus:** poets; religious leaders; entertainers; popular figures; honoured spouses; prolific families  
- **17°–21° Mercury:** philosophers; interpreters; lawyers; strategists; military tacticians; subtle teachers  
- **21°–26° Saturn:** exiles; impoverished wanderers; invalids; recluses; labourers with hardship  
- **26°–30° Mars:** soldiers; hunters; reckless fighters; quarrellers; violent deaths

### Capricorn (Cardinal Earth — structure, discipline, institutions, endurance)
- **1°–7° Mercury:** clerks; actors; merchants; brokers; administrators; accountants  
- **7°–14° Jupiter:** officials; judges; estate-holders; bankrupt nobles; fluctuating fortunes  
- **14°–22° Venus:** adulterers; profligates; vain entertainers; unstable unions; lovers of excess  
- **22°–26° Saturn:** elders; hermits; miners; harsh rulers; cold-hearted governors  
- **26°–30° Mars:** military commanders; quarrelsome rulers; fratricides; violent exiles; solitary tyrants

### Aquarius (Fixed Air — systems, collectives, innovation, reform)
- **1°–7° Mercury:** lawyers; administrators; accountants; statisticians; supervisors; judges  
- **7°–13° Venus:** sailors; benefactors; social patrons; unions; philanthropists; fortunate marriages  
- **13°–20° Jupiter:** scholars; philosophers; hermits; fortunate householders; aloof guides  
- **20°–25° Mars:** criminals; litigants; rebels; wounded soldiers; disputants; troublemakers  
- **25°–30° Saturn:** invalids; orphans; destitute; envious rivals; impoverished households; untimely deaths

### Pisces (Mutable Water — imagination, mysticism, dissolution, sacrifice)
- **1°–12° Venus:** poets; musicians; entertainers; celebrants; charitable figures; popular companions  
- **12°–16° Jupiter:** priests; prophets; writers; lecturers; orators; sacred scribes  
- **16°–19° Mercury:** teachers; interpreters; messengers; clerics; administrators; charitable officials  
- **19°–28° Mars:** sailors; warriors; pirates; naval leaders; explorers; shipwrecks  
- **28°–30° Saturn:** prisoners; invalids; addicts; chronic sufferers; despairing exiles

---

# HOUSES

- **1st House:** body; vitality; life; appearance; temperament  
- **2nd House:** possessions; livelihood; income; sustenance  
- **3rd House:** siblings; travel; letters; neighbours; devotion  
- **4th House:** parents; ancestry; land; home; foundations  
- **5th House:** children; erotic matters; delights; gifts; festivals  
- **6th House:** illness; injuries; servitude; toil; subordinates  
- **7th House:** spouse; marriage; contracts; partnerships; rivals  
- **8th House:** death; inheritance; debts; fear; deprivation  
- **9th House:** religion; divination; long journeys; law; teachings  
- **10th House:** career; authority; actions; honours; reputation  
- **11th House:** friends; allies; benefactors; assemblies; rewards  
- **12th House:** enemies; confinement; exile; affliction; ruin

---

# ASPECTS

- **Conjunction:** union; binding; intensification  
- **Sextile:** assistance; cooperation; facilitation  
- **Square:** clash; coercion; contest  
- **Trine:** support; harmony; reinforcement  
- **Opposition:** division; contrariety; contention  
- **Aversion:** separation; disconnection; disregard
MD
echo "→ Wrote $PKG/astrology_keywords_pack.md"

# 2) OpenAPI schema
cat > "$PKG/openai_completions.yaml" <<'YAML'
openapi: 3.1.0
info:
  title: OpenAI Completions
  version: 1.0.2
  description: Minimal spec to call POST https://api.openai.com/v1/completions with model and prompt.
servers:
  - url: https://api.openai.com
security:
  - OpenAIBearer: []
paths:
  /v1/completions:
    post:
      operationId: createOpenAICompletion
      summary: Create completion
      description: Create a text completion using the specified model and prompt.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/OpenAICompletionRequest'
            examples:
              basic:
                value:
                  model: text-davinci-003
                  prompt: Write a short haiku about the ocean.
      responses:
        '200':
          description: Completion created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OpenAICompletionResponse'
        '401':
          description: Unauthorized (invalid or missing API key)
        '429':
          description: Rate limited
        '500':
          description: Server error
components:
  securitySchemes:
    OpenAIBearer:
      type: http
      scheme: bearer
      bearerFormat: API key
  schemas:
    OpenAICompletionRequest:
      type: object
      additionalProperties: true
      properties:
        model:
          type: string
          description: Model name (e.g., text-davinci-003)
        prompt:
          type: string
          description: Input prompt
        max_tokens:
          type: integer
          minimum: 1
          description: Max tokens to generate
        temperature:
          type: number
          minimum: 0
          maximum: 2
          description: Sampling temperature
      required: [model, prompt]
    OpenAICompletionChoice:
      type: object
      properties:
        text: { type: string }
        index: { type: integer }
        finish_reason: { type: [string, 'null'] }
        logprobs: { type: [object, 'null'] }
      required: [text, index]
    OpenAICompletionResponse:
      type: object
      properties:
        id: { type: string }
        object: { type: string }
        model: { type: string }
        choices:
          type: array
          items:
            $ref: '#/components/schemas/OpenAICompletionChoice'
        usage:
          type: object
          properties:
            prompt_tokens: { type: integer }
            completion_tokens: { type: integer }
            total_tokens: { type: integer }
      required: [id, object, model, choices]
YAML
echo "→ Wrote $PKG/openai_completions.yaml"

# 3) Privacy policy
cat > "$PKG/privacy.md" <<'MD'
# Privacy Policy — Irish Palo
**Effective date:** 2025-09-02  
**Contact:** irish.palo@gmail.com

This Privacy Policy explains how **Irish Palo** (“we”, “us”, “our”) processes information when you use our ChatGPT Action (“the Action”). The Action is intended for both consumers and businesses and is not for users under 16.

## 1) What the Action does
The Action sends your prompts (and any files you choose to include) to third-party AI services to generate responses. We aim to minimise what we collect and store.

## 2) Personal data we process
- **Content you provide:** prompts, questions, and any text you submit via the Action.  
- **Usage metadata (minimal):** timestamps, request IDs, and basic technical logs needed to operate and troubleshoot the Action.  
- **No user accounts:** we do not create or manage user accounts for this Action.  
- **No payments via this Action.**

**Sensitive data:** Please do not include special-category or sensitive information (e.g., health, financial account numbers, government IDs, precise location) in prompts.

## 3) Sources
- Directly from you when you use the Action.  
- From service providers who help us run the Action (see “Processors”).

## 4) Purposes and legal bases
- Provide and operate the Action (contract/legitimate interests).  
- Troubleshoot, secure, and improve the Action (legitimate interests).  
- Legal compliance where required (legal obligation).  
- No marketing is performed from Action data.

## 5) Processors (service providers)
- **LLM provider:** OpenAI, LLC (processing of prompts/outputs to generate results).  
- **Hosting for this policy page or site:** Google (Google Docs/Drive) or GitHub Pages.  
- **Analytics:** none by default.

We require processors to protect your data and to use it only to provide their services to us.

## 6) International transfers
If you are in the EU/UK/ZA, your data may be transferred to countries outside your region (e.g., the United States) for processing by our providers. We rely on appropriate safeguards such as Standard Contractual Clauses or provider data protection addenda.

## 7) Retention
- **Prompts/outputs:** we do not persist prompts or outputs on our own servers. Providers may retain limited data per their policies to run and protect the service.  
- **Operational logs:** minimal logs kept for **30 days** for security and troubleshooting, then deleted or aggregated.  
- **Backups:** none for Action data.

## 8) Security
We use industry-standard measures such as encryption in transit (HTTPS) and least-privilege access. No method is 100% secure, but we work to protect your information.

## 9) Your rights
Depending on your location (EU/UK GDPR, South Africa POPIA, California CPRA), you may have rights to access, correct, delete, port, or object to certain processing.  
To exercise your rights, email **irish.palo@gmail.com**. We will verify and respond within applicable timeframes.

## 10) Children
The Action is not intended for users under 16. We do not knowingly process data from children in that age group.

## 11) Cookies & tracking
The Action itself does not use analytics or advertising cookies. If you view this policy page on the web, the hosting platform may set strictly necessary cookies.

## 12) “Sale” or “Sharing” (US—CPRA)
We do not sell personal information and do not share it for cross-context behavioural advertising.

## 13) Changes to this policy
We may update this policy from time to time. We will post the updated version here with a new Effective date.

## 14) Contact
**Irish Palo**  
Email: **irish.palo@gmail.com**
MD
echo "→ Wrote $PKG/privacy.md"

# 4) GH Pages push helper
cat > "$PKG/push_to_github_pages.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail

# Publish privacy.md to GitHub Pages as https://<USER>.github.io/privacy/
# Prereqs:
#  1) Create an empty GitHub repo named "privacy"
#  2) Set env var REMOTE to that repo URL, e.g.:
#       export REMOTE=git@github.com:<USER>/privacy.git
#     or export REMOTE=https://github.com/<USER>/privacy.git
#  3) Run this script from inside the folder that contains privacy.md

if [[ -z "${REMOTE:-}" ]]; then
  echo "❌ Please set REMOTE to your GitHub repo URL, e.g.:"
  echo "   export REMOTE=git@github.com:<USER>/privacy.git"
  exit 1
fi

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

cp privacy.md "$WORKDIR/index.md"
touch "$WORKDIR/.nojekyll"

(
  cd "$WORKDIR"
  git init -q
  git add .
  git commit -m "Initial privacy site"
  git branch -M main
  git remote add origin "$REMOTE"
  git push -u origin main
)

echo "✅ Pushed to $REMOTE"
echo "➡ Enable GitHub Pages: Settings → Pages → Deploy from branch: main / root"
echo "🌐 Live URL: https://<USER>.github.io/privacy/"
SH
chmod +x "$PKG/push_to_github_pages.sh"
echo "→ Wrote $PKG/push_to_github_pages.sh (made executable)"

# 5) README
cat > "$PKG/README.md" <<'MD'
# Astrology Pack — Upload & Publish

This bundle contains:
- `astrology_keywords_pack.md` → upload under **Create a GPT → Knowledge**.
- `openai_completions.yaml` → paste into **Create a GPT → Actions → Schema** and set Bearer auth (OpenAI API key).
- `privacy.md` → your privacy policy (use Google Docs “Publish to web” or GitHub Pages).
- `push_to_github_pages.sh` → tiny script to publish `privacy.md` to GitHub Pages at a clean URL.

## Knowledge upload
1. Go to **Create a GPT → Knowledge**.
2. Upload `astrology_keywords_pack.md`.

## Actions setup (OpenAI Completions)
1. Go to **Create a GPT → Actions**.
2. Authentication → **API Key (Bearer)**, value = your OpenAI key (`sk-...`).
3. Paste the contents of `openai_completions.yaml` into the Schema box.
4. Save and test:
   - “Call `createOpenAICompletion` with `{ model: "text-davinci-003", prompt: "Write a two-line rhyme about coffee." }`.”

## Privacy policy — Option A: Google Docs
- Paste `privacy.md` into a Google Doc → **File → Share → Publish to web** → copy the `…/pub` URL.
- Use that URL in the Actions “Privacy policy link”.

## Privacy policy — Option B: GitHub Pages (clean URL)
1. Create a new GitHub repo named **privacy** (empty).
2. In Terminal, set your repo URL as an env var:
   - `export REMOTE=git@github.com:<USER>/privacy.git`
3. Run the script from inside this folder:
   - `./push_to_github_pages.sh`
4. In GitHub: **Settings → Pages** → Deploy from branch: **main / root**.
5. Your link will be: `https://<USER>.github.io/privacy/`

Tip: replace `<USER>` with your GitHub username (e.g., `irishpalo`).
MD
echo "→ Wrote $PKG/README.md"

# 6) Zip it
zip -rq "$ZIP" "$PKG"
echo "→ Created $ZIP"

echo ""
echo "✅ Done. Files are in: $PKG/"
echo "▶  Next:"
echo "   chmod +x build_astrology_pack.sh"
echo "   ./build_astrology_pack.sh           # or: VERSION=v1.1 ./build_astrology_pack.sh"
echo "   open .                              # opens Finder to locate $ZIP"
