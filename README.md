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
3. Verify:
   ```bash
   aragora-verify decision-receipt.odr.json
   ```
   Exit code `0` means the structural checks passed.
4. Compare the `odr_digest` that the verifier prints with the `odr_digest` in the check run's **Summary** tab. GitHub recorded that value when the receipt was created. If the two differ, your copy has been changed.

## What these receipts do and don't prove

- **The verifier checks structure.** The document conforms to the ODR schema, and every agent listed as supporting or dissenting is a declared participant.
- **The digest comparison checks that your copy is unchanged.** Receipts from this demo are **unsigned**, because the Action doesn't take a signing key yet. For an unsigned receipt, the verifier recomputes the digest from whatever file you give it, so an edited copy still passes step 3. Step 4 catches the edit, because the recorded digest lives in GitHub's run summary rather than in the file.
- **They don't prove who produced them** beyond "this repository's workflow run". Signed receipts carry an Ed25519 signature and are verified with `aragora-verify <file> --pubkey <key.pem>`, which catches any edit on its own. Examples are attached to the [`receipts-*` releases](https://github.com/synaptent/aragora/releases) of the main repository.

## Use it in your own repository

Copy `.github/workflows/aragora-receipt.yml` and add two repository secrets: `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`. Each pull request calls both providers, so it costs money on both accounts. Pull requests from forks don't receive secrets, so the review is skipped for them.

The full setup guide is [docs/GITHUB_ACTION_SETUP.md](https://github.com/synaptent/aragora/blob/main/docs/GITHUB_ACTION_SETUP.md). The receipt format is specified in [docs/specs/OPEN_DECISION_RECEIPT.md](https://github.com/synaptent/aragora/blob/main/docs/specs/OPEN_DECISION_RECEIPT.md).

## Run the demo tests locally

```bash
python3 -m pip install pytest
PYTHONPATH=src python3 -m pytest -q
```
