![lapzbot](http://i.imgur.com/txlWePx.png)

[![Documentation Status](https://readthedocs.org/projects/lapzbot/badge/?version=flaskdev)](http://lapzbot.readthedocs.org/en/flaskdev/index.html)
[![ReviewNinja](https://app.review.ninja/49250931/badge)](https://app.review.ninja/lapoozza/lapzbot)
[![Requirements Status](https://requires.io/github/lapoozza/lapzbot/requirements.svg?branch=flaskdev)](https://requires.io/github/lapoozza/lapzbot/requirements/?branch=flaskdev)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/27aa17781b5a40debf850b1c96fcd1a4/snapshot/origin:flaskdev:HEAD/badge.svg)](https://www.quantifiedcode.com/app/project/27aa17781b5a40debf850b1c96fcd1a4)

[<img align="right" title="Art by Supergiant Games" src="http://www.distilnetworks.com/wp-content/themes/distil/images/fraud-bot.png">](http://www.distilnetworks.com/wp-content/themes/distil/images/fraud-bot.png)
**This version is in the alpha stage. If you want a stable version, download from master branch.**

[[Official Help and Announcements Group]](https://discord.gg/0lzW6jSQESAO1HSU)
### What is lapzbot?

[![Join the chat at https://gitter.im/lapoozza/lapzbot](https://badges.gitter.im/lapoozza/lapzbot.svg)](https://gitter.im/lapoozza/lapzbot?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
Its a nifty little utility bot. Some of its features include :
* Playing music- both local files and online songs
* Fun games- Number guess, Trivia quiz, 8ball, tic tac toe, rock paper scissors, chess
* Your game details are tracked so that you can compare with your friends. Details include: games played, games won, games draw etc.
* Awesome chat emotes
* Osu related functions- stats, top plays, beat map information and real time message scanning for osu based links

*and much more...*

For server admins, lapzbot offers the following functionalites:

* Powerful message filter
* Ability to customize the filter with regex as well as words
* Supports loading of filter lists as well as runtime addition/removal of words/regex
* Add / leave servers on the fly
* Logs are dumped to a hard coded channel

### Commands list
The `?` part is the command prefix. It can be configured to anything. For the sake of explanation, I will show the commands with `?` as the prefix below.

**Games**

|Command   |Information              |
|----------|-------------------------|
|?help     |sends a private message to the user with a list of avilable functions|
|?guess|Starts number guessing game|
|?quizlist|Shows a list of avilable quiz modules along side the quiz_id|
|?startquiz `quiz_id`|Starts a trivia quiz session specified by the quiz_id|
|?rps|Starts rock paper scissor|
|?ttt|Starts tic tac toe|
|?chess `@discord_user`|Starts a game of chess with a specified discord user. The user will be asked to cofirm before the game can start.|

*P.S. currently only rock paper scissors and tic tac toe are configured with stat track*

**Utility**

|Command   |Information              |
|----------|-------------------------|
|?quote add `text/msgs/etc to add`|Add a quote|
|?quote search `search_term`|Search through saved quotes|
|?quote read `quote_id`|Read a quote specified by the quote_id|
|?quote delete `quote_id`|Deletes a saved quote|
|?stats `osu_username`|Shows osu profile stats of the specifed user|
|?top `osu_username`|Shows osu top plays of the specifed user|
|Osu beatmap id/ set id|Shows the beatmap information of the beatmap/ beatmap set|
|?giphy `search_querry`|Giphy GIF search|
|?whoami|Displays your discord related information|
|?whois `@discord_user`|Displays disord related information of a specified discord user|
|?8ball `question`|Replies to a 8 ball question|
|?clean|Deletes the last 20 messages sent by lapzbot|
|?kappa|Default emoticons|
|?feelsgoodman|Default emoticons|
|?feelsbadman|Default emoticons|
|?lapz|Default emoticons|

*P.S. Lapzbot also scans all incoming messages for any links related to osu and displays appropriate information accordingly*


**Music**

|Command   |Information              |
|----------|-------------------------|
|?play `song_id/song_url`|Play or queue a song. Song_ID for local songs and Song_URL for online songs |
|?pause|Pauses the current song|
|?next|Goes to the next song on the queue|
|?stop|Stops all music related activity|
|?resume|Resumes the current song|
|?scan|Scans for all available songs iside the `audio_library` folder. This commands must be used before using `?playlist`|
|?playlist|Displays the local songs that are inside the `audio_library` folder|

**Misc. / Admin**

|Command   |Information              |
|----------|-------------------------|
|?invite `discord_invite`|Invites lapzbot to a server|
|?leave `server_id`|Leaves a currently joined server specified by the `server_id`|
|?serverlist|Shows a list of servers Lapzbot has currently joined along with the server id's|
|?filter_add `word/regex`|Adds a word or regex to message filter during runtime|
|?filter_remove `word/regex`|Removes a word or regex from the message filter during runtime|

*P.S. words or regex added/removed with ?filter_add / ?filter_remove will be lost once the bot is turned off. To make the changes permanent, edit the `message_filter_list.txt` file inside static folder*

### How to set it up?
* Refer to this wiki page :- [How to setup the bot?](https://github.com/lapoozza/lapzbot/wiki/How-to-setup-the-bot%3F)

### Dependencies
1. FFMPEG Library
2. Rest of the dependencies will be handled using the `requirements.txt` file

