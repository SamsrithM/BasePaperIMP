from simulators.virtual_edge import VirtualEdgeDevice
from simulators.virtual_network import VirtualNetwork
from simulators.virtual_cloud import VirtualCloud


class MemberBSimulation:

    def __init__(
        self,
        device_type="smartphone",
        network_condition="good",
        cloud_condition="idle",
        seed=42
    ):
        self.seed = seed

        # -----------------------------------------------------
        # EDGE
        # -----------------------------------------------------

        self.edge = VirtualEdgeDevice(
            device_type=device_type,
            seed=seed
        )

        # -----------------------------------------------------
        # NETWORK
        # -----------------------------------------------------

        self.network = VirtualNetwork(
            initial_condition=network_condition,
            seed=seed + 1
        )

        # -----------------------------------------------------
        # CLOUD
        # -----------------------------------------------------

        self.cloud = VirtualCloud(
            initial_condition=cloud_condition,
            seed=seed + 2
        )

        self.history = []
        self.step = 0

    # =========================================================
    # GENERATE EDGE WORKLOAD
    # =========================================================

    def generate_workload(self):

        """
        Generate a synthetic inference workload.

        This belongs entirely to Member B.

        It is NOT related to Member A's model.
        """

        return {
            "cpu": round(
                self.edge.random.uniform(
                    10.0,
                    25.0
                ),
                2
            ),

            "ram": round(
                self.edge.random.uniform(
                    3.0,
                    8.0
                ),
                2
            ),

            "energy": round(
                self.edge.random.uniform(
                    0.5,
                    1.5
                ),
                2
            )
        }

    # =========================================================
    # GENERATE CLOUD WORKLOAD
    # =========================================================

    def generate_cloud_workload(self):

        """
        Generate synthetic remote workload.

        This is completely internal to Member B.

        It represents changing cloud demand in the
        simulation environment, NOT a model-splitting
        decision.
        """

        if self.cloud.target_condition == "idle":

            return round(
                self.cloud.random.uniform(
                    0.5,
                    2.5
                ),
                2
            )

        elif self.cloud.target_condition == "moderate":

            return round(
                self.cloud.random.uniform(
                    3.0,
                    6.0
                ),
                2
            )

        elif self.cloud.target_condition == "busy":

            return round(
                self.cloud.random.uniform(
                    6.0,
                    10.0
                ),
                2
            )

        return 0.0

    # =========================================================
    # RUN ONE STEP
    # =========================================================

    def run_step(self):

        # -----------------------------------------------------
        # 1. Generate synthetic workload
        # -----------------------------------------------------

        workload = self.generate_workload()

        # -----------------------------------------------------
        # 2. Generate cloud demand
        # -----------------------------------------------------

        cloud_workload = (
            self.generate_cloud_workload()
        )

        # -----------------------------------------------------
        # 3. Update edge
        # -----------------------------------------------------

        self.edge.update(
            workload
        )

        # -----------------------------------------------------
        # 4. Update network
        # -----------------------------------------------------

        self.network.update()

        # -----------------------------------------------------
        # 5. Update cloud
        # -----------------------------------------------------

        self.cloud.update(
            incoming_workload=cloud_workload
        )

        # -----------------------------------------------------
        # 6. Collect Member B state
        # -----------------------------------------------------

        state = {

            "step": self.step,

            "edge": self.edge.get_state(),

            "network": self.network.get_state(),

            "cloud": self.cloud.get_state(),

            "workload": workload,

            "cloud_workload": cloud_workload
        }

        # -----------------------------------------------------
        # 7. Store history
        # -----------------------------------------------------

        self.history.append(
            state
        )

        self.step += 1

        # -----------------------------------------------------
        # 8. Allow edge to recover slightly
        # -----------------------------------------------------

        self.edge.idle()

        return state

    # =========================================================
    # CHANGE NETWORK CONDITION
    # =========================================================

    def set_network_condition(
        self,
        condition
    ):

        self.network.set_condition(
            condition
        )

    # =========================================================
    # CHANGE CLOUD CONDITION
    # =========================================================

    def set_cloud_condition(
        self,
        condition
    ):

        self.cloud.set_condition(
            condition
        )

    # =========================================================
    # GET HISTORY
    # =========================================================

    def get_history(self):

        return self.history

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):

        self.edge.reset()

        self.network.reset()

        self.cloud.reset()

        self.history = []

        self.step = 0