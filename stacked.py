
import pandas as pd
import matplotlib.pyplot as plt

a = [3,5,4,2,1]
b = [3,4,5,2,1]
c = [3,5,4,6,1]

df = pd.DataFrame({'a' : a,'a2' : b, 'c' : c})
ax = df.plot.barh(stacked=True, color = {'a':"red","a2":"red","c":"yellow"});

# ax.figure.set_size_inches(6,6)
# ax.set_title("My ax title")

ax.legend(loc='upper right')
plt.show()
