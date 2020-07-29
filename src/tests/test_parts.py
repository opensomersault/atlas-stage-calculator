import pytest
import src.parts as parts
from src.constants import GRAVITATIONAL_ACCELERATION as g


# Tank Tests
@pytest.mark.parametrize(
    "tank_name, expected_vals",
    [
        ('Atlas-Tapered', (0.175, 3.5)),
        ('Atlas-Long', (0.55, 11))
    ]
)
def test_tank(tank_name: str, expected_vals: tuple):
    tank = parts.Tank(tank_name)
    # Tanks by definition don't produce thrust
    assert tank.thrust == 0.
    assert tank.isp == 0.
    assert tank.exhaust_mass_flow_rate == 0.
    # Check
    assert tank.dry_mass == expected_vals[0]
    assert tank.propellant_mass == expected_vals[1]
    assert tank.is_composite() is False


def test_tank_custom():
    tank = parts.Tank()
    assert tank._tank_name == 'Custom'
    assert tank.thrust == 0.
    assert tank.propellant_mass == 0.


def test_tank_error():
    with pytest.raises(ValueError, match='not a fuel tank'):
        parts.Tank('LR89-5')


def test_tank_setters():
    tank = parts.Tank()

    assert tank.dry_mass == 0
    tank.dry_mass = 1
    assert tank.dry_mass == 1

    assert tank.propellant_mass == 0
    tank.propellant_mass = 1
    assert tank.propellant_mass == 1


# Engine tests
@pytest.mark.parametrize(
    "engine_name, expected_vals",
    [
        ('LR89-5', (205., 1.75, 290)),
        ('LR89-7', (236., 1.75, 294)),
        ('RS56', (261., 1.75, 299))
    ]
)
def test_engine(engine_name, expected_vals):
    engine = parts.Engine(engine_name)
    assert engine.propellant_mass == 0.
    assert engine.thrust == expected_vals[0]
    assert engine.dry_mass == expected_vals[1]
    assert engine.isp == expected_vals[2]
    assert engine.is_composite() is False
    assert engine.exhaust_mass_flow_rate == (
        expected_vals[0] / (g * expected_vals[2])
    )


def test_engine_custom():
    engine = parts.Engine()
    assert engine.dry_mass == 0.
    assert engine.thrust == 0.
    assert engine.isp == 0


def test_engine_not_an_engine():
    with pytest.raises(ValueError, match='not an engine'):
        parts.Engine('Atlas-Long')


def test_engine_setters():
    engine = parts.Engine()
    assert engine.dry_mass == 0.
    engine.dry_mass = 1.
    assert engine.dry_mass == 1.

    assert engine.isp == 0.
    engine.isp = 1.
    assert engine.isp == 1.

    assert engine.thrust == 0.
    engine.thrust = 1.
    assert engine.thrust == 1.


# Assembly Tests
@pytest.fixture
def engine():
    engine = parts.Engine()
    engine.dry_mass = 1
    engine.thrust = 2
    engine.isp = 1
    return engine


@pytest.fixture
def tank():
    tank = parts.Tank()
    tank.dry_mass = 1
    tank.propellant_mass = 1
    return tank


def test_stage_construction(tank):
    stage = parts.Stage()
    stage.add(tank)
    assert tank in stage._parts
    assert tank.parent == stage

    stage.remove(tank)
    assert tank not in stage._parts
    assert tank.parent is None


@pytest.fixture
def stage(engine, tank):
    stage = parts.Stage()
    stage.add(engine.copy())
    stage.add(engine.copy())
    stage.add(tank.copy())
    return stage


def test_stage_calculations(stage):
    assert stage.dry_mass == 3.
    assert stage.propellant_mass == 1.
    assert stage.thrust == 4.
    assert stage.isp == 1.
    assert stage.exhaust_mass_flow_rate == stage.thrust / (g * stage.isp)


def test_stage_composite(stage):
    assert stage.is_composite() is True


@pytest.mark.parametrize(
    "fuel_remaining, expected_value",
    [
        (1, 4. / (4*g)),
        (0.75, 4. / (3.75*g)),
        (0, 4. / (3*g))
    ]
)
def test_stage_twr(stage, fuel_remaining, expected_value):
    assert stage.thrust_to_weight_ratio(fuel_remaining) == expected_value


def test_vehicle_calculations(stage):
    vehicle = parts.Vehicle()
    stage1 = stage.copy()
    stage1._parts[0].thrust = 3
    stage2 = stage
    vehicle.add(stage1)
    vehicle.add(stage2)

    assert vehicle.dry_mass == 6.
    assert vehicle.propellant_mass == 2.
    assert vehicle.thrust == 5.
    assert vehicle.isp == 1.
    assert vehicle.exhaust_mass_flow_rate == stage1.exhaust_mass_flow_rate


def test_add_parent(stage):
    vehicle = parts.Vehicle
    stage.parent = vehicle

    assert stage.parent == vehicle