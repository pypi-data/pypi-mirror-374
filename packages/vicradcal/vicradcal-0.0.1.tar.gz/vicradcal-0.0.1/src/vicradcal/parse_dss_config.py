# parse_dss_config.py

import pandas as pd
import numpy as np

translator = {
    "VIC1": "VIC Band 1 \n(415nm)",
    "VIC2": "VIC Band 2 \n(850nm)",
    "VIC3": "VIC Band 3 \n(750nm)",
    "VIC4": "VIC Band 4 \n(565nm)",
    "VIC5": "VIC Band 5 \n(675nm)",
    "VIC6": "VIC Band 6 \n(900nm)",
    "VIC7": "VIC Band 7 \n(950nm)"
}


def parse_dss_config(excel_path: str):
    """
    Creates nested dictionaries of albedos and radiance levels stored in
    the "DSS_Spectra_As-run_consolidated_2025cal.xlsx" excel spreadsheet.

    Parameters
    ----------
    excel_path: str
        File path to the excel sheet

    Returns
    -------
    dict
        Returns a dictionary that will be accesbile through `constants.py`.
        The format of the dictionary is:
        {
            "filter1": {
                "albedos": [...],
                "radiances: [...]
            },
            .
            .
            .
            "filter7": {
                "albedos": [...],
                "radiances: [...]
            }
        }
    """
    df = pd.read_excel(excel_path,
                       header=[0, 1, 2],
                       sheet_name="DSS Config Table")

    def get_filter_idx(filtname):
        filter_levels = df.xs("Config. Label", axis=1, level=2)
        spec_qty = df.xs("CXR Spectra Qty", axis=1, level=2)
        colname = "VIC Band As-run %-Albedo"
        horiz_idx = (df.columns.get_level_values(0) == colname) &\
                    (df.columns.get_level_values(2) == translator[filtname])
        idx1 = (
            filter_levels.iloc[:, 0].str.contains(filtname)  # type: ignore
        ) &\
            (
                spec_qty.iloc[:, 0] != '-'  # type: ignore
            )

        albedo_5pct = (abs(df.iloc[:, horiz_idx] - 0.05) < 0.003).squeeze()
        albedo_20pct = (abs(df.iloc[:, horiz_idx] - 0.20) < 0.03).squeeze()
        albedo_50pct = (abs(df.iloc[:, horiz_idx] - 0.50) < 0.13).squeeze()

        name_list = df.loc[idx1, :].iloc[:, 3].to_numpy().tolist()
        low_check = any([("5%" in j) | ("6%" in j) | ("6.5%" in j)
                        for j in name_list])
        mid_check = any(["20%" in j for j in name_list])
        hi_check = any(["50%" in j for j in name_list])

        checklist = np.array([low_check, mid_check, hi_check])
        extra_albedos = np.array([albedo_5pct, albedo_20pct, albedo_50pct])

        if not all(checklist):
            for arr in extra_albedos[~checklist]:
                idx1 = idx1 | arr
            return idx1
        else:
            return idx1

    def get_filter_albedos(filtname):

        vert_idx = get_filter_idx(filtname)
        colname = "VIC Band As-run %-Albedo"
        horiz_idx = (df.columns.get_level_values(0) == colname) &\
                    (df.columns.get_level_values(2) == translator[filtname])
        return pd.Series(
            df.loc[vert_idx, horiz_idx].squeeze("columns"),  # type: ignore
            name="Albedos"
        ).to_frame()  # type: ignore

    def get_filter_radiances(filtname):
        vert_idx = get_filter_idx(filtname)
        colname = "VIC Band As-run Band-averaged Spectral Radiance "\
                  "[W/(m^2-sr-um)]"
        horiz_idx = (df.columns.get_level_values(0) == colname) &\
                    (df.columns.get_level_values(2) == translator[filtname])
        return pd.Series(
            df.loc[vert_idx, horiz_idx].squeeze("columns"),  # type: ignore
            name="Radiances"
        ).to_frame()  # type: ignore

    def get_filter_DSS(filtname):
        vert_idx = get_filter_idx(filtname)
        horiz_idx = (df.columns.get_level_values(2) == "DSS Lamp State")
        return pd.Series(
            df.loc[vert_idx, horiz_idx].squeeze("columns"),  # type: ignore
            name="Radiances"
        ).to_frame()  # type: ignore

    def compile_filter_values(filtname):
        albedo_df = get_filter_albedos(filtname)
        radiance_df = get_filter_radiances(filtname)
        dss = get_filter_DSS(filtname)
        out_df = pd.concat([albedo_df, radiance_df], axis=1)
        out_df.index = dss  # type: ignore
        out_df.index.name = "DSS_Level"
        return out_df

    def format_dicts(filtname):
        res = compile_filter_values(filtname)
        return {
            f"filter{filtname[-1]}": {
                "albedos": res.Albedos.to_numpy(),
                "radiances": res.Radiances.to_numpy()
            }
        }

    def consolidate_dicts(d: dict, print_results: bool = False):
        tiny_dict = {}
        for filt, filt_dict in d.items():
            low_vals = np.array([
                (i, j)
                for i, j in zip(filt_dict["albedos"], filt_dict["radiances"])
                if abs(i-0.05) < 0.02
            ])
            mid_vals = np.array([
                (i, j)
                for i, j in zip(filt_dict["albedos"], filt_dict["radiances"])
                if abs(i-0.2) < 0.1
            ])
            hi_vals = np.array([
                (i, j)
                for i, j in zip(filt_dict["albedos"], filt_dict["radiances"])
                if abs(i-0.5) < 0.13
            ])

            if print_results:
                print(f"{filt}\n\tLow: {low_vals.mean(axis=0)}"
                      f"\n\tMid: {mid_vals.mean(axis=0)}\n\t"
                      f"High: {hi_vals.mean(axis=0)}")

            lowalb = low_vals[:, 0]
            midalb = mid_vals[:, 0]
            hialb = hi_vals[:, 0]
            lowrad = low_vals[:, 1]
            midrad = mid_vals[:, 1]
            hirad = hi_vals[:, 1]
            tiny_dict = {
                **tiny_dict,
                filt: {
                    "low_albedo": (lowalb.mean(axis=0), lowalb.std(axis=0)),
                    "mid_albedo": (midalb.mean(axis=0), midalb.std(axis=0)),
                    "high_albedo": (hialb.mean(axis=0), hialb.std(axis=0)),
                    "low_radiance": (lowrad.mean(axis=0), lowrad.std(axis=0)),
                    "mid_radiance": (midrad.mean(axis=0), midrad.std(axis=0)),
                    "high_radiance": (hirad.mean(axis=0), hirad.std(axis=0))
                }
            }

        return tiny_dict

    filtlist = [f"VIC{n}" for n in range(1, 8)]
    filtdict = {}
    for i in filtlist:
        filtdict = {**filtdict, **format_dicts(i)}

    condensed_filtdict = consolidate_dicts(filtdict)
    return condensed_filtdict
