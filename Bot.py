from abc import abstractmethod
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext



class Bot(object):
    @abstractmethod
    def _set_handlers(self) -> None:
        raise NotImplementedError('Missing _set_handlers')

    @abstractmethod
    def _start(self, update: Updater, context: CallbackContext) -> None:
        raise NotImplementedError('Missing _start fun')

    @abstractmethod
    def _help(self, update: Updater, context: CallbackContext) -> None:
        raise NotImplementedError('Missing _help fun')




class BotRunner(object):
    '''Take a Bot as input and run it'''


    def __init__(self, bot):
        self._bot = bot

        self._initialize_updater()
        self._initialize_dispatcher()
        self._initialize_handlers()
        return

    def _initialize_updater(self):
        self.updater = Updater(self._bot._API, use_context=True)

    def _initialize_dispatcher(self):
        self.dispatcher = self.updater.dispatcher


    def _initialize_handlers(self):
        '''Add all handlers in HandlersDict'''

        for k in self._bot._handlers:
            type_tmp = self._bot._handlers[k]['type']
            fun_tmp = self._bot._handlers[k]['fun']
            handler_tmp = self._handler_hub(handler_type=type_tmp)(k, fun_tmp)

            self.dispatcher.add_handler(handler_tmp)


    def _handler_hub(self, handler_type: str):
        if handler_type == 'command':
            return CommandHandler
        elif handler_type == 'message':
            MessageHandler_wrap = lambda k, fun: MessageHandler(Filters.text & (~Filters.command), fun)
            return MessageHandler_wrap
        else:
            raise NotImplementedError(f'Handler type {handler_type}')

    def run(self):
        '''Run the bot once everything has been initialized'''
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()




