# Provider matrix

| Provider/profile | Search mode | Consumer surface equivalence | Citations | MVP use |
| --- | --- | --- | --- | --- |
| Perplexity sonar | `native_search` | `direct` | yes | Implemented in M1; primary visible-citation measurement |
| Gemini grounding | `web_grounding` | `partial` | yes | Cross-engine divergence comparison |
| OpenAI-compatible, search on | `web_grounding` | `partial` | profile-dependent | Only with explicit tool/search confirmation |
| OpenAI-compatible, no search | `none` | `no` | no | Model capability baseline, not AI-search visibility |
| Anthropic, search off | `none` | `no` | no | Model capability baseline, not AI-search visibility |

Reports must preserve this distinction. A no-search profile belongs in a
separate interpretation section and must not be averaged with grounded results.
