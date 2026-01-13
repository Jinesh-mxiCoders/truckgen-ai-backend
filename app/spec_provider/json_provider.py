import json
from typing import List, Dict, Any

CATEGORY_MAP = {
    "stationary_pump": "Stationary Pumps",
    "boom_pump": "Boom Pumps",
    "loop_belt": "Loop Belts",
    "placing_boom" : "Placing Booms"
}

class JsonModelSpecProvider():
    def __init__(self, json_path: str):
        with open(json_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self._index = {
            item["name"]: item
            for item in self.data
        }

    def get_specs_by_models(
        self,
        *,
        product_type: str,
        model_names: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        result = []
        mapped_category = CATEGORY_MAP.get(product_type.lower())
        if not mapped_category:
            return result 
        
        for model, score in model_names.items():
            record = self._index.get(model)
            print("record", record)
            if not record:
                continue

            if record["category"] != mapped_category:
                continue

            result.append({
                "model": model,
                "score": score,
                "category": record["category"],
                "specifications": record["specifications"],
                # "brochure_url": record.get("brochure_url"),
                # "source_url": record.get("source_url"),
            })
            
        return result