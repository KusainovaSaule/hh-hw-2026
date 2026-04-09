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

    def register_call(self, raw_call: str) -> ActiveCall:
        '''
        Метод должен принимать только 1 строку и возвращать класс ActiveCall.
        На входе строка должна быть вида "caller_id,caller_name,caller_phone,receiver_id,receiver_name,receiver_phone"

        Например: "1001,Иван Петров,+71234567890,1085,Адам Яковлев,+71255556666"
        '''
        parts = raw_call.split(',')
        
        caller_id, caller_name, caller_phone = parts[0], parts[1], parts[2]
        receiver_id, receiver_name, receiver_phone = parts[3], parts[4], parts[5]
        
        if caller_phone.startswith(LOCAL_PHONE_PREFIX):
            caller = LocalUser(id=int(caller_id), fullname=caller_name, phone=caller_phone)
        else:
            caller = ForeignUser(id=int(caller_id), fullname=caller_name, phone=caller_phone)
        
        if receiver_phone.startswith(LOCAL_PHONE_PREFIX):
            receiver = LocalUser(id=int(receiver_id), fullname=receiver_name, phone=receiver_phone)
        else:
            receiver = ForeignUser(id=int(receiver_id), fullname=receiver_name, phone=receiver_phone)
        
        active_call = ActiveCall(caller=caller, receiver=receiver)
        self._active_calls.append(active_call)
        
        if active_call.is_cross_border:
            self._cross_border_count += 1
        
        return active_call

    def get_active_calls_count(self) -> int:
        return len(self._active_calls)

    def get_cross_border_calls_count(self) -> int:
        return self._cross_border_count
