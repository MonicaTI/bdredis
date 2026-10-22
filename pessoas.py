for i in range(5):
    globals()[f'pessoa{i}'] = f'pessoa{i}'

# Acessando as variáveis
for i in range(5):
    print(globals()[f'pessoa{i}'])
