"""Management command to fine-tune SmartRecruitAI's matcher model."""

import argparse
from pathlib import Path

from django.core.management.base import BaseCommand

from ...training.matcher_finetune import MatcherTrainer, TrainingDatasetBuilder


class Command(BaseCommand):
    help = "Fine-tune the matcher model using CV datasets"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--data-root",
            type=str,
            default="data/data",
            help="Path to root directory containing category folders",
        )
        parser.add_argument(
            "--jobs-file",
            type=str,
            default=None,
            help="Optional JSON file with job descriptions per category",
        )
        parser.add_argument(
            "--output",
            type=str,
            default="models/custom_matcher",
            help="Directory where the fine-tuned model will be saved",
        )
        parser.add_argument(
            "--loss",
            type=str,
            default="cosine",
            choices=["cosine", "multiple_negatives", "triplet"],
            help="Training loss to use",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=16,
            help="Batch size",
        )
        parser.add_argument(
            "--epochs",
            type=int,
            default=2,
            help="Number of training epochs",
        )
        parser.add_argument(
            "--learning-rate",
            type=float,
            default=2e-5,
            help="Learning rate for AdamW",
        )
        parser.add_argument(
            "--max-files",
            type=int,
            default=None,
            help="Optional limit of files per category",
        )
        parser.add_argument(
            "--negative-ratio",
            type=float,
            default=1.0,
            help="How many negative samples to generate per positive sample",
        )
        parser.add_argument(
            "--warmup-ratio",
            type=float,
            default=0.1,
            help="Warmup steps ratio",
        )

    def handle(self, *args, **options):
        # Use fixed dataset configuration (no need to pass these via CLI)
        data_root = Path("data/data")
        builder = TrainingDatasetBuilder(
            data_root=data_root,
            job_description_file="job_descriptions.json",
            max_files_per_category=30,
            negative_ratio=0.5,
        )

        self.stdout.write(self.style.NOTICE("Building dataset ..."))
        train_examples, metadata = builder.build_dataset()
        self.stdout.write(self.style.SUCCESS(f"Prepared {len(train_examples)} training pairs"))

        # Always write training metadata next to the custom matcher model
        metadata_path = Path("models/custom_matcher") / "training_metadata.jsonl"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        builder.export_metadata(metadata, metadata_path)

        trainer = MatcherTrainer(
            model_name="sentence-transformers/all-mpnet-base-v2",
            batch_size=16,
            epochs=2,
            learning_rate=2e-5,
            loss_name="cosine",
            output_path="models/custom_matcher",
            warmup_ratio=0.1,
        )

        self.stdout.write(self.style.NOTICE("Starting fine-tuning (AdamW optimizer) ..."))
        output_path = trainer.train(train_examples)
        self.stdout.write(self.style.SUCCESS(f"Model saved to {output_path}"))
