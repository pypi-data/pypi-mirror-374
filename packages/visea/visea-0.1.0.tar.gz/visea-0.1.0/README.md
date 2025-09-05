Visea — Visual Insights for Tabular EDA

Bu depo, PyPI’ye yüklenebilir “visea” kütüphanesinin kaynak kodunu içerir. Amaç: tabular veri setlerinde hedef odaklı keşif (EDA), otomatik istatistiksel özetler ve görselleştirme ile tek dosya HTML rapor üretimi.

Hızlı Başlangıç
- Python 3.10+
- Yerel kurulum:

  pip install -e .

- Kullanım (Python API):

  from visea import analyze
  report = analyze(df, target="y", task="auto")
  report.to_html("report.html")

- CLI:

  visea report --csv data.csv --target y --out report.html

Önemli Dosyalar
- visea/analyze.py: Ana giriş noktası (`analyze`)
- visea/report.py: HTML rapor oluşturucu
- visea/stats.py: Özet istatistikler ve testler
- visea/assoc.py: Hedef ilişkileri ve metrikler
- visea/plots.py: Matplotlib/Seaborn grafikler
- visea/typing.py: Tip çıkarım heuristikleri
- visea/cli.py: Komut satırı aracı

Örnek
- examples/quickstart.py — sentetik veri ile örnek rapor üretimi
