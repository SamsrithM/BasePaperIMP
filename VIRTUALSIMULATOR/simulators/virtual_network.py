import random

from simulators.base import BaseSimulator


class VirtualNetwork(BaseSimulator):

    # =========================================================
    # NETWORK PROFILES
    # =========================================================
    #
    # These are synthetic profiles designed to model realistic
    # network behavior.
    #
    # Member C receives ONLY:
    #     bandwidth
    #     latency
    #
    # =========================================================

    NETWORK_PROFILES = {

        "good": {
            "bandwidth_min": 60.0,
            "bandwidth_max": 120.0,

            "latency_min": 5.0,
            "latency_max": 15.0,

            # Short-term bandwidth fluctuation
            "bandwidth_noise": 2.5,

            # Speed of transition toward target
            "transition_rate": 0.12,

            # Speed of latency adjustment
            "latency_response": 0.30,

            # Small latency variation
            "latency_noise": 0.8
        },

        "moderate": {
            "bandwidth_min": 25.0,
            "bandwidth_max": 70.0,

            "latency_min": 12.0,
            "latency_max": 35.0,

            "bandwidth_noise": 2.0,

            "transition_rate": 0.10,

            "latency_response": 0.28,

            "latency_noise": 1.0
        },

        "poor": {
            "bandwidth_min": 5.0,
            "bandwidth_max": 20.0,

            "latency_min": 35.0,
            "latency_max": 80.0,

            "bandwidth_noise": 1.2,

            "transition_rate": 0.08,

            "latency_response": 0.25,

            "latency_noise": 1.5
        }
    }

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(
        self,
        initial_condition="good",
        seed=42
    ):

        if initial_condition not in self.NETWORK_PROFILES:
            raise ValueError(
                f"Unknown network condition: "
                f"{initial_condition}. "
                f"Available: "
                f"{list(self.NETWORK_PROFILES.keys())}"
            )

        super().__init__("Virtual Network")

        self.random = random.Random(seed)

        self.seed = seed

        # Current condition
        self.condition = initial_condition

        # Target condition
        self.target_condition = initial_condition

        # Current profile
        self.profile = self.NETWORK_PROFILES[
            initial_condition
        ]

        # Target profile
        self.target_profile = self.profile

        # Target bandwidth for the current condition
        self.target_bandwidth = None

        self.reset()

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):

        profile = self.profile

        # -----------------------------------------------------
        # Initial bandwidth
        # -----------------------------------------------------

        self.bandwidth = (
            profile["bandwidth_min"]
            +
            profile["bandwidth_max"]
        ) / 2.0

        # -----------------------------------------------------
        # Select one stable target for this condition
        # -----------------------------------------------------

        self.target_bandwidth = (
            self._generate_target_bandwidth(
                profile
            )
        )

        # -----------------------------------------------------
        # Initial latency based on bandwidth
        # -----------------------------------------------------

        self.latency = self._calculate_latency(
            self.bandwidth,
            profile
        )

        self.time = 0

    # =========================================================
    # GENERATE TARGET BANDWIDTH
    # =========================================================

    def _generate_target_bandwidth(
        self,
        profile
    ):

        """
        Select one target bandwidth for the current
        network condition.

        The target stays relatively stable while
        short-term fluctuations occur around it.
        """

        minimum = profile[
            "bandwidth_min"
        ]

        maximum = profile[
            "bandwidth_max"
        ]

        midpoint = (
            minimum +
            maximum
        ) / 2.0

        spread = (
            maximum -
            minimum
        )

        target = (
            midpoint
            +
            self.random.gauss(
                0,
                spread * 0.12
            )
        )

        target = max(
            minimum,
            min(
                target,
                maximum
            )
        )

        return target

    # =========================================================
    # CALCULATE LATENCY
    # =========================================================

    def _calculate_latency(
        self,
        bandwidth,
        profile
    ):

        bandwidth_min = profile[
            "bandwidth_min"
        ]

        bandwidth_max = profile[
            "bandwidth_max"
        ]

        latency_min = profile[
            "latency_min"
        ]

        latency_max = profile[
            "latency_max"
        ]

        bandwidth_range = (
            bandwidth_max -
            bandwidth_min
        )

        if bandwidth_range <= 0:

            ratio = 0.5

        else:

            ratio = (
                bandwidth -
                bandwidth_min
            ) / bandwidth_range

        ratio = max(
            0.0,
            min(
                ratio,
                1.0
            )
        )

        # -----------------------------------------------------
        # High bandwidth -> low latency
        # Low bandwidth  -> high latency
        # -----------------------------------------------------

        latency = (
            latency_max
            -
            ratio *
            (
                latency_max -
                latency_min
            )
        )

        return latency

    # =========================================================
    # SET NETWORK CONDITION
    # =========================================================

    def set_condition(
        self,
        condition
    ):

        """
        Set a new TARGET network condition.

        The network does NOT instantly jump to the
        new condition.

        Instead:

            current state
                  ↓
            gradual transition
                  ↓
            target condition
        """

        if condition not in self.NETWORK_PROFILES:

            raise ValueError(
                f"Unknown network condition: "
                f"{condition}. "
                f"Available: "
                f"{list(self.NETWORK_PROFILES.keys())}"
            )

        self.target_condition = condition

        self.target_profile = (
            self.NETWORK_PROFILES[
                condition
            ]
        )

        # Select ONE target bandwidth for this
        # transition rather than generating a new
        # target every timestep.

        self.target_bandwidth = (
            self._generate_target_bandwidth(
                self.target_profile
            )
        )

    # =========================================================
    # UPDATE BANDWIDTH
    # =========================================================

    def _update_bandwidth(self):

        profile = self.target_profile

        # -----------------------------------------------------
        # Move gradually toward target bandwidth
        # -----------------------------------------------------

        difference = (
            self.target_bandwidth -
            self.bandwidth
        )

        transition = (
            profile["transition_rate"]
            *
            difference
        )

        # -----------------------------------------------------
        # Short-term network fluctuation
        # -----------------------------------------------------

        noise = self.random.gauss(
            0,
            profile["bandwidth_noise"]
        )

        self.bandwidth += (
            transition +
            noise
        )

        # -----------------------------------------------------
        # IMPORTANT:
        #
        # Do NOT clamp bandwidth to the target profile's
        # min/max here.
        #
        # Otherwise:
        #
        # GOOD -> POOR
        #
        # could immediately become:
        #
        # 90 Mbps -> 20 Mbps
        #
        # We only enforce broad physical limits.
        # -----------------------------------------------------

        self.bandwidth = max(
            1.0,
            min(
                self.bandwidth,
                200.0
            )
        )

    # =========================================================
    # UPDATE LATENCY
    # =========================================================

    def _update_latency(self):

        profile = self.target_profile

        # -----------------------------------------------------
        # Calculate latency expected from current bandwidth
        # -----------------------------------------------------

        target_latency = (
            self._calculate_latency(
                self.bandwidth,
                profile
            )
        )

        # -----------------------------------------------------
        # Small natural latency variation
        # -----------------------------------------------------

        noise = self.random.gauss(
            0,
            profile["latency_noise"]
        )

        target_latency += noise

        # -----------------------------------------------------
        # Gradual latency movement
        # -----------------------------------------------------

        response = profile[
            "latency_response"
        ]

        difference = (
            target_latency -
            self.latency
        )

        self.latency += (
            response *
            difference
        )

        # -----------------------------------------------------
        # Broad physical safety limit
        # -----------------------------------------------------

        self.latency = max(
            1.0,
            min(
                self.latency,
                150.0
            )
        )

    # =========================================================
    # CHECK WHETHER TRANSITION IS COMPLETE
    # =========================================================

    def _update_condition_status(self):

        profile = self.target_profile

        # -----------------------------------------------------
        # We consider the transition sufficiently complete
        # when bandwidth is close to its target.
        # -----------------------------------------------------

        bandwidth_difference = abs(
            self.bandwidth -
            self.target_bandwidth
        )

        bandwidth_tolerance = max(
            3.0,
            (
                profile["bandwidth_max"]
                -
                profile["bandwidth_min"]
            ) * 0.10
        )

        if bandwidth_difference <= bandwidth_tolerance:

            self.condition = (
                self.target_condition
            )

            self.profile = (
                self.target_profile
            )

    # =========================================================
    # UPDATE
    # =========================================================

    def update(self):

        """
        Advance the network by one simulation step.
        """

        self._update_bandwidth()

        self._update_latency()

        self._update_condition_status()

        self.tick()

    # =========================================================
    # GET STATE
    # =========================================================

    def get_state(self):

        """
        Return exactly the values required by Member C.

        No extra network variables are exposed.
        """

        return {

            "bandwidth": round(
                self.bandwidth,
                2
            ),

            "latency": round(
                self.latency,
                2
            )
        }