# Rehearsal Dry-Run Checklist

Run through this once, end to end, timing yourself, before the real on-site.

- [ ] Cold-read `docs/01-problem-statement.md` and `docs/02-requirements.md`
      in under 10 minutes, as if at kickoff.
- [ ] Start a 4-hour timer. Build your own version on a local branch.
- [ ] Backend: `cd apps/api && pip install -r requirements.txt && python -m pytest tests -v`
      all pass.
- [ ] Backend runs: `uvicorn app.main:app --reload --port 8000`,
      `curl http://localhost:8000/api/reps` returns data.
- [ ] Frontend: `cd apps/web && npm install && npm test` all pass.
- [ ] Frontend runs: `npm run dev`, dashboard/call/rep pages load and link
      to each other correctly at `http://localhost:3000`.
- [ ] Draft your own 5-8 slide presentation in the last hour.
- [ ] Compare: `git fetch origin && git diff main origin/solution -- design/ apps/`
      - note what you did differently and why.
- [ ] Rehearse answering: "how would this look at 100x the customers and
      calls?" out loud, in under 3 minutes.
