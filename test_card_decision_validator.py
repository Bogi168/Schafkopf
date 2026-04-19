from wsgiref.validate import validator

import pytest
from CardDecisionValidator import SoloCardDecisionValidator
from Player import Player
from Cards import Card, Color, Type


@pytest.fixture
def player():
    return Player(player_name="Testplayer")


@pytest.fixture
def trumps():
    return [
        Card(card_color=Color.EICHEL, card_type=Type.OBER),
        Card(card_color=Color.GRUEN, card_type=Type.OBER),
        Card(card_color=Color.HERZ, card_type=Type.OBER),
        Card(card_color=Color.SCHELLEN, card_type=Type.OBER),
        Card(card_color=Color.EICHEL, card_type=Type.UNTER),
        Card(card_color=Color.GRUEN, card_type=Type.UNTER),
        Card(card_color=Color.HERZ, card_type=Type.UNTER),
        Card(card_color=Color.SCHELLEN, card_type=Type.UNTER),
        Card(card_color=Color.HERZ, card_type=Type.SAU),
        Card(card_color=Color.HERZ, card_type=Type.TEN),
        Card(card_color=Color.HERZ, card_type=Type.KOENIG),
        Card(card_color=Color.HERZ, card_type=Type.NINE),
        Card(card_color=Color.HERZ, card_type=Type.EIGHT),
        Card(card_color=Color.HERZ, card_type=Type.SEVEN),
    ]


@pytest.fixture
def eichel_sau():
    return Card(Color.EICHEL, Type.SAU)


@pytest.fixture
def eichel_ten():
    return Card(Color.EICHEL, Type.TEN)


@pytest.fixture
def eichel_seven():
    return Card(Color.EICHEL, Type.SEVEN)


@pytest.fixture
def schellen_seven():
    return Card(Color.SCHELLEN, Type.SEVEN)


@pytest.fixture
def gruen_eight():
    return Card(Color.GRUEN, Type.EIGHT)


@pytest.fixture
def eichel_ober():
    return Card(Color.EICHEL, Type.OBER)


@pytest.fixture
def herz_seven():
    return Card(Color.HERZ, Type.SEVEN)


@pytest.fixture
def gruen_unter():
    return Card(Color.GRUEN, Type.UNTER)


def test_last_card_freedom(
    player, trumps, eichel_ten, eichel_seven, schellen_seven, eichel_ober, herz_seven
):
    validator = SoloCardDecisionValidator()
    lead_card = eichel_ten

    player.player_cards = [eichel_seven]
    assert validator.is_move_legal(
        decision=eichel_seven, lead_card=lead_card, player=player, trumps=trumps
    )

    player.player_cards = [schellen_seven]
    assert validator.is_move_legal(
        decision=schellen_seven, lead_card=lead_card, player=player, trumps=trumps
    )

    player.player_cards = [eichel_ober]
    assert validator.is_move_legal(
        decision=eichel_ober, lead_card=lead_card, player=player, trumps=trumps
    )

    player.player_cards = [herz_seven]
    assert validator.is_move_legal(
        decision=herz_seven, lead_card=lead_card, player=player, trumps=trumps
    )


def test_lead_card_color_obligation(
    player, trumps, eichel_ten, eichel_seven, schellen_seven, eichel_ober
):
    validator = SoloCardDecisionValidator()
    lead_card = eichel_ten
    player.player_cards = [eichel_seven, schellen_seven, eichel_ober]

    assert not validator.is_move_legal(
        decision=schellen_seven, lead_card=lead_card, player=player, trumps=trumps
    )
    assert not validator.is_move_legal(
        decision=eichel_ober, lead_card=lead_card, player=player, trumps=trumps
    )
    assert validator.is_move_legal(
        decision=eichel_seven, lead_card=lead_card, player=player, trumps=trumps
    )


def test_lead_trump_obligation(
    player, trumps, gruen_unter, eichel_ten, herz_seven, eichel_ober, gruen_eight
):
    validator = SoloCardDecisionValidator()
    lead_card = gruen_unter
    player.player_cards = [eichel_ten, herz_seven, eichel_ober, gruen_eight]
    assert not validator.is_move_legal(
        decision=eichel_ten, lead_card=lead_card, player=player, trumps=trumps
    )
    assert not validator.is_move_legal(
        decision=gruen_eight, lead_card=lead_card, player=player, trumps=trumps
    )
    assert validator.is_move_legal(
        decision=herz_seven, lead_card=lead_card, player=player, trumps=trumps
    )
    assert validator.is_move_legal(
        decision=eichel_ober, lead_card=lead_card, player=player, trumps=trumps
    )


def test_lead_freedom(
    player, trumps, gruen_unter, eichel_ten, herz_seven, eichel_ober, gruen_eight
):
    validator = SoloCardDecisionValidator()
    lead_card = None
    player.player_cards = [eichel_ten, herz_seven, eichel_ober, gruen_eight]
    assert validator.is_move_legal(
        decision=eichel_ten, lead_card=lead_card, player=player, trumps=trumps
    )
    assert validator.is_move_legal(
        decision=gruen_eight, lead_card=lead_card, player=player, trumps=trumps
    )
    assert validator.is_move_legal(
        decision=herz_seven, lead_card=lead_card, player=player, trumps=trumps
    )
    assert validator.is_move_legal(
        decision=eichel_ober, lead_card=lead_card, player=player, trumps=trumps
    )


def test_no_lead_color_freedom(
    player, trumps, gruen_unter, eichel_ten, herz_seven, eichel_ober, gruen_eight
):
    validator = SoloCardDecisionValidator()
    lead_card = gruen_eight
    player.player_cards = [eichel_ten, herz_seven, eichel_ober]
    assert validator.is_move_legal(
        decision=eichel_ten, lead_card=lead_card, player=player, trumps=trumps
    )
    assert validator.is_move_legal(
        decision=herz_seven, lead_card=lead_card, player=player, trumps=trumps
    )
    assert validator.is_move_legal(
        decision=eichel_ober, lead_card=lead_card, player=player, trumps=trumps
    )
