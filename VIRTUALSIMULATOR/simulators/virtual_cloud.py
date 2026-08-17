import random

from simulators.base import BaseSimulator


class VirtualCloud(BaseSimulator):

    # =========================================================
    # CLOUD PROFILES
    # =========================================================
    #
    # These represent different cloud-load conditions.
    #
    # Member C receives ONLY:
    #
    #     queue_delay
    #
    # The internal queue/load values are used by the simulator
    # to generate that delay.
    #
    # =========================================================

    CLOUD_PROFILES = {

        "idle": {
            "processing_capacity": 12.0,

            "base_delay": 5.0,

            "max_queue": 100.0,

            "queue_response": 0.25,

            "delay_per_queue": 0.45,

            "noise": 0.3
        },

        "moderate": {
            "processing_capacity": 7.0,

            "base_delay": 12.0,

            "max_queue": 100.0,

            "queue_response": 0.20,

            "delay_per_queue": 0.65,

            "noise": 0.5
        },

        "busy": {
            "processing_capacity": 4.0,

            "base_delay": 25.0,

            "max_queue": 100.0,

            "queue_response": 0.15,

            "delay_per_queue": 0.90,

            "noise": 0.8
        }
    }

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(
        self,
        initial_condition="idle",
        seed=42
    ):

        if initial_condition not in self.CLOUD_PROFILES:

            raise ValueError(
                f"Unknown cloud condition: "
                f"{initial_condition}. "
                f"Available: "
                f"{list(self.CLOUD_PROFILES.keys())}"
            )

        super().__init__("Virtual Cloud")

        self.random = random.Random(seed)

        self.seed = seed

        # Current cloud condition
        self.condition = initial_condition

        # Target cloud condition
        self.target_condition = initial_condition

        self.profile = self.CLOUD_PROFILES[
            initial_condition
        ]

        self.target_profile = self.profile

        self.reset()

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):

        self.queue = 0.0

        self.queue_delay = (
            self.profile["base_delay"]
        )

        self.time = 0

    # =========================================================
    # CHANGE CLOUD CONDITION
    # =========================================================

    def set_condition(
        self,
        condition
    ):

        """
        Change the target cloud-load condition.

        The cloud does not instantly jump to the new
        condition.

        Instead, queue behavior gradually changes.
        """

        if condition not in self.CLOUD_PROFILES:

            raise ValueError(
                f"Unknown cloud condition: "
                f"{condition}. "
                f"Available: "
                f"{list(self.CLOUD_PROFILES.keys())}"
            )

        self.target_condition = condition

        self.target_profile = (
            self.CLOUD_PROFILES[
                condition
            ]
        )

    # =========================================================
    # ADD REMOTE WORKLOAD
    # =========================================================

    def add_workload(
        self,
        workload=1.0
    ):

        """
        Add remote inference workload to the cloud queue.

        Example:

            cloud.add_workload(5)

        means approximately five workload units
        have arrived.
        """

        workload = max(
            0.0,
            float(workload)
        )

        self.queue += workload

        self.queue = min(
            self.queue,
            self.target_profile["max_queue"]
        )

    # =========================================================
    # UPDATE QUEUE
    # =========================================================

    def _update_queue(
        self,
        incoming_workload
    ):

        profile = self.target_profile

        # -----------------------------------------------------
        # Incoming workload
        # -----------------------------------------------------

        incoming_workload = max(
            0.0,
            float(incoming_workload)
        )

        self.queue += incoming_workload

        # -----------------------------------------------------
        # Cloud processing
        # -----------------------------------------------------

        processing_capacity = (
            profile["processing_capacity"]
        )

        # Some small variation in cloud processing
        processing_variation = self.random.uniform(
            0.90,
            1.10
        )

        actual_processing = (
            processing_capacity *
            processing_variation
        )

        # Cannot process more than currently queued
        actual_processing = min(
            actual_processing,
            self.queue
        )

        self.queue -= actual_processing

        # -----------------------------------------------------
        # Queue cannot become negative
        # -----------------------------------------------------

        self.queue = max(
            0.0,
            self.queue
        )

        # -----------------------------------------------------
        # Maximum queue limit
        # -----------------------------------------------------

        self.queue = min(
            self.queue,
            profile["max_queue"]
        )

    # =========================================================
    # UPDATE QUEUE DELAY
    # =========================================================

    def _update_delay(self):

        profile = self.target_profile

        # -----------------------------------------------------
        # Queue-based delay
        # -----------------------------------------------------

        target_delay = (
            profile["base_delay"]
            +
            self.queue *
            profile["delay_per_queue"]
        )

        # -----------------------------------------------------
        # Small cloud processing variation
        # -----------------------------------------------------

        noise = self.random.gauss(
            0,
            profile["noise"]
        )

        target_delay += noise

        # -----------------------------------------------------
        # Smooth delay transition
        # -----------------------------------------------------

        response = profile[
            "queue_response"
        ]

        difference = (
            target_delay -
            self.queue_delay
        )

        self.queue_delay += (
            response *
            difference
        )

        # -----------------------------------------------------
        # Physical lower bound
        # -----------------------------------------------------

        self.queue_delay = max(
            1.0,
            self.queue_delay
        )

    # =========================================================
    # UPDATE
    # =========================================================

    def update(
        self,
        incoming_workload=0.0
    ):

        """
        Advance the cloud simulation by one step.

        incoming_workload:
            Amount of remote inference workload arriving
            at the cloud during this step.
        """

        self._update_queue(
            incoming_workload
        )

        self._update_delay()

        self.tick()

    # =========================================================
    # GET STATE
    # =========================================================

    def get_state(self):

        """
        Return ONLY the value required by Member C.
        """

        return {
            "queue_delay": round(
                self.queue_delay,
                2
            )
        }