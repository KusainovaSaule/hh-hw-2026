from __future__ import annotations

from dataclasses import dataclass

from app.users import User
from app.users.local_user import LocalUser
from app.users.foreign_user import ForeignUser


LOCAL_PHONE_PREFIX = "+7"


@dataclass(slots=True)
class ActiveCall:
    caller: User
    receiver: User

    @property
    def is_cross_border(self) -> bool:
        return type(self.caller) is not type(self.receiver)


class Switchboard:
    def __init__(self) -> None:
        self._active_calls: list[ActiveCall] = []
        self._cross_border_count = 0

    def _validate_and_create_user(self, user_id: str, fullname: str, phone: str) -> User:
        if not user_id or not user_id.strip():
            raise ValueError("Id пользователя не может быть пустым")
        
        try:
            user_id_int = int(user_id.strip())
        except ValueError:
            raise ValueError(f"Id пользователя должен быть числом: {user_id}")
        
        if user_id_int < 0:
            raise ValueError(f"Id пользователя должен быть положительным числом: {user_id_int}")
        
        if not fullname or not fullname.strip():
            raise ValueError("Имя пользователя не может быть пустым")
        
        fullname_clean = fullname.strip()
        
        if len(fullname_clean) < 2:
            raise ValueError("Имя пользователя должно содержать минимум 2 символа")
        
        if fullname_clean.isdigit():
            raise ValueError("Имя пользователя не может состоять только из цифр")
        
        if not phone or not phone.strip():
            raise ValueError("Номер телефона не может быть пустым")
        
        phone_clean = phone.strip()
        
        allowed_chars = set("0123456789+- ")
        if not all(c in allowed_chars for c in phone_clean):
            raise ValueError("Номер телефона содержит недопустимые символы")
        
        if phone_clean.startswith(LOCAL_PHONE_PREFIX):
            return LocalUser(id=user_id_int, fullname=fullname_clean, phone=phone_clean)
        else:
            return ForeignUser(id=user_id_int, fullname=fullname_clean, phone=phone_clean)

    def register_call(self, raw_call: str) -> ActiveCall:
        '''
        Метод должен принимать только 1 строку и возвращать класс ActiveCall.
        На входе строка должна быть вида "caller_id,caller_name,caller_phone,receiver_id,receiver_name,receiver_phone"

        Например: "1001,Иван Петров,+71234567890,1085,Адам Яковлев,+71255556666"
        '''
        if not raw_call or not isinstance(raw_call, str):
            raise ValueError("Строка вызова не может быть пустой")
        
        parts = raw_call.split(',')
        
        if len(parts) != 6:
            raise ValueError(f"Неверный формат вызова. Ожидается 6 полей, получено {len(parts)}")
        
        for i, part in enumerate(parts):
            if not part or not part.strip():
                raise ValueError(f"Поле {i} не может быть пустым")
        
        caller_id = parts[0].strip()
        caller_name = parts[1].strip()
        caller_phone = parts[2].strip()
        receiver_id = parts[3].strip()
        receiver_name = parts[4].strip()
        receiver_phone = parts[5].strip()
        
        caller = self._validate_and_create_user(caller_id, caller_name, caller_phone)
        receiver = self._validate_and_create_user(receiver_id, receiver_name, receiver_phone)
        
        active_call = ActiveCall(caller=caller, receiver=receiver)
        self._active_calls.append(active_call)
        
        if active_call.is_cross_border:
            self._cross_border_count += 1
        
        return active_call

    def get_active_calls_count(self) -> int:
        return len(self._active_calls)

    def get_cross_border_calls_count(self) -> int:
        return self._cross_border_count
