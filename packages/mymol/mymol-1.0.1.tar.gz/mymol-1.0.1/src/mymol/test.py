import pandas as pd

# Data for nutritional values of the dessert
nutrition_data_dessert = {
    "Voedingsstof": ["Calorieën (kcal)", "Vet (gram)", "Koolhydraten (gram)", "Eiwit (gram)"],
    "Per portie (1/4 gerecht)": [350, 20, 40, 8],
    "In totaal (hele gerecht)": [1400, 80, 160, 32],
    "Per 100 gram gerecht": [250, 14.3, 28.6, 5.7],
}

# Data for cost breakdown of the dessert
cost_data_dessert = {
    "Ingrediënt": ["Appels", "Pecannoten", "Vanillestokje", "Rozijnen", "Kaneel", "Honing", "Havermout", "Kokosolie", "Griekse yoghurt"],
    "Hoeveelheid": ["4 stuks (~600 g)", "75 g", "1 stokje", "2 el (~30 g)", "2 tl (~5 g)", "2 el (~40 g)", "150 g", "5 el (~75 g)", "1 kommetje (~150 g)"],
    "Prijs per eenheid": ["\u20ac2,99 per kg", "\u20ac3,49 per 150 g", "\u20ac1,49 per stokje", "\u20ac1,29 per 250 g", "\u20ac1,99 per 50 g", "\u20ac6,49 per 450 g", "\u20ac0,89 per 500 g", "\u20ac4,99 per 400 g", "\u20ac1,29 per 150 g"],
    "Kosten": ["\u20ac1,79", "\u20ac1,74", "\u20ac1,49", "\u20ac0,15", "\u20ac0,20", "\u20ac0,58", "\u20ac0,27", "\u20ac0,94", "\u20ac1,29"],
}

# Save dataframes as an Excel file
nutrition_df_dessert = pd.DataFrame(nutrition_data_dessert)
cost_df_dessert = pd.DataFrame(cost_data_dessert)

output_file = "C:/school/indelen/Dessert_Analysis_Jan2025.xlsx"
with pd.ExcelWriter(output_file) as writer:
    nutrition_df_dessert.to_excel(writer, index=False, sheet_name="Voedingswaarden")
    cost_df_dessert.to_excel(writer, index=False, sheet_name="Kostenanalyse")

print(f"Excel-bestand opgeslagen als: {output_file}")
