import pandas as pd
import os

def save_product_table_to_excel(data: list, output_path: str):
    df = pd.DataFrame(data)
    df = df.dropna(axis=1, how='all')  

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Products")

        workbook = writer.book
        worksheet = writer.sheets["Products"]

        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
            adjusted_width = (max_length + 2)
            col_letter = column_cells[0].column_letter
            worksheet.column_dimensions[col_letter].width = adjusted_width
 
