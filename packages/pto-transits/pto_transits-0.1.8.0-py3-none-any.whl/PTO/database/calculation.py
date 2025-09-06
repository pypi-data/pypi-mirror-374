import numpy as np
from dataclasses import dataclass
import astropy.units as u
import astropy.nddata as nddata
import astropy.constants as con
from sympy import symbols, Eq, solve, sin, pi, sqrt, asin, cos, acos, simplify
import logging
import pandas as pd
import sympy as smp

from ..utils.utilities import logger_default, time_function, disable_func

logger = logging.getLogger(__name__)
if not logger.handlers:
    logger = logger_default(logger)


class CalculationUtilities():

    def __drop_errors(self,
                      key: str) -> None:
        """
        Drops values where the key has no errorbar.

        Parameters
        ----------
        key : str
            Key which to check for NaNs to drop.
        """
        condition = (self.table[key].notna() & (
            self.table[f'{key}.Error.Lower'].isna() |
            self.table[f'{key}.Error.Upper'].isna()
        ))
        indices = self.table[condition].index

        self.table.loc[indices, key] = np.nan
        self.table.loc[indices, f'{key}.Error.Lower'] = np.nan
        self.table.loc[indices, f'{key}.Error.Upper'] = np.nan

    def __replace_errors(self,
                         key: str) -> None:
        """
        Replace NaN errors with 0 for given key.

        Parameters
        ----------
        key : str
            Key which to check for NaNs to replace.
        """
        condition = (self.table[key].notna() & (
            self.table[f'{key}.Error.Lower'].isna() |
            self.table[f'{key}.Error.Upper'].isna()
        ))
        indices = self.table[condition].index

        self.table.loc[indices, f'{key}.Error.Lower'] = 0
        self.table.loc[indices, f'{key}.Error.Upper'] = 0

    def _handle_keys_without_errors(self,
                                    mode: str = 'drop') -> None:
        """
        Handles keys which don't hold error values.

        Parameters
        ----------
        mode : str, optional
            How to deal with NaNs errors, by default 'drop'. If 'drop', the values are dropped, if "replace", the errorbars are replaced with 0.

        Raises
        ------
        ValueError
            Raising error when invalid mode is provided.
        """
        keys_with_erros = [
            key for key in self.table.keys() if (
                f'{key}.Error.Lower' in self.table.keys() and
                f'{key}.Error.Upper' in self.table.keys() and
                not (f'{key}'.startswith('Position.'))
            )
        ]

        match mode:
            case 'drop':
                for key in keys_with_erros:
                    self.__drop_errors(key)
            case 'replace':
                for key in keys_with_erros:
                    self.__replace_errors(key)
            case _:
                raise ValueError('Invalid mode')

    def _unit_conversion(self,
                         key_original: str,
                         unit_original: u.Unit,
                         key_result: str,
                         unit_result: u.Unit
                         ) -> None:
        """
        Converts units between x and y units for given keys, if not present.

        Parameters
        ----------
        key_original : str
            Original key to look to.
        unit_original : u.Unit
            Unit of the original key.
        key_result : str
            Resulting key to pass the converted value.
        unit_result : u.Unit
            Resulting unit to pass into the converted value
        """

        condition = (self.table[key_original].notna() &
                     self.table[key_result].isna()
                     )
        indices = self.table[condition].index

        if len(indices) == 0:
            return

        ArrayValues = nddata.NDDataArray(data=self.table.loc[indices, key_original].to_numpy(),
                                         uncertainty=nddata.StdDevUncertainty(np.max(
                                             [self.table.loc[indices, f'{key_original}.Error.Lower'].to_numpy(),
                                              self.table.loc[indices, f'{key_original}.Error.Upper'].to_numpy(
                                             ),
                                             ])),
                                         unit=unit_original
                                         )
        ConvertedArray = ArrayValues.convert_unit_to(unit_result)

        self.table.loc[indices, f'{key_result}'] = ConvertedArray.data
        self.table.loc[indices,
                       f'{key_result}.Error.Lower'] = ConvertedArray.uncertainty.array
        self.table.loc[indices,
                       f'{key_result}.Error.Upper'] = ConvertedArray.uncertainty.array

    def _add_Earth_and_Jupiter_units(self) -> None:
        """
        Handles keys which are related by simple conversion, like units between Earth and Jupiter.
        """
        self._unit_conversion(key_original='Planet.RadiusEarth',
                              unit_original=u.R_earth,
                              key_result='Planet.RadiusJupiter',
                              unit_result=u.R_jupiter)

        self._unit_conversion(key_original='Planet.RadiusJupiter',
                              unit_original=u.R_jupiter,
                              key_result='Planet.RadiusEarth',
                              unit_result=u.R_earth)

        self._unit_conversion(key_original='Planet.MassEarth',
                              unit_original=u.M_earth,
                              key_result='Planet.MassJupiter',
                              unit_result=u.M_jupiter)

        self._unit_conversion(key_original='Planet.MassJupiter',
                              unit_original=u.R_jupiter,
                              key_result='Planet.MassEarth',
                              unit_result=u.R_earth)

        self._unit_conversion(key_original='Planet.MinimumMassEarth',
                              unit_original=u.M_earth,
                              key_result='Planet.MinimumMassJupiter',
                              unit_result=u.M_jupiter)

        self._unit_conversion(key_original='Planet.MinimumMassJupiter',
                              unit_original=u.R_jupiter,
                              key_result='Planet.MinimumMassEarth',
                              unit_result=u.R_earth)

        self._unit_conversion(key_original='Planet.BestMassEstimateEarth',
                              unit_original=u.M_earth,
                              key_result='Planet.BestMassEstimateJupiter',
                              unit_result=u.M_jupiter)

        self._unit_conversion(key_original='Planet.BestMassEstimateJupiter',
                              unit_original=u.R_jupiter,
                              key_result='Planet.BestMassEstimateEarth',
                              unit_result=u.R_earth)

    def __filter_degree_solution(self,
                                 solution: list,
                                 missing_variable: str,
                                 UNIT_MAPPER: dict) -> list:
        """
        Filters solutions for degree, when multiple solutions are given.

        The boundary is defined by np.pi, or 180 degrees.

        Parameters
        ----------
        solution : list
            Solution with more than single result. Typical for inclination values.
        missing_variable : str
            The name of the missing variable.
        UNIT_MAPPER : dict
            Mapper for units. This ensures correct units are used

        Returns
        -------
        solution : list
            Filtered solution to just single value.

        Raises
        ------
        ValueError
            For invalid units this raises error. Shouldn't happen.
        """

        if UNIT_MAPPER[missing_variable].unit == u.rad:
            return [value for value in solution if value < np.pi]
        elif UNIT_MAPPER[missing_variable].unit == u.deg:
            return [value for value in solution if value < 180]
        else:
            raise ValueError('Invalid unit.')

    def _filter_solutions(self,
                          solution: list,
                          missing_variable: str,
                          UNIT_MAPPER: dict) -> list:
        """
        Filter solutions with multiple results.

        Parameters
        ----------
        solution : list
            Solution to filter results in.
        missing_variable : str
            Which variable has been calculated
        UNIT_MAPPER : dict
            Unit mapper to double-check units

        Returns
        -------
        solution : list
            Filtered list with single solution.

        Raises
        ------
        NotImplementedError
            Not all variables are implemented by default. If triggered, it needs to be added to the match case syntax.
        """
        match missing_variable:
            case 'i':
                return self.__filter_degree_solution(solution, missing_variable, UNIT_MAPPER)
            case _:
                raise NotImplementedError(
                    'This variable is not implemented. FIXME')

# TODO
    def _build_condition(self,
                         MAPPER: dict,
                         missing_variable: str,
                         other_variables: dict,
                         transiting: bool) -> pd.Index:
        """
        Builds a combined condition to filter the table for given missing variable.

        Parameters
        ----------
        MAPPER : dict
            Mapper to use between symbolic map and table keys
        missing_variable : str
            Missing variable to solve the equation for
        other_variables : dict
            Other variables that are already available.
        transiting : bool
            Whether to filter out by transiting planets.

        Returns
        -------
        pd.Index
            Index where the table has the relevant condition. 
        """

        primary_condition = self.table[MAPPER[missing_variable]].isna()
        other_conditions = [self.table[MAPPER[variable]].notna()
                            for variable in other_variables]
        combined_condition = np.logical_and.reduce(other_conditions)

        if transiting:
            transiting_condition = (self.table['Flag.Transit'] == 1)
            condition = primary_condition & combined_condition & transiting_condition
        else:
            condition = primary_condition & combined_condition
        return self.table[condition].index

    def constraint_values(self,
                          values: list,
                          error_values: list,
                          missing_variable: str,
                          ) -> [pd.Series, pd.Series]:
        """
        Apply constraints to values and their errors

        Parameters
        ----------
        values : list
            List of pandas Series containing values
        error_values : list
            List of pandas Series containing error values
        missing_variable : str
            Variable name to check constraints against

        Returns
        -------
        list, list
            Modified values and error values lists
        """
        CONSTRAINT_MAPPER = {
            'R_s': (0, float('inf')),  # Stellar radius must be positive
            'b': (0, float('inf')),    # Impact parameter
            'a': (0, float('inf')),    # Semi-major axis must be positive
            # Inclination must be positive and below 90 degrees
            'i': (0, 90),
            'a_over_Rs': (0, float('inf')),  # a/Rs must be positive
            'T_14': (0, float('inf')),
            'P': (0, float('inf')),
            'R_p': (0, float('inf')),
            'omega': (0, 360),
            'S_earth': (0, float('inf')),
            'L': (0, float('inf')),
            'g': (0, float('inf')),
            'H': (0, float('inf')),

        }

        assert missing_variable in CONSTRAINT_MAPPER.keys(
        ), f"Variable not found in constraints \n '{missing_variable}': (0, float('inf')),"

        min_val, max_val = CONSTRAINT_MAPPER[missing_variable]

        for ind, (value, error) in enumerate(zip(values, error_values)):
            # Apply both conditions at once
            value = value.where((value >= min_val) & (value <= max_val))

            # Get indices where values are NaN
            indices = value.isna()

            # Handle errors based on drop_mode
            if self.drop_mode == 'drop':
                error.loc[indices] = np.nan
            elif self.drop_mode == 'replace':
                error.loc[indices] = 0
            else:
                raise ValueError('Invalid type for drop mode')

            values[ind] = value
            error_values[ind] = error

        nan_counts = [series.isna().sum() for series in values]
        best_index = nan_counts.index(min(nan_counts))

        return values[best_index], error_values[best_index]

    def _solve_equation(self,
                        Equation: Eq,
                        MAPPER: dict,
                        UNIT_MAPPER: dict,
                        transiting: bool = True
                        ) -> None:
        """
        Solves the equation given a mapper and unit mapper.

        Parameters
        ----------
        Equation : Eq
            Equation to solve for.
        MAPPER : dict
            Mapper matching the symbols and the column names in the table.
        UNIT_MAPPER : dict
            Unit mapper to match symbols and the units for the symbol.
        transiting : bool
            Whether the system must be transiting. If true, only transiting planets are considered.
        """
        import warnings
        warnings.filterwarnings('ignore')

        for missing_variable in MAPPER:
            other_variables = {
                variable: MAPPER[variable] for variable in MAPPER if variable != missing_variable}

            indices = self._build_condition(
                MAPPER=MAPPER,
                missing_variable=missing_variable,
                other_variables=other_variables,
                transiting=transiting
            )

            if len(indices) == 0:
                continue

            solutions = solve(Equation, missing_variable)

            column_values_results = []
            uncertainty_results = []
            for solution in solutions:
                func = smp.lambdify([symbols(var)
                                    for var in other_variables.keys()], solution)
                column_values = [(self.table.loc[indices][var] * UNIT_MAPPER[key].value)
                                 for key, var in other_variables.items()]
                column_values_results.append(
                    func(*column_values) / UNIT_MAPPER[missing_variable].value)
                uncertainties = [symbols(f"sigma_{variable}")
                                 for key, variable in other_variables.items()]

                total_uncertainty = 0
                for variable, uncertainty_variable in zip(other_variables.keys(), uncertainties):
                    partial_derivative = smp.diff(solution, symbols(variable))
                    total_uncertainty += ((partial_derivative *
                                          uncertainty_variable)**2)
                total_uncertainty = smp.sqrt(total_uncertainty)

                total_uncertainty_func = smp.lambdify(
                    [smp.symbols(var) for var in other_variables.keys()] +
                    [uncertainty_variable for uncertainty_variable in uncertainties],
                    total_uncertainty,
                )
                column_values.extend(
                    [(self.table.loc[indices][[f"{variable}.Error.Upper",
                                               f"{variable}.Error.Lower"]].max(axis=1)) * UNIT_MAPPER[key] for key, variable in other_variables.items()]
                )
                uncertainty_result = total_uncertainty_func(*column_values)
                uncertainty_results.append(
                    uncertainty_result / UNIT_MAPPER[missing_variable].value)

            column_values_results, uncertainty_results = self.constraint_values(column_values_results,
                                                                                uncertainty_results,
                                                                                missing_variable=missing_variable
                                                                                )

            self.table.loc[indices, MAPPER[str(
                missing_variable)]] = column_values_results
            self.table.loc[indices,
                           f"{MAPPER[str(missing_variable)]}.Error.Lower"] = uncertainty_results
            self.table.loc[indices,
                           f"{MAPPER[str(missing_variable)]}.Error.Upper"] = uncertainty_results
        return

    def _calculate_impact_parameter(self) -> None:
        """
        Calculates the impact parameter related parameters.
        """
        self.__check_inclination()

        b, a, i, R_s = symbols('b, a i R_s')

        Equation = Eq(b,
                      a*cos(i)/R_s
                      )

        MAPPER = {
            'b': 'Planet.ImpactParameter',
            'a': 'Planet.SemiMajorAxis',
            'i': 'Planet.Inclination',
            'R_s': 'Star.Radius'
        }

        UNIT_MAPPER = {
            'b': 1 * u.dimensionless_unscaled,
            'a': (1 * u.au).to(u.R_sun),
            'i': (1 * u.deg).to(u.rad),
            'R_s': (1 * u.R_sun).to(u.R_sun)
        }

        self._solve_equation(
            Equation=Equation,
            MAPPER=MAPPER,
            UNIT_MAPPER=UNIT_MAPPER,
            transiting=True
        )

    def __check_inclination(self) -> None:
        condition_nan = (self.table['Planet.Inclination'].isna())
        condition_zer = (self.table['Planet.Inclination'] > 90)

        condition = condition_nan | condition_zer

        indices = self.table[condition].index

        if len(indices) == 0:
            return

        self.table.loc[indices, 'Planet.Inclination'] = 180 - \
            self.table.loc[indices, 'Planet.Inclination']
        return

    def __check_eccentricity(self) -> None:
        """
        Checks for eccentricity values.

        If a value of eccentricity is NaN or 0, it will be converted to 0. This ensures the equation for T14 is unaffected.
        Furthermore, Argument of periastron (omega) is set to 90 degrees, which gives 1 when used in 
        """

        condition_nan = (self.table['Planet.Eccentricity'].isna())
        condition_zer = (self.table['Planet.Eccentricity'] == 0)

        condition = condition_nan | condition_zer

        indices = self.table[condition].index

        if len(indices) == 0:
            return

        self.table.loc[indices, 'Planet.Eccentricity'] = 0
        self.table.loc[indices, 'Planet.Eccentricity.Error.Lower'] = 0
        self.table.loc[indices, 'Planet.Eccentricity.Error.Upper'] = 0
        self.table.loc[indices, 'Planet.ArgumentOfPeriastron'] = 90
        self.table.loc[indices, 'Planet.ArgumentOfPeriastron.Error.Lower'] = 0
        self.table.loc[indices, 'Planet.ArgumentOfPeriastron.Error.Upper'] = 0
        return

    def _calculate_transit_length(self) -> None:
        """
        Calculates transit length, if not provided.

        It also reformats the values for eccentricity/ argument of periastron to ensure it will not impact the equation.
        """

        self.__check_eccentricity()

        T_14, P, R_s, R_p, a, b, i, e, omega = symbols(
            'T_14, P R_s R_p a b i e omega')

        Equation = Eq(T_14,
                      (P / pi) * asin(
                          (R_s / a) * sqrt((1 + (R_p / R_s))**2 - b**2) / sin(i)
                      ) * (sqrt(1-e**2) / ((1 + e)*sin(omega)))
                      )

        MAPPER = {
            'T_14': 'Planet.TransitDuration',
            'P': 'Planet.Period',
            'R_s': 'Star.Radius',
            'R_p': 'Planet.RadiusJupiter',
            'a': 'Planet.SemiMajorAxis',
            'b': 'Planet.ImpactParameter',
            'i': 'Planet.Inclination',
            'e': 'Planet.Eccentricity',
            'omega': 'Planet.ArgumentOfPeriastron'
        }

        UNIT_MAPPER = {
            'T_14': (1*u.hour).to(u.h),
            'P': (1*u.day).to(u.h),
            'R_s': (1 * u.R_sun).to(u.R_sun),
            'R_p': (1 * u.R_jup).to(u.R_sun),
            'a': (1 * u.au).to(u.R_sun),
            'b': 1 * u.dimensionless_unscaled,
            'i': (1 * u.deg).to(u.rad),
            'e': 1 * u.dimensionless_unscaled,
            'omega': (1 * u.deg).to(u.rad),
        }

        self._solve_equation(
            Equation=Equation,
            MAPPER=MAPPER,
            UNIT_MAPPER=UNIT_MAPPER,
        )

        return

    def _calculate_R_s_a(self) -> None:

        a_over_Rs, a, R_s = symbols('a_over_Rs, a R_s')

        Equation = Eq(a_over_Rs,
                      a/R_s
                      )

        MAPPER = {
            'a_over_Rs': 'Planet.RatioSemiMajorAxisToStellarRadius',
            'a': 'Planet.SemiMajorAxis',
            'R_s': 'Star.Radius'
        }

        UNIT_MAPPER = {
            'a_over_Rs': 1 * u.dimensionless_unscaled,
            'a': (1 * u.au).to(u.R_sun),
            'R_s': (1 * u.R_sun).to(u.R_sun)
        }

        self._solve_equation(
            Equation=Equation,
            MAPPER=MAPPER,
            UNIT_MAPPER=UNIT_MAPPER,
            transiting=True
        )
        return

    def _calculate_insolation_flux(self) -> None:

        S_earth, L, a = symbols('S_earth, L a')

        Equation = Eq(S_earth,
                      L/(a**2)
                      )

        MAPPER = {
            'S_earth': 'Planet.InsolationFlux',
            'L': 'Star.Luminosity',
            'a': 'Planet.SemiMajorAxis'
        }

        UNIT_MAPPER = {
            'S_earth': 1 * u.dimensionless_unscaled,
            'L': (1 * u.L_sun),
            'a': (1 * u.au)
        }

        self._solve_equation(
            Equation=Equation,
            MAPPER=MAPPER,
            UNIT_MAPPER=UNIT_MAPPER,
            transiting=False
        )
        return

    def _calculate_surface_gravity(self) -> None:
        self.table['Planet.SurfaceGravity'] = np.nan

        g, M, R = symbols('g, M R')
        G = con.G.value

        Equation = Eq(g,
                      G * M / (R**2)
                      )

        MAPPER = {
            'g': 'Planet.SurfaceGravity',
            'M': 'Planet.MassJupiter',
            'R': 'Planet.RadiusJupiter',
        }

        UNIT_MAPPER = {
            'g': (1 * u.m/u.s**2),
            'M': (1 * u.M_jup).to(u.kg),
            'R': (1 * u.R_jup).to(u.m)
        }

        self._solve_equation(
            Equation=Equation,
            MAPPER=MAPPER,
            UNIT_MAPPER=UNIT_MAPPER,
            transiting=False
        )
        return

    def _calculate_atmospheric_scale_height(self) -> None:
        self.table['Planet.AtmosphericScaleHeight'] = np.nan

        H, T, g = symbols('H, T g')
        mu = 2.3 / (6.02214*10**23)
        kb = con.k_B.value

        Equation = Eq(H,
                      kb * T / (mu * g)
                      )

        MAPPER = {
            'H': 'Planet.AtmosphericScaleHeight',
            'T': 'Planet.EquilibriumTemperature',
            'g': 'Planet.SurfaceGravity'
        }

        UNIT_MAPPER = {
            'H': (1 * u.km),
            'T': (1 * u.T),
            'g': (1 * u.m/u.s**2)
        }

        self._solve_equation(
            Equation=Equation,
            MAPPER=MAPPER,
            UNIT_MAPPER=UNIT_MAPPER,
            transiting=False
        )
        return
