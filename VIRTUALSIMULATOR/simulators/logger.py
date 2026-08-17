import csv
import json
import os


class SimulationLogger:

    def __init__(self):
        self.records = []

    # =========================================================
    # ADD RECORD
    # =========================================================

    def log(self, state):
        """
        Store one simulation state.
        """

        self.records.append(state.copy())

    # =========================================================
    # ADD MULTIPLE RECORDS
    # =========================================================

    def log_many(self, states):
        """
        Store multiple simulation states.
        """

        for state in states:
            self.log(state)

    # =========================================================
    # GET RECORDS
    # =========================================================

    def get_records(self):
        return self.records

    # =========================================================
    # FLATTEN RECORD
    # =========================================================

    def _flatten(self, state):

        return {
            "step": state["step"],
            "scenario_id": state.get("scenario_id"),

            "device_type": state.get(
                "device_type"
            ),

            "network_condition": state.get(
                "network_condition"
            ),

            "cloud_condition": state.get(
                "cloud_condition"
            ),

            # -----------------------------
            # EDGE
            # -----------------------------

            "edge_cpu": state["edge"]["cpu"],

            "edge_ram": state["edge"]["ram"],

            "edge_battery": state["edge"]["battery"],

            # -----------------------------
            # NETWORK
            # -----------------------------

            "bandwidth": state[
                "network"
            ]["bandwidth"],

            "latency": state[
                "network"
            ]["latency"],

            # -----------------------------
            # CLOUD
            # -----------------------------

            "queue_delay": state[
                "cloud"
            ]["queue_delay"],

            # -----------------------------
            # EDGE WORKLOAD
            # -----------------------------

            "workload_cpu": state[
                "workload"
            ]["cpu"],

            "workload_ram": state[
                "workload"
            ]["ram"],

            "workload_energy": state[
                "workload"
            ]["energy"],

            # -----------------------------
            # CLOUD WORKLOAD
            # -----------------------------

            "cloud_workload": state.get(
                "cloud_workload",
                0.0
            )
        }

    # =========================================================
    # SAVE CSV
    # =========================================================

    def save_csv(
        self,
        filepath="results/member_b_results.csv"
    ):

        if not self.records:

            raise ValueError(
                "No simulation records to save."
            )

        # -----------------------------------------------------
        # Create directory if necessary
        # -----------------------------------------------------

        directory = os.path.dirname(
            filepath
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        # -----------------------------------------------------
        # Flatten records
        # -----------------------------------------------------

        rows = [
            self._flatten(record)
            for record in self.records
        ]

        # -----------------------------------------------------
        # CSV columns
        # -----------------------------------------------------

        fieldnames = [
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

        # -----------------------------------------------------
        # Write CSV
        # -----------------------------------------------------

        with open(
            filepath,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            writer.writerows(rows)

        print(
            f"\nCSV saved to: {filepath}"
        )

    # =========================================================
    # SAVE JSON
    # =========================================================

    def save_json(
        self,
        filepath="results/member_b_results.json"
    ):

        if not self.records:

            raise ValueError(
                "No simulation records to save."
            )

        # -----------------------------------------------------
        # Create directory
        # -----------------------------------------------------

        directory = os.path.dirname(
            filepath
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        # -----------------------------------------------------
        # Save JSON
        # -----------------------------------------------------

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.records,
                file,
                indent=2
            )

        print(
            f"JSON saved to: {filepath}"
        )

    # =========================================================
    # CLEAR
    # =========================================================

    def clear(self):

        self.records = []