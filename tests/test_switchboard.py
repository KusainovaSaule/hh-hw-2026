import pytest

from app.switchboard import Switchboard
from app.users import ForeignUser, LocalUser


def test_register_call_creates_local_and_foreign_users() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )

    assert isinstance(active_call.caller, LocalUser)
    assert isinstance(active_call.receiver, ForeignUser)
    assert active_call.caller.id == 1
    assert active_call.receiver.id == 2


def test_register_call_counts_active_calls() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,Petr Petrov,+78880000000"
    )
    switchboard.register_call(
        "3,John Smith,+15551234567,4,Jane Doe,+33123456789"
    )

    assert switchboard.get_active_calls_count() == 2


def test_register_call_counts_calls_between_local_and_foreign_users() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )
    switchboard.register_call(
        "3,Petr Petrov,+78880000000,4,Maria Petrova,+79991112233"
    )
    switchboard.register_call(
        "5,Jane Doe,+33123456789,6,Alex Doe,+442012345678"
    )

    assert switchboard.get_active_calls_count() == 3
    assert switchboard.get_cross_border_calls_count() == 1


def test_both_local():
    switchboard = Switchboard()
    active_call = switchboard.register_call("1,Ivan Ivanov,+79990000000,2,Petr Petrov,+78880000000")
    from app.switchboard import ActiveCall
    assert isinstance(active_call, ActiveCall)
    assert isinstance(active_call.caller, LocalUser)
    assert isinstance(active_call.receiver, LocalUser)


def test_both_foreign():
    switchboard = Switchboard()
    active_call = switchboard.register_call("3,John Smith,+15551234567,4,Jane Doe,+33123456789")
    assert isinstance(active_call.caller, ForeignUser)
    assert isinstance(active_call.receiver, ForeignUser)


def test_cross_border_count():
    switchboard = Switchboard()
    switchboard.register_call("1,Local,+79990000000,2,Foreign,+15551234567")
    switchboard.register_call("3,Local2,+79990000001,4,Local3,+79990000002")
    switchboard.register_call("5,Foreign2,+15551234568,6,Local4,+79990000003")
    assert switchboard.get_active_calls_count() == 3
    assert switchboard.get_cross_border_calls_count() == 2


def test_no_cross_border():
    switchboard = Switchboard()
    switchboard.register_call("1,User1,+79990000001,2,User2,+79990000002")
    switchboard.register_call("3,User3,+79990000003,4,User4,+79990000004")
    assert switchboard.get_active_calls_count() == 2
    assert switchboard.get_cross_border_calls_count() == 0


def test_phone_without_plus_is_foreign():
    switchboard = Switchboard()
    active_call = switchboard.register_call("1,Ivan Ivanov,79990000000,2,John Smith,15551234567")
    assert isinstance(active_call.caller, ForeignUser)


def test_phone_with_plus_but_not_7_is_foreign():
    switchboard = Switchboard()
    active_call = switchboard.register_call("1,Ivan Ivanov,+15551234567,2,John Smith,+442012345678")
    assert isinstance(active_call.caller, ForeignUser)


def test_sequential_calls_counts():
    switchboard = Switchboard()
    
    switchboard.register_call("1,Local,+79990000001,2,Local,+79990000002")
    assert switchboard.get_active_calls_count() == 1
    assert switchboard.get_cross_border_calls_count() == 0
    
    switchboard.register_call("3,Local,+79990000003,4,Foreign,+15550000004")
    assert switchboard.get_active_calls_count() == 2
    assert switchboard.get_cross_border_calls_count() == 1
    
    switchboard.register_call("5,Foreign,+15550000005,6,Foreign,+15550000006")
    assert switchboard.get_active_calls_count() == 3
    assert switchboard.get_cross_border_calls_count() == 1
