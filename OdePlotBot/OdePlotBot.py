"""
Simple Bot to generate plot of functions

Usage:
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sympy as sp
from copy import deepcopy, copy
from scipy.integrate import odeint

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


# --------------------------------------------------------------
# ------------------------- GLOBAL VAR -------------------------
# --------------------------------------------------------------

PLOT_PATH = 'C:\\Users\\pc\\workspace\\TelegramBot\\OdePlotBot\\plot'
Y0 = 0
X_INTERVAL = (0,1)


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)




def check_ode(ode_str: str):
    '''Parse ode formula'''

    ode_str = ode_str.replace(' ','')

    if ode_str.startswith("y'="):
        return 0, ode_str, f"Your ODE: {ode_str}"
    else:
        logger.info("ODE formula should starts with y' ")
        return 1, ode_str, "ODE formula should starts with y'= "


class OdeSolver(object):
    '''
    Class to parse string starting with y' into a proper equation ready to apply discretization

    :param y0: initial condition for x=0
    :param x_interval: x axis plot interval
    Example:
        y'(x)=3*x+ 2*y(x)
        ---> y(x+1) = -y(x) + 3*x + 2*y(x)
    '''

    def __init__(self, ode_str: str, y0: float = 1, x_interval: tuple = (0,1)):

        self.equation = ode_str
        self.y0 = y0
        self.x_interval = x_interval
        self.x_interval_array = np.linspace(self.x_interval[0], self.x_interval[1])

        # Format equation
        self.formatted_equation = self._python_equation_formatter(eq = ode_str)
        self.formatted_expression = self.formatted_equation.split('=')[1].replace(' ', '')



    def _python_equation_formatter(self, eq: str) -> str:
        '''
        Return equation string with symbols mapped to python syntax

        Example:
            sin --> np.sin
            log --> np.log
            x^2 --> x**2
        '''

        symbol_map = self._symbol_map()
        formatted_eq = copy(eq)
        for k in symbol_map:
            formatted_eq = formatted_eq.replace(k, symbol_map[k])

        return formatted_eq

    def _symbol_map(self) -> dict:

        symbol_map = {
            'sin': 'np.sin',
            'cos': 'np.cos',
            'log': 'np.log',
            '^': '**',
            'e^': 'np.exp',
            'tan': 'np.tan',
            'tg': 'np.tan',
            'arctan': 'np.arctan',
            'arctg': 'np.arctg'
        }

        return symbol_map

    def _model(self, x, y):
        '''Equation evaluation'''
        dydx = eval(self.formatted_expression)
        return dydx

    def solve(self):
        '''Equation solver'''
        self.y = odeint(self._model, self.y0, self.x_interval_array)
        return self.y



    def plot(self, image_path):
        '''Generate plot and save tmp.png'''

        plt.plot(self.x_interval_array, self.y)
        plt.grid()
        plt.title(self.equation)
        plt.savefig(image_path)
        plt.close()



# ----------------------------------------------------------
# ------------------------ HANDLERS ------------------------
# ----------------------------------------------------------


def _emoji():

     emoji_str = '''
     ʕ•́ᴥ•̀ʔっ
     '''
     return emoji_str

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=_emoji())
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'am OdePlotBot. Write down a first order ode to plot the solution \n ATTENTION: I can work only with equation of the following form: y'=f(x,y) \n Example: y' = cos(y)")

def set_y0(update, context):

    try:
        new_Y0 = float(update.message.text)
        logger.info(f'Setting Y0: {new_Y0}')
        Y0 = new_Y0
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'New initial condition: {Y0}')
    except:
        logger.info(f'Can not set Y0: {update.message.text}')
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Can not set Y0: {update.message.text}')

def set_x_interval(update, context):
    try:
        x_interval_val = update.message.text.split(' ')
        new_X_INTERVAL = (float(x_interval_val[0]), float(x_interval_val[1]))
        X_INTERVAL = new_X_INTERVAL
    except:
        logger.info(f'Can not set Y0: {update.message.text}')
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Can not set X_INTERVAL: {update.message.text}')


def reset_setting(update, context):

    logger.info('Reset global variables')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Settings resetted')
    Y0 = 1
    X_INTERVAL = (0,1)

def current_settings(update, context):
    logger.info(f'Print current settings. Y0: {Y0}. X_INTERVAL: {X_INTERVAL}')
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Current settings are: Y0 --> {Y0}. X_INTERVAL --> {X_INTERVAL}')


def solve_ode(update, context):

    logger.info(f'Receiving message: {update.message.text}')
    status, eq, msg = check_ode(update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    if status == 0:
        # everything is fine, you can solve ode
        solver = OdeSolver(eq)

        # equation feedback
        msg = f"Python formatted equation: {solver.formatted_equation}"
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

        # solve
        logger.info(f'Solve ode: {solver.formatted_equation}')
        y = solver.solve()

        # plot
        image_path = os.path.join(PLOT_PATH, 'tmp.png')
        solver.plot(image_path)

        # send the image
        logger.info('Send image...')
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(image_path, 'rb'))

    return




def main():
    """Start the bot."""

    # Initialize the updater
    updater = Updater("2045130516:AAFo2MuDN_bCd0B8mJAOWq4voX-AKQxRiAU", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # --------------- Initialize handlers
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    set_y0_handler = CommandHandler('set_y0', set_y0)
    dispatcher.add_handler(set_y0_handler)

    set_x_interval_handler = CommandHandler('set_x_interval', set_x_interval)
    dispatcher.add_handler(set_x_interval_handler)

    current_settings_handler = CommandHandler('current_settings', current_settings)
    dispatcher.add_handler(current_settings_handler)

    reset_handler = CommandHandler('reset', reset_setting)
    dispatcher.add_handler(reset_handler)

    solver_handler = MessageHandler(Filters.text & (~Filters.command), solve_ode)
    dispatcher.add_handler(solver_handler)

    # Start the Bot
    updater.start_polling()


    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()







if __name__ == '__main__':

    main()