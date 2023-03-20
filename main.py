import websockets
import asyncio
import json
import time
import matplotlib.pyplot as plt
import pandas as pd

fig = plt.figure()


fig.show()



def show_info(data, max_v, min_v): #вывод информации (фрейм с ценами и временем, максимум, минимум)

    fig.clear()
    size = int(data.size / 5)
    ax = fig.add_subplot(111)
    ax.plot(data['Time'], data['Close']) #основной график
    ax.set_xlabel('Время')
    ax.set_ylabel('Цена')
    ax.xaxis.set_major_locator(plt.MaxNLocator(20)) #максимум точек на оси х(для удобства)
    plt.xticks(rotation=90, ha='right')
    ax.plot(max_v['Time'].loc[max_v.index[0]], max_v['Close'].loc[max_v.index[0]], 'o', color = 'green',
            label=f"Максимум {max_v['Close'].loc[max_v.index[0]]} в {max_v['Time'].loc[max_v.index[0]]}")#точка максимума
    ax.plot(min_v['Time'].loc[min_v.index[0]], min_v['Close'].loc[min_v.index[0]], 'o', color = 'red',
            label=f"Минимум {min_v['Close'].loc[min_v.index[0]]} в {min_v['Time'].loc[min_v.index[0]]}")#точка минимума
    ax.plot(data['Time'].loc[data.index[size - 1]], data['Close'].loc[data.index[size - 1]], 'o', color='blue',
            label=f"Текущая стоимость {data['Close'].loc[data.index[size - 1]]}")#точка текущей цены
    if data['Close'].loc[data.index[size - 1]] * 100 / max_v['Close'].loc[max_v.index[0]] <= 99:#условие для разницы 1% вних
        print(f"Разница в {float(100 - (data['Close'].loc[data.index[size - 1]] * 100 / max_v['Close'].loc[max_v.index[0]])):.2f}%"
              f" достигнута в {data['Time'].loc[data.index[size - 1]]} ")
    elif data['Close'].loc[data.index[size - 1]] * 100 / min_v['Close'].loc[min_v.index[0]] >= 101:#условие для разницы 1% вверх
        print(f"Разница в {float((data['Close'].loc[data.index[size - 1]] * 100 / min_v['Close'].loc[min_v.index[0]]) - 100):.2f}%"
              f" достигнута в {data['Time'].loc[data.index[size - 1]]} ")
    ax.legend()
    fig.canvas.draw()
    plt.pause(0.5)


async def main():
    url = "wss://stream.binance.com:9443/stream?streams=ethusdt@miniTicker" #ссылка для получения информации
    async with websockets.connect(url) as client:
        eth = pd.DataFrame(columns=['Time', 'Open', 'Close', 'High', 'Low'])#колонки фрейма
        max_v = pd.DataFrame(columns=['Time', 'Open', 'Close', 'High', 'Low'])
        min_v = pd.DataFrame(columns=['Time', 'Open', 'Close', 'High', 'Low'])
        while True:
            data = json.loads(await client.recv())['data']#загрузка данных
            e_time = time.localtime(data['E'] // 1000)
            e_time = f"{e_time.tm_hour}:{e_time.tm_min}:{e_time.tm_sec}"#форматирование времени
            tmp = pd.DataFrame([{'Time':e_time, 'Open':float(data['o']), 'Close':float(data['c']),
                                 'High':float(data['h']), 'Low':float(data['l'])}])#временная ячейка с последней ценой
            size = int(eth.size / 5)
            if size >= 3600:
                eth.drop(index = eth.index[0], axis=0, inplace=True)#удаление самой старой ячейки
            eth = pd.concat([eth, tmp], ignore_index=True, axis=0)#добавление новой
            size += 1
            if size == 1:
                max_v = pd.concat([max_v, tmp], ignore_index=True, axis=0)
                min_v = max_v
            elif max_v['Close'].loc[max_v.index[0]] <= tmp['Close'].loc[eth.index[0]]:#поиск максимума
                max_v = tmp
            elif min_v['Close'].loc[min_v.index[0]] >= tmp['Close'].loc[tmp.index[0]]:#поиск минимума
                min_v = tmp
            show_info(eth, max_v, min_v)#вывод на экран


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())