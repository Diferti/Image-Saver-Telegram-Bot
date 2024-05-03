import telebot
import os
import requests

from telebot import types

# Telegram bot token for connection.
token=""
bot=telebot.TeleBot(token)

users_directories=[]
newDirectoryStatus=False
sendPictureStatus=False
saveByFoldersStatus=False

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

def exitKeyboard():
    exit = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Back")
    button2 = types.KeyboardButton("Stop bot")
    exit.row(button1, button2)
    return exit

@bot.message_handler(commands=['start'])
def start(message):
    menu = keyboard()
    bot.send_message(message.chat.id,
                     text="<b>Hi, {0.first_name}!</b>\nI am the <i>Image Saver Bot</i>, I'll help you as much as I can to save your photos!\n"
                          "<u>Feel free to use buttons to interact with me!</u>".format(message.from_user),
                     parse_mode='html', reply_markup=menu)

@bot.message_handler(func=lambda message: message.text == 'Back')
def back(message):
    global newDirectoryStatus, sendPictureStatus, saveByFoldersStatus
    newDirectoryStatus = False
    sendPictureStatus = False
    saveByFoldersStatus = False
    mainMenu = keyboard()
    bot.send_message(message.chat.id,
                     text="<b>Back to main menu</b>".format(message.from_user),
                     parse_mode='html', reply_markup=mainMenu)

@bot.message_handler(func=lambda message: message.text == 'Stop bot')
def stop_bot(message):
    global newDirectoryStatus, sendPictureStatus, saveByFoldersStatus
    newDirectoryStatus = False
    sendPictureStatus = False
    saveByFoldersStatus = False
    hideMarkup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id,
                     text="<b>Bot stopped. To restart, send /start command</b>".format(message.from_user),
                     parse_mode='html', reply_markup=hideMarkup)

@bot.message_handler(func=lambda message: message.text == 'Save photos')
def savePhotos(message):
    directoryMenu = secondKeyboard()
    bot.send_message(message.chat.id,
                     text="<b>Save photos option</b> will save your images that you sent to <b><i>folder</i></b>!\n"
                          "<u>Before send your images make sure that you set up folder path!</u>".format(message.from_user),
                     parse_mode='html', reply_markup=directoryMenu)

@bot.message_handler(func=lambda message: message.text == 'Save by folders')
def saveByFolders(message):
    global saveByFoldersStatus
    directoryMenu = secondKeyboard()
    bot.send_message(message.chat.id,
                     text="<b>Save by folders option</b> will save your images that you sent to <b><i>new folders</i></b>!\n"
                          "<u>Before send your images/videos make sure that you set up folder path!</u>".format(message.from_user),
                     parse_mode='html', reply_markup=directoryMenu)
    saveByFoldersStatus = True

@bot.message_handler(func=lambda message: message.text == 'New directory path')
def changeDirectory(message):
    global newDirectoryStatus
    hideMarkup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id,
                     text="<b>Send directory path</b> like this: \n<b><i>C:\\Users\\User123\\Downloads</i></b>".format(message.from_user),
                     parse_mode='html', reply_markup=hideMarkup)
    newDirectoryStatus = True

@bot.message_handler(func=lambda message: message.text == 'Leave previous one')
def leaveDirectory(message):
    global newDirectoryStatus, sendPictureStatus, saveByFoldersStatus
    user_id=message.chat.id
    exitMarkup = exitKeyboard()
    directory_path=None

    for user_directory in users_directories:
        if user_directory['user_id'] == user_id:
            directory_path=user_directory['path']
            break

    if directory_path is None:
        directoryMenu = secondKeyboard()
        bot.send_message(user_id, "You need to set your directory path first.", reply_markup=directoryMenu)
        return

    if saveByFoldersStatus:
        bot.send_message(user_id, text=f"<b>Directory path is left as:</b> \n<b><i>{directory_path}</i></b>"
                         "\n\nNow send name of new folder and then your images/videos that you want to save!", parse_mode='html',
                         reply_markup=exitMarkup)
    else:
        bot.send_message(user_id, text=f"<b>Directory path is left as:</b> \n<b><i>{directory_path}</i></b>"
                        "\n\nNow send your images/videos that you want to save!", parse_mode='html', reply_markup=exitMarkup)
    newDirectoryStatus = False
    sendPictureStatus = True

@bot.message_handler(func=lambda message: newDirectoryStatus)
def changeDirectoryPath(message):
    global newDirectoryStatus, sendPictureStatus, saveByFoldersStatus
    if not newDirectoryStatus:
        return

    exitMarkup = exitKeyboard()
    user_id = message.chat.id
    new_directory = message.text

    # Check if user_id is already in users_directories
    for user_directory in users_directories:
        if user_directory['user_id'] == user_id:
            user_directory['path'] = new_directory
            if saveByFoldersStatus:
                bot.send_message(user_id, text=f"<b>Directory path changed successfully to:</b> \n<b><i>{new_directory}</i></b>"
                                 "\n\nNow send name of new folder and then your images/videos that you want to save!", parse_mode='html',
                                 reply_markup=exitMarkup)
            else:
                bot.send_message(user_id, text=f"<b>Directory path changed successfully to:</b> \n<b><i>{new_directory}</i></b>"
                                "\n\nNow send your images/videos that you want to save!", parse_mode='html', reply_markup=exitMarkup)

            newDirectoryStatus = False
            sendPictureStatus = True
            return

    # If user_id is not found in users_directories, add it
    users_directories.append({'user_id': user_id, 'path': new_directory, 'newFolder': None})
    if saveByFoldersStatus:
        bot.send_message(user_id, text=f"<b>Directory path changed successfully to:</b> \n<b><i>{new_directory}</i></b>"
                                       "\n\nNow send name of new folder and then your images/videos that you want to save!",
                         parse_mode='html',
                         reply_markup=exitMarkup)
    else:
        bot.send_message(user_id, text=f"<b>Directory path changed successfully to:</b> \n<b><i>{new_directory}</i></b>"
                                       "\n\nNow send your images/videos that you want to save!", parse_mode='html',
                         reply_markup=exitMarkup)
    newDirectoryStatus = False
    sendPictureStatus = True

@bot.message_handler(func=lambda message: saveByFoldersStatus and not newDirectoryStatus)
def newFolder(message):
    global saveByFoldersStatus, newDirectoryStatus, sendPictureStatus
    if not saveByFoldersStatus or newDirectoryStatus:
        return

    user_id = message.chat.id
    folder = message.text.strip()
    directory_path = None

    # Find the directory path for the user
    for user_directory in users_directories:
        if user_directory['user_id'] == user_id:
            directory_path = user_directory['path']
            # Construct new path for the new folder
            new_directory = os.path.join(directory_path, folder)
            user_directory['newFolder'] = new_directory
            break

    if directory_path is None:
        mainMenu = keyboard()
        bot.send_message(user_id, "You need to set your directory path first.", reply_markup=mainMenu)
        sendPictureStatus = False
        saveByFoldersStatus = False
        return

    # Check if the new folder already exists
    if os.path.exists(new_directory):
        bot.send_message(user_id, "Directory already exists.")
    else:
        try:
            # Create the new folder
            os.makedirs(new_directory)
            bot.send_message(user_id, f"New folder created: {new_directory}")
        except Exception as e:
            bot.send_message(user_id, f"Error creating directory: {e}")

@bot.message_handler(content_types=['photo', 'video'])
def save_image_video(message):
    global sendPictureStatus, saveByFoldersStatus
    if not sendPictureStatus:
        return

    exitMarkup = exitKeyboard()

    if message.content_type == 'photo':
        media_type = 'jpg'
        file_id = message.photo[-1].file_id
    elif message.content_type == 'video':
        media_type = 'mp4'
        file_id = message.video.file_id
    else:
        return

    file_info = bot.get_file(file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))

    user_id = message.chat.id
    directory_path = None

    # Find the directory path for the user
    for user_directory in users_directories:
        if user_directory['user_id'] == user_id:
            if user_directory['newFolder'] is not None:
                directory_path = user_directory['newFolder']
            else:
                directory_path = user_directory['path']
            break

    if directory_path is None:
        mainMenu = keyboard()
        bot.send_message(user_id, "You need to set your directory path first.", reply_markup=mainMenu)
        sendPictureStatus = False
        saveByFoldersStatus = False
        return

    # Count existing files to determine the next file name
    file_count = len([name for name in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, name))])

    # Save the content to the directory with a sequential file name
    with open(os.path.join(directory_path, f"{file_count + 1}.{media_type}"), 'wb') as new_file:
        new_file.write(file.content)

    bot.send_message(user_id, f"File №{file_count + 1} saved successfully!", reply_markup=exitMarkup)

bot.polling(none_stop=True)