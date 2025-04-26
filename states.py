from enum import IntEnum, auto
from typing import Dict, List

class BotState(IntEnum):
    """
    Все возможные состояния бота в виде перечисления.
    Использует автоматическую нумерацию для удобства добавления новых состояний.
    """
    
    # --- Основные состояния ---
    START = auto()              # Начальное состояние после /start
    MAIN_MENU = auto()          # Главное меню
    HELP_MENU = auto()          # Меню помощи
    TYPING = auto()             # Ожидание ввода текста от пользователя
    
    # --- Волонтерские состояния ---
    VOLUNTEER_START = auto()    # Начало регистрации волонтера
    VOLUNTEER_NAME = auto()     # Ввод имени волонтера
    VOLUNTEER_REGION = auto()   # Ввод региона волонтера
    VOLUNTEER_HELP_TYPE = auto()# Выбор типа помощи
    VOLUNTEER_CONTACT = auto()  # Ввод контактов
    
    # --- Медицинские состояния ---
    MEDICAL_MENU = auto()       # Меню медицинской помощи
    GENDER_THERAPY_MENU = auto()# Меню гормональной терапии
    FTM_HRT = auto()            # Информация о ФТМ ГТ
    MTF_HRT = auto()            # Информация о МТФ ГТ
    SURGERY_PLANNING = auto()   # Планирование операций
    
    # --- Юридические состояния ---
    LEGAL_MENU = auto()         # Меню юридической помощи
    DOCUMENTS_HELP = auto()     # Помощь со сменой документов
    ABUSE_REPORT = auto()       # Сообщение о нарушении прав
    
    # --- Специальные состояния ---
    ANONYMOUS_MSG = auto()      # Анонимное сообщение
    RESOURCE_ADD = auto()       # Добавление ресурса
    DONATION_INFO = auto()      # Информация о донатах
    CONFIRMATION = auto()       # Подтверждение действия
    DONE = auto()               # Финальное состояние

    @classmethod
    def get_transitions(cls) -> Dict[IntEnum, List[IntEnum]]:
        """
        Возвращает граф допустимых переходов между состояниями.
        Используется для валидации переходов в обработчиках.
        """
        return {
            # Из START можно перейти только в MAIN_MENU
            cls.START: [cls.MAIN_MENU],
            
            # Из главного меню
            cls.MAIN_MENU: [
                cls.HELP_MENU,
                cls.VOLUNTEER_START,
                cls.ANONYMOUS_MSG,
                cls.RESOURCE_ADD,
                cls.DONATION_INFO
            ],
            
            # Из меню помощи
            cls.HELP_MENU: [
                cls.MEDICAL_MENU,
                cls.LEGAL_MENU,
                cls.MAIN_MENU,
                cls.TYPING
            ],
            
            # Медицинские переходы
            cls.MEDICAL_MENU: [
                cls.GENDER_THERAPY_MENU,
                cls.SURGERY_PLANNING,
                cls.HELP_MENU,
                cls.TYPING
            ],
            
            cls.GENDER_THERAPY_MENU: [
                cls.FTM_HRT,
                cls.MTF_HRT,
                cls.MEDICAL_MENU
            ],
            
            # Волонтерские переходы
            cls.VOLUNTEER_START: [cls.VOLUNTEER_NAME],
            cls.VOLUNTEER_NAME: [cls.VOLUNTEER_REGION],
            cls.VOLUNTEER_REGION: [cls.VOLUNTEER_HELP_TYPE],
            cls.VOLUNTEER_HELP_TYPE: [cls.VOLUNTEER_CONTACT],
            cls.VOLUNTEER_CONTACT: [cls.MAIN_MENU],
            
            # Юридические переходы
            cls.LEGAL_MENU: [
                cls.DOCUMENTS_HELP,
                cls.ABUSE_REPORT,
                cls.HELP_MENU,
                cls.TYPING
            ],
            
            # Специальные состояния
            cls.ANONYMOUS_MSG: [cls.MAIN_MENU, cls.TYPING],
            cls.RESOURCE_ADD: [cls.MAIN_MENU, cls.TYPING],
            cls.DONATION_INFO: [cls.MAIN_MENU]
        }

    @classmethod
    def is_valid_transition(cls, current: IntEnum, new: IntEnum) -> bool:
        """
        Проверяет, возможен ли переход между состояниями.
        
        Args:
            current: Текущее состояние
            new: Новое состояние
            
        Returns:
            bool: True если переход допустим
        """
        return new in cls.get_transitions().get(current, [])


# Короткий алиас для удобства
States = BotState
