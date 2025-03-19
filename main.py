import pandas as pd
import matplotlib.pyplot as plt


def countEMA(data, i, N):
    alpha = 2 / (N + 1)
    EMA = 0
    x = -1

    if i - N >= -1:
        Elements = N
    else:
        Elements = i + 1
    y = Elements

    if isinstance(data, pd.DataFrame):
        if i >= len(data):
            return 0
        values = data["Zamkniecie"]
    elif isinstance(data, list):
        if i >= len(data):
            return 0
        values = data

    for value in values:
        x += 1
        if x < i - Elements + 1:
            continue
        elif x > i:
            break
        y -= 1
        EMA = EMA + value * ((1 - alpha) ** y)

    EMA_Denominator = 0
    for i in range(Elements):
        EMA_Denominator = EMA_Denominator + 1 * (1 - alpha) ** i

    EMA = EMA / EMA_Denominator
    return EMA


def Simulate(data, i, sell, buy, N):  # i oznacza indeks w danych od których zaczynamy; N oznacza okres na którym symulujemy
    x = i
    wallet_list = []
    capital = 1000  # posiadana liczba jednostek instrumentu finansowego
    wallet = data['Otwarcie'][i] * capital  # posiadane pieniadze w akcjach lub portfelu
    investing_capital = 0  # kwota w portfelu przeznaczona na inwestycje
    wallet_begin_value = wallet
    while x < i + N:

        if x in sell:
            investing_capital += capital * data['Zamkniecie'][x]
            wallet = investing_capital
            capital = 0
        elif x in buy:
            new_capital = int(investing_capital / data['Otwarcie'][x])
            capital += new_capital
            investing_capital -= new_capital * data['Otwarcie'][x]
            wallet = investing_capital + capital * data['Zamkniecie'][x]
        else:
            wallet = capital*data['Zamkniecie'][x] + investing_capital

        x += 1
        wallet_list.append(wallet)

    data_subset = data.iloc[i:i + N]

    buy_indices_subset = [element for element in buy if i <= element < i + N]

    sell_indices_subset = [element for element in sell if i <= element < i + N]

    plt.subplot(2, 1, 1)

    plt.plot(data_subset['Zamkniecie'])

    plt.title('Wartość podmiotu')

    plt.scatter(buy_indices_subset, [data_subset['Zamkniecie'][i] for i in buy_indices_subset], color='green', label='Punkt kupna')

    plt.scatter(sell_indices_subset, [data_subset['Zamkniecie'][i] for i in sell_indices_subset], color='red', label='Punkt sprzedaży')

    plt.xlabel('Okres [Dni]')

    plt.ylabel('Wartość Zamknięcia')

    plt.legend(loc='best')

    plt.subplot(2, 1, 2)

    profit = wallet - wallet_begin_value
    percent_profit = (profit / wallet_begin_value) * 100

    plt.plot(wallet_list)

    plt.title('Wartość portfela')


    plt.annotate(f'Całkowity zysk: {profit} ({percent_profit:.2f}%)', xy=(0.5, 0.2), xycoords='figure fraction', ha='center', fontsize=10)

    plt.subplots_adjust(bottom=0.5)

    plt.xlabel('Okres inwestycji [Dni]')

    plt.ylabel('Wartość')

    plt.tight_layout()

    plt.show()


data = pd.read_csv("wig20_d.csv")

print(data)
ema_12 = []
ema_26 = []
macd = []
signal = []

for i in range(1000):
    e_12 = countEMA(data, i, 12)
    e_26 = countEMA(data, i, 26)
    ema_12.append(e_12)
    ema_26.append(e_26)
    macd.append(e_12 - e_26)
    signal.append(countEMA(macd, i, 9))

buy_indices = []
sell_indices = []

for i in range(1, len(macd)):
    # Warunek dla sygnału kupna: MACD przekracza SIGNAL w górę
    if macd[i] >= signal[i] and macd[i - 1] < signal[i - 1]:
        buy_indices.append(i)  # dodanie indeksu do listy buy_indices

    # Warunek dla sygnału sprzedaży: MACD przekracza SIGNAL w dół
    elif macd[i] <= signal[i] and macd[i - 1] > signal[i - 1]:
        sell_indices.append(i)  # dodanie indeksu do listy sell_indices

Simulate(data, 200, sell_indices, buy_indices, 50)

Simulate(data, 15, sell_indices, buy_indices, 800)

plt.subplot(2, 1, 1)

plt.plot(data['Zamkniecie'])
plt.title('Wartosc akcji zamknięcia')

plt.subplot(2, 1, 2)

plt.plot(macd, label='MACD')

plt.plot(signal, label='SIGNAL')

plt.scatter(buy_indices, [macd[i] for i in buy_indices], color='green', marker='s', label='buy')

# Dodanie punktów sprzedaży
plt.scatter(sell_indices, [macd[i] for i in sell_indices], color='red', marker='s', label='sell')

plt.legend(loc='best')

plt.title('Wykres MACD i Signal')

plt.tight_layout()
plt.show()
