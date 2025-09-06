import seawolf as sw
import matplotlib.pyplot as plt

# Datos de ejemplo para la gráfica apilada
categorias = ["A", "B", "C", "D"]
valores1 = [5, 7, 3, 4]
valores2 = [2, 3, 4, 1]

fig, ax = plt.subplots()
ax.barh(categorias, valores1, label="Grupo 1")
ax.barh(categorias, valores2, left=valores1, label="Grupo 2")
ax.yaxis.set_visible(True)
show_values(
    ax=ax,
    kind="bar",
    loc="bottom",
    xpad=0.2,
    kw_values={"color": "black", "fontsize": 10, "fontweight": "bold"},
)
set_title(
    ax=ax,
    title="Gráfica de barras apiladas",
    loc="left",
    kw_title={"rotation": 0, "fontweight": "bold", "fontsize": 14, "color": "blue"},
)
set_subtitle(
    ax=ax,  subtitle="Subtítulo de la gráfica", loc="left",
    kw_subtitle={"fontsize": 10, "color": "gray"}
)   
set_legend(
    ax=ax,  title="Grupos", title_loc="left", ncols=2)
