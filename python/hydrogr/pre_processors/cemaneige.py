from typing import Dict, Optional, Union
import numpy as np
from pandas import DataFrame
from hydrogr._hydrogr import cemaneige as cemaneige_rust


class CemaNeige:
    """CEMANEIGE snow model preprocessing wrapper for GR models.
    CEMANEIGE transforms raw precipitation into liquid-equivalent precipitation
    accounting for snow accumulation and melt.

    When hypso_data is provided the model runs on N independent elevation bands,
    adjusting the input temperature per band with a lapse rate, and returns the
    band-averaged liquid precipitation. This mirrors the multi-layer approach in
    AirGR.

    Parameters (hysteresis=False):
        X1 (float): Snowpack thermal coefficient [0-1].
        X2 (float): Melt coefficient [mm/(°C·timestep)].

    Parameters (hysteresis=True, adds):
        X3 (float): Accumulation threshold [mm] (>0). Controls the rate at
                    which snow cover area rebuilds during accumulation.
        X4 (float): fraction of mean annual solid precipitation defining the
                    melt threshold (0-1].

    States (single band):
        snowpack (float): Snow storage [mm].
        snowpack_thermal_state (float): Thermal state [°C].
        melt_threshold (float): Melt threshold [mm] (only when hysteresis=True).
        local_max_snowpack (float): Local maximum snowpack [mm] (only when hysteresis=True).

    States (multi-band):
        Same keys as single band; values are numpy arrays of shape (n_bands,).

    References:
        Valéry, A., Andréassian, V. & Perrin, C. (2014). Journal of Hydrology, 517.
        Riboust, P., Thirel, G., Le Moine, N. & Ribstein, P. (2019). Journal of
        Hydrology and Hydromechanics, 67(1), 70-81.
    """

    def __init__(
        self,
        parameters: Dict[str, float],
        hysteresis: bool = False,
        hypso_data: Optional[np.ndarray] = None,
        n_bands: int = 5,
        lapse_rate: float = -0.006,
    ):
        """Initialize CEMANEIGE model.

        Args:
            parameters (Dict[str, float]): Parameter dict. Keys 'X1' and 'X2' are always required. 
                                           When hysteresis=True, also requires 'X3' (>0 [mm]) and 'X4' (in (0, 1]).
            hysteresis (bool, optional): Use the hysteresis formulation (Riboust et al. 2019). Defaults to False.
            hypso_data (Optional[np.ndarray], optional): Hypsometric curve of the catchment. elevations [m] at
                                                         equal-area percentiles (e.g. 101 values: 0th to 100th percentile
                                                         of area). If None, runs as a single elevation band. Defaults to None.
            n_bands (int, optional): Number of elevation bands. Only used when hypso_data is given. Defaults to 5.
            lapse_rate (float, optional): Temperature lapse rate [°C/m]. Default -0.006 (-0.6°C/100m).
        """
        self.hysteresis = hysteresis
        self.parameters_names = ["X1", "X2", "X3", "X4"] if hysteresis else ["X1", "X2"]
        self.states_names = ["snowpack", "snowpack_thermal_state"]

        self.set_parameters(parameters)

        if hypso_data is not None:
            hypso = np.asarray(hypso_data, dtype=np.float64)
            self.n_bands = n_bands
            self.band_elevations = self._compute_band_elevations(hypso, n_bands)
            mean_basin_elev = float(np.mean(hypso))
            self.temp_offsets = lapse_rate * (self.band_elevations - mean_basin_elev)
        else:
            self.n_bands = 1
            self.band_elevations = None
            self.temp_offsets = np.array([0.0])

        if self.n_bands == 1:
            self.snowpack = 0.0
            self.snowpack_thermal_state = 0.0
            self.melt_threshold = 0.0
            self.local_max_snowpack = 0.0
        else:
            self.snowpack = np.zeros(self.n_bands)
            self.snowpack_thermal_state = np.zeros(self.n_bands)
            self.melt_threshold = np.zeros(self.n_bands)
            self.local_max_snowpack = np.zeros(self.n_bands)


    # Parameter / state management
    # ----------------------------

    def _compute_band_elevations(
        self, hypso_data: np.ndarray, n_bands: int
    ) -> np.ndarray:
        """Return the mean elevation of each equal-area band."""
        n = len(hypso_data)
        band_means = np.zeros(n_bands)
        for i in range(n_bands):
            start = round(i * n / n_bands)
            end = max(round((i + 1) * n / n_bands), start + 1)
            band_means[i] = np.mean(hypso_data[start:end])
        return band_means

    def _validate_parameters(self, parameters: Dict[str, float]) -> None:
        for key in self.parameters_names:
            if key not in parameters:
                raise ValueError(f"Missing required parameter: {key}")

        x1 = parameters["X1"]
        x2 = parameters["X2"]

        if not (0.0 <= x1 <= 1.0):
            raise ValueError(f"X1 (thermal coeff) must be in [0, 1], got {x1}")
        if x2 < 0.0:
            raise ValueError(f"X2 (melt coeff) must be non-negative, got {x2}")

        if "X3" in self.parameters_names:
            x3 = parameters["X3"]
            x4 = parameters["X4"]
            if x3 <= 0.0:
                raise ValueError(f"X3 (Gacc) must be positive, got {x3}")
            if not (0.0 < x4 <= 1.0):
                raise ValueError(f"X4 (prct) must be in (0, 1], got {x4}")

    def set_parameters(self, parameters: Dict[str, float]) -> None:
        """_summary_

        Args:
            parameters (Dict[str, float]): Parameter dict. Keys 'X1' and 'X2' are always required. 
                                           X1 (float): Snowpack thermal coefficient [0-1].
                                           X2 (float): Melt coefficient [mm/(°C·timestep)].
                                           When hysteresis=True, also requires 'X3' and 'X4'.
                                           X3 (float): Accumulation threshold [mm] (>0). Controls the rate at
                                           which snow cover area rebuilds during accumulation.
                                           X4 (float): fraction of mean annual solid precipitation defining the
                                           melt threshold (0-1].
        """
        self._validate_parameters(parameters)
        self.parameters = parameters

    def set_states(self, states: Dict[str, Union[float, np.ndarray]]) -> None:
        """Set model states.

        Args:
            states: Dict with at minimum 'snowpack' and 'snowpack_thermal_state'.
                Optionally 'melt_threshold' and 'local_max_snowpack' when hysteresis=True.
                For multi-band models values must be arrays of shape (n_bands,).
        """
        for key in self.states_names:
            if key not in states:
                raise ValueError(f"Missing required state: {key}")

        if self.n_bands == 1:
            self.snowpack = float(states["snowpack"])
            self.snowpack_thermal_state = float(states["snowpack_thermal_state"])
            if self.hysteresis:
                self.melt_threshold = float(states.get("melt_threshold", 0.0))
                self.local_max_snowpack = float(states.get("local_max_snowpack", 0.0))
        else:
            self.snowpack = np.asarray(states["snowpack"], dtype=np.float64)
            self.snowpack_thermal_state = np.asarray(
                states["snowpack_thermal_state"], dtype=np.float64
            )
            if self.hysteresis:
                self.melt_threshold = np.asarray(
                    states.get("melt_threshold", np.zeros(self.n_bands)),
                    dtype=np.float64,
                )
                self.local_max_snowpack = np.asarray(
                    states.get("local_max_snowpack", np.zeros(self.n_bands)),
                    dtype=np.float64,
                )

    def get_states(self) -> Dict[str, Union[float, np.ndarray]]:
        """Return current model states.

        Returns:
            Dict with 'snowpack' and 'snowpack_thermal_state' (and 'melt_threshold',
            'local_max_snowpack' when hysteresis=True). Values are floats for single-band
            models and numpy arrays of shape (n_bands,) for multi-band models.
        """
        if self.n_bands == 1:
            states: Dict[str, Union[float, np.ndarray]] = {
                "snowpack": self.snowpack,
                "snowpack_thermal_state": self.snowpack_thermal_state,
            }
            if self.hysteresis:
                states["melt_threshold"] = self.melt_threshold
                states["local_max_snowpack"] = self.local_max_snowpack
        else:
            states = {
                "snowpack": self.snowpack.copy(),
                "snowpack_thermal_state": self.snowpack_thermal_state.copy(),
            }
            if self.hysteresis:
                states["melt_threshold"] = self.melt_threshold.copy()
                states["local_max_snowpack"] = self.local_max_snowpack.copy()
        return states

    # Snow fraction helper
    # --------------------

    def _prepare_solid_precip_fraction(self, temperature: np.ndarray) -> np.ndarray:
        t_min = -1.0
        t_max = 3.0
        solid_frac = 1.0 - (temperature - t_min) / (t_max - t_min)
        return np.clip(solid_frac, 0.0, 1.0)

    # Core model execution
    # --------------------

    def _run_band(
        self,
        precipitation: np.ndarray,
        temperature: np.ndarray,
        snowpack: float,
        snowpack_thermal_state: float,
        melt_threshold: float,
        local_max_snowpack: float,
    ):
        """Run CemaNeige for one elevation band. Returns (state_end, liquid_flow)."""
        solid_frac = self._prepare_solid_precip_fraction(temperature)
        n_years = max(len(precipitation) / 365.25, 1.0)
        mean_annual_solid_precip = float(np.sum(precipitation * solid_frac) / n_years)

        if self.hysteresis:
            state_start = np.array(
                [snowpack, snowpack_thermal_state, melt_threshold, local_max_snowpack],
                dtype=np.float64,
            )
            param_array = [
                self.parameters["X1"],
                self.parameters["X2"],
                self.parameters["X3"],
                self.parameters["X4"],
            ]
        else:
            state_start = np.array([snowpack, snowpack_thermal_state], dtype=np.float64)
            param_array = [self.parameters["X1"], self.parameters["X2"]]

        return cemaneige_rust(
            param_array,
            precipitation.astype(np.float64),
            solid_frac.astype(np.float64),
            temperature.astype(np.float64),
            mean_annual_solid_precip,
            state_start,
            self.hysteresis,
        )

    def _run(
        self,
        precipitation: np.ndarray,
        temperature: np.ndarray,
        potential_evapotranspiration: Optional[np.ndarray] = None,
    ) -> Dict[str, np.ndarray]:
        """Run CEMANEIGE preprocessing.

        Args:
            precipitation: Precipitation [mm].
            temperature: Mean air temperature [°C] at mean basin elevation.
            potential_evapotranspiration: PET [mm] (passed through unchanged).

        Returns:
            Dict with 'liquid_precip' (liquid precipitation + melt, band-averaged
            for multi-band) and 'potential_evapotranspiration'.
        """
        n_steps = len(precipitation)
        precip = precipitation.astype(np.float64)

        if self.n_bands == 1:
            state_end, liquid_flow = self._run_band(
                precip,
                temperature,
                self.snowpack,
                self.snowpack_thermal_state,
                self.melt_threshold,
                self.local_max_snowpack,
            )
            self.snowpack = float(state_end[0])
            self.snowpack_thermal_state = float(state_end[1])
            if self.hysteresis:
                self.melt_threshold = float(state_end[2])
                self.local_max_snowpack = float(state_end[3])
        else:
            liquid_flows = np.zeros((self.n_bands, n_steps))
            for i in range(self.n_bands):
                temp_band = temperature + self.temp_offsets[i]
                state_end, liquid_flow = self._run_band(
                    precip,
                    temp_band,
                    float(self.snowpack[i]),
                    float(self.snowpack_thermal_state[i]),
                    float(self.melt_threshold[i]),
                    float(self.local_max_snowpack[i]),
                )
                liquid_flows[i] = liquid_flow
                self.snowpack[i] = float(state_end[0])
                self.snowpack_thermal_state[i] = float(state_end[1])
                if self.hysteresis:
                    self.melt_threshold[i] = float(state_end[2])
                    self.local_max_snowpack[i] = float(state_end[3])
            liquid_flow = np.mean(liquid_flows, axis=0)

        if potential_evapotranspiration is None:
            potential_evapotranspiration = np.zeros(n_steps)

        return {
            "liquid_precip": liquid_flow,
            "potential_evapotranspiration": potential_evapotranspiration,
        }

    def run(self, df: DataFrame) -> DataFrame:
        """Run CEMANEIGE on a DataFrame.

        Args:
            df: DataFrame with required columns 'precipitation' and 'temperature'
                (temperature at mean basin elevation), and optional
                'potential_evapotranspiration'.

        Returns:
            DataFrame with 'precipitation' (liquid + melt, band-averaged for
            multi-band) and 'potential_evapotranspiration'.
        """
        required_cols = ["precipitation", "temperature"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        pet = df.get("potential_evapotranspiration", None)
        if pet is not None:
            pet = pet.values

        result = self._run(
            precipitation=df["precipitation"].values,
            temperature=df["temperature"].values,
            potential_evapotranspiration=pet,
        )

        output_df = DataFrame(
            {
                "precipitation": result["liquid_precip"],
                "potential_evapotranspiration": result["potential_evapotranspiration"],
            }
        )
        output_df.index = df.index
        return output_df
