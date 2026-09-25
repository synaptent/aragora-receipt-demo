# Aragora receipt demo

Every pull request in this repository is reviewed by two independent model families (Claude and OpenAI) through the [Aragora GitHub Action](https://github.com/synaptent/aragora). Each review produces an **Open Decision Receipt (ODR)**: a portable JSON record of what was decided, who agreed, and who dissented. The receipt is then checked by a verifier that shares no code with the reviewer.

The code under review is a deliberately small rate limiter (`src/demo/ratelimit.py`), so the focus stays on the receipt.

## What happens on a pull request

1. The workflow in `.github/workflows/aragora-receipt.yml` runs the Aragora review with `emit-receipt: 'true'`.
2. Aragora posts a review comment. The comment ends with a **Decision Receipt** section that gives the receipt id and verdict.
3. The receipt is uploaded as the build artifact `decision-receipt-pr-<number>`.
4. The same job installs the standalone [`aragora-verify`](https://pypi.org/project/aragora-verify/) package from PyPI and re-verifies the receipt. If it fails verification, the check fails.

## Verify a receipt yourself

You need Python 3.10 or newer and about 60 seconds.

1. Open any pull request, click the **Aragora decision receipt** check, and download the `decision-receipt-pr-<number>` artifact. With the GitHub CLI you can do it in one line: `gh run download <run-id> -R synaptent/aragora-receipt-demo`
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

## What these receipts prove

- **Who produced them.** Each receipt carries an Ed25519 signature from this repository's signing key. The private half is a GitHub secret; the public half is committed here, so anyone can check it offline.
- **That your copy is unaltered.** Any edit to the signed content fails verification.
- **What was decided and who dissented.** The verifier also checks the schema and that every agent listed as supporting or dissenting is a declared participant.

The check run's **Summary** tab also records each receipt's digest and signing key id at the moment it was created.

## Use it in your own repository

Copy `.github/workflows/aragora-receipt.yml` and add three repository secrets: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and `ARAGORA_ODR_SIGNING_KEY` (an Ed25519 private key from `openssl genpkey -algorithm ed25519`). Commit the matching public key so others can verify your receipts. Each pull request calls both providers, so it costs money on both accounts. Pull requests from forks don't receive secrets, so the review is skipped for them.

The full setup guide is [docs/GITHUB_ACTION_SETUP.md](https://github.com/synaptent/aragora/blob/main/docs/GITHUB_ACTION_SETUP.md). The receipt format is specified in [docs/specs/OPEN_DECISION_RECEIPT.md](https://github.com/synaptent/aragora/blob/main/docs/specs/OPEN_DECISION_RECEIPT.md).

## Run the demo tests locally

```bash
python3 -m pip install pytest
PYTHONPATH=src python3 -m pytest -q
```
