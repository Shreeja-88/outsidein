
# OutsideIn Project Instructions

- Keep AI inference local through Ollama; do not introduce remote
  inference APIs.
- Keep reusable application logic in src/outsidein.py.
- Keep the Streamlit interface in app.py.
- Write automated tests with pytest.
- Mock Ollama in unit tests; CI must not download models.
- Validate all model-generated mission data before displaying it.
- Preserve the curated fallback when local inference fails.
- Keep observations on the user's device and out of Git.
- Avoid adding dependencies without a clear reason.
- Run pytest and Python compilation checks after meaningful changes.
- Never claim a test, benchmark, or outdoor experiment occurred
  unless there is evidence that it did.
