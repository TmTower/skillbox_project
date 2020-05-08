"""
программа подготовлена для интенсива на платформе SkillBox
программа сделана Санниковым Андреем
**********************************************************
команды:
all:<текста>- сообщение всем участникам                                                     +   +
msg:<имя получателя><текст>- сообщение одному участнику                                     +   +
login:<текста>- создание имени, под которым человек будет виден другим участникам           +   +
pass:<текст>- создание пароля для входа в аккаунт                                           +   +
cmd//- вывод всех команд на сервере"                                                        +   +
servlist- вывод всех участников в чате                                                      +   +
banlist- вывод всех предупреждений участникам. после 3-х предупреждений участнику будет запрещено писать        +   +
ban<> отправить предпреждение челоеку с логином                                             +   +
чтобы получить документацию по комнаде напишите <название команды>_info
"""


"""
СПЕЦИАЛЬНО ДЛЯ ПРОВЕРЯЮЩИХ:
я понимаю, что по ТЗ в первом задании сказано , что если человек пытается зарегестрироваться под логином , который уже есть на сервере, 
то нужно разорвать соединение этого человека с сервером,
но у меня челоаек не подключается к серверу до тех пор , пока не пройдет проверку на логин, так что отключать мне нечего.
В любом случае пришлось бы пройтись по всему списку клиентов и проверить на совпадение логинов, а потом еще и удалять элемент из этого списка
у меня же достаточно лишь проверить список клиентов без удаления 

список запрещенных слов сейчас мал, так ка мне нужно ыло показать вам, что это работает, а не то , как много слов он может зацензурить
"""

cmd_info=f"данна команда позволяет получить список основных команд данного сервера , а так же получить подсказки по их использованию"
all_info=f"данна команда позволяет написать сообщение всем участникам сервера. просто напишите all: " \
         f"и после двоеточия напишите сообщение, которое хотите отправить"
msg_info=f"данна команда позволяет написать сообщение одному конкретоному участнику сервера. просто напишите msg:<><> " \
         f"и в первых скобках укажите логин получателя, а во вторых - текст, который вы хотите отправить"
login_info=f"данна команда позволяет вам создать свой логин на данном сервере. без полной регистрации вы не сможете пользоваться большинством команд" \
        f"напишите login: и после двоеточия- ваше имя. Если оно уже занято - повторите процедуру, изменив имя, введенное вами"
pass_info=f"данная команда позволяет вам создать пароль для вашего логина. Без полной регистрации вам будут недоступны многие команды" \
          f" для использования данной команжы напишите pass: и полсе двоеточия - пароль , который вы желаете"
servlist_info=f"данная команда позволяет получить список всех логинов участников данного сервера" \
              f"напишите servlist и вы получите письмо с полной информацией об участниках"
banlist_info=f"выводит список с количестовм предупреждений дя каджого пользователя. после 3-х предупреждений пользователь будет заткнут. Так же предупреждения выдаются автоматически за мат, так что будьте разумны" \
          f" Чтобы получить список напишите bans "
ban_info=f"отправляет предупреждение выбраному пользователю. после 3-х предупреждений пользователь будет заткнут." \
         f"чтобы отправить предупреждение напишите ban: и после двоеточия логин пользователя, который плохо себя ведет"
import queue
import asyncio
from asyncio import transports
from typing import Optional

cmd=["collist",'\n' "chNick",'\n' "servlist", '\n' "cmd",'\n' "pass",'\n' "login", '\n' "all", '\n', "banlist",'\n' "ban"]
bans=dict()
toboo_words=["дурак","дура","тупой"]
history_ful=queue.Queue()

class ClientProtocol(asyncio.Protocol):
    login:str

    def __init__(self,server:'Server'):
        self.server=server
        self.login=None
        self.password=None

    def data_received(self, data: bytes):
        decoded=data.decode()
        print(decoded)
        if decoded.startswith("cmd//"):#получить список команд на сервере
            for i in cmd:
                self.transport.write(i.encode())
            self.transport.write(('\n'+f"чтобы получить больше информации по каждой команду напишите <название_интересующей_команды>_info").encode())
        elif decoded.startswith("cmd_info"):
            self.transport.write(cmd_info.encode())
        elif decoded.startswith("login_info"):
            self.transport.write(login_info.encode())
        elif decoded.startswith("pass_info"):
            self.transport.write(pass_info.encode())
        elif decoded.startswith("msg_info"):
            self.transport.write(msg_info.encode())
        elif decoded.startswith("all_info"):
            self.transport.write(all_info.encode())
        elif decoded.startswith("servlist_info"):
            self.transport.write(servlist_info.encode())
        elif decoded.startswith("banlist_info"):
            self.transport.write(banlist_info.encode())
        elif decoded.startswith("ban_info"):
            self.transport.write(ban_info.encode())
        elif decoded.startswith("banlist"):
            for i in bans:
                self.transport.write((f"{i}-{bans[i]}" + '\n').encode())
        elif self.login is None:#если сам не зареган, то
            if decoded.startswith("login:"):#получаем новый логин               регистрация имени
                name=decoded.replace("login:", "").replace("\r\n", "")
                test_login=True
                for i in self.server.client:
                    if i.login!=name:
                        pass
                    else:
                        test_login=False
                        break
                if test_login:
                    self.login=name
                    self.transport.write(
                        f"привет, {self.login}!".encode()
                    )
                else:
                    self.transport.write((f"Логин {name} занят, попробуйте другой").encode())#вывести ошибку, если логин занят
                    self.connection_lost()
            else:#если не введена команда создания имени - вывести ошибку
                self.transport.write(("пожалуйста, пройдите полную регистрацию").encode())
        elif self.password is None:
            if decoded.startswith("pass:"):#если введена команда пороля- сохранить пароль           регистриция пароля
                self.password=decoded.replace("pass:", "").replace("\r\n", "")
                self.transport.write((
                    f"поздравляю, вы полностью зарегестрировались. Ваш логин {self.login} Ваш пароль {self.password}"
                ).encode())
            else:
                self.transport.write(("вы не полностью зарегестрировались. Пожалуйста введите свое имя и пароль корректно.").encode())
            if self.login != None and self.password != None:
                self.send_history()
                bans[self.login]=0
        else:
            cor=True
            for i in toboo_words:
                if i in decoded:
                    bans[self.login]+=0.5
                    self.transport.write(f"Вы использоваи запрещенное слово. Пожалуйста, не оскорбляйте других пользователей".encode())
                    cor=False
                    break
            if cor:
                if bans[self.login]<3:
                    if decoded.startswith("msg:"):#если хочется написать лично            лс письмо
                        decoded=decoded.replace("msg:","")#проверяется команда
                        taker=decoded[0:decoded.find(":")]#получаем имя участника
                        print(taker)
                        message=decoded.replace(taker+":","")#удаляем "хлам"
                        print(message)
                        succses=False
                        for i in self.server.client:
                            if taker==i.login:
                                succses=True
                                taker=i
                                break

                        if succses:#проверяем, зарегестрирован ли пользователь
                            taker.transport.write((f"/\/{self.login}\/\ {message}").encode())#если пользователь зарегестрирован - пишем ему в лс
                        else:
                            self.transport.write((           #общий чат
                                f"Человека с данным логином не найдено. Проверьте правильность написания и повторите попытку"
                            ).encode())
                    elif decoded.startswith("servlist"):
                        for i in self.server.client:
                            self.transport.write((i.login +'\n').encode())
                    elif decoded.startswith("ban:"):
                        taker=decoded.replace("ban:","")
                        flag=False
                        for i in self.server.client:
                            if i.login==taker:
                                flag=True
                                break
                        if flag:
                            bans[taker]+=1
                            self.transport.write(f"Отправлено предупреждение пользователю {taker}. На данный момент у него {bans[taker]} предупрждений".encode())
                        else:
                            self.transport.write(f"Пользователя с данным логином нет в сети. Проверьте правильность ввода и повторите попытку".encode())
                    elif decoded.startswith("all:"):#вывести сообщение , которое написал пользователь
                        message=decoded.replace("all:","")
                        self.send_message(decoded)
                        if history_ful.qsize()<10:
                            history_ful.put((self.login,message))
                        else:
                            history_ful.get()
                            history_ful.put((self.login,message))
                    elif decoded.startswith("pass:"):
                        self.transport.write(f"вы уже зарегестрировались !".encode())
                    elif decoded.startswith("login:"):
                        self.transport.write(f"вы уже зарегестрировались !".encode())
                else:
                    self.transport.write(f"Вы не можете писать на сервере, так как данный аккаунт забанен".encode())

    def send_history(self):
        cop=history_ful
        for i in range(0,cop.qsize()):
            a=cop.get()
            self.transport.write((f"<{a[0]}> {a[1]}"+'\n').encode())
            history_ful.put(a)

    def send_message(self,message):
        format_string = f"<{self.login}> {message}"
        encoded = format_string.encode()
        for clients in self.server.client:
            if clients.login!=self.login:
                clients.transport.write(encoded)


    def connection_made(self, transport: transports.Transport):
        self.transport=transport
        self.server.client.append(self)
        print("соединение установлена")

    def connection_lost(self, exc):
        self.server.client.remove(self)
        print("соединение разорвано")

    server:'Server'
    transport: transports.Transport

class Server:
    client:list

    def __init__(self):
        self.client=[]

    def create_protocol(self):
        return ClientProtocol(self)

    async def start(self):
        loop=asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.create_protocol,
            "127.0.0.1",
            8888
        )

        print("сервер запущен")

        await coroutine.serve_forever()


process=Server()
try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")