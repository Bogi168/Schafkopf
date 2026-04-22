import pytest
from CardPowerCalculator import (
    SauspielCardPowerCalculator,
    WenzCardPowerCalculator,
)
from Cards import Card, Color, Type


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
def eichel_eight():
    return Card(Color.EICHEL, Type.EIGHT)


@pytest.fixture
def eichel_nine():
    return Card(Color.EICHEL, Type.NINE)


@pytest.fixture
def eichel_koenig():
    return Card(Color.EICHEL, Type.KOENIG)


@pytest.fixture
def schellen_seven():
    return Card(Color.SCHELLEN, Type.SEVEN)


@pytest.fixture
def schellen_sau():
    return Card(Color.SCHELLEN, Type.SAU)


@pytest.fixture
def gruen_eight():
    return Card(Color.GRUEN, Type.EIGHT)


@pytest.fixture
def eichel_ober():
    return Card(Color.EICHEL, Type.OBER)


@pytest.fixture
def gruen_ober():
    return Card(Color.GRUEN, Type.OBER)


@pytest.fixture
def herz_ober():
    return Card(Color.HERZ, Type.OBER)


@pytest.fixture
def schellen_ober():
    return Card(Color.SCHELLEN, Type.OBER)


@pytest.fixture
def eichel_unter():
    return Card(Color.EICHEL, Type.UNTER)


@pytest.fixture
def gruen_unter():
    return Card(Color.GRUEN, Type.UNTER)


@pytest.fixture
def herz_unter():
    return Card(Color.HERZ, Type.UNTER)


@pytest.fixture
def schellen_unter():
    return Card(Color.SCHELLEN, Type.UNTER)


@pytest.fixture
def herz_seven():
    return Card(Color.HERZ, Type.SEVEN)


@pytest.fixture
def herz_eight():
    return Card(Color.HERZ, Type.EIGHT)


@pytest.fixture
def herz_ten():
    return Card(Color.HERZ, Type.TEN)


@pytest.fixture
def herz_sau():
    return Card(Color.HERZ, Type.SAU)


# tests for Ramsch, Sauspiel, Solo
def test_same_color(trumps, eichel_eight, eichel_nine, eichel_ten, eichel_sau):
    card_power_calculator = SauspielCardPowerCalculator()

    played_cards = [eichel_eight, eichel_nine, eichel_ten, eichel_sau]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=trumps
        )
        == eichel_sau
    )

    played_cards = [eichel_eight, eichel_nine, eichel_ten]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=trumps
        )
        == eichel_ten
    )


def test_mixed_colors(
    trumps, eichel_sau, eichel_ten, eichel_nine, schellen_sau, schellen_seven
):
    card_power_calculator = SauspielCardPowerCalculator()

    played_cards = [schellen_seven, eichel_nine, eichel_ten, eichel_sau]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=trumps
        )
        == schellen_seven
    )

    played_cards = [eichel_nine, schellen_sau, schellen_seven, eichel_sau]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=trumps
        )
        == eichel_sau
    )


def test_lead_trump(
    trumps,
    herz_seven,
    herz_eight,
    eichel_ober,
    gruen_ober,
    herz_ober,
    schellen_ober,
    eichel_unter,
    gruen_unter,
    herz_unter,
    schellen_unter,
    schellen_sau,
    eichel_sau,
    herz_sau,
    herz_ten,
):
    card_power_calculator = SauspielCardPowerCalculator()

    played_cards = [herz_seven, herz_sau, gruen_unter, eichel_ober]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=trumps
        )
        == eichel_ober
    )

    played_cards = [herz_eight, herz_seven, schellen_sau, eichel_sau]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=trumps
        )
        == herz_eight
    )

    played_cards = [eichel_ober, gruen_ober, herz_ober, schellen_ober]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=trumps
        )
        == eichel_ober
    )

    played_cards = [gruen_ober, herz_ober, schellen_ober, eichel_unter]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=trumps
        )
        == gruen_ober
    )

    played_cards = [herz_ober, schellen_ober, eichel_unter, gruen_unter]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=trumps
        )
        == herz_ober
    )

    played_cards = [schellen_ober, eichel_unter, gruen_unter, herz_unter]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=trumps
        )
        == schellen_ober
    )

    played_cards = [eichel_unter, gruen_unter, herz_unter, schellen_unter]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=trumps
        )
        == eichel_unter
    )

    played_cards = [gruen_unter, herz_unter, schellen_unter, herz_sau]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=trumps
        )
        == gruen_unter
    )

    played_cards = [herz_unter, schellen_unter, herz_sau, herz_ten]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=trumps
        )
        == herz_unter
    )


# special rules for Wenz
@pytest.fixture
def wenz_trumps():
    return [
        Card(card_color=Color.EICHEL, card_type=Type.UNTER),
        Card(card_color=Color.GRUEN, card_type=Type.UNTER),
        Card(card_color=Color.HERZ, card_type=Type.UNTER),
        Card(card_color=Color.SCHELLEN, card_type=Type.UNTER),
    ]


def test_same_color_ober(
    wenz_trumps,
    eichel_nine,
    eichel_ober,
    eichel_ten,
    eichel_koenig,
    eichel_sau,
    gruen_eight,
    gruen_ober,
):
    card_power_calculator = WenzCardPowerCalculator()

    played_cards = [eichel_nine, eichel_ober, eichel_ten, eichel_sau]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=wenz_trumps
        )
        == eichel_sau
    )

    played_cards = [eichel_nine, eichel_ober, eichel_ten, eichel_koenig]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=wenz_trumps
        )
        == eichel_ten
    )

    played_cards = [eichel_nine, eichel_ober, gruen_eight, eichel_koenig]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=wenz_trumps
        )
        == eichel_koenig
    )

    played_cards = [eichel_nine, eichel_ober, gruen_eight, gruen_ober]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=wenz_trumps
        )
        == eichel_ober
    )


def test_played_trump(
    wenz_trumps, eichel_nine, eichel_ober, eichel_unter, schellen_unter, eichel_sau
):
    card_power_calculator = WenzCardPowerCalculator()

    played_cards = [schellen_unter, eichel_ober, eichel_unter, eichel_nine]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=wenz_trumps
        )
        == eichel_unter
    )

    played_cards = [eichel_sau, eichel_ober, schellen_unter, eichel_nine]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=wenz_trumps
        )
        == schellen_unter
    )
