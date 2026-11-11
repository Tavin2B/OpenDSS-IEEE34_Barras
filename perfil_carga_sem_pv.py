import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r"C:\Users\Otavi\Downloads\04-Modelo_OpenDSS\Q1\SemPV.csv", skipinitialspace=True)   # ajuste o nome do arquivo

# demanda do alimentador = -(soma das fases)
df["P_kW"]   = -(df["P1 (kW)"]   + df["P2 (kW)"]   + df["P3 (kW)"])
df["Q_kvar"] = -(df["Q1 (kvar)"] + df["Q2 (kvar)"] + df["Q3 (kvar)"])
df["S_kVA"]  = (df["P_kW"]**2 + df["Q_kvar"]**2) ** 0.5

# resumo
h_pico = df.loc[df["P_kW"].idxmax(), "hour"]
h_vale = df.loc[df["P_kW"].idxmin(), "hour"]
print(f"Pico:  {df['P_kW'].max():.1f} kW na hora {h_pico}")
print(f"Vale:  {df['P_kW'].min():.1f} kW na hora {h_vale}")
print(f"Energia em 24 h: {df['P_kW'].sum():.1f} kWh")

# gráfico
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["hour"], df["P_kW"], marker="o", label="P (kW)")
ax.plot(df["hour"], df["Q_kvar"], marker="s", label="Q (kvar)")
ax.axhline(0, color="gray", lw=0.8)
ax.set_xlabel("Hora do dia")
ax.set_ylabel("Potência")
ax.set_title("Perfil de carga do alimentador")
ax.set_xticks(range(1, 25))
ax.grid(alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig("perfil_carga.png", dpi=200)
plt.show()

df[["hour", "P_kW", "Q_kvar", "S_kVA"]].to_csv("perfil_carga_total.csv", index=False)