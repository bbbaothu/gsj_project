import sys
print("Starting SDV test...", flush=True)

import pandas as pd
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer

df = pd.DataFrame({
    'category': ['Tivi', 'Máy lạnh', 'Tủ lạnh', 'Máy giặt', 'Gia dụng'],
    'spending': [16500000, 11200000, 14800000, 9500000, 3200000],
    'discount_pct': [0.05, 0.10, 0.0, 0.08, 0.15]
})

metadata = SingleTableMetadata()
metadata.detect_from_dataframe(df)

synth = GaussianCopulaSynthesizer(metadata)
synth.fit(df)
synthetic_data = synth.sample(num_rows=3)

print("SDV SUCCESS! Synthetic samples:")
print(synthetic_data)
