import pandas as pd


FILE = "results/member_b_results.csv"


REQUIRED_COLUMNS = [
    "step",
    "scenario_id",
    "device_type",
    "network_condition",
    "cloud_condition",

    "edge_cpu",
    "edge_ram",
    "edge_battery",

    "bandwidth",
    "latency",

    "queue_delay",

    "workload_cpu",
    "workload_ram",
    "workload_energy",

    "cloud_workload"
]


def load_data():

    df = pd.read_csv(FILE)

    assert len(df) > 0, (
        "Member B dataset is empty"
    )

    return df


def test_required_columns():

    df = load_data()

    for column in REQUIRED_COLUMNS:

        assert column in df.columns, (
            f"Missing required column: {column}"
        )


def test_edge_ranges():

    df = load_data()

    assert df["edge_cpu"].between(
        0, 100
    ).all()

    assert df["edge_ram"].between(
        0, 100
    ).all()

    assert df["edge_battery"].between(
        0, 100
    ).all()


def test_network_values():

    df = load_data()

    assert (
        df["bandwidth"] >= 0
    ).all()

    assert (
        df["latency"] >= 0
    ).all()


def test_cloud_values():

    df = load_data()

    assert (
        df["queue_delay"] >= 0
    ).all()

    assert (
        df["cloud_workload"] >= 0
    ).all()


def test_all_scenarios_exist():

    df = load_data()

    assert df["scenario_id"].nunique() == 18


def test_both_devices_exist():

    df = load_data()

    devices = set(
        df["device_type"]
    )

    assert "smartphone" in devices
    assert "raspberry_pi" in devices


def test_network_conditions_exist():

    df = load_data()

    conditions = set(
        df["network_condition"]
    )

    assert "good" in conditions
    assert "moderate" in conditions
    assert "poor" in conditions


def test_cloud_conditions_exist():

    df = load_data()

    conditions = set(
        df["cloud_condition"]
    )

    assert "idle" in conditions
    assert "moderate" in conditions
    assert "busy" in conditions


def test_dynamic_values():

    df = load_data()

    # At least one environmental variable
    # must change during simulation.

    assert (
        df["edge_cpu"].nunique() > 1
    )

    assert (
        df["bandwidth"].nunique() > 1
    )

    assert (
        df["latency"].nunique() > 1
    )


def test_each_scenario_has_multiple_steps():

    df = load_data()

    steps_per_scenario = (
        df.groupby(
            "scenario_id"
        )["step"]
        .nunique()
    )

    assert (
        steps_per_scenario >= 2
    ).all()


def test_good_network_is_better_than_poor():

    df = load_data()

    good = df[
        df["network_condition"] == "good"
    ]

    poor = df[
        df["network_condition"] == "poor"
    ]

    assert (
        good["bandwidth"].mean()
        >
        poor["bandwidth"].mean()
    )

    assert (
        good["latency"].mean()
        <
        poor["latency"].mean()
    )


def test_busy_cloud_has_more_delay():

    df = load_data()

    idle = df[
        df["cloud_condition"] == "idle"
    ]

    busy = df[
        df["cloud_condition"] == "busy"
    ]

    assert (
        busy["queue_delay"].mean()
        >
        idle["queue_delay"].mean()
    )