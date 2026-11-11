import pandas as pd
import matplotlib.pyplot as plt
import opendssdirect as dss

ARQ = r"C:\Users\Otavi\Downloads\04-Modelo_OpenDSS\ieee34Mod2.dss"   # ajuste


def simular(com_pv=True):
    dss.Command("Clear")
    dss.Command(f'Redirect "{ARQ}"')
    if not com_pv:
        dss.Command("Disable PVSystem.PV")
        dss.Command("Disable Transformer.pv_up")

    # reinicia do instante 0 e zera os registradores (o Redirect já resolveu 24 h)
    dss.Command("Set mode=daily stepsize=1h number=1 hour=0")
    dss.Command("Reset Meters")

    perdas_kw = []
    for h in range(24):
        dss.Solution.Solve()
        p_w, _ = dss.Circuit.Losses()      # [W, var] de todo o circuito
        perdas_kw.append(p_w / 1000)

    # registrador do medidor, para conferir
    dss.Meters.First()
    reg = dict(zip(dss.Meters.RegisterNames(), dss.Meters.RegisterValues()))
    return pd.Series(perdas_kw, index=range(1, 25)), reg.get("Losses kWh")


sem, reg_sem = simular(com_pv=False)
com, reg_com = simular(com_pv=True)

# como o passo é de 1 h, kW médio no passo = kWh
e_sem, e_com = sem.sum(), com.sum()
print(f"Perdas em 24 h SEM GFV: {e_sem:.1f} kWh")
print(f"Perdas em 24 h COM GFV: {e_com:.1f} kWh")
print(f"Variação: {e_com - e_sem:+.1f} kWh ({(e_com/e_sem - 1)*100:+.1f} %)")
print(f"(registrador Losses kWh do M1: sem={reg_sem}, com={reg_com})")

# gráfico
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(sem.index, sem.values, "o-", label=f"Sem GFV ({e_sem:.0f} kWh)")
ax.plot(com.index, com.values, "s-", label=f"Com GFV ({e_com:.0f} kWh)")
ax.set_xlabel("Hora do dia")
ax.set_ylabel("Perdas de potência ativa (kW)")
ax.set_title("Perdas ativas do sistema em 24 h")
ax.set_xticks(range(1, 25))
ax.grid(alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig("perdas_24h.png", dpi=200)
plt.show()

pd.DataFrame({"sem_GFV_kW": sem, "com_GFV_kW": com,
              "delta_kW": com - sem}).to_csv("perdas_comparativo.csv")