import re
import html
import json
import traceback

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

import app.bot.messages as msg
from app.bot.constants import *

from app.db.sqlite_db import SqliteDataBase


class TelegramBot:
    def __init__(self, token: str, db: SqliteDataBase, admin_id: int):
        self.__db = db
        self.admin_id = admin_id

        self.__max_page = 0
        self.__keyboard: list[InlineKeyboardMarkup] = list()

        self._create_keyboard(self.__db.get_organizations())

        self.__app = ApplicationBuilder().token(token).build()
        self._add_handlers()

    def run(self):
        self.__app.run_polling()

    ### Private ###

    def _add_handlers(self):
        self.__app.add_handlers([
            CommandHandler(["start", "ls"], self._start),
            CallbackQueryHandler(self._keyboard_callback, pattern="^keyboard"),
            ConversationHandler(
                entry_points=[
                    CommandHandler("create", self._start_creating)
                ],
                states = {
                    ADD_NAME: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self._add_name)
                    ],
                    ADD_TIMETABLE: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self._add_timetable)
                    ],
                    ADD_ADDINFO: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self._add_addinfo)
                    ],
                    ADD_ADDRESS: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self._add_address)
                    ],
                },
                fallbacks=[
                    CommandHandler("stop", self._stop)
                ]
            ),
            CommandHandler("add_info", self._update_addinfo),
            CommandHandler("delete", self._delete_organization)
        ])
        self.__app.add_error_handler(self._error_callback)

    def _create_keyboard(self, organizations: list):
        batches: list[list] = list()
        batches.append(list())

        values = [org.name for org in organizations]
        callback_data = [org.id for org in organizations]

        for value, data in zip(values, callback_data):
            if len(batches[-1]) == ON_PAGE:
                batches.append(list())

            batches[-1].append([value, data])

        self.__max_page = len(batches)

        keyboard_tag = "keyboard:"
        self.__keyboard = list()
        for batch in batches:
            keyboard = [
                [InlineKeyboardButton(value, callback_data=keyboard_tag + str(data))]
                for value, data in batch
            ]

            # Add navigation buttons
            keyboard.append(
                [
                    InlineKeyboardButton("<<<", callback_data=keyboard_tag + "left"),
                    InlineKeyboardButton(">>>", callback_data=keyboard_tag + "right")
                ]
            )
            self.__keyboard.append(InlineKeyboardMarkup(keyboard))

    ### Decorators ###

    @staticmethod
    def admin_command(func):

        async def inner(*args, **kwargs):
            bot: TelegramBot = args[0]
            update: Update = args[1]

            if bot.admin_id == update.effective_user.id:
                return await func(*args, **kwargs)
            else:
                await update.message.reply_text(msg.you_cannot_message())

        return inner
    
    @staticmethod
    def command_syntax(syntax: str):

        def wrapper(func):

            async def inner(*args, **kwargs):
                update: Update = args[1]
                command: str = update.message.text

                if re.match(syntax, command):
                    return await func(*args, **kwargs)
                else:
                    await update.message.reply_text(
                        msg.incorrect_syntax_message(syntax),
                        parse_mode="HTML"
                    )

            return inner
        return wrapper
    
    ### Callbacks ###

    @admin_command
    @command_syntax(DELETE_COMMAND_SYNTAX)
    async def _delete_organization(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        command = update.message.text

        name = re.findall(DELETE_COMMAND_SYNTAX, command)[0]
        org = self.__db.get_organization_by_name(name)
        
        if org is None:
            await update.message.reply_text(msg.organization_does_not_found())
        else:
            self.__db.delete_by_id(org.id)
            self._create_keyboard(self.__db.get_organizations())

            await update.message.reply_text(msg.organization_deleted_message())
    
    @admin_command
    @command_syntax(UPDATE_ADDINFO_COMMAND_SYNTAX)
    async def _update_addinfo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        command = update.message.text

        name, addinfo = re.findall(UPDATE_ADDINFO_COMMAND_SYNTAX, command)[0]
        org = self.__db.get_organization_by_name(name)
        
        if org is None:
            await update.message.reply_text(msg.organization_does_not_found())
        else:
            if len(addinfo) == 0:
                addinfo = None

            self.__db.update_addinfo(org, addinfo)

            await update.message.reply_text(msg.addinfo_updated_message())

    async def _create_organization(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.__db.add_organization(
            context.user_data[NAME_KEY],
            context.user_data[TIMETABLE_KEY],
            context.user_data[ADDINFO_KEY],
            context.user_data[ADDRESS_KEY],
        )

        self._create_keyboard(self.__db.get_organizations())

    @admin_command
    async def _start_creating(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(msg.organization_name_message())
        
        return ADD_NAME
    
    async def _add_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        field_data = update.message.text
        context.user_data[NAME_KEY] = field_data

        await update.message.reply_text(msg.organization_timetable_message())

        return ADD_TIMETABLE

    async def _add_timetable(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        field_data = update.message.text
        context.user_data[TIMETABLE_KEY] = field_data

        await update.message.reply_text(
            msg.organization_addinfo_message(),
            reply_markup=SKIP_KEYBOARD
        )

        return ADD_ADDINFO

    async def _add_addinfo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        field_data = update.message.text

        if field_data == SKIP_WORD:
            context.user_data[ADDINFO_KEY] = None
        else:
            context.user_data[ADDINFO_KEY] = field_data


        await update.message.reply_text(
            msg.organization_address_message(),
            reply_markup=SKIP_KEYBOARD
        )

        return ADD_ADDRESS

    async def _add_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        field_data = update.message.text

        if field_data == SKIP_WORD:
            context.user_data[ADDRESS_KEY] = None
        else:
            context.user_data[ADDRESS_KEY] = field_data

        await self._create_organization(update, context)
        await update.message.reply_text(msg.organization_created_message())

        return ConversationHandler.END
    
    async def _stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(msg.stop_message())

        return ConversationHandler.END

    async def _keyboard_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        _, param = query.data.split(":")
        current_page = self._get_current_keyboard_page(context)
        
        if param == "right":
            context.user_data[PAGE_KEY] = min(self.__max_page - 1, current_page + 1)
        elif param == "left":
            context.user_data[PAGE_KEY] = max(0, current_page - 1)
        else:
            org = self.__db.get_organization_by_id(int(param))

            if org is None:
                await update.effective_chat.send_message(
                    msg.organization_does_not_found()
                )
            else:
                await update.effective_chat.send_message(
                    str(org), parse_mode="HTML"
                )

        if current_page != context.user_data[PAGE_KEY]:
            await query.edit_message_reply_markup(
                self._get_current_keyboard(context)
            )

    async def _get_organizations_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.__keyboard:
            await update.message.reply_text(
                msg.organizations_list_message(),
                reply_markup=self._get_current_keyboard(context)
            )
        else:
            await update.message.reply_text(msg.list_empty_message())

    async def _start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await self._get_organizations_list(update, context)

    async def _error_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)

        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            "An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )

        await context.bot.send_message(
            chat_id=self.admin_id, text=message, parse_mode="HTML"
        )

    def _get_current_keyboard(self, context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
        return self.__keyboard[self._get_current_keyboard_page(context)]

    def _get_current_keyboard_page(self, context: ContextTypes.DEFAULT_TYPE) -> int:
        if PAGE_KEY not in context.user_data:
                context.user_data[PAGE_KEY] = 0

        return context.user_data[PAGE_KEY]