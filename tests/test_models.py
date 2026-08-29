from db.models import User, Chat, ChatType, Message, BusinessConnection


def test_user_full_name_with_last_name():
    user = User(telegram_id=1, first_name="Ada", last_name="Lovelace")
    assert user.full_name == "Ada Lovelace"


def test_user_full_name_without_last_name():
    user = User(telegram_id=1, first_name="Cher", last_name=None)
    assert user.full_name == "Cher"


def test_user_repr_contains_key_fields():
    user = User(id=1, telegram_id=42, username="ada")
    text = repr(user)
    assert "42" in text
    assert "ada" in text


def test_chat_is_business_true_when_business_connection_id_set():
    chat = Chat(telegram_chat_id=1, type=ChatType.PRIVATE, business_connection_id=5)
    assert chat.is_business is True


def test_chat_is_business_false_when_no_business_connection_id():
    chat = Chat(telegram_chat_id=1, type=ChatType.PRIVATE, business_connection_id=None)
    assert chat.is_business is False


def test_chat_repr_contains_key_fields():
    chat = Chat(id=1, telegram_chat_id=555, type=ChatType.GROUP)
    text = repr(chat)
    assert "555" in text
    assert "GROUP" in text or "ChatType.GROUP" in text


def test_message_repr_contains_key_fields():
    message = Message(id=1, telegram_message_id=777, chat_id=1)
    text = repr(message)
    assert "777" in text


def test_business_connection_repr_contains_key_fields():
    conn = BusinessConnection(id=1, connection_id="conn-abc", user_chat_id=999)
    text = repr(conn)
    assert "conn-abc" in text
    assert "999" in text


def test_chat_type_enum_values():
    assert ChatType.PRIVATE.value == "private"
    assert ChatType.GROUP.value == "group"
    assert ChatType.SUPERGROUP.value == "supergroup"
    assert ChatType.CHANNEL.value == "channel"


def test_chat_type_constructible_from_string_value():
    assert ChatType("private") is ChatType.PRIVATE
