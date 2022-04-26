# -*- coding: utf-8 -*-

import threading
import datetime
import time

import requests
import json
import lxml.html

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters

import pretty_errors


"""
Xpath para pagina eusica
titutlo:
h1,class="font-product-title"
1) "//h1[@class='font-product-title']/text()"

Dispo:
//div[@class="form-row"//label/text
1) "//div[@class='form-row']//div[@class='field']/span[not(contains(@class,'hide'))]/span/text()"
2) "//div[@class='form-row']//div[@class='field']/span[@class='stock-row']/span/text()"

Precio
span,class="lbl-price"
1) "//div[@class='form-row']//span[@class='lbl-price']/text()"
"""
"""
Xpath para pagina panini:

Titulo:
1) "//div[@class='product-price']/../h1[contains(@class,'product-title')]/text()"

Dispo:
2) "//div[@class='addto']/*/text()"

Precio
1) "//div[@class='product-price']/span/text()"

"""


def get_info_from_html(tree, x_path: str):
    pass
    ejemplo = tree.xpath(x_path)
    # breakpoint()
    return ''.join(ejemplo)


def read_prod_page(products, x_paths):
    all_results = []
    for page in products:
        respuesta = requests.get(page)
        tree = lxml.html.fromstring(respuesta.content)
        time.sleep(2)

        results = {
            item: get_info_from_html(tree, value)
            for (item, value) in x_paths.items()
        }
        all_results.append(results)

    return all_results


def check_page(page_prods:str,page_xPaths:str):
    with open('./pages.json', 'r') as json_file:
        json_data = json.load(json_file)

    products = json_data[page_prods]
    x_paths = json_data[page_xPaths]

    return read_prod_page(products, x_paths)



class notifyBot:
    def __init__(self, name, token):
        self.bot_name = name
        self.token = token
        self.bot = telegram.Bot(token=self.token)
        # mi usuario:
        self.user = 1470416228

    def check_prods(self):
        lineas = check_page("eusica_prods","eusica_xPaths") + check_page("Panini_prods","Panini_xPaths")
        #breakpoint()
        for result in lineas:
            msj = f"{result['titulo']}\nDispo: {result['dispo']}\nPrecio: {result['precio']}"
            print(result['dispo'].replace('\Xa0',''))

            if result['dispo'] == 'Disponible' or 'Comprar' in result['dispo']:
                self.bot.send_message(chat_id=self.user,
                                      text=msj)
                time.sleep(1)

    def notify_thread(self):
        self.bot.send_message(self.user,text='thread-init')
        self.check_prods()
        threading.Timer(90, self.notify_thread  ).start()

    def greet_user(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="hola " +
                                 update._effective_user.first_name)


    @staticmethod
    def check_avai(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='revisando...')

        lineas = check_page("eusica_prods","eusica_xPaths") + check_page("Panini_prods","Panini_xPaths")

        for result in lineas:
            msj = f"{result['titulo']}\nDispo: {result['dispo']}\nPrecio: {result['precio']}"
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=msj)
            time.sleep(1)

    def init_bot(self):
        updater = Updater(token=self.token, use_context=True)
        dispatcher = updater.dispatcher

        # bot = telegram.Bot(token=self.token)
        print(self.bot.get_me())
        ## commands
        start_handler = CommandHandler('start', notifyBot.greet_user)

        ## Raw text handler_func
        check_handler = CommandHandler('check', notifyBot.check_avai)

        dispatcher.add_handler(start_handler)  # 1
        dispatcher.add_handler(check_handler)  # 2

        updater.start_polling()


def main(bot_name):

    with open('./../token.json', 'r') as json_file:
        bots = json.load(json_file)

    notify_bot = notifyBot(bot_name, bots[bot_name])
    notify_bot.init_bot()

    notify_bot.notify_thread()

if __name__ == '__main__':

    main('pascal')
    #print(check_panini())
