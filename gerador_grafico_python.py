import matplotlib.pyplot as plt
import mpld3

# Criando um gráfico simples
fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4], [10, 20, 25, 30], marker='o')
ax.set_title("Gráfico Interativo com mpld3")

# Salvando o gráfico como HTML
html = mpld3.fig_to_html(fig)
with open("grafico.html", "w") as f:
    f.write(html)