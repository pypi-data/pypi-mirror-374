# *********************************************************
# Copyright (C) 2024 Mariana Moreira - All Rights Reserved
# You may use, distribute and modify this code under the
# terms of the MIT License.

# You should have received a copy of the MIT License with
# this file. If not, please write to:
# mtrocadomoreira@gmail.com
# *********************************************************


import numpy as np
import xarray as xr
from flox.xarray import xarray_reduce
from tqdm import tqdm

from .new_dataobj import new_dataset
from .utils import (
    axis_from_extent,
    bins_from_axis,
    convert_interval_to_mid,
    get_attr_if_exists,
    insert_str_at_index,
    stopwatch,
)


class PartMixin:
    @staticmethod
    def _define_q_units(raw_sdims, rvar_attrs: dict | None):
        if all("units" in raw_sdims[each].attrs for each in raw_sdims.data_vars):
            ustrings = [
                raw_sdims[each].attrs["units"].strip("$")
                for each in raw_sdims.data_vars
            ]
            extra = ""
            for ustr in ustrings:
                extra += rf"/ {ustr}"
            if rvar_attrs is not None:
                extra += rf"/ {rvar_attrs['units'].strip('$')}"
            units_str = rf"$Q_w {extra}$"
        else:
            units_str = "a.u."
        return units_str

    @staticmethod
    def _calc_geometric_emittance(
        ds: xr.Dataset,
        x_var: str,
        p_var: str,
        p_longit: str,
        w_var: str,
    ) -> float | xr.DataArray:
        q_tot = ds[w_var].sum(dim="pid", skipna=True)

        x_prime = ds[p_var] / ds[p_longit]
        x_sq = (ds[w_var] * ds[x_var] ** 2).sum(dim="pid", skipna=True) / q_tot
        x_prime_sq = (ds[w_var] * x_prime**2).sum(dim="pid", skipna=True) / q_tot
        x_x_prime = (ds[w_var] * ds[x_var] * x_prime).sum(
            dim="pid", skipna=True
        ) / q_tot
        emit = np.sqrt(x_sq * x_prime_sq - x_x_prime**2)

        return emit

    def _calc_beta_gamma(
        self,
        p_vars: list[str],
        w_var: str,
    ) -> xr.DataArray:
        ds = self._obj

        p_abs_sqr = 0
        for p_var in p_vars:
            p_abs_sqr += ds[p_var] ** 2

        return ds[w_var] * np.sqrt(p_abs_sqr)

    def sample_particles(self, n: int) -> xr.Dataset:
        """Downsample a particle Dataset by randomly choosing particles.

        Parameters
        ----------
        n : int
            Number of particles to sample.

        Returns
        -------
        xarray.Dataset
            Dataset with sampled particles.

        Examples
        --------

        ???+ example "Sample 1000 particles"
            ```python
            import ozzy as oz
            import numpy as np


            # Create a sample particle dataset
            ds = oz.Dataset(
                {
                    "x1": ("pid", np.random.rand(10000)),
                    "x2": ("pid", np.random.rand(10000)),
                    "p1": ("pid", np.random.rand(10000)),
                    "p2": ("pid", np.random.rand(10000)),
                    "q": ("pid", np.ones(10000)),
                },
                coords={"pid": np.arange(10000)},
                pic_data_type="part",
                data_origin="ozzy",
            )

            # Sample 1000 particles
            ds_small = ds.ozzy.sample_particles(1000)
            print(len(ds_small.pid))
            # 1000

            # Try to sample more particles than available
            ds_all = ds.ozzy.sample_particles(20000)
            # WARNING: number of particles to be sampled is larger than total particles. Proceeding without any sampling.
            print(len(ds_all.pid))
            # 10000
            ```
        """

        dvar = list(set(list(self._obj)) - {"pid", "t", "q"})[0]

        if "t" in self._obj.dims:
            surviving = self._obj[dvar].isel(t=-1).notnull().compute()
            pool = self._obj.coords["pid"][surviving]
        else:
            pool = self._obj.coords["pid"]
        nparts = len(pool)

        if n > nparts:
            print(
                "WARNING: number of particles to be sampled is larger than total particles. Proceeding without any sampling."
            )
            newds = self._obj
        else:
            rng = np.random.default_rng()
            downsamp = rng.choice(pool["pid"], size=n, replace=False, shuffle=False)
            newds = self._obj.sel(pid=np.sort(downsamp))

        return newds

    def mean_std(
        self,
        vars: str | list[str],
        axes_ds: xr.DataArray | xr.Dataset | xr.Coordinates,
        expand_time: bool = True,
        axisym: bool = False,
    ) -> xr.Dataset:
        """Calculate mean and standard deviation of variables.

        Bins the particle data onto the grid specified by `axes_ds`
        and calculates the mean and standard deviation for each bin.

        Parameters
        ----------
        vars : str | list[str]
            The variable(s) for which to calculate statistics.
        axes_ds : xarray.Dataset | xarray.DataArray | xarray.Coordinates
            Data object containing the axes to use for the calculation (as [xarray coordinates](https://docs.xarray.dev/en/v2024.06.0/user-guide/data-structures.html#coordinates)).

            !!! tip
                The axes object can be taken from an existing Dataset or DataArray via `axes_ds = <data_obj>.coords`.

        expand_time : bool, optional
            If `True`, statistics are calculated separately for each timestep.
        axisym : bool, optional
            If `True`, azimuthal symmetry is assumed.

        Returns
        -------
        xarray.Dataset
            Dataset containing the calculated mean and standard deviation of the particle variables.

        Examples
        --------

        ???+ example "Get mean and std of `'x2'` and `'p2'`"
            ```python
            import ozzy as oz
            import numpy as np

            # Create a sample particle dataset
            ds = oz.Dataset(
                {
                    "x1": ("pid", np.random.rand(10000)),
                    "x2": ("pid", np.random.rand(10000)),
                    "p1": ("pid", np.random.rand(10000)),
                    "p2": ("pid", np.random.rand(10000)),
                    "q": ("pid", np.ones(10000)),
                },
                coords={"pid": np.arange(10000)},
                pic_data_type="part",
                data_origin="ozzy",
            )

            # Create axes for binning
            axes_ds = oz.Dataset(
                coords={
                    "x1": np.linspace(0, 1, 21),
                },
                pic_data_type="grid",
                data_origin="ozzy",
            )

            # Calculate mean and standard deviation
            ds_mean_std = ds.ozzy.mean_std(["x2", "p2"], axes_ds)
            ```
        """
        if "grid" not in axes_ds.attrs["pic_data_type"]:
            raise ValueError("axes_ds must be grid data")

        if isinstance(axes_ds, xr.DataArray):
            axes_ds = new_dataset(axes_ds, pic_data_type="grid")
        elif isinstance(axes_ds, xr.Coordinates):
            axes_ds = new_dataset(coords=axes_ds, pic_data_type="grid")

        if isinstance(vars, str):
            vars = [vars]

        # Prepare binning array

        bin_arr = []
        bin_vars = []
        bin_axes = []

        for var in axes_ds.data_vars:
            axis = np.array(axes_ds[var])
            bin_axes.append(axis)
            bin_arr.append(bins_from_axis(axis))
            bin_vars.append(var)

        # Prepare dataset for calculation

        ds = self._obj[bin_vars + vars + ["q"]]

        for dim in vars:
            ds[dim + "_sqw"] = (ds[dim] ** 2) * ds["q"]
            if axisym is False:
                ds[dim + "_w"] = ds[dim] * ds["q"]
                # TODO : check if this is correct for all codes or only for LCODE
        ds = ds.drop_vars(["q"] + vars)

        # Determine bin index for each particle (and for each binning variable)

        for i, bvar in enumerate(bin_vars):
            group_id = np.digitize(ds[bvar].isel(t=0), bin_arr[i])
            group_labels = [bin_axes[i][j] for j in group_id]
            ds = ds.assign_coords({bvar + "_bin": ("pid", group_labels)})

        # Perform mean along the dataset and get final variables

        print("\nCalculating mean and standard deviation...")

        by_dims = [ds[key] for key in ds.coords if "_bin" in key]

        result = ds
        for dim_da in by_dims:
            try:
                result = xarray_reduce(
                    result,
                    dim_da,
                    func="mean",
                    sort=True,
                    dim="pid",
                    keep_attrs=True,
                    fill_value=np.nan,
                )
            except Exception:
                print(
                    "This is probably a problem with the multiple binning axes. Have to look over this."
                )
                raise

        for dim in vars:
            if axisym is False:
                result[dim + "_std"] = np.sqrt(
                    result[dim + "_sqw"] - result[dim + "_w"] ** 2
                )
                result = result.rename({dim + "_w": dim + "_mean"})

                newlname = get_attr_if_exists(
                    self._obj[dim], "long_name", lambda x: f"mean({x})", "mean"
                )
                result[dim + "_mean"].attrs["long_name"] = newlname

                newunits = get_attr_if_exists(self._obj[dim], "units")
                if newunits is not None:
                    result[dim + "_mean"].attrs["units"] = newunits

            else:
                result[dim + "_std"] = np.sqrt(result[dim + "_sqw"])

            result[dim + "_std"].attrs["long_name"] = get_attr_if_exists(
                self._obj[dim], "long_name", lambda x: f"std({x})", "std"
            )

            newunits = get_attr_if_exists(self._obj[dim], "units")
            if newunits is not None:
                result[dim + "_std"].attrs["units"] = newunits

            result = result.drop_vars(dim + "_sqw")

        result.attrs["pic_data_type"] = "grid"

        print("\nDone!")

        return result

    # BUG: debug units
    # TODO: add unit tests
    @stopwatch
    def bin_into_grid(
        self,
        axes_ds: xr.Dataset,
        t_var: str = "t",
        w_var: str = "q",
        r_var: str | None = None,
    ):
        r"""
        Bin particle data into a grid (density distribution).

        Parameters
        ----------
        axes_ds : Dataset
            Dataset containing grid axes information.

            ??? tip
                The axis information can be created for example with:
                ```python
                import ozzy as oz
                nx = 200
                ny = 150
                xlims = (0.0, 30.0)
                ylims = (-4.0, 4.0)
                axes_ds = oz.Dataset(
                    coords={
                        "x1": oz.utils.axis_from_extent(nx, xlims),
                        "x2": oz.utils.axis_from_extent(ny, ylims),
                    },
                    pic_data_type = "grid")
                ```
                Or it can be obtained from an existing grid data object with:
                ```python
                # fields may be an existing Dataset or DataArray
                axes_ds = fields.coords
                ```

            ??? note "Note about axis attributes"

                By default, the `long_name` and `units` attributes of the resulting grid axes are taken from the original particle Dataset. But these attributes are overriden if they are passed along with the `axes_ds` Dataset.

        t_var : str, optional
            Name of the time dimension in the input datasets.
        w_var : str, optional
            Name of the variable representing particle weights or particle charge.
        r_var : str | None, optional
            Name of the variable representing particle radial positions. If provided and if one of the `axes_ds` coordinates is `r_var`, the particle weights are divided by this variable.

        Returns
        -------
        parts : xarray.Dataset
            Dataset containing the charge density distribution on the grid.

        Raises
        ------
        KeyError
            If no spatial dimensions are found in the input `axes_ds`.
        ValueError
            If the `axes_ds` argument does not contain grid data.

        Notes
        -----
        The binned density data is multiplied by a factor that ensures that the total volume integral of the density corresponds to the sum of all particle weights $Q_w$. If $w$ is each particle's weight variable and $N_p$ is the total number of particles, then $Q_w$ is defined as:

        \[
        Q_w = \sum_i^{N_p} w_i
        \]

        Note that different simulation codes have different conventions in terms of what $Q_w$ corresponds to.

        Examples
        --------

        ???+ example "Usage"

            ```python
            import ozzy as oz
            import numpy as np

            # Create a sample particle dataset
            particles = oz.Dataset(
                {
                    "x1": ("pid", np.random.uniform(0, 10, 10000)),
                    "x2": ("pid", np.random.uniform(0, 5, 10000)),
                    "q": ("pid", np.ones(10000)),
                },
                coords={"pid": np.arange(10000)},
                attrs={"pic_data_type": "part"}
            )

            # Create axes for binning
            axes = oz.Dataset(
                coords={
                    "x1": oz.utils.axis_from_extent(100, (0.0, 10.0)),
                    "x2": oz.utils.axis_from_extent(50, (0.0, 5.0)),
                },
                pic_data_type = "grid",
            )

            # Bin particles into grid (Cartesian geometry)
            grid_data = particles.ozzy.bin_into_grid(axes)

            # Example 2: Using a different weight variable
            particles["w"] = ("pid", np.random.uniform(0.5, 1.5, 10000))
            grid_data_weighted = particles.ozzy.bin_into_grid(axes, w_var="w")

            # Example 3: Axisymmetric geometry
            grid_data_axisym = particles.ozzy.bin_into_grid(axes, r_var="x2")

            # Example 4: Time-dependent data
            time_dependent_particles = particles.expand_dims(dim={"t": [0, 1, 2]})
            time_dependent_grid = time_dependent_particles.ozzy.bin_into_grid(axes)

            ```
        """

        # Check grid dataset
        if "grid" not in axes_ds.attrs["pic_data_type"]:
            raise ValueError(
                "Axes Dataset must contain grid data (pic_data_type attribute must contain 'grid')"
            )

        # Check spatial dims
        spatial_dims = axes_ds.ozzy.get_space_dims(t_var)
        if len(spatial_dims) == 0:
            raise KeyError("Did not find any non-time dimensions in input axes dataset")

        # Get bin edges
        bin_edges = axes_ds.ozzy.get_bin_edges(t_var)

        q_binned = []
        raw_ds = self._obj

        # Divide weight by radius, if r_var is part of axes_ds

        def integrate_cart(da):
            # Put all delta factors together in dx_factor
            dx_factor = 1
            for dim in spatial_dims:
                dx = axes_ds[dim][1] - axes_ds[dim][0]
                dx_factor = dx_factor * dx
            return dx_factor * da.sum(dim=spatial_dims)

        def integrate_cyl(da):
            # Put all delta factors together in dx_factor
            dx_factor = 1
            for dim in spatial_dims:
                dx = axes_ds[dim][1] - axes_ds[dim][0]
                dx_factor = dx_factor * dx
            return dx_factor * (da[r_var] * da).sum(dim=spatial_dims)

        total_w = raw_ds[w_var].sum()

        print("\nBinning particles into grid...")

        if (r_var is not None) & (r_var in axes_ds):
            print(
                f"\n   - assuming {r_var} is the radial coordinate in axisymmetric geometry"
            )
            w_var_new = w_var + "_r"
            raw_ds[w_var_new] = raw_ds[w_var] / raw_ds[r_var]
            integrate = integrate_cyl
        else:
            w_var_new = w_var
            integrate = integrate_cart

        def get_dist(ds):
            part_coords = [ds[var] for var in spatial_dims]
            dist, edges = np.histogramdd(
                part_coords, bins=bin_edges, weights=ds[w_var_new]
            )
            return dist

        # Loop along time

        if t_var in raw_ds.dims:
            for i in np.arange(0, len(raw_ds[t_var])):
                ds_i = raw_ds.isel({t_var: i})
                dist = get_dist(ds_i)

                newcoords = {var: axes_ds[var] for var in spatial_dims}
                newcoords[t_var] = ds_i[t_var]
                qds_i = new_dataset(
                    data_vars={"rho": (spatial_dims, dist)},
                    coords=newcoords,
                    pic_data_type="grid",
                    data_origin=raw_ds.attrs["data_origin"],
                )
                q_binned.append(qds_i)

            parts = xr.concat(q_binned, t_var)

        else:
            dist = get_dist(raw_ds)
            newcoords = {var: axes_ds[var] for var in spatial_dims}
            parts = new_dataset(
                data_vars={"rho": (spatial_dims, dist)},
                coords=newcoords,
                pic_data_type="grid",
                data_origin=raw_ds.attrs["data_origin"],
            )

        # TODO: improve the formatting of the resulting units
        if r_var is None:
            rvar_attrs = None
        else:
            rvar_attrs = raw_ds[r_var].attrs
        units_str = self._define_q_units(raw_ds[spatial_dims], rvar_attrs)

        # Multiply by factor to ensure that integral of density matches sum of particle weights
        factor = total_w / integrate(parts["rho"])
        parts["rho"] = factor * parts["rho"]

        parts["rho"] = parts["rho"].assign_attrs(
            {"long_name": r"$\rho$", "units": units_str}
        )

        # Assign variable attributes
        for var in parts.coords:
            parts.coords[var] = parts.coords[var].assign_attrs(raw_ds[var].attrs)

            if var in spatial_dims:
                for attr_override in ["long_name", "units"]:
                    label = get_attr_if_exists(axes_ds[var], attr_override)
                    if label is not None:
                        parts.coords[var].attrs[attr_override] = label

        # Reorder and rechunk dimensions (e.g. x2,x1,t)

        dims_3d = ["x3", "x1", "x2"]
        dims_2d = ["x2", "x1"]
        dims_3d_box = ["x3", "x1_box", "x2"]
        dims_2d_box = ["x2", "x1_box"]

        for option in [dims_2d, dims_2d_box, dims_3d, dims_3d_box]:
            if all([var in parts.dims for var in option]):
                new_coords = option + [t_var] if t_var in parts.dims else option
                parts = parts.transpose(*new_coords).compute()
                parts = parts.chunk()

        return parts

    @stopwatch
    def get_phase_space(
        self,
        vars: list[str],
        extents: dict[str, tuple[float, float]] | None = None,
        nbins: int | dict[str, int] = 200,
        r_var: str | None = None,
        t_var: str = "t",
        w_var: str = "q",
    ):
        """Generate a phase space grid from particle data.

        Creates a gridded dataset by depositing particle quantities onto
        a 2D phase space.

        Parameters
        ----------
        vars : list[str]
            Variables to deposit onto phase space.
        extents : dict[str, tuple[float,float]], optional
            Minimum and maximum extent for each variable. If not specified, extents are calculated from the data.
        nbins : int | dict[str, int], optional
            Number of bins for each variable. If `int`, the same number of bins is used for all variables.
        r_var : str | None, optional
            Name of the variable representing particle radial positions. If provided and if one of `vars` is `r_var`, the particle weights are divided by this variable.
        t_var : str, optional
            Name of the time dimension in the input datasets.
        w_var : str, optional
            Name of the variable representing particle weights or particle charge.

        Returns
        -------
        xarray.Dataset
            Dataset with phase space data.

        Examples
        --------

        ???+ example "Transverse phase space"
            ```python

            import ozzy as oz
            import numpy as np

            # Create a sample particle dataset
            ds = oz.Dataset(
                {
                    "x1": ("pid", np.random.rand(10000)),
                    "x2": ("pid", np.random.rand(10000)),
                    "p1": ("pid", np.random.rand(10000)),
                    "p2": ("pid", np.random.rand(10000)),
                    "q": ("pid", np.ones(10000)),
                },
                coords={"pid": np.arange(10000)},
                pic_data_type="part",
                data_origin="ozzy",
            )

            ds_ps = ds.ozzy.get_phase_space(['p2', 'x2'], nbins=100)
            ```
        """
        if extents is None:
            extents = {}
            for v in vars:
                maxval = float(self._obj[v].max().compute().to_numpy())
                minval = float(self._obj[v].min().compute().to_numpy())

                if minval == maxval:
                    minval = minval - 0.05 * abs(minval)
                    maxval = maxval + 0.05 * abs(maxval)

                if (minval < 0) & (maxval > 0):
                    extr = max([abs(minval), maxval])
                    lims = (-extr, extr)
                else:
                    lims = (minval, maxval)
                if lims[0] == lims[1]:
                    lims = (lims[0] - 0.5, lims[0] + 0.5)
                extents[v] = lims

        if isinstance(nbins, int):
            bins = {}
            for v in vars:
                bins[v] = nbins
        else:
            bins = nbins

        axes_ds = new_dataset(
            pic_data_type="grid", data_origin=self._obj.attrs["data_origin"]
        )
        for v in vars:
            ax = axis_from_extent(bins[v], extents[v])
            axes_ds = axes_ds.assign_coords({v: ax})
            axes_ds[v].attrs.update(self._obj[v].attrs)

        # Deposit quantities on phase space grid

        ps = self.bin_into_grid(axes_ds, r_var=r_var, w_var=w_var, t_var=t_var)
        ps["rho"].attrs["units"] = r"a.u."

        return ps

    @stopwatch
    def get_emittance(
        self,
        norm_emit: bool = True,
        axisym: bool = False,
        p_all_vars: list[str] = ["p1", "p2", "p3"],
        x_var: str = "x2",
        p_var: str = "p2",
        w_var: str = "q",
    ) -> xr.Dataset:
        r"""Calculate the RMS beam emittance.

        Computes the normalized or geometric RMS emittance based on particle positions and momenta.
        For axisymmetric beams, returns the Lapostolle emittance (see _Notes_ below).

        !!! warning

            This method assumes that the particle dimension is `"pid"`.

        Parameters
        ----------
        norm_emit : bool
            Whether to calculate normalized emittance (multiplied by $\left< \beta \gamma \right>$).
        axisym : bool
            If `True`, calculate Lapostolle emittance for axisymmetric beams
        p_all_vars : list[str]
            List of names of momentum components.

            !!! note

                The components should be sorted, e.g. `["px", "py", "pz"]`.

                If `axisym=True`, only the two first components will be adopted.

        x_var : str
            Variable name for position coordinate in Dataset that should be used for emittance calculation
        p_var : str
            Variable name for momentum coordinate in Dataset that should be used for emittance calculation. This argument is only relevant when `axisym=False`, otherwise it is set to `p_all_vars[1]`.
        w_var : str
            Variable name for particle weights in Dataset


        Returns
        -------
        xarray.Dataset
            Dataset containing the calculated emittance and particle counts for each data point.

            The emittance variable is named `"emit_norm"` if `norm_emit=True`,
            otherwise `"emit"`. Also includes a `"counts"` variable with particle
            counts.


        Notes
        -----

        The geometric emittance along a given transverse dimension $i$ is calculated according to:

        $\epsilon_i = \sqrt{\left<x_i^2\right> \left<{x'_i}^2\right> - \left(x_i x'_i\right)^2}$

        where $x_i$ is the particle position, and $x'_i \approx p_i / p_\parallel$ is the trace for relativistic particles with longitudinal momentum $p_\parallel$ and transverse momentum $p_i \ll p_\parallel$. The angle brackets denote a weighted average over particles.

        The normalized emittance (`norm_emit=True`, default) is calculated as:

        $\epsilon_{N,i} = \left< \beta \gamma \right> \ \epsilon_i$

        where $\beta \gamma = \left| \vec{p} \right| / (m_\mathrm{sp} c)$.

        For a 2D cylindrical, axisymmetric geometry (`axisym=True`) this function returns the Lapostolle emittance[^1]<sup>,</sup>[^2], i.e.:

        $\epsilon = 4 \ \epsilon_i$


        [^1]: [J. D. Lawson, P. M. Lapostolle, and R. L. Gluckstern, Particle Accelerators **5**, 61–65 (1973)](https://inspirehep.net/literature/87013),
        [^2]: [P. M. Lapostolle, IEEE Transactions on Nuclear Science **18**, 1101–1104 (1971)](https://ieeexplore-ieee-org.ezproxy.cern.ch/document/4326292)


        Examples
        --------
        ???+ example "Calculate normalized emittance in 2D cyl. geometry"
            ```python
            import ozzy as oz
            import numpy as np

            # Create a sample particle dataset
            particles = oz.Dataset(
                {
                    "x": ("pid", np.random.uniform(0, 10, 10000)),
                    "r": ("pid", np.random.uniform(0, 5, 10000)),
                    "px": ("pid", np.random.uniform(99, 101, 10000)),
                    "pr": ("pid", np.random.uniform(-2e-4, 2e-4, 10000)),
                    "q": ("pid", np.ones(10000)),
                },
                coords={"pid": np.arange(10000)},
                attrs={"pic_data_type": "part"}
            )

            emittance = particles.ozzy.get_emittance(axisym=True, x_var="r", p_all_vars=["px", "pr"])
            # Returns Dataset with normalized emittance in k_p^(-1) rad
            ```
        """

        ds = self._obj

        # Process axisymmetry option
        if axisym:
            factor = 4
            suffix_dim = ""
            p_all_vars = p_all_vars[0:2]
            p_var = p_all_vars[1]
        else:
            factor = 1
            p_all_vars = p_all_vars[0:3]
            try:
                var_label = ds[x_var].attrs["long_name"].strip("$").split("_", 1)
                suffix_dim = var_label[1]
            except KeyError:
                suffix_dim = ""

        # Process xvar and pvar arguments
        self._contains_datavars([x_var, p_var] + p_all_vars)

        # Get secondary quantities

        p_longit = p_all_vars[0]

        ds["x_prime"] = ds[p_var] / ds[p_longit]
        ds["x_sq"] = ds[w_var] * ds[x_var] ** 2
        ds["x_prime_sq"] = ds[w_var] * ds["x_prime"] ** 2
        ds["x_x_prime"] = ds[w_var] * ds[x_var] * ds["x_prime"]

        ds["beta_gamma"] = ds.ozzy._calc_beta_gamma(p_all_vars, w_var)

        # Calculate emittance

        q_tot = ds[w_var].sum(dim="pid", skipna=True)

        x_sq_mean = ds["x_sq"].sum(dim="pid", skipna=True) / q_tot
        x_prime_sq_mean = ds["x_prime_sq"].sum(dim="pid", skipna=True) / q_tot
        x_x_prime_mean = ds["x_x_prime"].sum(dim="pid", skipna=True) / q_tot
        beta_gamma_mean = ds["beta_gamma"].sum(dim="pid", skipna=True) / q_tot

        emit = np.sqrt(x_sq_mean * x_prime_sq_mean - x_x_prime_mean**2)

        if norm_emit:
            emit = beta_gamma_mean * emit
            suffix_norm = "N"
            var_name = "emit_norm"
        else:
            suffix_norm = ""
            var_name = "emit"

        emit_result = factor * emit
        emit_result = emit_result.rename(var_name)

        # Get number of particles in each bin

        counts = ds[x_var].notnull().sum(dim="pid", skipna=True).rename("counts")

        # Create output dataset

        emit = new_dataset(
            data_vars={var_name: emit_result, "counts": counts},
            pic_data_type="grid",
            data_origin="ozzy",
        )

        # Set units and label

        suffix = ",".join(filter(None, [suffix_norm, suffix_dim]))

        emit[var_name].attrs["units"] = r"$k_p^{-1} \ \mathrm{rad}$"
        emit[var_name].attrs["long_name"] = r"$\epsilon_{" + suffix + "}$"

        emit["counts"].attrs["units"] = r"1"
        emit["counts"].attrs["long_name"] = "Counts"

        return emit

    @stopwatch
    def get_slice_emittance(
        self,
        axis_ds: xr.Dataset | None = None,
        nbins: int | None = None,
        norm_emit: bool = True,
        axisym: bool = False,
        p_all_vars: list[str] = ["p1", "p2", "p3"],
        min_count: int | None = None,
        slice_var: str = "x1_box",
        x_var: str = "x2",
        p_var: str = "p2",
        w_var: str = "q",
    ) -> xr.Dataset:
        r"""
        Calculate the RMS slice emittance of particle data.

        This method computes the slice emittance by binning particles along a specified
        variable and calculating the RMS emittance (normalized or geometric) for each slice.
        For axisymmetric beams, returns the Lapostolle emittance (see _Notes_ below).

        !!! warning

            This method assumes that the particle dimension is `"pid"`.

        Parameters
        ----------
        axis_ds : xarray.Dataset or None, optional
            Dataset containing coordinate information for binning. If provided, bin edges
            are extracted from this dataset. Either `axis_ds` or `nbins` must be specified.

            !!! note
                If the label and unit attributes exist in `axis_ds[slice_var]` (`'long_name'` and `'units'`, respectively), these attributes are adopted for the output dataset.

        nbins : int or None, optional
            Number of bins to use for slicing. Either `axis_ds` or `nbins` must be specified.
        norm_emit : bool, default True
            Whether to calculate normalized emittance (multiplied by $\left< \beta \gamma \right>$).
        axisym : bool, default False
            Whether to apply Lapostolle factor of 4.
        p_all_vars : list[str]
            List of names of momentum components.

            !!! note

                The components should be sorted, e.g. `["px", "py", "pz"]`.

                If `axisym=True`, only the two first components will be adopted.

        min_count : int or None, optional
            Minimum number of particles required in each bin for valid calculation.
        slice_var : str
            Variable name to use for slicing/binning the particles.
        x_var : str
            Variable name for the transverse position coordinate that should be used for emittance calculation.
        p_var : str
            Variable name for the transverse momentum coordinate that should be used for emittance calculation. This argument is only relevant when `axisym=False`, otherwise it is set to `p_all_vars[1]`.
        w_var : str
            Variable name for the particle weights/charges.


        Returns
        -------
        xarray.Dataset
            Dataset containing the calculated slice emittance and particle counts per bin.

            The emittance variable is named `"slice_emit_norm"` if `norm_emit=True`,
            otherwise `"slice_emit"`. Also includes a `"counts"` variable with particle
            counts per bin.

        Notes
        -----

        Particles are binned along the specified `slice_var` variable, and the emittance is computed for each binned ensemble.

        The geometric emittance along a given transverse dimension $i$ is calculated according to:

        $\epsilon_i = \sqrt{\left<x_i^2\right> \left<{x'_i}^2\right> - \left(x_i x'_i\right)^2}$

        where $x_i$ is the particle position, and $x'_i \approx p_i / p_\parallel$ is the trace for relativistic particles with longitudinal momentum $p_\parallel$ and transverse momentum $p_i \ll p_\parallel$. The angle brackets denote a weighted average over particles.

        The normalized emittance (`norm_emit=True`, default) is calculated as:

        $\epsilon_{N,i} = \left< \beta \gamma \right> \ \epsilon_i$

        where $\beta \gamma = \left| \vec{p} \right| / (m_\mathrm{sp} c)$.

        For a 2D cylindrical, axisymmetric geometry (`axisym=True`) this function returns the Lapostolle emittance[^1]<sup>,</sup>[^2], i.e.:

        $\epsilon = 4 \ \epsilon_i$


        [^1]: [J. D. Lawson, P. M. Lapostolle, and R. L. Gluckstern, Particle Accelerators **5**, 61–65 (1973)](https://inspirehep.net/literature/87013),
        [^2]: [P. M. Lapostolle, IEEE Transactions on Nuclear Science **18**, 1101–1104 (1971)](https://ieeexplore-ieee-org.ezproxy.cern.ch/document/4326292)


        Examples
        --------
        ???+ example "Calculate normalized slice emittance in 2D cyl. geometry"
            ```python
            import ozzy as oz
            import numpy as np

            # Create a sample particle dataset
            particles = oz.Dataset(
                {
                    "x": ("pid", np.random.uniform(0, 10, 10000)),
                    "r": ("pid", np.random.uniform(0, 5, 10000)),
                    "px": ("pid", np.random.uniform(99, 101, 10000)),
                    "pr": ("pid", np.random.uniform(-2e-4, 2e-4, 10000)),
                    "q": ("pid", np.ones(10000)),
                },
                coords={"pid": np.arange(10000)},
                attrs={"pic_data_type": "part"}
            )

            # Longitudinal axis along which to bin
            axis = oz.utils.axis_from_extent(500, (0,10))
            axis_ds = oz.Dataset({"x": axis}, pic_data_type = "grid")

            emittance = particles.ozzy.get_slice_emittance(axis_ds=axis_ds, axisym=True, slice_var="x", x_var="r", p_all_vars=["px","pr"])
            # Returns Dataset with normalized emittance in k_p^(-1) rad
            ```
        """
        ds = self._obj

        # Process axisymmetry option
        if axisym:
            factor = 4
            suffix_dim = ""
            p_all_vars = p_all_vars[0:2]
            p_var = p_all_vars[1]
        else:
            factor = 1
            p_all_vars = p_all_vars[0:3]
            try:
                var_label = ds[x_var].attrs["long_name"].strip("$").split("_", 1)
                suffix_dim = var_label[1]
            except KeyError:
                suffix_dim = ""

        # Process xvar and pvar arguments
        self._contains_datavars([slice_var, x_var, p_var, w_var] + p_all_vars)

        # Process axis_ds and nbins arguments
        if (axis_ds is None) and (nbins is None):
            raise ValueError("Either axis_ds or nbins must be provided")
        elif axis_ds is not None:
            if slice_var not in axis_ds.coords:
                raise KeyError(
                    f"Cannot find '{slice_var}' variable in provided axis_ds"
                )
            bins = axis_ds.ozzy.get_bin_edges()[0]
        elif nbins is not None:
            xmin = ds[slice_var].min().compute().data
            xmax = ds[slice_var].max().compute().data
            axis = axis_from_extent(nbins, (xmin, xmax))
            axis_ds = new_dataset({slice_var: axis}, pic_data_type="grid")
            bins = axis_ds.ozzy.get_bin_edges()[0]

        # Process axisymmetry option
        if axisym:
            factor = 4
            suffix_dim = ""
        else:
            factor = 1
            suffix_dim = ds[x_var].attrs["long_name"].strip("$")

        # Get secondary quantities

        p_longit = p_all_vars[0]

        ds["x_prime"] = ds[p_var] / ds[p_longit]
        ds["x_sq"] = ds[w_var] * ds[x_var] ** 2
        ds["x_prime_sq"] = ds[w_var] * ds["x_prime"] ** 2
        ds["x_x_prime"] = ds[w_var] * ds[x_var] * ds["x_prime"]

        ds["beta_gamma"] = ds.ozzy._calc_beta_gamma(p_all_vars, w_var)

        # Calculate emittance and bin along slice_var

        reduce_args = {
            "func": "sum",
            "isbin": True,
            "expected_groups": bins,
            "dim": "pid",
            "skipna": True,
            "min_count": min_count,
        }

        q_slice = xarray_reduce(ds[[w_var, slice_var]], slice_var, **reduce_args)[w_var]

        x_sq_slice = (
            xarray_reduce(ds[["x_sq", slice_var]], slice_var, **reduce_args)["x_sq"]
            / q_slice
        )
        x_prime_sq_slice = (
            xarray_reduce(ds[["x_prime_sq", slice_var]], slice_var, **reduce_args)[
                "x_prime_sq"
            ]
            / q_slice
        )
        x_x_prime_slice = (
            xarray_reduce(ds[["x_x_prime", slice_var]], slice_var, **reduce_args)[
                "x_x_prime"
            ]
            / q_slice
        )
        bg_slice = (
            xarray_reduce(ds[["beta_gamma", slice_var]], slice_var, **reduce_args)[
                "beta_gamma"
            ]
            / q_slice
        )

        emit_slice = np.sqrt(x_sq_slice * x_prime_sq_slice - x_x_prime_slice**2)

        if norm_emit:
            emit_slice = bg_slice * emit_slice
            suffix_norm = "N"
            var_name = "slice_emit_norm"
        else:
            suffix_norm = ""
            var_name = "slice_emit"

        emit_result = factor * emit_slice
        emit_result = emit_result.rename(var_name)

        # Get number of particles in each bin

        ds["counts"] = ds[slice_var].notnull()
        counts = xarray_reduce(
            ds[["counts", slice_var]], slice_var, **reduce_args, fill_value=0
        )
        counts = counts["counts"]

        # Create output dataset

        emit = new_dataset(
            data_vars={var_name: emit_result, "counts": counts},
            pic_data_type="grid",
            data_origin="ozzy",
        )

        # Convert binned coordinate to normal Numpy array instead of pandas.Interval
        # (since this leads to an error when trying to save the object)
        emit = emit.rename_dims({slice_var + "_bins": slice_var})
        emit = emit.reset_index(slice_var + "_bins")
        emit = emit.assign_coords(
            {slice_var: convert_interval_to_mid(emit[slice_var + "_bins"])}
        )
        emit = emit.drop_vars(slice_var + "_bins")

        # Set units and label

        suffix = ",".join(filter(None, [suffix_norm, suffix_dim]))

        emit[var_name].attrs["units"] = r"$k_p^{-1} \ \mathrm{rad}$"
        emit[var_name].attrs["long_name"] = r"$\epsilon_{" + suffix + "}$"

        emit["counts"].attrs["units"] = r"1"
        emit["counts"].attrs["long_name"] = "Counts"

        # Overwrite attributes of slice_var if they're provided with axis_ds,
        # otherwise try to take the attributes from original dataset
        for attr_item in ["long_name", "units"]:
            if attr_item in axis_ds[slice_var].attrs:
                emit[slice_var].attrs[attr_item] = axis_ds[slice_var].attrs[attr_item]
            elif attr_item in ds[slice_var].attrs:
                emit[slice_var].attrs[attr_item] = ds[slice_var].attrs[attr_item]

        return emit

    @stopwatch
    def get_energy_spectrum(
        self,
        axis_ds: xr.Dataset | None = None,
        nbins: int | None = None,
        ene_var: str = "ene",
        w_var: str = "q",
    ) -> xr.Dataset:
        r"""
        Calculate the energy spectrum of particles.

        This method computes a histogram of particle energy, binning the energy values
        and summing the associated charge or weighting variable in each bin.

        Parameters
        ----------
        axis_ds : xarray.Dataset or None, optional
            Dataset containing the energy axis to use for binning. Must have `ene_var`
            as a coordinate. If `None`, `nbins` must be provided.

            !!! note
                If the label and unit attributes exist in `axis_ds[ene_var]` (`'long_name'` and `'units'`, respectively), these attributes are adopted for the output dataset.

        nbins : int or None, optional
            Number of bins to use for the energy axis. Only used if `axis_ds` is `None`.
            If `None`, `axis_ds` must be provided.
        ene_var : str, optional
            Name of the energy variable in the dataset, default is `"ene"`.
        w_var : str, optional
            Name of the weighting variable (typically charge) in the dataset,
            default is `"q"`.

        Returns
        -------
        xarray.Dataset
            A new dataset containing the energy spectrum with the following variables:
            - The weighting variable (e.g., `"q"`) containing the histogram of charge per energy bin
            - `"counts"` containing the number of particles in each energy bin

        Notes
        -----
        The **absolute value** of the weighting variable is used for the calculation.

        Examples
        --------
        ???+ example "Basic usage with number of bins"
            ```python
            import numpy as np
            import ozzy as oz

            # Create a sample particle dataset
            rng = np.random.default_rng()
            ds = oz.Dataset(
                {
                    "ene": ("pid", rng.normal(100, 5, size=10000) ),
                    "q": ("pid", rng.random(10000)),
                },
                coords={"pid": np.arange(10000)},
                attrs={"pic_data_type": "part"}
            )

            # Get energy spectrum
            spectrum = ds.ozzy.get_energy_spectrum(nbins=100)
            # Plot the result
            spectrum.q.plot()
            ```

        ???+ example "Using a custom energy axis"
            ```python
            import numpy as np
            import ozzy as oz

            # Create a sample particle dataset
            rng = np.random.default_rng()
            ds = oz.Dataset(
                {
                    "p1": ("pid", rng.lognormal(3.0, 1.0, size=10000) ),
                    "weight": ("pid", rng.random(10000)),
                },
                coords={"pid": np.arange(10000)},
                attrs={"pic_data_type": "part"}
            )

            # Create a custom logarithmic energy axis
            energy_axis = np.logspace(-1, 3, 50)  # 50 points from 0.1 to 1000
            axis_ds = oz.Dataset(coords={"p1": energy_axis}, pic_data_type="grid")
            axis_ds["p1"].attrs["long_name"] = r"$p_1$"
            axis_ds["p1"].attrs["units"] = r"$m_\mathrm{sp} c$"

            # Get energy spectrum using this axis
            spectrum = ds.ozzy.get_energy_spectrum(axis_ds=axis_ds, ene_var="p1", w_var="weight")
            # Plot the result
            spectrum["weight"].plot(marker=".")
            # Spectrum now contains the summed weights in each logarithmic energy bin
            ```
        """
        ds = self._obj

        # Process xvar and pvar arguments
        self._contains_datavars([ene_var, w_var])

        # Process axis_ds and nbins arguments
        if (axis_ds is None) and (nbins is None):
            raise ValueError("Either axis_ds or nbins must be provided")
        elif axis_ds is not None:
            if ene_var not in axis_ds.coords:
                raise KeyError(f"Cannot find '{ene_var}' variable in provided axis_ds")
            bins = axis_ds.ozzy.get_bin_edges()[0]
        elif nbins is not None:
            xmin = ds[ene_var].min().compute().data
            xmax = ds[ene_var].max().compute().data
            axis = axis_from_extent(nbins, (xmin, xmax))
            axis_ds = new_dataset({ene_var: axis}, pic_data_type="grid")
            bins = axis_ds.ozzy.get_bin_edges()[0]

        # Bin along energy variable and sum charge

        reduce_args = {
            "func": "sum",
            "isbin": True,
            "expected_groups": bins,
            "dim": "pid",
            "skipna": True,
        }

        # Take absolute value of charge/weighting variable
        ds[w_var] = abs(ds[w_var])

        ene_hist = xarray_reduce(ds[[w_var, ene_var]], ene_var, **reduce_args)[w_var]

        # Get number of particles in each bin

        ds["counts"] = ds[ene_var].notnull()
        counts = xarray_reduce(
            ds[["counts", ene_var]], ene_var, **reduce_args, fill_value=0
        )
        counts = counts["counts"]

        # Create output dataset

        ene_spectrum = new_dataset(
            data_vars={w_var: ene_hist, "counts": counts},
            pic_data_type="grid",
            data_origin="ozzy",
        )

        # Convert binned coordinate to normal Numpy array instead of pandas.Interval
        # (since this leads to an error when trying to save the object)
        ene_spectrum = ene_spectrum.rename_dims({ene_var + "_bins": ene_var})
        ene_spectrum = ene_spectrum.reset_index(ene_var + "_bins")
        ene_spectrum = ene_spectrum.assign_coords(
            {ene_var: convert_interval_to_mid(ene_spectrum[ene_var + "_bins"])}
        )
        ene_spectrum = ene_spectrum.drop_vars(ene_var + "_bins")

        # Set units and labels

        # Add "| ... |" to label of w_var
        if "long_name" in ene_spectrum[w_var].attrs:
            old_label = ene_spectrum[w_var].attrs["long_name"]

            if (old_label[0] == "$") & (old_label[-1] == "$"):
                new_label = insert_str_at_index(old_label, "|", 1)
                new_label = insert_str_at_index(new_label, "|", -1)
            else:
                new_label = "|" + old_label + "|"

            ene_spectrum[w_var].attrs["long_name"] = new_label
        else:
            ene_spectrum[w_var].attrs["long_name"] = "Weighted counts"

        ene_spectrum["counts"].attrs["units"] = r"1"
        ene_spectrum["counts"].attrs["long_name"] = "Counts"

        # Overwrite attributes of ene_var if they're provided with axis_ds,
        # otherwise try to take the attributes from original dataset
        for attr_item in ["long_name", "units"]:
            if attr_item in axis_ds[ene_var].attrs:
                ene_spectrum[ene_var].attrs[attr_item] = axis_ds[ene_var].attrs[
                    attr_item
                ]
            elif attr_item in ds[ene_var].attrs:
                ene_spectrum[ene_var].attrs[attr_item] = ds[ene_var].attrs[attr_item]

        return ene_spectrum

    # CAVEAT: assumes particle dimension is "pid"
    def get_weighted_median(
        self,
        var: str,
        w_var: str = "q",
        t_var: str = "t",
    ):
        r"""
        Calculate the weighted median of a variable in the particle dataset.

        This method computes the median of `var` weighted by the values in `w_var`,
        for each value in the time variable `t_var` (if the `t_var` dimension exists).

        Parameters
        ----------
        var : str
            Name of the variable for which to calculate the weighted median.
        w_var : str, optional
            Name of the weighting variable, by default `"q"`.
            The absolute value of this variable is used for weighting.
        t_var : str, optional
            Name of the time dimension to iterate over, by default `"t"`.
            If this dimension exists in the dataset, a weighted median
            is calculated for each time step.

        Returns
        -------
        xarray.DataArray
            DataArray containing the weighted median value(s).
            If `t_var` is present in the dataset, the result will have
            the same `t_var` dimension.

        Notes
        -----
        The weighted median is calculated by:
        1. Sorting the data according to the variable of interest
        2. Computing the cumulative sum of weights
        3. Finding the point where the cumulative sum of weights reaches half
        of the total weight

        For an odd number of observations, the midpoint value is used directly.
        For an even number, the average of the two middle values is used.


        Examples
        --------
        ???+ example "Basic usage with particle energy"
            ```python
            import numpy as np
            import ozzy as oz

            # Create a sample particle dataset
            rng = np.random.default_rng(seed=42)
            ds = oz.Dataset(
                {
                    "energy": ("pid", rng.normal(100, 20, size=1000)),
                    "q": ("pid", rng.random(1000)),
                },
                coords={"pid": np.arange(1000)},
                pic_data_type = "part",
            )

            # Calculate the weighted median of energy
            median_energy = ds.ozzy.get_weighted_median(var="energy")
            print(f"Weighted median energy: {median_energy.values:.2f}")
            # Weighted median energy: ~100.00 (exact value will vary)
            ```

        ???+ example "Time-dependent weighted median"
            ```python
            import numpy as np
            import ozzy as oz

            # Create a sample particle dataset with time dimension
            rng = np.random.default_rng(seed=42)
            times = np.linspace(0, 10, 5)
            energies = np.zeros((5, 100))

            # Create time-dependent energies
            for i, t in enumerate(times):
                energies[i] = rng.normal(100 + t*10, 20, size=100)

            ds = oz.Dataset(
                {
                    "energy": (["t", "pid"], energies),
                    "q": (["t", "pid"], rng.random((5, 100))),
                },
                coords={
                    "t": times,
                    "pid": np.arange(100)
                },
                pic_data_type = "part",
            )

            # Calculate the time-dependent weighted median of energy
            median_energy = ds.ozzy.get_weighted_median(var="energy")

            # Plot the result
            median_energy.plot()
            # The plot will show the weighted median energy increasing over time
            ```
        """
        ds = self._obj
        pidvar = "pid"

        # Process var and w_var arguments
        self._contains_datavars([var, w_var])

        # Define function where weighted median is calculated at each time
        def process_single(ds_single):
            # Sort according to values
            ds_sorted = ds_single.sortby(var)

            # Add variable with cumulative sum of weight
            ds_sorted["w_cumsum"] = abs(ds_sorted[w_var]).cumsum(skipna=True).compute()

            # Get value at which median cumulative sum of weight reaches 1/2 of total weights
            mid_weight = (
                0.5 * abs(ds_sorted[w_var]).sum(dim=pidvar, skipna=True).compute()
            )

            # Median value is determined differently depending on
            # whether number of values/observations is even or odd

            ntotal = ds_sorted.sizes[pidvar]

            if ntotal % 2 == 0:
                upper_half = ds_sorted.where(
                    ds_sorted["w_cumsum"] > mid_weight, drop=True
                )
                lower_half = ds_sorted.where(
                    ds_sorted["w_cumsum"] <= mid_weight, drop=True
                )

                val1 = upper_half[var][0].compute()
                val2 = lower_half[var][-1].compute()

                da_wmedian = (val1 + val2) * 0.5

            else:
                upper_half = ds_sorted.where(
                    ds_sorted["w_cumsum"] >= mid_weight, drop=True
                )

                da_wmedian = upper_half[var][0].compute()

            return da_wmedian

        # Check whether iteration along t is necessary

        if t_var in ds.dims:
            ds_t_all = []
            for tval in tqdm(ds[t_var]):
                ds_t = ds.sel({t_var: tval})
                ds_t_all.append(process_single(ds_t))
            # Concatenate all median values
            da_out = xr.concat(ds_t_all, t_var)

        else:
            da_out = process_single(ds)

        # Change label of processed quantity

        if "long_name" in da_out.attrs:
            quant_label = da_out.attrs["long_name"]

            if (quant_label[0] == "$") & (quant_label[-1] == "$"):
                quant_label = quant_label.strip("$")
                new_label = r"$\mathrm{med}\left(" + quant_label + r"\right) $"

            else:
                new_label = f"med({quant_label})"

            da_out.attrs["long_name"] = new_label

        else:
            da_out.attrs["long_name"] = f"med({da_out.name})"

        return da_out
