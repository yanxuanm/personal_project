# Manual Test Scripts

These are manual testing scripts - not pytest tests. Run them directly with Python.

## Scripts

| Script | Usage | Description |
|--------|-------|-------------|
| `test_api_key.py` | `python scripts/test_api_key.py` | Test DeepSeek API key loading |
| `test_llm_integration.py` | `python scripts/test_llm_integration.py` | Test LLM integration (mock vs real) |
| `test_server.py` | `python scripts/test_server.py` | Start server and test API |
| `test_ui_demo.py` | `python scripts/test_ui_demo.py` | Demo UI functionality |

## Note

These are for manual testing only. Automated tests are in `red_dust/` and run via pytest.
