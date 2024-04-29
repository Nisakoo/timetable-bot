def error_message():
    return "😥 Извините, я сломался!\nНе волнуйтесь, меня уже чинят 🚑"

def list_empty_message():
    return "❗Список пуст"

def organizations_list_message():
    return "Привет, здесь вы можете найти расписание работ организаций!"

def stop_message():
    return "❗ Вы прервали операцию"

def you_cannot_message():
    return "🚫 Вы не можете выполнить эту команду 🚫"

def organization_does_not_found():
    return "❗Организация не найдена"

def incorrect_syntax_message(syntax: str):
    return f"""❗Команда некорректна.
<pre>{syntax}</pre>"""

def organization_deleted_message():
    return "❗Организация удалена"

def addinfo_updated_message():
    return "❗Доп. информация обновлена"

def organization_name_message():
    return "Укажите название новой организации:"

def organization_timetable_message():
    return """Укажите расписание:
            
ПН - ПТ:
🕒 9:30 - 18:00
😴 13:00 - 14:00

СБ - ВС:
Выходной"""

def organization_addinfo_message():
    return "Укажите доп.инфо:"

def organization_address_message():
    return "Укажите адресс:"

def organization_created_message():
    return "Организация создана!"