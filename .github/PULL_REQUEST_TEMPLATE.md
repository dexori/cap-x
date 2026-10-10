## Summary

<!-- What problem does this solve, and what is the user-visible result? -->

## Benchmark impact

<!-- Note any change to tasks, prompts, APIs, success criteria, seeds, model settings, or result formats. Write "None" if there is no impact. -->

## Validation

<!-- List exact commands and environments used. For simulator tests include GPU, simulator, model, config, and trial count. -->

- [ ] `python -m compileall -q capx scripts tests verl_agent_reward`
- [ ] `python scripts/check_repository.py`
- [ ] Relevant simulator or web UI checks (describe above)

## Checklist

- [ ] I kept the change focused and updated tests or documentation where needed.
- [ ] I did not add credentials, private data, generated outputs, or restricted assets.
- [ ] I documented new dependencies and checked their redistribution terms.
- [ ] I disclosed tests I could not run.
