# Decision Layer Documentation

## Overview

The Decision Layer is a memory admission control system that decides whether to add, skip, replace, or merge agent runs into the knowledge base. This prevents redundancy, maintains quality, and keeps the knowledge base focused on valuable experiences.

## Architecture

### Two-Stage Decision System

```
Run Complete
    ↓
Summarization
    ↓
Similarity Search (find top-K similar runs)
    ↓
Stage 1: Deterministic Pre-Filter (cheap rules)
    ↓
Stage 2: LLM Judge (for ambiguous cases)
    ↓
Execute Decision (ADD / NOT / REPLACE / MERGE)
```

## Decision Operations

### ADD
**When**: New run adds valuable, non-redundant information

**Action**:
- Create new Run node
- Link to Task, References, Artifacts
- Mark as `status = 'active'`

**Example**: First run for a new task type

### NOT
**When**: Run is redundant or adds little value

**Action**:
- Do NOT create Run node
- Store decision for observability
- Log reason

**Example**: Identical run to existing one (very high similarity, same outcome)

### REPLACE
**When**: New run is a better version of an existing run

**Action**:
- Create new Run node
- Mark old run: `status = 'superseded'`, `superseded_by = new_run_id`
- Old run excluded from retrieval but preserved for audit

**Example**: Same task, but new run succeeded where old one failed

### MERGE
**When**: New run is similar but complementary to existing run

**Action**:
- Create new Run node
- Keep both runs active
- Mark one as canonical (success > failure, newer > older)
- Aggregate metadata (usage counters, reference unions)

**Example**: Two successful runs with slightly different approaches

## Deterministic Pre-Filter Rules

These rules avoid LLM calls for clear-cut cases:

1. **No similar runs found** → `ADD`
2. **Similarity < 0.7** → `ADD` (too different)
3. **Similarity > 0.95 + same structure** → Pass to LLM (likely MERGE)

All other cases → LLM Judge

## LLM Judge

The LLM receives:
- Current run summary
- Task text
- Outcome
- References and artifacts counts
- Top 1-3 similar runs (summary, outcome, similarity, references, artifacts)

The LLM must respond with JSON:
```json
{
  "decision": "ADD|NOT|REPLACE|MERGE",
  "target_run_id": "run_id_here (only for REPLACE/MERGE)",
  "reason": "brief explanation"
}
```

## Configuration

### Thresholds (in `services/decision.py`)

```python
LOW_SIMILARITY_THRESHOLD = 0.7      # Below this → ADD
VERY_HIGH_SIMILARITY_THRESHOLD = 0.95  # Above this → likely MERGE
```

### Similarity Search

- Searches for runs with similarity >= `LOW_SIMILARITY_THRESHOLD`
- Returns top 3 similar runs
- Only considers active runs (excludes superseded)

## Observability

Every decision is stored in Neo4j as a `MemoryDecision` node:

```cypher
(:MemoryDecision {
  run_id: string,
  decision: "ADD|NOT|REPLACE|MERGE",
  target_run_id: string?,
  reason: string,
  similarity_score: float?,
  timestamp: datetime
})
```

## Retrieval Impact

Retrieval queries automatically exclude superseded runs:

```cypher
MATCH (r:Run)
WHERE r.embedding IS NOT NULL
  AND (r.status IS NULL OR r.status = 'active')  // Excludes superseded
```

## Example Scenarios

### Scenario 1: New Unique Task
- Similarity: 0.3 (very low)
- Decision: `ADD` (deterministic)
- Reason: "Similarity below threshold"

### Scenario 2: Identical Run
- Similarity: 0.98
- Same outcome, same structure
- Decision: `NOT` (LLM judge)
- Reason: "Redundant run, no new information"

### Scenario 3: Better Version
- Similarity: 0.92
- Old run: failure
- New run: success
- Decision: `REPLACE` (LLM judge)
- Reason: "New run succeeded where old one failed"

### Scenario 4: Complementary Approaches
- Similarity: 0.88
- Both successful, different references
- Decision: `MERGE` (LLM judge)
- Reason: "Complementary approaches, both valuable"

## Testing

Test all four decision types:

```python
# Test ADD
run1 = {"task": "Generate schema", "outcome": "success"}
# Should ADD (no similar runs)

# Test NOT
run2 = {"task": "Generate schema", "outcome": "success"}  # Identical
# Should NOT (redundant)

# Test REPLACE
run3 = {"task": "Generate schema", "outcome": "failure"}
run4 = {"task": "Generate schema", "outcome": "success"}  # Better
# Should REPLACE run3 with run4

# Test MERGE
run5 = {"task": "Generate schema", "outcome": "success", "refs": ["A"]}
run6 = {"task": "Generate schema", "outcome": "success", "refs": ["B"]}
# Should MERGE (complementary)
```

## Future Enhancements

1. **Auto-Tune Thresholds**: Learn optimal thresholds from decision outcomes
2. **Pattern-Based Decisions**: Use learned patterns to inform decisions
3. **User Feedback**: Incorporate user feedback on decision quality
4. **Batch Decisions**: Decide on multiple runs at once for efficiency

