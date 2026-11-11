import pandas as pd
import matplotlib.pyplot as plt

def carregar(arq):
    df = pd.read_csv(arq, skipinitialspace=True)
    df["P_kW"]   = -(df["P1 (kW)"]   + df["P2 (kW)"]   + df["P3 (kW)"])
    df["Q_kvar"] = -(df["Q1 (kvar)"] + df["Q2 (kvar)"] + df["Q3 (kvar)"])
    return df

sem = carregar(r"C:\Users\Otavi\Downloads\04-Modelo_OpenDSS\Q1\SemPV.csv")   # ajuste os nomes
com = carregar(r"C:\Users\Otavi\Downloads\04-Modelo_OpenDSS\Q1\ComPV.csv")

# checagem: se der 0, você está lendo o mesmo arquivo
print("Diferença máxima em P (kW):", (sem["P_kW"] - com["P_kW"]).abs().max())

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(sem["hour"], sem["P_kW"], "o-", label="P sem GFV")
ax.plot(com["hour"], com["P_kW"], "s-", label="P com GFV")
ax.set_xlabel("Hora do dia")
ax.set_ylabel("Potência ativa (kW)")
ax.set_title("Perfil de carga do alimentador")
ax.set_xticks(range(1, 25))
ax.grid(alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig("perfil_comparativo.png", dpi=200)
plt.show()