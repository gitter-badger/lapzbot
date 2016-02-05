#
# The MIT License (MIT)
#
# Copyright (c) 2016 lapoozza
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from __future__ import unicode_literals
from flask import Flask, render_template, flash, redirect, url_for, request, session
import os
import yaml
import threading
import lapzbot
import asyncio
import logging
import discord

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

app = Flask(__name__)
app.config.update(dict(SECRET_KEY=os.urandom(12)))

botle = lapzbot.Bot()
loop = asyncio.get_event_loop()

OPUS_DIR = 'libopus'
OPUS_LIB_NAME = 'libopus-0.dll'

try:
    if not discord.opus.is_loaded():
        path = os.path.join(OPUS_DIR, OPUS_LIB_NAME)
        discord.opus.load_opus(path)
except FileNotFoundError:
    print('The opus library file could not be found.' +
          '\nMake sure the file is present and run the bot again.')
    quit()


@app.route('/')
def welcome_screen():
    """
    This function is called when the FLASK Application first loads. This serves
    as the index.
    :return: This functions returns a rendered HTML page 'instruction.html' found inside the template folder.
    :rtype: html
    """
    return render_template('instruction.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    This part is used to get the login credentials for the bot. The data is
    sent from the login.html form using post method.

    :return: This functions returns a rendered HTML page 'login.html' found inside the template folder.
    :rtype: html
    """
    error = None
    if request.method == 'POST':

        if request.form['prefix'] == '' or request.form['help_id'] == '' or request.form['email'] == '' or \
                        request.form['password'] == '' or request.form['osu_key'] == '':
            return render_template('login.html', error='Do not leave any fields blank.')

        stream = {"BOT": {"command_prefix": ''},
                  "CHANNELS": {"help_channel": ''},
                  "DISCORD_LOGIN": {"email": '', "password": ''},
                  "OSU_API": {"KEY": ''}}

        stream['BOT']['command_prefix'] = str(request.form['prefix'])
        stream['CHANNELS']['help_channel'] = str(request.form['help_id'])
        stream['DISCORD_LOGIN']['email'] = str(request.form['email'])
        stream['DISCORD_LOGIN']['password'] = str(request.form['password'])
        stream['OSU_API']['KEY'] = str(request.form['osu_key'])

        with open('config.yaml', 'w') as f2:
            yaml.dump(stream, f2, default_flow_style=False, explicit_start=True)

        # This starts the lapzbot thread to work in the background)

        t1 = threading.Thread(target=bottie)
        t1.start()

        i = 0
        if not botle.is_logged_in:
            while not botle.is_logged_in:
                i += 1

            if botle.is_logged_in:
                session['logged_in'] = True
                flash('You are logged in')
                return redirect(url_for('logged'))
        elif botle.is_logged_in:
            session['logged_in'] = True
            flash('You are logged in')
            return redirect(url_for('logged'))

    return render_template('login.html', error=error)


@app.route('/logged', methods=['GET', 'POST'])
def logged():
    """
    This function is called once the user succesfully logs in.

    :return: This functions returns a rendered HTML page 'chat_interface.html' found inside the template folder.
    :rtype: html
    """
    error = None
    if request.method == 'POST':
        a = str(request.form['msg'])
        b = str(request.form['chnl'])
        channel = discord.Object(id=b)
        asyncio.run_coroutine_threadsafe(botle.send_message(channel, a), loop)

    return render_template('chat_interface.html', error=error)


@app.route('/logout')
def logout():
    """
    This function is called once the user succesfully logs out. It also clears the
    config.yaml file so that the credentials are not compromised.

    :return: This functions returns a rendered HTML page 'logout.html' found inside the template folder.
    :rtype: html
    """
    asyncio.run_coroutine_threadsafe(botle.logout(), loop)
    stream1 = {}
    with open('config.yaml', 'w') as f2:
        yaml.dump(stream1, f2, default_flow_style=True)
    session.pop('logged_in', None)
    flash('You are logged out')
    return render_template('logout.html')


def bottie():
    """
    This function is threaded function. This function is responsible
    for logging lapzbot into discord and to keep the event loop running.

    :return: This functions returns nothing
    """

    # TODO fix the subsequent login problem

    # asyncio.set_event_loop(asyncio.new_event_loop())
    # global loop
    # loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)

    print('bottie')
    # This function run in the background and keeps lapzbot running
    with open('config.yaml', 'r') as f2:
        stream1 = yaml.load(f2)

    # Set properties for Lapzbot
    botle.prefix = stream1['BOT']['command_prefix']
    botle.key = stream1['OSU_API']['KEY']
    botle.hchid = stream1['CHANNELS']['help_channel']

    try:
        print('run')
        t = loop.create_task(botle.login(stream1['DISCORD_LOGIN']['email'], stream1['DISCORD_LOGIN']['password']))
        loop.run_until_complete(t)
        b = loop.create_task(botle.connect())
        loop.run_until_complete(b)
    except Exception:
        print('except')
        loop.run_until_complete(botle.logout())
    finally:
        print('finally')
        loop.close()


if __name__ == '__main__':
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='127.0.0.0', port=port)
    app.run(debug=False)
