from collections import defaultdict
from typing import Dict, List, Any

class ModelMatchResolver:
    """
    Resolves best-matching models based on collected field constraints.
    """

    def resolve(
        self,
        collected_data: Dict[str, Dict[str, Any]],
        top_k: int = 3,
        field_weights: Dict[str, int] | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Returns top matched models with specifications.
        """

        model_scores = self._aggregate_scores(collected_data, field_weights)
        ranked_models = self._rank_models(model_scores)
        selected_models = ranked_models[:top_k]
        models_list = self._models_list(selected_models)

        return {
            "model_scores": model_scores,
            "ranked_models": ranked_models,
            "selected_models": selected_models,
            "models_list": models_list
        }

    def _aggregate_scores(
        self,
        collected_data: Dict[str, Dict[str, Any]],
        field_weights: Dict[str, int] | None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Builds model -> score mapping.
        """

        scores = defaultdict(lambda: {
            "score": 0,
            "matched_fields": []
        })

        for field, details in collected_data.items():
            weight = field_weights.get(field, 1) if field_weights else 1
            matched_models = details.get("matched_models", [])

            for model in matched_models:
                scores[model]["score"] += weight
                scores[model]["matched_fields"].append(field)

        return scores

    def _rank_models(
        self,
        model_scores: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Sorts models by score (descending).
        """

        ranked = sorted(
            model_scores.items(),
            key=lambda item: item[1]["score"],
            reverse=True
        )

        return [
            {
                "model": model,
                "score": meta["score"],
                "matched_fields": meta["matched_fields"]
            }
            for model, meta in ranked
        ]

    def _models_list(self, selected_models: List[Dict[str, Any]]) -> Dict[str, int]:
        return {
            item["model"]: item["score"]
            for item in selected_models
            if "model" in item and "score" in item
        }
