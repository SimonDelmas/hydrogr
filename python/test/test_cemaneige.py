import numpy as np
import pandas as pd
import pytest
from hydrogr.pre_processors.cemaneige import CemaNeige


class TestCemaNeige:
    """Test suite for CemaNeige preprocessing model."""

    @pytest.fixture
    def default_params(self):
        """Default parameters for testing."""
        return {
            "X1": 0.8,  # Thermal coefficient
            "X2": 2.5,  # Melt coefficient [mm/(°C·day)]
        }

    @pytest.fixture
    def default_params_hyst(self):
        """Default parameters for hysteresis testing (4-parameter version)."""
        return {
            "X1": 0.8,  # Thermal coefficient
            "X2": 2.5,  # Melt coefficient [mm/(°C·day)]
            "X3": 100.0,  # accumulation threshold [mm]
            "X4": 0.5,  # fraction of MASP defining melt threshold
        }

    @pytest.fixture
    def test_inputs(self):
        """Generate synthetic test inputs."""
        np.random.seed(42)
        n_days = 365

        # Winter snow period followed by spring melt
        months = np.tile(np.arange(1, 13), 31)[:n_days]
        precipitation = np.zeros(n_days)
        precipitation[months <= 5] = np.random.gamma(
            2, 2, sum(months <= 5)
        )  # Winter precip
        precipitation[months >= 10] = np.random.gamma(
            2, 2, sum(months >= 10)
        )  # Fall precip

        # Temperature: cold in winter, warm in summer
        temperature = 15 * np.cos(2 * np.pi * np.arange(n_days) / 365 - np.pi / 2)
        temperature += np.random.normal(0, 2, n_days)  # Add noise

        pet = np.ones(n_days) * 3.0  # Constant PET

        return {
            "precipitation": precipitation,
            "temperature": temperature,
            "pet": pet,
        }

    def test_initialization(self, default_params):
        """Test CemaNeige initialization."""
        model = CemaNeige(
            parameters=default_params,
            hysteresis=False,
        )
        assert model.snowpack == 0.0
        assert model.snowpack_thermal_state == 0.0
        assert model.melt_threshold == 0.0
        assert model.local_max_snowpack == 0.0
        assert model.hysteresis is False

    def test_parameter_validation_missing(self, default_params):
        """Test that missing parameters raise an error."""
        bad_params = {"X1": 0.8}  # Missing X2
        with pytest.raises(ValueError, match="Missing required parameter"):
            CemaNeige(bad_params)

    def test_parameter_validation_x1_range(self):
        """Test that X1 outside [0, 1] raises an error."""
        with pytest.raises(ValueError, match="X1"):
            CemaNeige(
                {"X1": 1.5, "X2": 2.5},
            )

        with pytest.raises(ValueError, match="X1"):
            CemaNeige(
                {"X1": -0.1, "X2": 2.5},
            )

    def test_parameter_validation_x2_positive(self):
        """Test that negative X2 raises an error."""
        with pytest.raises(ValueError, match="X2"):
            CemaNeige(
                {"X1": 0.5, "X2": -0.1},
            )

    def test_set_get_states(self, default_params):
        """Test setting and getting states."""
        model = CemaNeige(default_params)

        new_states = {
            "snowpack": 100.0,
            "snowpack_thermal_state": -5.0,
        }
        model.set_states(new_states)

        retrieved = model.get_states()
        assert retrieved["snowpack"] == 100.0
        assert retrieved["snowpack_thermal_state"] == -5.0

    def test_set_states_missing_key(self, default_params):
        """Test that missing state keys raise an error."""
        model = CemaNeige(default_params)

        bad_states = {"snowpack": 100.0}  # Missing thermal state
        with pytest.raises(ValueError, match="Missing required state"):
            model.set_states(bad_states)

    def test_set_states_with_hysteresis(self, default_params_hyst):
        """Test setting states with hysteresis parameters."""
        model = CemaNeige(
            default_params_hyst,
            hysteresis=True,
        )

        states = {
            "snowpack": 50.0,
            "snowpack_thermal_state": -2.0,
            "melt_threshold": 10.0,
            "local_max_snowpack": 150.0,
        }
        model.set_states(states)

        retrieved = model.get_states()
        assert retrieved["melt_threshold"] == 10.0
        assert retrieved["local_max_snowpack"] == 150.0

    def test_prepare_solid_precip_fraction(self, default_params):
        """Test solid precipitation fraction calculation."""
        model = CemaNeige(default_params)

        # Test at key temperatures
        # Threshold range: T_min = -1°C (all snow), T_max = 3°C (all rain)
        # Linear interpolation between
        temps = np.array([-2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0])
        fracs = model._prepare_solid_precip_fraction(temps)

        # Below -1°C: all snow
        assert np.isclose(fracs[0], 1.0)
        # At -1°C: all snow
        assert np.isclose(fracs[1], 1.0)
        # At 0°C: (3 - 0) / (3 - (-1)) = 3/4 = 0.75
        assert np.isclose(fracs[2], 0.75)
        # At 1°C: (3 - 1) / (3 - (-1)) = 2/4 = 0.5
        assert np.isclose(fracs[3], 0.5)
        # At 3°C: all rain
        assert np.isclose(fracs[5], 0.0)
        # Above 3°C: all rain
        assert np.isclose(fracs[6], 0.0)

        # Check monotonic decrease
        assert np.all(np.diff(fracs) <= 0.01)  # Allow for rounding

    def test_run_basic(self, default_params, test_inputs):
        """Test basic run method."""
        model = CemaNeige(default_params)

        result = model._run(
            precipitation=test_inputs["precipitation"],
            temperature=test_inputs["temperature"],
            potential_evapotranspiration=test_inputs["pet"],
        )

        assert "liquid_precip" in result
        assert "potential_evapotranspiration" in result
        assert len(result["liquid_precip"]) == len(test_inputs["precipitation"])
        assert len(result["potential_evapotranspiration"]) == len(test_inputs["pet"])

    def test_run_state_updates(self, default_params, test_inputs):
        """Test that states are updated during run."""
        model = CemaNeige(default_params)

        _ = model._run(
            precipitation=test_inputs["precipitation"],
            temperature=test_inputs["temperature"],
        )

        # After a full year, snowpack should have changed
        # (accumulated snow in winter, melted in spring)
        assert isinstance(model.snowpack, float)
        assert isinstance(model.snowpack_thermal_state, float)

    def test_run_snow_accumulation(self, default_params):
        """Test snow accumulation in cold period."""
        model = CemaNeige(default_params)

        # Cold period with heavy snow
        precip = np.array([10.0] * 30)  # 30 days of 10mm precip
        temp = np.array([-5.0] * 30)  # Cold temperatures

        result = model._run(precip, temp)

        # Most precipitation should be snow accumulation
        # Liquid output should be much less than input
        liquid_sum = np.sum(result["liquid_precip"])
        precip_sum = np.sum(precip)

        assert liquid_sum < precip_sum * 0.5
        assert model.snowpack > 100.0

    def test_run_snow_melt(self, default_params):
        """Test snow melt in warm period."""
        model = CemaNeige(default_params)

        # First accumulate snow
        cold_precip = np.array([5.0] * 20)
        cold_temp = np.array([-10.0] * 20)
        model._run(cold_precip, cold_temp)

        initial_snowpack = model.snowpack

        # Then warm up (melt period)
        warm_precip = np.array([2.0] * 20)
        warm_temp = np.array([10.0] * 20)

        result = model._run(warm_precip, warm_temp)

        # Snowpack should decrease (melt)
        assert model.snowpack < initial_snowpack
        # Liquid output should include melt
        assert np.sum(result["liquid_precip"]) > np.sum(warm_precip)

    def test_run_with_dataframe(self, default_params, test_inputs):
        """Test run_with_dataframe method."""
        model = CemaNeige(default_params)

        df = pd.DataFrame(
            {
                "precipitation": test_inputs["precipitation"],
                "temperature": test_inputs["temperature"],
                "potential_evapotranspiration": test_inputs["pet"],
            }
        )
        df.index = pd.date_range("2023-01-01", periods=len(df))

        result_df = model.run(df)

        assert isinstance(result_df, pd.DataFrame)
        assert "precipitation" in result_df.columns
        assert "potential_evapotranspiration" in result_df.columns
        assert len(result_df) == len(df)
        assert result_df.index.equals(df.index)

    def test_run_with_dataframe_missing_column(self, default_params, test_inputs):
        """Test that missing required columns raise an error."""
        model = CemaNeige(default_params)

        df = pd.DataFrame(
            {
                "precipitation": test_inputs["precipitation"],
                # Missing 'temperature'
            }
        )

        with pytest.raises(ValueError, match="Missing required column"):
            model.run(df)

    def test_run_state_continuity(self, default_params):
        """Test that states persist correctly across multiple runs."""
        model = CemaNeige(default_params)

        # First run: accumulate snow
        precip1 = np.array([5.0] * 10)
        temp1 = np.array([-5.0] * 10)
        model._run(precip1, temp1)

        snowpack_after_first = model.snowpack

        # Second run: more precipitation
        precip2 = np.array([5.0] * 10)
        temp2 = np.array([-5.0] * 10)
        model._run(precip2, temp2)

        snowpack_after_second = model.snowpack

        # Snowpack should increase across runs
        assert snowpack_after_second > snowpack_after_first

    def test_hysteresis_mode(self, default_params_hyst):
        """Test hysteresis mode initialization and state handling."""
        model = CemaNeige(
            default_params_hyst,
            hysteresis=True,
        )

        assert model.hysteresis is True

        # Run should handle hysteresis states
        precip = np.array([5.0] * 20)
        temp = np.array([0.0] * 20)

        _ = model._run(precip, temp)

        states = model.get_states()
        assert "melt_threshold" in states
        assert "local_max_snowpack" in states

    def test_run_without_pet(self, default_params, test_inputs):
        """Test run without providing PET (should default to zeros)."""
        model = CemaNeige(default_params)

        result = model._run(
            precipitation=test_inputs["precipitation"],
            temperature=test_inputs["temperature"],
        )

        assert result["potential_evapotranspiration"] is not None
        assert len(result["potential_evapotranspiration"]) == len(
            test_inputs["precipitation"]
        )

    def test_liquid_output_bounds(self, default_params, test_inputs):
        """Test that liquid output is reasonable (non-negative)."""
        model = CemaNeige(default_params)

        result = model._run(
            precipitation=test_inputs["precipitation"],
            temperature=test_inputs["temperature"],
        )

        # Liquid precip should be non-negative
        assert np.all(result["liquid_precip"] >= 0.0)

    def test_output_dtype(self, default_params, test_inputs):
        """Test that outputs have correct dtype."""
        model = CemaNeige(default_params)

        result = model._run(
            precipitation=test_inputs["precipitation"],
            temperature=test_inputs["temperature"],
        )

        # Should be numpy arrays
        assert isinstance(result["liquid_precip"], np.ndarray)
        assert result["liquid_precip"].dtype in [np.float32, np.float64]

    # ------------------------------------------------------------------
    # Multi-band (elevation distribution) tests
    # ------------------------------------------------------------------

    @pytest.fixture
    def flat_hypso(self):
        """All elevations identical — every band gets zero temperature offset."""
        return np.full(101, 1000.0)

    @pytest.fixture
    def varying_hypso(self):
        """Realistic hypsometric curve from 500 m to 2000 m."""
        return np.linspace(500.0, 2000.0, 101)

    def test_multiband_initialization(self, default_params, varying_hypso):
        """Band elevations and temperature offsets are computed correctly."""
        model = CemaNeige(default_params, hypso_data=varying_hypso, n_bands=5)

        assert model.n_bands == 5
        assert model.band_elevations is not None
        assert len(model.band_elevations) == 5
        assert model.snowpack.shape == (5,)
        assert model.snowpack_thermal_state.shape == (5,)
        # Band elevations should increase monotonically
        assert np.all(np.diff(model.band_elevations) > 0)
        # Lowest band below mean, highest above mean
        mean_elev = np.mean(varying_hypso)
        assert model.band_elevations[0] < mean_elev
        assert model.band_elevations[-1] > mean_elev
        # Lower bands are warmer than the mean (positive offset), higher bands colder (negative)
        assert model.temp_offsets[0] > 0
        assert model.temp_offsets[-1] < 0

    def test_multiband_flat_hypso_equals_single_band(
        self, default_params, test_inputs, flat_hypso
    ):
        """Flat hypso → all temp offsets = 0 → multi-band output == single-band output."""
        model_single = CemaNeige(default_params)
        result_single = model_single._run(
            precipitation=test_inputs["precipitation"],
            temperature=test_inputs["temperature"],
        )

        model_multi = CemaNeige(default_params, hypso_data=flat_hypso, n_bands=5)
        result_multi = model_multi._run(
            precipitation=test_inputs["precipitation"],
            temperature=test_inputs["temperature"],
        )

        np.testing.assert_allclose(
            result_single["liquid_precip"], result_multi["liquid_precip"]
        )

    def test_multiband_state_shape_after_run(
        self, default_params, varying_hypso, test_inputs
    ):
        """State arrays keep shape (n_bands,) after a run."""
        model = CemaNeige(default_params, hypso_data=varying_hypso, n_bands=5)
        model._run(
            precipitation=test_inputs["precipitation"],
            temperature=test_inputs["temperature"],
        )

        assert model.snowpack.shape == (5,)
        assert model.snowpack_thermal_state.shape == (5,)
        assert np.all(model.snowpack >= 0.0)

    def test_multiband_higher_bands_colder(
        self, default_params, varying_hypso, test_inputs
    ):
        """Higher elevation bands should accumulate more snow (colder temperatures)."""
        model = CemaNeige(default_params, hypso_data=varying_hypso, n_bands=5)
        model._run(
            precipitation=test_inputs["precipitation"],
            temperature=test_inputs["temperature"],
        )
        # Highest band is coldest — snowpack should be >= lowest band
        assert model.snowpack[-1] >= model.snowpack[0]

    def test_multiband_get_set_states(self, default_params, varying_hypso, test_inputs):
        """States can be saved and restored across multi-band models."""
        model = CemaNeige(default_params, hypso_data=varying_hypso, n_bands=5)
        model._run(
            precipitation=test_inputs["precipitation"],
            temperature=test_inputs["temperature"],
        )
        states = model.get_states()

        assert states["snowpack"].shape == (5,)
        assert states["snowpack_thermal_state"].shape == (5,)

        model2 = CemaNeige(default_params, hypso_data=varying_hypso, n_bands=5)
        model2.set_states(states)

        np.testing.assert_array_equal(model2.snowpack, model.snowpack)
        np.testing.assert_array_equal(
            model2.snowpack_thermal_state, model.snowpack_thermal_state
        )

    def test_multiband_output_nonnegative(
        self, default_params, varying_hypso, test_inputs
    ):
        """Band-averaged liquid precipitation must be non-negative."""
        model = CemaNeige(default_params, hypso_data=varying_hypso, n_bands=5)
        result = model._run(
            precipitation=test_inputs["precipitation"],
            temperature=test_inputs["temperature"],
        )
        assert np.all(result["liquid_precip"] >= 0.0)
