import pandas as pd

df = pd.read_csv('Free_Proxy_List.csv')

results = []
for i, row in df.iterrows():
    ip = row['ip']
    port = row['port']
    results.append(f'http://{ip}:{port}')

with open('list.txt', 'w') as file:
    file.write('\n'.join(results))