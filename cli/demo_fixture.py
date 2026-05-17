"""Constants used by ``prism demo``.

The backend must recognise this PR/repo combination and return a pre-baked
``AnalysisResponse`` — no GitHub fetch, no AI service call, sub-second response.
This is the live-demo parachute: if the realistic path stutters, ``prism demo``
always works.
"""

DEMO_PR_ID = "pr-142"
DEMO_REPO_URL = "https://github.com/prism-demo/payment-service"
