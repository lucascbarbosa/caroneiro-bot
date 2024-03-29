from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import numpy as np
import asyncio

class Caroneiro(object):
    def __init__(self):
        self.caronas_ida = np.empty((0,4))
        self.caronas_volta = np.empty((0,4))
        self.horarios = np.empty((0,5))
        self.ouvir = True

    def convert_horario_string(self, horario):
        try:
            horario = int(horario)
            horario_string = '%02d:00'%horario
            return horario_string
        except:
            return horario
    
    async def ajuda(self, update, context):
        channel = update.message.chat.type
        if channel == 'private':
            msg = """O caroneiro te avisa das caronas que te interessam. LEMBRANDO QUE ESTE BOT SÓ FUNCIONA NO PRIVADO. Os comandos são:
            \t/hora [ida/volta] [horario de ida/volta inicial] [horario de ida/volta final] -> Informa ou atualiza a janela de horários de ida ou volta. Caso queira somente um horário, digite o mesmo horário duas vezes. Para visualizar os horários, digite somente /hora.
            \tEx: /hora ida 8 8 para IDA às 8:00
            \tEx: /hora volta 15 16 para VOLTA entre 15:00 e 16:00
            \t/remover [ida/volta]-> remove os horários de ida ou volta informados. Caso não seja informado o trajeto, ambos os horários serão removidos.
            \tEx: /remover ida para remover horários de IDA.
            \t/avisa -> HABILITA o bot para avisar de caronas.
            \t/silencia -> SILENCIA o bot."""
            await update.message.reply_text(msg)
        
    async def add_carona(self, update, context):
        args = update.message.text.split()
        if len(args) > 1:
            horario = self.convert_horario_string(args[1])
            vagas = args[2]
            local = args[3]
            user = update.message.from_user
            username = user.username
            # msg_carona = f'@{username} - {horario} de {local} ({vagas} vagas)'
            # await update.message.reply_text(msg_carona)
            if args[0] == '/ida':
                if username in self.caronas_ida[:,0]:
                    idx = np.where(self.caronas_ida[:,0]==username)[0]
                    self.caronas_ida[idx,1] = horario
                    self.caronas_ida[idx,2] = vagas
                    self.caronas_ida[idx,3] = local
                else:
                    self.caronas_ida = np.append(self.caronas_ida,[[username, horario, vagas,local]],axis=0)
                # check if this ride is desired by anyone in the database
                for idx in np.where((self.horarios[:,1]<=horario)&(self.horarios[:,2]>=horario))[0]:
                    chat_id = self.horarios[idx,0]
                    msg = f"IDA: Carona de @{username} às {horario} com {vagas} vagas saindo de {local}"
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
                for idx in np.where((self.horarios[:,3]<=horario)&(self.horarios[:,4]>=horario))[0]:
                    chat_id = self.horarios[idx,0]
                    msg = f"VOLTA: Carona de @{username} às {horario} com {vagas} vagas voltando para {local}"
                    context.bot.send_message(chat_id, msg)

    async def get_set_horario(self, update, context):
        channel = update.message.chat.type
        if channel == 'private':
            args = context.args
            if len(args) > 0: # set hora
                trajeto = args[0]
                user = update.message.from_user
                username = user.username
                chat_id = str(update.message.chat.id)
                if chat_id in self.horarios[:,0]:
                    idx = np.where(self.horarios[:,0]==chat_id)[0]
                    if trajeto == "ida":
                        horario_ida_inicio = self.convert_horario_string(args[1])
                        try:
                            horario_ida_fim = self.convert_horario_string(args[2])
                        except:
                            horario_ida_fim  = horario_ida_inicio
                        self.horarios[idx,1] = horario_ida_inicio
                        self.horarios[idx,2] = horario_ida_fim
                
                    elif trajeto == "volta":
                        horario_volta_inicio = self.convert_horario_string(args[1])
                        try:
                            horario_volta_fim = self.convert_horario_string(args[2])
                        except:
                            horario_volta_fim  = horario_volta_inicio
                        self.horarios[idx,3] = horario_volta_inicio
                        self.horarios[idx,4] = horario_volta_fim

                else:
                    if trajeto == "ida":
                        horario_ida_inicio = self.convert_horario_string(args[1])
                        try:
                            horario_ida_fim = self.convert_horario_string(args[2])
                        except:
                            horario_ida_fim  = horario_ida_inicio
                        self.horarios = np.append(self.horarios, [[int(chat_id), horario_ida_inicio,horario_ida_fim, "0:00", "0:00"]],axis=0)
                    if trajeto == "volta":
                        horario_volta_inicio = self.convert_horario_string(args[1])
                        try:
                            horario_volta_fim = self.convert_horario_string(args[2])
                        except:
                            horario_volta_fim  = horario_volta_inicio
                        self.horarios = np.append(self.horarios, [[int(chat_id), "0:00", "0:00", horario_volta_inicio, horario_volta_fim]],axis=0)

                if trajeto == "ida":
                    msg = f"Horários de @{username} para IDA: "
                    if horario_ida_inicio == horario_ida_fim:
                        msg += f"{horario_ida_inicio}"
                    else:
                        msg += f"{horario_ida_inicio}-{horario_ida_fim}"
                
                elif trajeto == "volta":
                    msg = f"Horários de @{username} para VOLTA: "
                    if horario_volta_inicio == horario_volta_fim:
                        msg += f"{horario_volta_inicio}"
                    else:
                        msg += f"{horario_volta_inicio}-{horario_volta_fim}"

                else:
                    msg = "Erro. Informe o trajeto correto."
            
            else: # get hora
                user = update.message.from_user
                username = user.username
                chat_id = str(update.message.chat.id)
                try:
                    idx = np.where(self.horarios[:,0]==chat_id)[0][0]
                    horario_ida_inicio = self.horarios[idx,1]
                    horario_ida_fim = self.horarios[idx,2]
                    horario_volta_inicio = self.horarios[idx,3]
                    horario_volta_fim = self.horarios[idx,4]
                    if (horario_ida_inicio != "0:00" and horario_ida_fim != "0:00") or (horario_volta_inicio != "0:00" and horario_volta_fim != "0:00"):  
                        msg = f"Horários de @{username}:\n"
                        if horario_ida_inicio != "0:00" and horario_ida_fim != "0:00":
                            if horario_ida_inicio == horario_ida_fim:
                                msg  += f"IDA: {horario_ida_inicio}\n"
                            else:
                                msg  += f"IDA: {horario_ida_inicio}-{horario_ida_fim}\n"
                        
                        if horario_volta_inicio != "0:00" and horario_volta_fim != "0:00":
                            if horario_volta_inicio == horario_volta_fim:
                                msg  += f"VOLTA: {horario_volta_inicio}\n"
                            else:
                                msg  += f"VOLTA: {horario_volta_inicio}-{horario_volta_fim}\n"
                    else:
                        msg = "Nenhum horário cadastrado no momento"
                except: 
                    msg = "Nenhum horário cadastrado no momento"
            await update.message.reply_text(msg)
        else:
            pass

    async def remove_horario(self, update, context):
        channel = update.message.chat.type
        if channel == 'private':
            args = context.args
            if len(args) > 0:
                trajeto = args[0]
                chat_id = str(update.message.chat.id)
                idx = np.where(self.horarios[:,0]==chat_id)[0][0]
                if trajeto == "ida":
                    self.horarios[idx,1] = "0:00"
                    self.horarios[idx,2] = "0:00"
                    msg = "Horário de IDA removido."
                elif trajeto == "volta":
                    self.horarios[idx,3] = "0:00"
                    self.horarios[idx,4] = "0:00"        
                    msg = "Horário de VOLTA removido."
            else:
                chat_id = str(update.message.chat.id)
                idx = np.where(self.horarios[:,0]==chat_id)[0][0]
                self.horarios[idx,1] = "0:00"
                self.horarios[idx,2] = "0:00"
                self.horarios[idx,3] = "0:00"
                self.horarios[idx,4] = "0:00"        
                msg = "Horários de IDA e VOLTA removidos."

            await update.message.reply_text(msg)

    async def avisa(self, update, context):
        channel = update.message.chat.type
        if channel == 'private':
            self.ouvir = True
            await update.message.reply_text("Aviso LIGADO")

    async def silencia(self, update, context):
        channel = update.message.chat.type
        if channel == 'private':
            self.ouvir = False
            await update.message.reply_text("Aviso DESLIGADO.")


if __name__ == '__main__':
    print("press CTRL + C to cancel.")
    # Create the Updater and pass it your bot's token.
    token = '5725480727:AAEi6lXGnvJzQMPm0R76Uss8HWtdhnmWdFY'
    
    caroneiro = Caroneiro()

    # initiliaze class that contains the callback functions for caronas
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(
            CommandHandler('help', caroneiro.ajuda)
        )

    application.add_handler(
            MessageHandler(filters.Regex(r'/ida'), caroneiro.add_carona)
        )
    
    application.add_handler(
            MessageHandler(filters.Regex(r'/volta'), caroneiro.add_carona)
        )
    
    application.add_handler(
            CommandHandler('hora', caroneiro.get_set_horario)
        )

    application.add_handler(
            CommandHandler('remover', caroneiro.remove_horario)
        )
    
    application.add_handler(
            CommandHandler('avisa', caroneiro.avisa)
        )

    application.add_handler(
            CommandHandler('silencia', caroneiro.silencia)
        )

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)



