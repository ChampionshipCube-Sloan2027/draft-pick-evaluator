# Feedback on Nebius Token Factory and NVIDIA models

Written during the build, from direct experience with the tools. Each entry records what was tried, what happened, and what would help.

## Token Factory

### 1. Reasoning models can return an empty response

**Tried:** Calling `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` through the OpenAI-compatible chat completions endpoint with `max_tokens=100`, then `500`.

**What happened:** At 100 tokens, the response content was empty. At 500 it returned text. At 4000 the explanation worked reliably. The model appeared to spend its token budget on internal reasoning before writing an answer.

**Suggestion:** Document the token budget a reasoning model needs for short answers. Consider returning the finish reason and the count of reasoning tokens in the response, so developers can tell an exhausted budget from a failed call.

### 2. Model IDs are hard to find

**Tried:** Looking up the Nemotron Nano model ID in the console and API reference.

**What happened:** The List Models reference page uses a sample ID (`meta-llama/Llama-3.3-70B-Instruct`) in its example output, not an NVIDIA model. Finding the exact ID meant querying the `/v1/models` endpoint and filtering the output with `grep`.

**Suggestion:** Show the exact model IDs for NVIDIA models in the catalogue, in a form that can be copied straight into code, with a one-line example call beside each.

### 3. The path from sign-up to first API key was not obvious

**Tried:** Setting up a new account, redeeming a promo code, and creating the first API key.

**What happened:** The console asked for billing details before the key could be created. The promo code redemption sat under the balance menu (Top up, then With promo code), which was not visible from the default page. The create-key route in the docs was the reliable way to reach the key screen, but it is not in the main navigation.

**Suggestion:** Make the route from sign-up to first API key explicit on the first screen after login. Separate key creation from the billing step where possible, so a developer can start building on free credit without entering card details first.

### 4. Redeeming a promo code was easy to miss

**Tried:** Applying the Builders Program promo code to the account.

**What happened:** The redemption option was not on the main page. It needed the balance menu and then Top up. A card was then requested alongside the promo code, which was not expected from the offer wording.

**Suggestion:** State on the promo page whether a card is needed to redeem, and show the redemption steps with a screenshot.

## NVIDIA Nemotron models

### 5. The model claimed fits the data did not support

**Tried:** Asking Nemotron 3 Nano to explain a draft recommendation using only the facts supplied, with an explicit instruction not to add anything beyond them.

**What happened:** The first explanation said that three prospects "also fill SG". The facts supported only two. The prompt instruction did not stop this. A rule-based check on the output caught the unsupported claim. A single retry, with the specific problem named in the message, produced an explanation that passed the check.

**Suggestion:** For grounded explanations, instruction-following alone was not reliable. A model or setting that supports constrained or structured output would let the facts be enforced at generation time, not only checked afterwards.

### 6. Explanations are fluent but can add unsupported detail

**Tried:** The retried explanation was correct about position fits but still wrote that a prospect's "playmaking and scoring fit the team's need".

**What happened:** The check tests claims about named position fits, so this descriptive claim was not caught. The text was fluent and plausible, which makes this kind of error harder to spot by reading.

**Suggestion:** The same as the previous point. Grounding would need to cover descriptive claims, not only named ones, or the model would need to be restricted to a fixed template for the factual parts.

### 7. Reasoning output can make responses slow

**Tried:** Running the explanation step through the deployed app.

**What happened:** The explanation took long enough that the spinner needed to stay visible for several seconds. This was tolerable for a demo but would matter for a live tool with many users.

**Suggestion:** Report typical latency for reasoning models on the model page, so developers can plan the user experience around it.

## Overall

### 8. What worked well

The OpenAI-compatible API meant the standard OpenAI Python SDK worked after changing the base URL and model name. Once the model ID was known, the first working call took under an hour. The `/v1/models` endpoint made it possible to confirm the exact ID programmatically.
