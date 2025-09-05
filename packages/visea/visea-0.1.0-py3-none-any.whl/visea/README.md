# Visea

Hedef odaklı (target-aware) tabular veri keşfi ve görselleştirme kütüphanesi. Tek satırla veri kümesini analiz eder, istatistiksel özetler ve yorumlarla birlikte HTML raporu üretir.

Özellikler (v0.1)
- Otomatik tip çıkarımı (sayısal/kategorik/tarihsel) ve temel veri profili.
- Target farkındalığı: sınıflandırma/regresyon için uygun metrikler.
- Tek değişkenli dağılımlar ve hedef ile ilişkiler (korelasyon, AUC/R², ANOVA/chi², Cramer’s V).
- Basit ama şık HTML rapor (inline görseller).
- CLI: CSV’den direkt rapor üretimi.

Kurulum (yerel)
- `pip install -e .` veya bağımlılıkları: numpy, pandas, scipy, scikit-learn, matplotlib, seaborn.

Kullanım
```python
from visea import analyze
report = analyze(df, target="y", task="auto")
report.to_html("report.html")
```

CLI
```bash
visea report --csv data.csv --target y --out report.html
```

Notlar
- Büyük veri setlerinde otomatik örnekleme ile hız korunur.
- İlerleyen sürümlerde: plotly backend, WoE/IV, Theil’s U, sızıntı uyarıları.
