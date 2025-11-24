# SmartRecruitAI Matcher Fine-Tuning Guide

This document explains how to train or fine-tune the SentenceTransformer-based matcher using Kaggle CV data and internal datasets.

## 1. Dataset Preparation

1. Place CV files under `data/data/<CATEGORY>/...` (already done for Kaggle dataset). Each folder name represents the job category.
2. Optionally create `job_descriptions.json` mapping category names to job description text.
3. The training pipeline will automatically parse PDFs/DOCX/TXT using `CVParser` and build positive + negative pairs.

## 2. Training Utilities

- `smartrecruitai/training/matcher_finetune.py`
  - `TrainingDatasetBuilder`: builds `InputExample` pairs and metadata.
  - `MatcherTrainer`: wraps SentenceTransformer training with configurable loss, optimizer (AdamW), epochs, learning rate, batch size, etc.
- `smartrecruitai/management/commands/fine_tune_matcher.py`
  - Django management command that orchestrates dataset building and fine-tuning.

## 3. Running Fine-Tuning

Inside the virtualenv:

```bash
python manage.py fine_tune_matcher \
    --data-root data/data \
    --jobs-file job_descriptions.json \
    --output models/custom_matcher \
    --loss cosine \
    --batch-size 16 \
    --epochs 2 \
    --learning-rate 2e-5 \
    --negative-ratio 1.0
```

### Key Arguments

- `--data-root`: Folder containing category subfolders with CV files.
- `--jobs-file`: Optional JSON file with job descriptions per category.
- `--output`: Directory to save the fine-tuned model + metadata.
- `--loss`: `cosine`, `multiple_negatives`, or `triplet`.
- `--batch-size`, `--epochs`, `--learning-rate`: Hyperparameters for AdamW.
- `--negative-ratio`: Number of negative samples generated per positive.

The command saves `training_metadata.jsonl` alongside the model for auditing.

## 4. Integrating the New Model

Update the matcher to load the fine-tuned checkpoint:

```python
from smartrecruitai.services.vector_matcher import VectorMatcher
matcher = VectorMatcher(model_name="models/custom_matcher")
```

Recompute stored embeddings if necessary (e.g., rerun any management command that regenerates embeddings for job offers or candidates).
