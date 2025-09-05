# make a Singleton class for simulation settings
# to ensure that the simulation settings are consistent across the application
# The class should have a setting like time_unit, which can be set to seconds, minutes, hours, days, or weeks but by default it's minute
from datetime import timedelta


class SimulationSettings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimulationSettings, cls).__new__(cls)
            cls._instance.time_unit = timedelta(minutes=1)  # Default to 1 minute
        return cls._instance

    def set_time_unit(self, time_unit: timedelta):
        if not isinstance(time_unit, timedelta):
            raise TypeError("time_unit must be a timedelta instance")
        self.time_unit = time_unit

    def get_time_unit(self) -> timedelta:
        return self.time_unit
