from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
import numpy as np

class Caroneiro(object):
    def __init__(self):
        self.caronas_ida = np.empty((0,4))
        self.caronas_volta = np.empty((0,4))
        self.horarios = np.empty((0,3))

    def convert_horario(self, horario):
        try:
            horario = int(horario)
            horario = '%d:00'%horario
        except:
            pass

        return horario

    def ajuda(self, update, context):
        update.message.reply_text("Your Message")
    
    def add_carona(self, update, context):
        args = update.message.text.split()
        if len(args) > 1:
            horario = self.convert_horario(args[1])
            vagas = args[2]
            local = args[3]
            user = update.message.from_user
            username = user.username
            # msg_carona = f'@{username} - {horario} de {local} ({vagas} vagas)'
            # update.message.reply_text(msg_carona)
        
            if args[0] == '/ida':
                if username in self.caronas_ida[:,0]:
                    idx = np.where(self.caronas_ida[:,0]==username)[0]
                    self.caronas_ida[idx,1] = horario
                    self.caronas_ida[idx,2] = vagas
                    self.caronas_ida[idx,3] = local
                else:
                    self.caronas_ida = np.append(self.caronas_ida,[[username, horario, vagas,local]],axis=0)
            
            if args[0] == '/volta':
                if username in self.caronas_volta[:,0]:
                    idx = np.where(self.caronas_volta[:,0]==username)[0]
                    self.caronas_volta[idx,1] = horario
                    self.caronas_volta[idx,2] = vagas
                    self.caronas_volta[idx,3] = local
                else:
                    self.caronas_volta = np.append(self.caronas_volta,[[username, horario, vagas,local]],axis=0)

    def get_set_horario(self, update, context):
        channel = update.message.chat.type
        if channel == 'private':
            args = context.args
            if len(args) > 0:
                horario_ida = self.convert_horario(args[0])
                horario_volta = self.convert_horario(args[1])
                user = update.message.from_user
                username = user.username
                if username in self.horarios[:,0]:
                    idx = np.where(self.horarios[:,0]==username)[0]
                    self.horarios[idx,1] = horario_ida
                    self.horarios[idx,2] = horario_volta
                else:
                    self.horarios = np.append(self.horarios, [[username, horario_ida, horario_volta]],axis=0)
                msg = f"Horários de @{username}:\nIda: {horario_ida}\nVolta: {horario_volta}"
            else:
                user = update.message.from_user
                username = user.username
                idx = np.where(self.horarios[:,0]==username)[0][0]
                msg = f"Horários de @{username}:\nIda: {self.horarios[idx,1]}\nVolta: {self.horarios[idx,2]}"
            update.message.reply_text(msg)
        else:
            pass

def main():
    
    # Create the Updater and pass it your bot's token.
    token = '5725480727:AAEi6lXGnvJzQMPm0R76Uss8HWtdhnmWdFY'
    
    caroneiro = Caroneiro()

    # initiliaze class that contains the callback functions for caronas
    updater = Updater(token=token, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(
            CommandHandler('help', caroneiro.ajuda)
        )

    dispatcher.add_handler(
            MessageHandler(Filters.regex(r'/ida'), caroneiro.add_carona)
        )
    
    dispatcher.add_handler(
            MessageHandler(Filters.regex(r'/volta'), caroneiro.add_carona)
        )

    dispatcher.add_handler(
            CommandHandler('hora', caroneiro.get_set_horario)
        )
    

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    print("press CTRL + C to cancel.")
    main()

