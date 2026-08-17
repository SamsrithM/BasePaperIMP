from itertools import product

from simulators.simulation_runner import MemberBSimulation


class ScenarioManager:

    # =========================================================
    # AVAILABLE CONDITIONS
    # =========================================================

    DEVICE_TYPES = [
        "smartphone",
        "raspberry_pi"
    ]

    NETWORK_CONDITIONS = [
        "good",
        "moderate",
        "poor"
    ]

    CLOUD_CONDITIONS = [
        "idle",
        "moderate",
        "busy"
    ]

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(
        self,
        steps_per_scenario=100,
        seed=42
    ):

        self.steps_per_scenario = (
            steps_per_scenario
        )

        self.seed = seed

        self.scenarios = []

        self.results = []

        self._create_scenarios()

    # =========================================================
    # CREATE ALL COMBINATIONS
    # =========================================================

    def _create_scenarios(self):

        """
        Generate every combination of:

            2 devices
            3 network conditions
            3 cloud conditions

        Total:

            2 × 3 × 3 = 18 scenarios
        """

        combinations = product(
            self.DEVICE_TYPES,
            self.NETWORK_CONDITIONS,
            self.CLOUD_CONDITIONS
        )

        for scenario_id, combination in enumerate(
            combinations,
            start=1
        ):

            device_type = combination[0]
            network_condition = combination[1]
            cloud_condition = combination[2]

            scenario = {

                "scenario_id": scenario_id,

                "device_type": device_type,

                "network_condition":
                    network_condition,

                "cloud_condition":
                    cloud_condition
            }

            self.scenarios.append(
                scenario
            )

    # =========================================================
    # GET SCENARIOS
    # =========================================================

    def get_scenarios(self):

        return self.scenarios

    # =========================================================
    # NUMBER OF SCENARIOS
    # =========================================================

    def get_scenario_count(self):

        return len(
            self.scenarios
        )

    # =========================================================
    # RUN ONE SCENARIO
    # =========================================================

    def run_scenario(
        self,
        scenario
    ):

        scenario_id = scenario[
            "scenario_id"
        ]

        # -----------------------------------------------------
        # Create independent simulation
        # -----------------------------------------------------

        simulation = MemberBSimulation(

            device_type=scenario[
                "device_type"
            ],

            network_condition=scenario[
                "network_condition"
            ],

            cloud_condition=scenario[
                "cloud_condition"
            ],

            seed=self.seed + scenario_id
        )

        history = []

        # -----------------------------------------------------
        # Run simulation
        # -----------------------------------------------------

        for _ in range(
            self.steps_per_scenario
        ):

            state = (
                simulation.run_step()
            )

            # Add scenario information to
            # every simulation record.

            state["scenario_id"] = (
                scenario_id
            )

            state["device_type"] = (
                scenario["device_type"]
            )

            state["network_condition"] = (
                scenario["network_condition"]
            )

            state["cloud_condition"] = (
                scenario["cloud_condition"]
            )

            history.append(
                state
            )

        return history

    # =========================================================
    # RUN ALL SCENARIOS
    # =========================================================

    def run_all(self):

        self.results = []

        print(
            f"\nRunning "
            f"{self.get_scenario_count()} scenarios..."
        )

        print(
            f"Steps per scenario: "
            f"{self.steps_per_scenario}"
        )

        print(
            f"Total simulation steps: "
            f"{self.get_scenario_count() * self.steps_per_scenario}"
        )

        print(
            "\n"
        )

        for scenario in self.scenarios:

            scenario_id = scenario[
                "scenario_id"
            ]

            print(
                f"[{scenario_id:02d}/"
                f"{self.get_scenario_count():02d}] "
                f"{scenario['device_type']} | "
                f"{scenario['network_condition']} | "
                f"{scenario['cloud_condition']}"
            )

            history = self.run_scenario(
                scenario
            )

            self.results.extend(
                history
            )

        print(
            "\nAll scenarios completed."
        )

        return self.results

    # =========================================================
    # GET RESULTS
    # =========================================================

    def get_results(self):

        return self.results