from telegram import ReplyKeyboardMarkup


### Add new organization conversation states
ADD_NAME = 0
ADD_TIMETABLE = 1
ADD_ADDINFO = 2
ADD_ADDRESS = 3

ON_PAGE = 5

PAGE_KEY = "page"
NAME_KEY = "org:name"
TIMETABLE_KEY = "org:timetable"
ADDINFO_KEY = "org:addinfo"
ADDRESS_KEY = "org:address"

SKIP_WORD = "Далее"

SKIP_KEYBOARD = ReplyKeyboardMarkup(
    [
        [SKIP_WORD]
    ],
    one_time_keyboard=True
)

DELETE_COMMAND_SYNTAX = r"^/[a-zA-Z_]+ \"(.+)\""
UPDATE_ADDINFO_COMMAND_SYNTAX = r"^/[a-zA-Z_]+ \"(.+)\" \"(.*?)\""