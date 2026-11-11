import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

V_BASE = 4160 / np.sqrt(3)          # barra 890: 4,16 kV -> base fase-neutro em volts
ARQ_SEM = r"C:\Users\Otavi\Downloads\04-Modelo_OpenDSS\Q2\SemPV.csv"        # ajuste os nomes
ARQ_COM = r"C:\Users\Otavi\Downloads\04-Modelo_OpenDSS\Q2\ComPV.csv"


def carregar(arq):
    df = pd.read_csv(arq, skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]      # remove espaços dos cabeçalhos
    out = pd.DataFrame({"hora": df["hour"]})
    for i, fase in zip((1, 2, 3), "ABC"):
        out[f"V{fase}_pu"] = df[f"V{i}"] / V_BASE
        out[f"ang{fase}"] = df[f"VAngle{i}"]
    return out


sem = carregar(ARQ_SEM)
com = carregar(ARQ_COM)

# checagem: se der 0, você está lendo o mesmo arquivo nos dois casos
dif = max((sem[f"V{f}_pu"] - com[f"V{f}_pu"]).abs().max() for f in "ABC")
print(f"Diferença máxima entre casos: {dif:.6f} pu\n")

# resumo por fase
for nome, d in (("SEM GFV", sem), ("COM GFV", com)):
    print(f"--- {nome} ---")
    for f in "ABC":
        col = f"V{f}_pu"
        hmax = d.loc[d[col].idxmax(), "hora"]
        hmin = d.loc[d[col].idxmin(), "hora"]
        print(f"Fase {f}: máx {d[col].max():.4f} pu (h {hmax}) | "
              f"mín {d[col].min():.4f} pu (h {hmin})")
    print()

# gráfico: uma fase por subplot, com e sem GFV
fig, axs = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
for ax, f in zip(axs, "ABC"):
    ax.plot(sem["hora"], sem[f"V{f}_pu"], "o-", label="Sem GFV")
    ax.plot(com["hora"], com[f"V{f}_pu"], "s-", label="Com GFV")
    ax.axhline(1.05, color="r", ls="--", lw=0.8)    # limites PRODIST/ANSI
    ax.axhline(0.95, color="r", ls="--", lw=0.8)
    ax.set_ylabel(f"Fase {f} (pu)")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")
axs[0].set_title("Tensões trifásicas na barra 890 (nó mais distante)")
axs[-1].set_xlabel("Hora do dia")
axs[-1].set_xticks(range(1, 25))
plt.tight_layout()
plt.savefig("tensoes_890.png", dpi=200)
plt.show()

# opcional: tabela comparativa
tab = sem[["hora"]].copy()
for f in "ABC":
    tab[f"V{f}_sem"] = sem[f"V{f}_pu"]
    tab[f"V{f}_com"] = com[f"V{f}_pu"]
tab.to_csv("tensoes_890_comparativo.csv", index=False)