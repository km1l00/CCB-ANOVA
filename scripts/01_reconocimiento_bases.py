import os
import pandas as pd
from pathlib import Path

def main():
    print("Iniciando reconocimiento de bases...")
    # Ajustar rutas asumiendo que el script se corre desde la carpeta 'scripts'
    base_dir = Path(__file__).parent.parent
    raw_dir = base_dir / "data" / "raw"
    if not raw_dir.exists():
        raw_dir.mkdir(parents=True, exist_ok=True)
        print(f"Se creó el directorio {raw_dir}. Por favor, pon tus datos aquí.")
        return
        
    archivos = list(raw_dir.rglob("*.xlsx")) + list(raw_dir.rglob("*.xls")) + list(raw_dir.rglob("*.csv"))
    if not archivos:
        print("No se encontraron archivos en data/raw/")
        return
        
    inventario = []
    for archivo in archivos:
        try:
            if archivo.suffix in ['.xlsx', '.xls']:
                excel_file = pd.ExcelFile(archivo)
                hojas = excel_file.sheet_names
                inventario.append({
                    "Archivo": archivo.name,
                    "Tipo": "Excel",
                    "Num_Hojas": len(hojas),
                    "Nombres_Hojas": ", ".join(hojas)
                })
                print(f"Procesado: {archivo.name} ({len(hojas)} hojas)")
            elif archivo.suffix == '.csv':
                inventario.append({
                    "Archivo": archivo.name,
                    "Tipo": "CSV",
                    "Num_Hojas": 1,
                    "Nombres_Hojas": "N/A"
                })
                print(f"Procesado: {archivo.name} (CSV)")
        except Exception as e:
            print(f"Error leyendo {archivo.name}: {e}")
            
    df_inventario = pd.DataFrame(inventario)
    output_dir = base_dir / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "inventario_bases.xlsx"
    df_inventario.to_excel(output_path, index=False)
    print(f"\n✅ Inventario guardado exitosamente en: {output_path}")

if __name__ == "__main__":
    main()
