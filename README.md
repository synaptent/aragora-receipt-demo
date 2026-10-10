# Aragora receipt demo

Every pull request in this repository is reviewed by two independent model families (OpenAI, and DeepSeek through OpenRouter) through the [Aragora GitHub Action](https://github.com/synaptent/aragora). Each review produces an **Open Decision Receipt (ODR)**: a portable JSON record of what was decided, who agreed, and who dissented. The receipt is then checked by a verifier that shares no code with the reviewer.

The code under review is a deliberately small rate limiter (`src/demo/ratelimit.py`), so the focus stays on the receipt.

## What happens on a pull request

The workflow in `.github/workflows/aragora-review.yml` has two jobs.

1. The `review` job runs the Aragora Action, pinned to release `v2.11.1`, with `emit-receipt: 'true'` and the receipt reviewers `openai deepseek`.
2. Aragora posts a review comment. The comment ends with a **Decision Receipt** section that gives the receipt id and verdict.
3. The receipt is uploaded as the build artifact `decision-receipt-pr-<number>`. If no verified receipt is produced, the `review` job fails.
4. The `receipt-first-hour` job downloads that artifact, installs the standalone [`aragora-verify`](https://pypi.org/project/aragora-verify/) package from PyPI, and verifies the receipt against this repository's public key. It prints the verifier's exit code and accepts `0` (verified) or `3` (structurally valid, signature not checked). Any other exit code fails the check.

Signed receipts need a key secret: the workflow passes the `ARAGORA_ODR_SIGNING_KEY` repository secret to the Action's `odr-signing-key` input, and the matching public key is committed here as [`odr-signing-key.pub.pem`](odr-signing-key.pub.pem). Without that secret the receipt is unsigned, and it can't show who produced it.

## Verify a receipt yourself

You need Python 3.10 or newer and about 60 seconds.

1. Open any pull request, click the **Aragora decision receipt** check, and download the `decision-receipt-pr-<number>` artifact. With the GitHub CLI you can do it in one line: `gh run download <run-id> -R synaptent/aragora-receipt-demo -n decision-receipt-pr-<number>`
2. Install the verifier:
   ```bash
   python3 -m pip install "aragora-verify>=0.2.0"
   ```
3. Verify the receipt against this repository's public key, [`odr-signing-key.pub.pem`](odr-signing-key.pub.pem):
   ```bash
   aragora-verify decision-receipt.odr.json --pubkey odr-signing-key.pub.pem
   ```
   Exit code `0` means the signature, content digest, schema and quorum checks all passed.
4. To see tamper detection, edit the `verdict` in a copy of the file and verify the copy the same way. It fails the `signature` check (exit code `1`).

To try the verifier on receipts from the Aragora repository itself, follow [Verify an Aragora decision receipt in 60 seconds](https://github.com/synaptent/aragora/blob/main/docs/receipts/VERIFY_IN_60_SECONDS.md). It uses the signed receipts of real merged pull requests attached to the [`receipts-2026-09-22`](https://github.com/synaptent/aragora/releases/tag/receipts-2026-09-22) release.

### A committed sample

[`receipts/pr-1-5cf4f6ceca72.odr.json`](receipts/pr-1-5cf4f6ceca72.odr.json) is the receipt for pull request #1 at head `5cf4f6ce`. It was produced by this repository's earlier configuration, which reviewed with Claude and OpenAI: both passed, with two advisory `[P3]` notes from Claude. It is signed with this repository's key, so you can check it without downloading anything:

```bash
aragora-verify receipts/pr-1-5cf4f6ceca72.odr.json --pubkey odr-signing-key.pub.pem
```

Its verdict is `PASS`, and `attestation.mechanism.decision_basis` is `reviews`: the Action decides on the reviewer verdicts, since it never posts merge-gate evidence.

## What these receipts prove

- **Who produced them.** Each receipt carries an Ed25519 signature from this repository's signing key. The private half is a GitHub secret; the public half is committed here, so anyone can check it offline.
- **That your copy is unaltered.** Any edit to the signed content fails verification.
- **What was decided and who dissented.** The verifier also checks the schema and that every agent listed as supporting or dissenting is a declared participant.

The check run's **Summary** tab also records each receipt's digest and signing key id at the moment it was created.

## Use it in your own repository

Copy `.github/workflows/aragora-review.yml` and add three repository secrets: `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, and `ARAGORA_ODR_SIGNING_KEY` (an Ed25519 private key from `openssl genpkey -algorithm ed25519`). Commit the matching public key so others can verify your receipts. Each pull request calls both providers, so it costs money on both accounts. Pull requests from forks don't receive secrets, so their review fails for lack of keys.

The full setup guide is [docs/guides/GITHUB_ACTION_SETUP.md](https://github.com/synaptent/aragora/blob/main/docs/guides/GITHUB_ACTION_SETUP.md). The receipt format is specified in [docs/specs/OPEN_DECISION_RECEIPT.md](https://github.com/synaptent/aragora/blob/main/docs/specs/OPEN_DECISION_RECEIPT.md).

## Run the demo tests locally

```bash
python3 -m pip install -r requirements.txt
PYTHONPATH=src python3 -m pytest -q
```
