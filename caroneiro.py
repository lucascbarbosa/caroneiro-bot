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
        self.horarios = np.empty((0,5))
        self.ouvir = True

    def convert_horario(self, horario):
        try:
            horario = int(horario)
            horario = '%d:00'%horario
        except:
            pass

        return horario

    def ajuda(self, update, context):
        channel = update.message.chat.type
        if channel == 'private':
            msg = """O caroneiro te avisa das caronas que te interessam. LEMBRANDO QUE ESTE BOT SÓ FUNCIONA NO PRIVADO. Os comandos são:
            \t/hora [horario_ida] [horario_volta] -> Para informar ou atualizar os horários de ida e volta. Caso queira somente um dos horários, mantenha o outro como 0.
            \tEx: /hora 8 15\n
            \tInforma que os horários de ida e volta desejados são 8:00 e 10:00 respectivamente.\n
            \t/remover -> remove os horários informados."""
            
            update.message.reply_text(msg)
        
    def add_carona(self, update, context):
        print('foo')
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
                # check if this ride is desired by anyone in the database
                for idx in np.where(self.horarios[:,1] == horario)[0]:
                    chat_id = self.horarios[idx,0]
                    msg = f"Aviso de carona de ida de @{username} às {horario} com {vagas} vagas saindo de {local}"
                    context.bot.send_message(chat_id, msg)

            if args[0] == '/volta':
                if username in self.caronas_volta[:,0]:
                    idx = np.where(self.caronas_volta[:,0]==username)[0]
                    self.caronas_volta[idx,1] = horario
                    self.caronas_volta[idx,2] = vagas
                    self.caronas_volta[idx,3] = local
                else:
                    self.caronas_volta = np.append(self.caronas_volta,[[username, horario, vagas,local]],axis=0)
                # check if this ride is desired by anyone in the database
                for idx in np.where(self.horarios[:,2] == horario)[0]:
                    chat_id = self.horarios[idx,0]
                    msg = f"Aviso de carona de volta de @{username} às {horario} com {vagas} vagas saindo de {local}"
                    context.bot.send_message(chat_id, msg)

    def get_set_horario(self, update, context):
        channel = update.message.chat.type
        if channel == 'private':
            args = context.args
            if len(args) > 0:
                horario_ida_inicio = self.convert_horario(args[0])
                horario_ida_fim = self.convert_horario(args[1])
                horario_volta_inicio = self.convert_horario(args[2])
                horario_volta_fim = self.convert_horario(args[3])

                user = update.message.from_user
                username = user.username
                chat_id = str(update.message.chat.id)
                if chat_id in self.horarios[:,0]:
                    idx = np.where(self.horarios[:,0]==chat_id)[0]
                    self.horarios[idx,1] = horario_ida_inicio
                    self.horarios[idx,2] = horario_ida_fim
                    self.horarios[idx,3] = horario_volta_inicio
                    self.horarios[idx,4] = horario_volta_fim
                else:
                    self.horarios = np.append(self.horarios, [[int(chat_id), horario_ida_inicio,horario_ida_fim, horario_volta_inicio, horario_volta_fim]],axis=0)
                
                msg = f"Horários de @{username}:\n"

                if horario_ida_inicio != "0:00" and horario_ida_fim != "0:00":
                    if horario_ida_inicio == horario_ida_fim:
                        msg += f"Ida: {horario_ida_inicio}\n"
                    else:
                        msg += f"Ida: {horario_ida_inicio}-{horario_ida_fim}\n"
                if horario_volta_inicio != "0:00" and horario_volta_fim != "0:00":
                    if horario_volta_inicio == horario_volta_fim:
                        msg += f"Volta: {horario_volta_inicio}\n"
                    else:
                        msg += f"Volta: {horario_volta_inicio}-{horario_volta_fim}\n"
                
            else:
                user = update.message.from_user
                username = user.username
                chat_id = str(update.message.chat.id)
                try:
                    idx = np.where(self.horarios[:,0]==chat_id)[0][0]
                    msg = f"Horários de @{username}:\nIda: {self.horarios[idx,1]}\nVolta: {self.horarios[idx,2]}"
                except: 
                    msg = "Nenhum horário cadastrado no momento"
            update.message.reply_text(msg)
        else:
            pass
    
    def remove_horario(self, update, context):
        channel = update.message.chat.type
        if channel == 'private':
            chat_id = str(update.message.chat.id)
            idx = np.where(self.horarios[:,0]==chat_id)[0][0]
            self.horarios = np.delete(self.horarios,idx,0)
    
    def avisa(self, update, context):
        channel = update.message.chat.type
        print('foo1')
        if channel == 'private':
            self.ouvir = True
            update.message.reply_text("Aviso LIGADO")

    def silencia(self, update, context):
        channel = update.message.chat.type
        print('foo2')
        if channel == 'private':
            self.ouvir = False
            update.message.reply_text("Aviso DESLIGADO.")

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

    dispatcher.add_handler(
            CommandHandler('remover', caroneiro.remove_horario)
        )
    
    dispatcher.add_handler(
            CommandHandler('avisa', caroneiro.avisa)
        )

    dispatcher.add_handler(
            CommandHandler('silencia', caroneiro.silencia)
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

