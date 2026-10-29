# EvidenceKit — design and limitations

## Retrieval model

Documents are split into overlapping word windows while retaining exact original character offsets. Case-folded Unicode word tokens form chunk-level term-frequency and document-frequency statistics. BM25 scores use k1=1.2 and b=0.75. Repeated query words are deduplicated. Results are sorted deterministically by score, source and offset; heavily overlapping windows from one source are suppressed.

Every excerpt contains the source SHA-256 and original character range. The test suite reconstructs excerpts from source offsets. A query with no lexical match returns no evidence and an explicit abstention warning. Query-term coverage measures matched vocabulary, never confidence or truth.

No embeddings, model answers, contradiction classifier or factual verification are implemented. Conflicting source documents can both appear in evidence and require human review. Search quality depends on vocabulary and chunk settings.

## Included scenario

Two synthetic invoice approval policies disagree on thresholds and retention. The tool exposes their text and provenance rather than synthesizing an unsupported authoritative answer.

## Next validation work

A labeled retrieval benchmark, citation coverage evaluation, ranking ablations and optional local semantic retrieval. Roadmap only.

## Public-demo boundary

The hosted workbench is served over HTTPS behind nginx. User scenarios are processed on the server, not in the visitor browser. Input is capped at 512 KB, analysis runs in a separate process with a 3-second CPU limit, a 5-second wall deadline and a 256 MB address-space limit on Linux. At most two analysis workers run per service. The reverse proxy rate-limits analysis and disables request/response buffering to disk. The service runs as a dynamic unprivileged user with a read-only filesystem, private temporary directory and localhost-only network access. These are resource and isolation boundaries, not a claim of a completed security audit.

The UI adds a live evidence visualization and domain-specific quick controls. JSON remains available for full reproducibility. No submitted inputs are intentionally persisted. Public demos are for synthetic data only.
