import telebot

def test_add():
    assert telebot.add(2, 3) == 5

def test_calc():
    calc = telebot.Calculator()
    assert calc.multiply(2, 4) == 8
