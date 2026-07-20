# LaunchDarkly Instruqt Workshop

Hands-on Instruqt tracks teaching LaunchDarkly's **AgentControl** product through guided labs. Learners build, evaluate, and coordinate an AI shopping assistant ("Otto") for a fictional e-commerce brand called **ToggleWear**.

## Tracks

| Track | Directory | Description | Status |
|-------|-----------|-------------|--------|
| **Build** | `instruqt-build/` | Otto's lifecycle — from first Config to monitoring | Near-final |
| **CodeControl** | `instruqt-codecontrol/` | Feature flags for AI — flags, targeting, rollouts, experiments, kill switch | In progress |
| **Evaluate** | `instruqt-evaluate/` | Judges, experiments, guarded rollout, adaptive switching | In progress |
| **Coordinate** | `instruqt-coordinate/` | Multi-agent Concierge team | Scaffolded |

Each track is ~2 hours instructor-led or ~1 hour self-paced.

## Repository layout

```
├── app/                        # ToggleWear storefront (shared across all tracks)
│   ├── server.py               # FastAPI backend
│   ├── static/                 # Vanilla JS frontend
│   └── requirements.txt
├── instruqt-build/             # Track 1 — Build
├── instruqt-codecontrol/       # Track 2 — CodeControl
├── instruqt-evaluate/          # Track 3 — Evaluate
├── instruqt-coordinate/        # Track 4 — Coordinate
├── terraform/                  # Terraform modules for per-challenge solve scripts
│   ├── student-bootstrap/      # Project + base resources (track-level setup)
│   ├── challenge-NN/           # Build track challenges
│   ├── codecontrol-NN/         # CodeControl track challenges
│   └── evaluate-NN/            # Evaluate track challenges
├── traffic-generator/          # Scripts for generating demo traffic
├── gcp-federation/             # AWS IAM + GCP OIDC trust for Bedrock credentials
└── vm-image/                   # Inputs for baking the shared Instruqt VM image
```

## Local development — ToggleWear app

### Prerequisites

- Python 3.11+
- A LaunchDarkly project with an SDK key
- AWS credentials for Bedrock (in `~/.aws/credentials` under a `BedrockProfile`)

### Setup

```bash
cd app
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and fill in:

| Variable | Description |
|----------|-------------|
| `LD_SDK_KEY` | Server-side SDK key from your LD project |
| `LD_CLIENT_KEY` | Client-side environment ID |
| `LD_PROJECT_KEY` | Your project key (e.g. `my-project`) |
| `AWS_PROFILE` | AWS profile name for Bedrock (default: `BedrockProfile`) |
| `AWS_REGION` | AWS region with Bedrock access (e.g. `us-east-1`) |

### Run

```bash
.venv/bin/uvicorn server:app --port 3000 --reload
```

Open [http://localhost:3000](http://localhost:3000).

### Stub mode

The app ships with stubbed endpoints (paste-block markers in `server.py`). This is intentional — learners paste code during the challenges to progressively wire up flag evaluation and event tracking. To see flags working locally, either:

- Run the challenge solve scripts, or
- Paste the completed code blocks from the assignment instructions into `server.py`

## Track challenges

### Build (AgentControl)

| # | Challenge | What it covers |
|---|-----------|----------------|
| 00 | Welcome to ToggleWear | Orientation and app overview |
| 01 | Otto is Born | Create Otto's first AI Config |
| 02 | Give Otto a Personality | Add prompt snippets and personality |
| 03 | Otto On-Brand at Scale | Brand-voice at scale with variations |
| 04 | Quiz — Configs and Snippets | Knowledge check |
| 05 | Otto for Everyone | Targeting and rollout |
| 06 | How is Otto Doing? | Monitoring and metrics |
| 07 | Wrap-Up | Summary and next steps |

### CodeControl

| # | Challenge | What it covers |
|---|-----------|----------------|
| 00 | Welcome to ToggleWear | Orientation and app overview |
| 01 | Your First Feature Flag | Create a boolean flag, wire it into the app |
| 02 | Target by User Tier | Segment-based targeting rules |
| 03 | Progressive Rollout | Percentage-based rollout (0% → 50% → 100%) |
| 04 | Run an Experiment | String flag A/B test, metrics, experimentation |
| 05 | The Kill Switch | Turn off a broken feature instantly |
| 06 | Quiz — CodeControl | Knowledge check |
| 07 | Wrap-Up | Summary and next steps |

### Evaluate

| # | Challenge | What it covers |
|---|-----------|----------------|
| 00 | Welcome to Evaluate | Orientation |
| 01 | Otto on the Bench | Baseline evaluation setup |
| 02 | Quick Takes from a Built-in Judge | Built-in judge integration |
| 03 | Otto Sounds Like Otto | Brand-voice custom judge |
| 04 | Otto Checks His Facts | Product-claim fact-checking judge |
| 05 | Quiz — Judging Otto | Knowledge check |
| 06 | A vs. B | Prompt experiment with A/B comparison |
| 07 | Trust But Verify | Guarded rollout |
| 08 | Otto Knows When to Fold | Adaptive switching |
| 09 | Wrap-Up | Summary and next steps |

## Upstream

This repo is forked from [launchdarkly-labs/ld-workshop-ai-configs-intro](https://github.com/launchdarkly-labs/ld-workshop-ai-configs-intro). To sync with upstream:

```bash
git fetch upstream
git merge upstream/main
```

## License

Apache 2.0 — see [LICENSE](LICENSE).
