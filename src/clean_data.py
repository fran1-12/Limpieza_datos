import json
import logging
from pathlib import Path

import pandas as pd


# Las rutas funcionan aunque ejecutes el programa desde otra carpeta.
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "raw" / "ventas.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

REQUIRED_COLUMNS = [
    "venta_id",
    "cliente",
    "email",
    "fecha",
    "cantidad",
    "precio_unitario",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)


def clean_sales(input_file: Path, output_dir: Path) -> dict:
    """Limpia ventas, separa rechazos y genera un reporte de calidad."""

    if not input_file.is_file():
        raise FileNotFoundError(f"No existe el archivo: {input_file}")

    # Leer como texto evita perder información antes de validarla.
    df = pd.read_csv(input_file, dtype="string", encoding="utf-8")

    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(df.columns))

    if missing_columns:
        raise ValueError(
            f"Faltan columnas obligatorias: {missing_columns}"
        )

    input_rows = len(df)

    # Normalizar espacios y convertir cadenas vacías en valores ausentes.
    for column in REQUIRED_COLUMNS:
        df[column] = df[column].str.strip()

    df = df.replace("", pd.NA)
    df["email"] = df["email"].str.lower()

    # Eliminar únicamente filas completamente iguales.
    df = df.drop_duplicates().copy()
    duplicates_removed = input_rows - len(df)

    # Conservar los valores originales para revisar los rechazos.
    original = df.copy()

    sale_ids = pd.to_numeric(df["venta_id"], errors="coerce")
    quantities = pd.to_numeric(df["cantidad"], errors="coerce")
    prices = pd.to_numeric(df["precio_unitario"], errors="coerce")
    dates = pd.to_datetime(
        df["fecha"],
        format="%Y-%m-%d",
        errors="coerce",
    )

    # Esta validación verifica la estructura básica del correo.
    # No comprueba si la dirección existe.
    email_valid = df["email"].str.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        na=False,
    )

    rules = {
        "venta_id_invalido": (
            sale_ids.isna()
            | sale_ids.le(0)
            | sale_ids.mod(1).ne(0)
        ),
        "cliente_vacio": df["cliente"].isna(),
        "email_invalido": ~email_valid,
        "fecha_invalida": dates.isna(),
        "cantidad_invalida": (
            quantities.isna()
            | quantities.le(0)
            | quantities.mod(1).ne(0)
        ),
        "precio_invalido": prices.isna() | prices.le(0),
        # Después de quitar duplicados exactos, un ID repetido
        # representa registros que necesitan revisión.
        "venta_id_repetido": sale_ids.duplicated(keep=False),
    }

    errors = pd.Series("", index=df.index, dtype="string")
    errors_by_rule = {}

    for reason, invalid in rules.items():
        invalid = invalid.fillna(True)
        errors_by_rule[reason] = int(invalid.sum())
        errors.loc[invalid] = errors.loc[invalid] + reason + ";"

    rejected_mask = errors.ne("")

    rejected = original.loc[rejected_mask].copy()
    rejected["motivo_rechazo"] = (
        errors.loc[rejected_mask].str.rstrip(";")
    )

    clean = df.loc[~rejected_mask].copy()
    clean["venta_id"] = sale_ids.loc[clean.index].astype("int64")
    clean["cantidad"] = quantities.loc[clean.index].astype("int64")
    clean["precio_unitario"] = prices.loc[clean.index]
    clean["fecha"] = dates.loc[clean.index].dt.strftime("%Y-%m-%d")
    clean["total_venta"] = (
        clean["cantidad"] * clean["precio_unitario"]
    )

    report = {
        "filas_entrada": input_rows,
        "duplicados_eliminados": duplicates_removed,
        "filas_validas": len(clean),
        "filas_rechazadas": len(rejected),
        "errores_por_regla": errors_by_rule,
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    clean.to_csv(
        output_dir / "ventas_limpias.csv",
        index=False,
        encoding="utf-8",
    )

    rejected.to_csv(
        output_dir / "ventas_rechazadas.csv",
        index=False,
        encoding="utf-8",
    )

    with (output_dir / "reporte_calidad.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    logging.info("Proceso completado: %s", report)

    return report


if __name__ == "__main__":
    clean_sales(INPUT_FILE, OUTPUT_DIR)