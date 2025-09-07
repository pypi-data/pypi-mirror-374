import torch
import torch.nn as nn
from typing import List, Union, Optional
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class Model:
    def __init__(
        self,
        model_path: str,
        **kwargs
    ):
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path, **kwargs)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.config = self.model.config
    
    def get_id2label(
        self
    ):
        id2label = self.config.id2label
        return id2label

    def get_label2id(
        self
    ):
        label2id = self.config.label2id
        return label2id

    def predict(
        self,
        text: Union[str, List[str]],
        batch_size: Optional[int] = 1
    ):
        max_length = self.config.max_position_embeddings
        device = self.model.device
        id2label = self.get_id2label()

        if isinstance(text, str):
            text = [text]

        res = []

        for i in range(0, len(text), batch_size):
            batch_text = text[i:i + batch_size]
            inputs = self.tokenizer(
                batch_text, 
                return_tensors="pt", 
                padding='longest', 
                truncation=True, 
                max_length=max_length
            )

            with torch.no_grad():
                logits = self.model(**inputs.to(device))["logits"]

            scores = nn.functional.softmax(logits, dim=-1)
            pred_scores, pred_indices = torch.max(scores, dim=-1)
            pred_scores = pred_scores.cpu().tolist()
            pred_indices = pred_indices.cpu().tolist()

            for score, idx in zip(pred_scores, pred_indices):
                score = round(score, 10)
                label = id2label[idx]
                res_dict = {"label": label, "confidence_score": score}
                res.append(res_dict)

        return res


def load_model(model_path: str = "MusubiAI/ZHLID", **kwargs):
    return Model(model_path=model_path, **kwargs)

