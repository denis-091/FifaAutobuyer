import fut
import os
from datetime import datetime
import time

cookieFile = os.getcwd() + '/cookies.txt'
tokenFile = os.getcwd() + '/token.txt'

player = 225663  # golovin https://docs.google.com/spreadsheets/d/1ufH7aLh6oUh4q_M4bRP-vpbt6YFclrfeNAlkE7z01iU/edit#gid=0
price = '700' # Цена покупки
sellPrice = 1000 # цена продажи
buy_now = 1100 # цена buy_now
duration = 3600 # время продажи, по стандарту один час
finishTrade = 50000 # сумма прерывания скрипта


def connect():
    session = fut.Core('login', 'password', 'secret')
    print('Залогинился успешно')
    session.token_file = tokenFile
    print('Активировал токен')
    session.cookies_file = cookieFile
    print('Активировал куки')
    return session


def sell(session, id='', tradeId=''):
    if (tradeId != ''):
        if str(session.tradeStatus(tradeId)) == 'None' or str(session.tradeStatus(tradeId)) == 'expired':
            print('Отправил в список продаж')
            session.sendToTradepile(id)
    if len(session.unassigned()) > 0:
        for i in session.unassigned():
            if str(i['tradeState']) == 'None' or str(i['tradeState']) == 'expired':
                print('Отправил в список продаж, из аукциона')
                session.sendToTradepile(id)
    if len(session.tradepile()) > 0:
        for i in session.tradepile():
            if str(i['tradeState']) == 'None' or str(i['tradeState']) == 'expired':
                print('Выставил на продажу за ' + price + 'монет')
                session.sell(i['id'], sellPrice, buy_now, duration)


def startWork(session):
    try:
        session.keepalive()
        sell(session)
        currentTime = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
        if len(session.tradepile()) == 30:
            print('Переполнен список продаж , ожидаю 30 секунд, текущее время - ' + datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"))
            session.keepalive()
            time.sleep(30)
            session.keepalive()
            session.saveSession()
            sell(session)
            startWork(session)
        if session.credits < int(price):
            print('Недостаточно денег, ожидаю 30 секунд, текущее время - ' + datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"))
            session.keepalive()
            time.sleep(30)
            session.keepalive()
            session.saveSession()
            sell(session)
            startWork(session)
        print(str(
            'Поиск слотов,текущее количество монет ' + str(
                session.credits) + ' время запуска - ' + currentTime))
        items = session.search('player', 'gold', '', '', player, '', price, '', '', '', '', '', '', '', '', '', '',
                               50)
        currentItems = []
        if len(items) > 0:
            for i in items:
                if len(session.tradepile()) == 30:
                    print('Переполнен список продаж , ожидаю 30 секунд, текущее время - ' + datetime.strftime(
                        datetime.now(), "%Y.%m.%d %H:%M:%S"))
                    session.keepalive()
                    time.sleep(30)
                    session.keepalive()
                    session.saveSession()
                    sell(session)
                    break
                if session.credits < int(price):
                    print('Недостаточно денег, ожидаю 30 секунд, текущее время - ' + datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"))
                    session.keepalive()
                    time.sleep(30)
                    session.keepalive()
                    session.saveSession()
                    sell(session)
                    break
                tradeId = i['tradeId']
                idPlayer = i['id']
                currentBid = i['currentBid']
                if currentItems.count(tradeId) == 0 and int(currentBid) == 0:
                    tradeState = i['tradeState']
                    if tradeState == 'active':
                        session.sendToWatchlist(tradeId)
                        session.bid(tradeId, int(price))
                        session.saveSession()
                        currentItems.append(tradeId)
                        print('Покупаю - ' + price + ' остаток монет ' + str(session.credits))
                        sell(session, idPlayer, tradeId)
                        continue
                else:
                    session.keepalive()
                    continue
        else:
            print('Не нашел, отдыхаю 15 сек, ' + datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"))
            sell(session)
            session.keepalive()
            session.saveSession()
            startWork(session)
        if session.credits < finishTrade:
            startWork(session)
        else:
            print('Закончил')

    except BaseException:
        print('Повторная попытка через 30 секунд')
        time.sleep(30)
        session = connect()
        startWork(session)


session = connect()
startWork(session)
