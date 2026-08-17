from simulators.scenario_manager import ScenarioManager
from simulators.logger import SimulationLogger


# =========================================================
# CREATE SCENARIO MANAGER
# =========================================================

manager = ScenarioManager(
    steps_per_scenario=20,
    seed=42
)


# =========================================================
# RUN ALL SCENARIOS
# =========================================================

results = manager.run_all()


# =========================================================
# CREATE LOGGER
# =========================================================

logger = SimulationLogger()


# =========================================================
# STORE RESULTS
# =========================================================

logger.log_many(
    results
)


# =========================================================
# SAVE RESULTS
# =========================================================

logger.save_csv(
    "results/member_b_results.csv"
)

logger.save_json(
    "results/member_b_results.json"
)


# =========================================================
# SUMMARY
# =========================================================

print(
    "\n===== MEMBER B SUMMARY ====="
)

print(
    "Scenarios:",
    manager.get_scenario_count()
)

print(
    "Records:",
    len(
        logger.get_records()
    )
)