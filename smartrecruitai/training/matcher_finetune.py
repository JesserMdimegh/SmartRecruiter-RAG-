"""Utilities for building datasets and fine-tuning the matcher model."""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import torch
from sentence_transformers import InputExample, SentenceTransformer, losses
from torch.utils.data import DataLoader

from ..services.cv_parser import CVParser
from ..services.vector_matcher import VectorMatcher


DEFAULT_JOB_DESCRIPTIONS: Dict[str, str] = {
    "ACCOUNTANT": "Accountant role responsible for financial reporting, ledgers, audits, GAAP compliance, and ERP tools.",
    "ADVOCATE": "Legal advocate handling case research, client counseling, litigation prep, and courtroom representation.",
    "AGRICULTURE": "Agriculture specialist focused on crop planning, soil analysis, irrigation, and agribusiness operations.",
    "APPAREL": "Fashion and apparel professional covering trend analysis, garment production, merchandising, and sourcing.",
    "ARTS": "Creative arts contributor producing visual concepts, exhibits, multimedia content, and cultural programming.",
    "AUTOMOBILE": "Automotive engineer/manager overseeing vehicle diagnostics, maintenance, and production workflows.",
    "AVIATION": "Aviation operations professional for flight planning, safety compliance, and fleet coordination.",
    "BANKING": "Banking specialist delivering client portfolio reviews, risk assessments, and lending services.",
    "BPO": "Business process outsourcing expert handling customer success, SLA adherence, and multi-channel support.",
    "BUSINESS-DEVELOPMENT": "Business development manager driving pipeline growth, partnerships, and go-to-market strategy.",
    "CHEF": "Culinary lead managing menu design, kitchen brigades, sourcing, and food safety protocols.",
    "CONSTRUCTION": "Construction project manager coordinating contractors, schedules, budgets, and safety inspections.",
    "CONSULTANT": "Management consultant producing strategy analyses, stakeholder workshops, and implementation roadmaps.",
    "DESIGNER": "Product/UX designer crafting wireframes, prototypes, and design systems aligned with user research.",
    "DIGITAL-MEDIA": "Digital media strategist executing campaigns, analytics, content calendars, and SEO/SEM initiatives.",
    "ENGINEERING": "Engineer responsible for systems design, testing, documentation, and cross-functional integration.",
    "FINANCE": "Finance analyst covering forecasting, FP&A models, KPI dashboards, and investment memos.",
    "FITNESS": "Fitness coach designing personalized programs, biomechanics assessments, and client motivation routines.",
    "HEALTHCARE": "Healthcare practitioner delivering patient care, diagnostics, treatment plans, and compliance records.",
    "HR": "Human resources partner managing talent acquisition, onboarding, engagement, and compliance.",
    "INFORMATION-TECHNOLOGY": "IT professional implementing software solutions, infrastructure, security, and DevOps practices.",
    "PUBLIC-RELATIONS": "PR specialist running media relations, press releases, crisis comms, and brand storytelling.",
    "SALES": "Sales executive handling prospecting, demos, negotiations, and revenue forecasting.",
    "TEACHER": "Educator planning curricula, classroom management, assessments, and student mentorship.",
}


@dataclass
class SampleMetadata:
    """Metadata captured for each training example."""

    candidate_path: str
    job_category: str
    label: float


class TrainingDatasetBuilder:
    """Build InputExample datasets from CV folders."""

    def __init__(
        self,
        data_root: Path | str,
        job_description_file: Optional[Path | str] = None,
        max_files_per_category: Optional[int] = None,
        negative_ratio: float = 1.0,
        seed: int = 42,
    ) -> None:
        self.data_root = Path(data_root)
        self.job_description_file = Path(job_description_file) if job_description_file else None
        self.max_files_per_category = max_files_per_category
        self.negative_ratio = negative_ratio
        self.random = random.Random(seed)
        self.cv_parser = CVParser()

    def _load_job_descriptions(self) -> Dict[str, str]:
        if self.job_description_file and self.job_description_file.exists():
            with open(self.job_description_file, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return {k.upper(): v for k, v in data.items() if isinstance(v, str) and v.strip()}
        return DEFAULT_JOB_DESCRIPTIONS.copy()

    def _iter_cv_files(self) -> Sequence[Tuple[str, Path]]:
        for category_path in sorted(self.data_root.glob("*/")):
            if not category_path.is_dir():
                continue
            category = category_path.name.upper()
            files = list(category_path.glob("*"))
            if self.max_files_per_category:
                files = files[: self.max_files_per_category]
            for file_path in files:
                yield category, file_path

    def build_dataset(self) -> Tuple[List[InputExample], List[SampleMetadata]]:
        job_descriptions = self._load_job_descriptions()
        categories = list(job_descriptions.keys())
        examples: List[InputExample] = []
        metadata: List[SampleMetadata] = []

        for category, file_path in self._iter_cv_files():
            try:
                candidate_text = CVParser.extract_text(str(file_path)).strip()
            except Exception:
                continue
            if len(candidate_text) < 200:
                continue

            job_text = job_descriptions.get(
                category,
                f"{category.title()} role covering responsibilities, required skills, and KPIs.",
            )
            examples.append(InputExample(texts=[candidate_text, job_text], label=1.0))
            metadata.append(SampleMetadata(str(file_path), category, 1.0))

            # Negative samples
            for _ in range(int(self.negative_ratio)):
                negative_category = self.random.choice(categories)
                if negative_category == category and len(categories) > 1:
                    negative_category = self.random.choice(
                        [cat for cat in categories if cat != category]
                    )
                negative_job_text = job_descriptions[negative_category]
                examples.append(InputExample(texts=[candidate_text, negative_job_text], label=0.0))
                metadata.append(SampleMetadata(str(file_path), negative_category, 0.0))

        self.random.shuffle(examples)
        self.random.shuffle(metadata)
        return examples, metadata

    def export_metadata(self, metadata: Sequence[SampleMetadata], output_path: Path | str) -> None:
        path = Path(output_path)
        with open(path, "w", encoding="utf-8") as fh:
            for item in metadata:
                fh.write(json.dumps(asdict(item)) + "\n")


class MatcherTrainer:
    """Fine-tune SentenceTransformer models for SmartRecruitAI."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-mpnet-base-v2",
        batch_size: int = 16,
        epochs: int = 2,
        learning_rate: float = 2e-5,
        loss_name: str = "cosine",
        output_path: Optional[str] = None,
        warmup_ratio: float = 0.1,
    ) -> None:
        self.model_name = model_name
        self.batch_size = batch_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.loss_name = loss_name.lower()
        self.output_path = output_path
        self.warmup_ratio = warmup_ratio
        self.model = SentenceTransformer(model_name)

    def _build_loss(self) -> losses.SentenceTransformerLoss:
        if self.loss_name == "cosine":
            return losses.CosineSimilarityLoss(self.model)
        if self.loss_name in {"multiple_negatives", "mnr"}:
            return losses.MultipleNegativesRankingLoss(self.model)
        if self.loss_name == "triplet":
            return losses.TripletLoss(self.model)
        raise ValueError(f"Unsupported loss '{self.loss_name}'")

    def train(
        self,
        train_examples: Sequence[InputExample],
        val_examples: Optional[Sequence[InputExample]] = None,
    ) -> str:
        if not train_examples:
            raise ValueError("No training examples provided")

        train_loader = DataLoader(train_examples, shuffle=True, batch_size=self.batch_size)
        train_loss = self._build_loss()

        warmup_steps = math.ceil(len(train_loader) * self.epochs * self.warmup_ratio)
        output_path = self.output_path or "models/custom_matcher"

        self.model.fit(
            train_objectives=[(train_loader, train_loss)],
            epochs=self.epochs,
            optimizer_class=torch.optim.AdamW,
            optimizer_params={"lr": self.learning_rate},
            warmup_steps=warmup_steps,
            output_path=output_path,
            show_progress_bar=True,
        )

        if val_examples:
            self.evaluate(val_examples)

        return output_path

    def evaluate(self, examples: Sequence[InputExample]) -> Dict[str, float]:
        matcher = VectorMatcher(model_name=self.model_name)
        scores = []
        labels = []
        for example in examples:
            candidate_text, job_text = example.texts
            similarity = matcher.match_candidate_to_job(candidate_text, job_text)
            scores.append(similarity)
            labels.append(example.label)
        if not scores:
            return {"count": 0, "mean_score": 0.0}
        mean_score = sum(scores) / len(scores)
        return {"count": len(scores), "mean_score": mean_score}
