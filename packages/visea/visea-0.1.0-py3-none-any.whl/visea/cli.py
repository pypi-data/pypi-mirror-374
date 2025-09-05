from __future__ import annotations

import argparse
import pandas as pd
from .analyze import analyze


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="visea", description="Visea – tabular EDA & report")
    sub = parser.add_subparsers(dest="cmd")

    p_report = sub.add_parser("report", help="CSV'den HTML rapor üret")
    p_report.add_argument("--csv", required=True, help="Girdi CSV yolu")
    p_report.add_argument("--target", required=False, help="Hedef sütun adı")
    p_report.add_argument("--task", default="auto", choices=["auto", "classification", "regression"], help="Görev tipi")
    p_report.add_argument("--out", required=True, help="Çıktı HTML yolu")
    p_report.add_argument("--sample-max-rows", type=int, default=100000)

    args = parser.parse_args(argv)
    if args.cmd == "report":
        df = pd.read_csv(args.csv)
        report = analyze(df, target=args.target, task=args.task, sample_max_rows=args.sample_max_rows)
        report.to_html(args.out)
        print(f"Rapor yazıldı: {args.out}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
