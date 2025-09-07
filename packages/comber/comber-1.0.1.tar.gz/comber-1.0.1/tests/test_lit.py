import pytest
from comber import Lit, ParseError

def test_lit_create():
    Lit('foo')

def test_lit_repr():
    assert repr(Lit('foo')) == 'Lit(foo)'

def test_lit_expect():
    assert ['foo'] == Lit('foo').expectCore()

def test_lit_parse():
    parser = Lit('foo')

    state = parser('foo')
    assert state.text == ''
    assert state.tree == ['foo']

    state = parser('foobar')
    assert state.text == 'bar'
    assert state.tree == ['foo']

    with pytest.raises(ParseError):
        parser('bar')
