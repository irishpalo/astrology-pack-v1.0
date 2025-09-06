# Astrology Pack — Upload & Publish

This bundle contains:
- `astrology_keywords_pack.md` → upload under **Create a GPT → Knowledge**.
- `openai_completions.yaml` → paste into **Create a GPT → Actions → Schema** and set Bearer auth (OpenAI API key).
- `privacy.md` → your privacy policy (use Google Docs “Publish to web” or GitHub Pages).
- `push_to_github_pages.sh` → tiny script to publish `privacy.md` to GitHub Pages at a clean URL.

---

## Knowledge upload
1. Go to **Create a GPT → Knowledge**.
2. Upload `astrology_keywords_pack.md`.

---

## Actions setup (OpenAI Completions)
1. Go to **Create a GPT → Actions**.
2. Authentication → **API Key (Bearer)**, value = your OpenAI key (`sk-...`).
3. Paste the contents of `openai_completions.yaml` into the Schema box.
4. Save and test:  
   ```json
   Call `createOpenAICompletion` with {
     "model": "text-davinci-003",
     "prompt": "Write a two-line rhyme about coffee."
   }