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
import yaml

import logging
from TelegramBot.Bot import Bot, BotRunner

from telegram import Update
from telegram.ext import CallbackContext


# --------------------------------------------------------------
# ------------------------- GLOBAL VAR -------------------------
# --------------------------------------------------------------


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)



class OdeSolver(object):
    '''
    ODE solver.
    Given a ode formula and inintial condition solve the ODE.
    '''

    def __init__(self, ode_str: str, y0: float = 1, x_interval: tuple = (0,1)):
        '''
       :param ode_str: equation formule as string
       :param y0: initial condition for x=0
       :param x_interval: x axis plot interval
       Example:
           y' = 3*x + 2
           y0 = 1
           x_interval = (-1, 1)
       '''

        self._load_config()
        self._set_equation_param(y0, x_interval)
        self._set_equation_formula(ode_str)

    def _load_config(self):
        '''Load config'''
        with open('.\config.yml') as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

        self._config = config
        self._plot_path = self._config['plot_path']

    def _set_x_interval(self, x_interval: tuple):
        self.x_interval = x_interval
        self.x_interval_array = np.linspace(self.x_interval[0], self.x_interval[1])

    def _set_y0(self, y0: float):
        self.y0 = y0

    def _set_equation_param(self, y0: float, x_interval: tuple):
        self._set_x_interval(x_interval)
        self._set_y0(y0)

    def _set_equation_formula(self, ode_str: str):
        '''Store ode str and format'''
        self.equation = ode_str
        self.formatted_equation = self._python_equation_formatter(eq=ode_str)
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
        '''Map main function in python syntax'''

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
        '''
        Transform string expression into a proper python function
        Return a function y'=f(x,y)
        '''
        dydx = eval(self.formatted_expression)
        return dydx

    def solve(self):
        '''Equation solver'''
        self.y = odeint(self._model, self.y0, self.x_interval_array, tfirst=True)
        return self.y

    def plot(self, image_path: str):
        '''Generate plot and save tmp.png'''

        plt.plot(self.x_interval_array, self.y)
        plt.grid()
        plt.title(self.equation)
        plt.savefig(image_path)
        plt.close()


class OdeBot(Bot):

    def __init__(self, Y0: int = 1, X_INTERVAL: tuple = (0,5)):

        self.Y0 = Y0
        self.X_INTERVAL = X_INTERVAL

        self._load_config()
        self._set_handlers()

    def _load_config(self):
        '''Load config'''
        with open('.\config.yml') as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

        self._config = config
        self._API = self._config['API']
        self._plot_path = self._config['plot_path']

    def _emoji(self) -> str:

         emoji_str = '''
         ʕ•́ᴥ•̀ʔっ
         '''
         return emoji_str

    def _start(self, update: Update, context: CallbackContext) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=self._emoji())
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'am OdePlot. Write down a first order ode to plot the solution.")
        context.bot.send_message(chat_id=update.effective_chat.id, text="ATTENTION: I can work only with equation of the following form: y'=f(x,y)")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Example: y' = cos(y)")

        context.bot.send_message(chat_id=update.effective_chat.id, text="Here a recap of the commands you can run: "
                                                                        "\n\t - /set_y0 _float_: set initial condition y(0). Example: /set_y0 2"
                                                                        "\n\t - /set_x_interval _float_ _float_: set x axis boundaries you want to plot. Example /set_x_interval -5 3"
                                                                        "\n\t - /current_settings: just print current ode settings "
                                                                        "\n\t - /reset_settings: reset default settings y(0) = 1, x_interval = (0,1)")

    def _help(self, update: Update, context: CallbackContext) -> None:
        '''Recap commands'''
        context.bot.send_message(chat_id=update.effective_chat.id, text="Here a recap of the commands you can run: "
                                                                        "\n\t - /set_y0 _float_: set initial condition y(0). Example: /set_y0 2"
                                                                        "\n\t - /set_x_interval _float_ _float_: set x axis boundaries you want to plot. Example /set_x_interval -5 3"
                                                                        "\n\t - /current_settings: just print current ode settings "
                                                                        "\n\t - /reset_settings: reset default settings y(0) = 1, x_interval = (0,1)")

    def _set_y0(self, update: Update, context: CallbackContext) -> None:
        '''Store y0 param sent by user'''
        try:
            tmp = update.message.text.split(' ')[1]
            tmp = tmp.replace(' ', '')
            new_Y0 = float(tmp)
            logger.info(f'Setting Y0: {new_Y0}')
            self.Y0 = new_Y0
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'New initial condition: Y0={self.Y0}')
        except Exception as e:
            logger.info(e)
            logger.info(f'Can not set Y0: {update.message.text}')
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Can not set Y0: {update.message.text}. Example of correct syntax: "/set_y0 3.5"')

    def _set_x_interval(self, update: Update, context: CallbackContext) -> None:
        '''Store x_interval param sent by user'''
        try:
            x0 = update.message.text.split(' ')[1]
            x1 = update.message.text.split(' ')[2]
            new_X_INTERVAL = (float(x0), float(x1))
            self.X_INTERVAL = new_X_INTERVAL
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'New initial condition: X_INTERVAL={self.X_INTERVAL}')

        except Exception as e:
            logger.info(e)
            logger.info(f'Can not set X_INTERVAL: {update.message.text}')
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Can not set X_INTERVAL: {update.message.text}. Example of correct syntax: "/set_x_interval 1 10.5"')

    def _reset_settings(self, update: Update, context: CallbackContext) -> None:

        logger.info('Reset global variables')
        self.Y0 = 1
        self.X_INTERVAL = (0, 1)

        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Settings resetted: Y0 = {self.Y0}, X_INTERVAL = {self.X_INTERVAL}')

    def _current_settings(self, update: Update, context: CallbackContext) -> None:
        '''Print current settings'''
        logger.info(f'Print current settings. Y0: {self.Y0}. X_INTERVAL: {self.X_INTERVAL}')
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Current settings are: Y0 = {self.Y0}. X_INTERVAL = {self.X_INTERVAL}')

    def _solve_ode(self, update: Update, context: CallbackContext) -> None:
        '''Solve ODE and send img back'''

        logger.info(f'Receiving message: {update.message.text}')
        status, eq, msg = self._check_ode(update.message.text)
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

        if status == 0:
            # everything is fine, you can solve ode
            solver = OdeSolver(eq, y0=self.Y0, x_interval=self.X_INTERVAL)

            # equation feedback
            msg = f"Python formatted equation: {solver.formatted_equation}"
            context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

            # solve
            logger.info(f'Solve ode: {solver.formatted_equation}')

            # equation feedback
            msg = f"Settings: Y0 = {self.Y0}, X_INTERVAL = {self.X_INTERVAL}"
            context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

            y = solver.solve()

            # plot
            image_path = os.path.join(self._plot_path, 'tmp.png')
            solver.plot(image_path)

            # send the image
            logger.info('Send image...')
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(image_path, 'rb'))

        else:
            # equation feedback
            msg = "Somethig went wrong with equation...try again"
            context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    def _check_ode(self, ode_str: str):
        '''Parse ode formula'''

        ode_str = ode_str.replace(' ', '')

        if ode_str.startswith("y'="):
            return 0, ode_str, f"Your ODE: {ode_str}"
        else:
            logger.info("ODE formula should starts with y' ")
            return 1, ode_str, "ODE formula should starts with y'= "


    def _set_handlers(self):

        self._handlers = {
            'start': {'type': 'command', 'fun': self._start},
            'set_y0': {'type': 'command', 'fun': self._set_y0},
            'set_x_interval': {'type': 'command', 'fun': self._set_x_interval},
            'current_settings': {'type': 'command', 'fun': self._current_settings},
            'reset_settings': {'type': 'command', 'fun': self._reset_settings},
            'solver': {'type': 'message', 'fun': self._solve_ode},
            'help': {'type': 'command', 'fun': self._help},
        }

def main():
    """Start the bot."""

    # Initialize bot
    bot = OdeBot(Y0 = 1, X_INTERVAL = (0,5))

    # Initialize bot runner and run
    bot_runner = BotRunner(bot)
    bot_runner.run()











if __name__ == '__main__':

    main()