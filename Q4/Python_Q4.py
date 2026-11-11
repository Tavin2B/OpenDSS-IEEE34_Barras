import numpy as np
import pandas as pd
import opendssdirect as dss

ARQ = r"C:\Users\Otavi\Downloads\04-Modelo_OpenDSS\Teste Py\ieee34Mod2.dss"   # ajuste o nome/caminho do seu arquivo principal


def simular(com_pv=True):
    """Roda 24 h passo a passo e devolve DataFrame (hora x nó) com tensões em pu."""
    dss.Command("Clear")
    dss.Command(f'Redirect "{ARQ}"')      # o arquivo já faz um Solve diário no final; não atrapalha

    if not com_pv:
        dss.Command("Disable PVSystem.PV")
        dss.Command("Disable Transformer.pv_up")   # no seu arquivo o trafo se chama pv_up

    # recomeça a simulação no instante 0, resolvendo um passo por vez
    dss.Command("Set mode=daily stepsize=1h number=1 hour=0")

    registros = []
    for h in range(24):
        dss.Solution.Solve()
        nos = dss.Circuit.AllNodeNames()
        v_pu = dss.Circuit.AllBusMagPu()
        registros.append(pd.Series(v_pu, index=nos, name=h))

    df = pd.DataFrame(registros)
    df.index.name = "hora"
    return df


def localizar_maximo(df, titulo, excluir=("sourcebus", "trafo_pv")):
    """Acha o (hora, nó) do maior valor do DataFrame e imprime nó, barra, fase e hora."""
    cols = [c for c in df.columns if c.split(".")[0].lower() not in excluir]
    df = df[cols]
    hora = df.max(axis=1).idxmax()
    no = df.loc[hora].idxmax()
    barra, fase = no.split(".")
    fase = {"1": "A", "2": "B", "3": "C"}.get(fase, fase)
    print(f"{titulo}: {df.loc[hora, no]:.5f} | barra {barra} | fase {fase} | hora {hora}")
    return hora, no


# ---------- simulações ----------
v_com = simular(com_pv=True)
v_sem = simular(com_pv=False)

# ---------- 1) maior tensão absoluta ----------
localizar_maximo(v_com, "Maior tensão COM GFV (pu)")
localizar_maximo(v_sem, "Maior tensão SEM GFV (pu)")

# ---------- 2) maior elevação causada pelo GFV ----------
comuns = v_com.columns.intersection(v_sem.columns)   # nós presentes nos dois casos
delta = v_com[comuns] - v_sem[comuns]
hora, no = localizar_maximo(delta, "Maior elevação de tensão devido ao GFV (pu)")

# ---------- tabela com as 10 maiores elevações ----------
top = (delta.stack()
            .sort_values(ascending=False)
            .head(10)
            .rename("delta_pu")
            .reset_index())
top.columns = ["hora", "nó", "delta_pu"]
print("\nTop 10 elevações:")
print(top.to_string(index=False))

# opcional: salvar tudo
v_com.to_csv("tensoes_com_gfv.csv")
v_sem.to_csv("tensoes_sem_gfv.csv")
delta.to_csv("elevacao_gfv.csv")