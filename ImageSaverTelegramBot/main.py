import telebot
import os
import requests

from telebot import types

# Telegram bot token for connection.
token=""
bot=telebot.TeleBot(token)

users_directories=[]

# Main button menu for interacting with the bot
def keyboard():
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Save photos")
    button2 = types.KeyboardButton("Save by folders")
    menu.row(button1, button2)
    return menu

# Second button menu for managing directories
def secondKeyboard():
    directoryMenu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("New directory path")
    button2 = types.KeyboardButton("Leave previous one")
    directoryMenu.row(button1, button2)
    return directoryMenu

@bot.message_handler(commands=['start'])
def start(message):
    menu = keyboard()
    bot.send_message(message.chat.id,
                     text="<b>Hi, {0.first_name}!</b>\nI am the <i>Image Saver Bot</i>, I'll help you as much as I can to save your photos!\n"
                          "<u>Feel free to use buttons to interact with me!</u>".format(message.from_user),
                     parse_mode='html', reply_markup=menu)

@bot.message_handler(func=lambda message: message.text == 'Save photos')
def savePhotos(message):
    directoryMenu = secondKeyboard()
    bot.send_message(message.chat.id,
                     text="<b>Save photos option</b> will save your images that you sent to <b><i>folder</i></b>!\n"
                          "<u>Before send your images make sure that you set up folder path!</u>".format(message.from_user),
                     parse_mode='html', reply_markup=directoryMenu)

@bot.message_handler(func=lambda message: message.text == 'Save by folders')
def saveByFolders(message):
    directoryMenu = secondKeyboard()
    bot.send_message(message.chat.id,
                     text="<b>Save by folders option</b> will save your images that you sent to <b><i>new folders</i></b>!\n"
                          "<u>Before send your images make sure that you set up folder path!</u>".format(message.from_user),
                     parse_mode='html', reply_markup=directoryMenu)

@bot.message_handler(func=lambda message: message.text == 'New directory path')
def changeDirectory(message):
    hideMarkup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id,
                     text="<b>Send directory path</b> like this: \n<b><i>C:\\Users\\User123\\Downloads</i></b>!".format(message.from_user),
                     parse_mode='html', reply_markup=hideMarkup)

@bot.message_handler(func=lambda message: True)
def changeDirectoryPath(message):
    user_id = message.chat.id
    new_directory = message.text

    # Check if user_id is already in users_directories
    for user_directory in users_directories:
        if user_directory['user_id'] == user_id:
            user_directory['path'] = new_directory
            bot.send_message(user_id,
                             text=f"<b>Directory path changed successfully to:</b> \n<b><i>{new_directory}</i></b>"
                             "\n\nNow send your images that you want to save!", parse_mode='html')
            return

    # If user_id is not found in users_directories, add it
    users_directories.append({'user_id': user_id, 'path': new_directory})
    bot.send_message(user_id,
                     text=f"<b>Directory path set successfully to:</b> \n<b><i>{new_directory}</i></b>"
                     "\n\nNow send your images that you want to save!",parse_mode='html')

@bot.message_handler(content_types=['photo'])
def save_image(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))

    user_id = message.chat.id
    directory_path = None

    # Find the directory path for the user
    for user_directory in users_directories:
        if user_directory['user_id'] == user_id:
            directory_path = user_directory['path']
            break

    if directory_path is None:
        bot.send_message(user_id, "You need to set your directory path first.")
        return

    # Save the image to the directory
    with open(os.path.join(directory_path, f"{message.photo[-1].file_id}.jpg"), 'wb') as new_file:
        new_file.write(file.content)

    bot.send_message(user_id, "Image saved successfully!")

bot.polling(none_stop=True)