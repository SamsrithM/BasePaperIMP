import random

from simulators.base import BaseSimulator


class VirtualEdgeDevice(BaseSimulator):

    # =========================================================
    # DEVICE PROFILES
    # =========================================================

    DEVICE_PROFILES = {

        "smartphone": {

            # CPU behavior
            "cpu": {
                "idle": 15.0,
                "min": 5.0,
                "max": 90.0,

                # How strongly inference affects CPU
                "workload_factor": 2.2,

                # How quickly CPU moves toward its target
                "response_rate": 0.55,

                # Recovery during idle
                "recovery_rate": 4.0,

                # Normal background activity
                "background_load": 5.0
            },

            # RAM behavior
            "ram": {
                "idle": 20.0,
                "min": 15.0,
                "max": 90.0,

                # Memory pressure caused by inference
                "workload_factor": 1.8,

                # Memory released during idle
                "release_rate": 2.0
            },

            # Battery behavior
            "battery": {
                "initial": 100.0,

                # Non-zero means battery-powered
                "capacity_mah": 5000,

                # Small background drain
                "base_drain": 0.015,

                # Energy cost multiplier
                "workload_drain": 0.025
            }
        },

        # -----------------------------------------------------

        "raspberry_pi": {

            "cpu": {
                "idle": 20.0,
                "min": 5.0,
                "max": 95.0,

                # Same inference creates more CPU pressure
                "workload_factor": 2.8,

                "response_rate": 0.45,

                "recovery_rate": 3.0,

                "background_load": 4.0
            },

            "ram": {
                "idle": 22.0,
                "min": 10.0,
                "max": 95.0,

                "workload_factor": 2.2,

                "release_rate": 1.5
            },

            "battery": {
                "initial": 100.0,

                # 0 = externally powered
                "capacity_mah": 0,

                "base_drain": 0.0,
                "workload_drain": 0.0
            }
        },

        # -----------------------------------------------------

        "low_power_iot": {

            "cpu": {
                "idle": 12.0,
                "min": 5.0,
                "max": 95.0,

                # Very sensitive to computation
                "workload_factor": 3.2,

                "response_rate": 0.40,

                "recovery_rate": 2.0,

                "background_load": 3.0
            },

            "ram": {
                "idle": 18.0,
                "min": 10.0,
                "max": 90.0,

                "workload_factor": 2.5,

                "release_rate": 1.0
            },

            "battery": {
                "initial": 100.0,

                "capacity_mah": 2500,

                "base_drain": 0.025,

                "workload_drain": 0.040
            }
        }
    }

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(
        self,
        device_type="smartphone",
        seed=42
    ):

        if device_type not in self.DEVICE_PROFILES:
            raise ValueError(
                f"Unknown device type: {device_type}. "
                f"Available: {list(self.DEVICE_PROFILES.keys())}"
            )

        super().__init__("Virtual Edge")

        self.device_type = device_type

        self.profile = self.DEVICE_PROFILES[
            device_type
        ]

        # Dedicated RNG makes experiments reproducible
        self.random = random.Random(seed)

        self.seed = seed

        self.reset()

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):

        cpu_cfg = self.profile["cpu"]
        ram_cfg = self.profile["ram"]
        battery_cfg = self.profile["battery"]

        self.state = {

            "cpu": cpu_cfg["idle"],

            "ram": ram_cfg["idle"],

            "battery": battery_cfg["initial"]
        }

        self.time = 0

    # =========================================================
    # UPDATE AFTER INFERENCE
    # =========================================================

    def update(self, inference_cost):
        """
        Update device state after one inference.

        Expected workload:

        {
            "cpu": 20,
            "ram": 5,
            "energy": 1.0
        }

        Only CPU, RAM and battery are exposed
        to Member C.
        """

        cpu_cfg = self.profile["cpu"]
        ram_cfg = self.profile["ram"]
        battery_cfg = self.profile["battery"]

        # =====================================================
        # 1. CPU UTILIZATION
        # =====================================================

        workload_cpu = max(
            0.0,
            float(
                inference_cost.get("cpu", 0)
            )
        )

        # Desired CPU level for this workload
        target_cpu = (
            cpu_cfg["idle"]
            +
            cpu_cfg["background_load"]
            +
            workload_cpu *
            cpu_cfg["workload_factor"]
        )

        target_cpu = max(
            cpu_cfg["min"],
            min(
                target_cpu,
                cpu_cfg["max"]
            )
        )

        # CPU moves toward target instead of
        # accumulating forever.
        cpu_difference = (
            target_cpu -
            self.state["cpu"]
        )

        cpu_change = (
            cpu_cfg["response_rate"]
            *
            cpu_difference
        )

        # Small measurement/system variation
        cpu_noise = self.random.gauss(
            0,
            0.8
        )

        self.state["cpu"] += (
            cpu_change +
            cpu_noise
        )

        self.state["cpu"] = max(
            cpu_cfg["min"],
            min(
                self.state["cpu"],
                cpu_cfg["max"]
            )
        )

        # =====================================================
        # 2. RAM UTILIZATION
        # =====================================================

        workload_ram = max(
            0.0,
            float(
                inference_cost.get("ram", 0)
            )
        )

        target_ram = (
            ram_cfg["idle"]
            +
            workload_ram *
            ram_cfg["workload_factor"]
        )

        target_ram = max(
            ram_cfg["min"],
            min(
                target_ram,
                ram_cfg["max"]
            )
        )

        # Move partly toward memory pressure
        ram_difference = (
            target_ram -
            self.state["ram"]
        )

        ram_change = (
            0.45 *
            ram_difference
        )

        ram_noise = self.random.gauss(
            0,
            0.25
        )

        self.state["ram"] += (
            ram_change +
            ram_noise
        )

        self.state["ram"] = max(
            ram_cfg["min"],
            min(
                self.state["ram"],
                ram_cfg["max"]
            )
        )

        # =====================================================
        # 3. BATTERY
        # =====================================================

        if battery_cfg["capacity_mah"] > 0:

            energy_cost = max(
                0.0,
                float(
                    inference_cost.get(
                        "energy",
                        0
                    )
                )
            )

            # Current CPU contributes to power consumption
            cpu_factor = (
                self.state["cpu"] / 100.0
            )

            # Base workload energy
            workload_drain = (
                energy_cost *
                battery_cfg["workload_drain"]
            )

            # Higher CPU means slightly higher drain
            cpu_drain = (
                cpu_factor *
                battery_cfg["base_drain"]
            )

            total_drain = (
                battery_cfg["base_drain"]
                +
                workload_drain
                +
                cpu_drain
            )

            self.state["battery"] -= total_drain

            self.state["battery"] = max(
                0.0,
                self.state["battery"]
            )

        self.tick()

    # =========================================================
    # IDLE / RECOVERY
    # =========================================================

    def idle(self):
        """
        Simulate a period where no inference is running.

        CPU gradually moves toward the device idle level.
        RAM releases temporary memory.
        Battery does not recover.
        """

        cpu_cfg = self.profile["cpu"]
        ram_cfg = self.profile["ram"]

        # -----------------------------------------------------
        # CPU RECOVERY
        # -----------------------------------------------------

        idle_target = (
            cpu_cfg["idle"]
            +
            cpu_cfg["background_load"]
        )

        cpu_difference = (
            self.state["cpu"] -
            idle_target
        )

        recovery = min(
            cpu_cfg["recovery_rate"],
            max(0.0, cpu_difference)
        )

        self.state["cpu"] -= recovery

        # Small natural variation
        self.state["cpu"] += self.random.gauss(
            0,
            0.4
        )

        self.state["cpu"] = max(
            cpu_cfg["min"],
            min(
                self.state["cpu"],
                cpu_cfg["max"]
            )
        )

        # -----------------------------------------------------
        # RAM RELEASE
        # -----------------------------------------------------

        self.state["ram"] -= (
            ram_cfg["release_rate"]
        )

        # Don't release below normal idle memory
        self.state["ram"] = max(
            ram_cfg["idle"],
            self.state["ram"]
        )

        self.tick()

    # =========================================================
    # GET STATE
    # =========================================================

    def get_state(self):
        """
        Return exactly the values required by Member C.
        """

        return {

            "cpu": round(
                self.state["cpu"],
                2
            ),

            "ram": round(
                self.state["ram"],
                2
            ),

            "battery": round(
                self.state["battery"],
                2
            )
        }