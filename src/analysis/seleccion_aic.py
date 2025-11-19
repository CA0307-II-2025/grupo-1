import itertools
import pandas as pd
import statsmodels.api as sm


def seleccionar_por_aic(X, y):
    variables = X.columns
    resultados = []
    for k in range(1, len(variables) + 1):
        for combo in itertools.combinations(variables, k):
            X_subset = sm.add_constant(X[list(combo)])
            modelo = sm.OLS(y, X_subset).fit()
            resultados.append((combo, modelo.aic))
    resultados_df = pd.DataFrame(resultados, columns=["variables", "AIC"])
    resultados_df = resultados_df.sort_values(by="AIC").reset_index(drop=True)
    return resultados_df


df = pd.read_csv("../../data/clean/datos_limpios.csv")
df_sobrepeso = df[df["condicion"] == "sobrepeso"]
df_obesidad = df[df["condicion"] == "obesidad"]

pred_sob = df_sobrepeso.drop(
    columns=[
        "codigo",
        "distrito",
        "provincia",
        "canton",
        "condicion",
        "total",
        "subtotal",
        "prevalencia",
    ]
)
pred_obe = df_obesidad.drop(
    columns=[
        "codigo",
        "distrito",
        "provincia",
        "canton",
        "condicion",
        "total",
        "subtotal",
        "prevalencia",
    ]
)

prev_sob = df_sobrepeso["prevalencia"]
prev_obe = df_obesidad["prevalencia"]

tabla_aic_sob = seleccionar_por_aic(pred_sob, prev_sob)
mejor_combo_sob = tabla_aic_sob.iloc[0]["variables"]

tabla_aic_obe = seleccionar_por_aic(pred_obe, prev_obe)
mejor_combo_obe = tabla_aic_obe.iloc[0]["variables"]

modelo_final_sob = sm.OLS(
    prev_sob, sm.add_constant(pred_sob[list(mejor_combo_sob)])
).fit()
modelo_final_obe = sm.OLS(
    prev_obe, sm.add_constant(pred_obe[list(mejor_combo_obe)])
).fit()

print(modelo_final_sob.summary())
print(modelo_final_obe.summary())
