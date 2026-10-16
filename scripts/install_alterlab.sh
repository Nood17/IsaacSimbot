#!/bin/bash
set -e
BASE=/home/ubuntu/nood
SKILLS=$BASE/.devin/skills
ALT=$BASE/alterlab-academic-skills/skills
ARS=$BASE/ars-upstream

echo "=== 1. backup old skills ==="
tar czf "$BASE/.devin/skills.bak-20261015.tar.gz" -C "$BASE/.devin" skills
ls -la "$BASE/.devin/skills.bak-20261015.tar.gz"

echo "=== 2. refresh old 4 + add sr-screener from upstream ==="
for s in deep-research academic-paper academic-paper-reviewer academic-pipeline sr-screener; do
  rm -rf "$SKILLS/$s"
  cp -r "$ARS/$s" "$SKILLS/$s"
  v=$(grep -m1 'version:' "$SKILLS/$s/SKILL.md" | tr -d ' ')
  echo "installed $s  $v"
done

echo "=== 3. install alterlab curated set ==="
LIST="
core/alterlab-citation-verifier
core/alterlab-deep-research
core/alterlab-link-health
core/alterlab-paper-reviewer
core/alterlab-paper-writer
core/alterlab-research-pipeline
core/alterlab-skill-finder
core/alterlab-teaching-design
core/alterlab-thesis-supervisor
core/alterlab-workflow-orchestration
methodology/alterlab-preregistration-discipline
methodology/alterlab-results-transparency
methodology/alterlab-test-selection-guard
data-science/alterlab-pufferlib
data-science/alterlab-stable-baselines3
data-science/alterlab-pytorch-lightning
data-science/alterlab-transformers
data-science/alterlab-scikit-learn
data-science/alterlab-statistical-analysis
data-science/alterlab-eda
data-science/alterlab-shap
data-science/alterlab-sympy
data-science/alterlab-pymoo
data-science/alterlab-simpy
data-science/alterlab-pymc
research-tools/alterlab-research-lookup
research-tools/alterlab-citation-graph
research-tools/alterlab-parallel-web
research-tools/alterlab-pdf-extract
research-tools/alterlab-scientific-brainstorm
research-tools/alterlab-scientific-thinking
research-tools/alterlab-research-ethics
research-tools/alterlab-open-science
writing-tools/alterlab-literature-review
writing-tools/alterlab-scientific-writing
writing-tools/alterlab-hypothesis-gen
writing-tools/alterlab-venue-templates
writing-tools/alterlab-peer-review
writing-tools/alterlab-scientific-slides
writing-tools/alterlab-ai-use-disclosure
writing-tools/alterlab-citation-mgmt
writing-tools/alterlab-research-grants
visualization/alterlab-matplotlib
visualization/alterlab-plotly
visualization/alterlab-seaborn
visualization/alterlab-scientific-viz
visualization/alterlab-figure-qa
visualization/alterlab-mermaid
visualization/alterlab-scientific-schematics
document-tools/alterlab-markitdown
document-tools/alterlab-open-notebook
document-tools/alterlab-pdf-explore
databases/alterlab-arxiv
databases/alterlab-openalex
domain-specific/alterlab-remote-compute
workflows/alterlab-research-workflows
"
for p in $LIST; do
  n=$(basename "$p")
  if [ -d "$ALT/$p" ]; then
    rm -rf "$SKILLS/$n"
    cp -r "$ALT/$p" "$SKILLS/$n"
  else
    echo "MISSING: $p"
  fi
done

echo "=== 4. shared contracts ==="
mkdir -p "$SKILLS/shared"
cp -r "$ALT/core/shared/"* "$SKILLS/shared/" 2>/dev/null
ls "$SKILLS/shared/"

echo "=== done ==="
ls "$SKILLS" | wc -l
ls "$SKILLS"
