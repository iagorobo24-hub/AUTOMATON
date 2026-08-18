# Repository coherence stabilization plan

**Goal:** make the documented and user-visible system match the runtime actually mounted by AUTOMATON without reactivating legacy Mongo/trading architecture.

## Scope

1. Reconcile environment examples and development dependencies.
2. Make `package.json`, Makefile and Windows launcher use the same 8000/5173/Electron startup.
3. Remove fake CI deploy/build placeholders.
4. Remove tracked generated logs/reports and tests that assert no product behavior.
5. Replace fabricated Dashboard, Ops Monitor and Crypto telemetry with real SQLModel/CoinGecko data or explicit N/D states.
6. Rewrite project-context documentation around `app.main`, `App.jsx` and `src/lib/api.js` as sources of truth.
7. Keep legacy services/modules isolated; defer destructive mass pruning until an explicit migration/removal decision.
8. Re-audit the resulting HEAD and report executable-validation limitations separately from static verification.
