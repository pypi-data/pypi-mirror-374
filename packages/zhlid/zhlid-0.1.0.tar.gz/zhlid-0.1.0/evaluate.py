import pandas as pd
import json
from tqdm import tqdm
from pathlib import Path
from src.zhlid import load_model


folder = "benchmark/eval_data"
save_path = "benchmark/res/ZHLID_eval_results.jsonl"
model = load_model("MusubiAI/ZHLID", device_map="auto")
files = Path(folder).glob("*.jsonl")

BATCH_SIZE = 5


for file in files:
    print("Start evaluating {} task".format(file.stem))
    df = pd.read_json(file, lines=True)
    num_batches = (len(df) + BATCH_SIZE - 1) // BATCH_SIZE

    start_idx = 0
    correct = 0
    for i in tqdm(range(num_batches)):
        texts = df.iloc[start_idx:start_idx+BATCH_SIZE]["text"].to_list()
        ground_label = df.iloc[start_idx:start_idx+BATCH_SIZE]["ground_label"].to_list()
        res = model.predict(texts, batch_size=BATCH_SIZE)

        for j, item in enumerate(res):
            pred_label = item["label"]
            if pred_label == ground_label[j]:
                correct += 1

        start_idx += BATCH_SIZE

    acc = correct / len(df)
    data = {"lang": file.stem, "accuracy": acc}
    with open(save_path, "a+", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")