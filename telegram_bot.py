from telebot import TeleBot
from envparse import Env
from model_db import BotInfo, db

'''
LINK = t.me/Home_Work_15_Bot
По запросу /order бот просит оставить сообщение заявки. После чего записывает все нужнные данные в таблицу БД 
'''
env = Env()
TOKEN = env.str('TOKEN')

bot = TeleBot(token=TOKEN)


def save_message(message):
    info_add = BotInfo(nickname=message.chat.username, id_chat=message.chat.id, message=message.text)
    db.session.add(info_add)
    db.session.flush()
    db.session.commit()
    bot.reply_to(message, 'Ваша заявка принята в обработку, с Вами скоро свяжутся!')


@bot.message_handler(commands=['order'])
def order_message(message):
    bot.reply_to(message, 'Для оформленния заявки - введите сообщенние')
    bot.register_next_step_handler(message, save_message)

bot.polling()