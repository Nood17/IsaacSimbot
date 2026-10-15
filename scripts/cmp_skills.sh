#!/bin/bash
BASE=/home/administrator/仿真
for s in deep-research academic-paper academic-paper-reviewer academic-pipeline research-paper-pipeline; do
  echo "=== OLD $s ==="
  grep -m3 -E "version:|name:" "$BASE/.devin/skills/$s/SKILL.md" 2>/dev/null
  wc -l "$BASE/.devin/skills/$s/SKILL.md" 2>/dev/null
  ls "$BASE/.devin/skills/$s/" 2>/dev/null | head -10
done
for s in alterlab-deep-research alterlab-paper-writer alterlab-paper-reviewer alterlab-research-pipeline alterlab-workflow-orchestration; do
  echo "=== NEW $s ==="
  grep -m3 -E "version:|name:" "$BASE/alterlab-academic-skills/skills/core/$s/SKILL.md" 2>/dev/null
  wc -l "$BASE/alterlab-academic-skills/skills/core/$s/SKILL.md" 2>/dev/null
  ls "$BASE/alterlab-academic-skills/skills/core/$s/" 2>/dev/null | head -10
done
echo "=== diff check: deep-research ==="
diff -q "$BASE/.devin/skills/deep-research/SKILL.md" "$BASE/alterlab-academic-skills/skills/core/alterlab-deep-research/SKILL.md" && echo IDENTICAL || echo DIFFERENT
