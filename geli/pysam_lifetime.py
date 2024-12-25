class PySAM_Lifetime:
    def __init__(
        self,
        simulationYears: int,
        degradation: list[float],
        use_dc_degradation: bool = False,
    ):
        self.set_analysis_period(simulationYears)
        self.set_default_annual_degradations()
        self.set_if_simulation_should_ac_or_dc_degradation(use_dc_degradation)
        self.set_multiyear_parameters(degradation)

    def set_analysis_period(self, simulationYears: int):
        assert (
            simulationYears >= 1
        ), "Simulation Years must be greater or equal to 1."
        self._analysis_period = simulationYears

    def get_analysis_period(self):
        return self._analysis_period

    def set_default_annual_degradations(self):
        self._annual_dc_degradation = list([0]) * self.get_analysis_period()
        self._annual_ac_degradation = list([0]) * self.get_analysis_period()

    def set_if_simulation_should_ac_or_dc_degradation(
        self, use_dc_degradation
    ):
        self._use_dc_degradation = use_dc_degradation
        self._use_ac_degradation = not use_dc_degradation

    def simulation_uses_ac_degradation(self):
        return self._use_ac_degradation

    def simulation_uses_dc_degradation(self):
        return self._use_dc_degradation

    def set_multiyear_parameters(self, degradation: list[float]):
        self.set_system_use_lifetime_output(0)
        # option 1: create a list of degradation values to multiply
        #           annual/monthly consumption for year 1
        if self.simulation_uses_ac_degradation():
            self.set_ac_degradation(degradation)

        # option 2: use PySAM's use_lifetime_output option which re-runs
        #           simulations based on degraded parameters for each year.
        #           Currently option 2 is always disabled since the
        #           boolean use_dc_degradation is False by default
        if (
            self.get_analysis_period() != 1
            and self.simulation_uses_dc_degradation()
        ):
            self.set_system_use_lifetime_output(1)
            self.set_yearly_dc_degradation(degradation)

    def set_system_use_lifetime_output(self, value: int):
        assert value in [0, 1], (
            "system_use_lifetime_output takes only 0/1; value supplies is"
            f" {value}"
        )
        self.system_use_lifetime_output = value

    def get_system_use_lifetime_output(self):
        return self.system_use_lifetime_output

    def set_yearly_dc_degradation(self, dc_degradation: list[float]):
        assert len(dc_degradation) == self.get_analysis_period(), (
            f"len(dc_degradation)={len(dc_degradation)} is not equal to"
            f" SimulationYears={self.get_analysis_period()}. Please"
            " provide dc_degradation for every year."
        )
        self.annual_dc_degradation = dc_degradation

    def set_ac_degradation(
        self, ac_degradation: list[float], use_compounding: bool = False
    ):
        assert len(ac_degradation) == self.get_analysis_period(), (
            f"len(ac_degradation)={len(ac_degradation)} is not equal to"
            f" SimulationYears={self.get_analysis_period()}. Please"
            " provide ac_degradation for every year."
        )
        annual_value = 1.0
        self._annual_ac_degradation = list([annual_value])
        for idx, percent in enumerate(ac_degradation[1:]):
            reduction = annual_value if use_compounding else 1.0
            annual_value -= reduction * percent
            assert annual_value > 0, (
                "System has completely degraded. Please check supplied yearly"
                " degradation factors."
            )
            self._annual_ac_degradation.append(annual_value)

    def get_yearly_ac_degradation(self):
        return self._annual_ac_degradation

    def get_yearly_dc_degradation(self):
        return self._annual_dc_degradation
