from blender_hand_drawn_npr.illustrate import Illustrator
from blender_hand_drawn_npr.primitives import Settings, ThicknessParameters, LightingParameters, StippleParameters
from skimage import io
import numpy as np

name_prefix = "cosinus"


def a():
    settings = []

    settings.append(Settings(out_filename=name_prefix + "_a.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=3, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=3, z=0, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=1,
                                                                    threshold=0.4),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=True,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=False,
                             in_path="/tmp/" + name_prefix))

    return settings


def b():
    settings = []

    settings.append(Settings(out_filename=name_prefix + "_b.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=3, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=3, z=0, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=1,
                                                                    threshold=0.4),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=True,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=False,
                             in_path="/tmp/" + name_prefix))

    return settings


def c():
    settings = []

    settings.append(Settings(out_filename=name_prefix + "_c.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=16,
                             silhouette_thickness_parameters=ThicknessParameters(const=3, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=3, z=0, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0, z=0, diffdir=0,
                                                                                 stroke_curvature=60),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=0.2, shadow=0.4, ao=1.5,
                                                                    threshold=0.4),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=True,
                             enable_internal_edges=True,
                             enable_streamlines=True,
                             enable_stipples=False,
                             in_path="/tmp/" + name_prefix))

    return settings


def d():
    settings = []

    settings.append(Settings(out_filename=name_prefix + "_d.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=16,
                             silhouette_thickness_parameters=ThicknessParameters(const=3, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=3, z=0, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.5, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=0.2, shadow=0.4, ao=1.5,
                                                                    threshold=0.4),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=True,
                             enable_internal_edges=True,
                             enable_streamlines=True,
                             enable_stipples=False,
                             in_path="/tmp/" + name_prefix))

    return settings


def e():
    settings = []

    settings.append(Settings(out_filename=name_prefix + "_e.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=16,
                             silhouette_thickness_parameters=ThicknessParameters(const=3, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=3, z=0, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=1, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=0.2, shadow=0.4, ao=1.5,
                                                                    # threshold=0.5),  # 25.763841 vs target 24.229248.
                                                                    # threshold=0.52),  # 22.985469
                                                                    threshold=0.51),  # 22.985469
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=False,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    return settings


def f():
    settings = []

    settings.append(Settings(out_filename=name_prefix + "_f.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=16,
                             silhouette_thickness_parameters=ThicknessParameters(const=3, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=3, z=0, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=1, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=0.2, shadow=0.4, ao=1.5,
                                                                    # threshold=0.45),  # 34.247858 vs target 35.425547.
                                                                    # threshold=0.43),  # 36.374631
                                                                    threshold=0.44),  # 36.374631
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=False,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    return settings


def g():
    settings = []

    settings.append(Settings(out_filename=name_prefix + "_g.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=16,
                             silhouette_thickness_parameters=ThicknessParameters(const=3, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=3, z=0, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.5, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=0.2, shadow=0.4, ao=1.5,
                                                                    threshold=0.44),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=False,
                             enable_internal_edges=True,
                             enable_streamlines=True,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    return settings


if __name__ == "__main__":

    settings = []
    # settings += a()
    # settings += b()
    # settings += c()
    # settings += d()
    # settings += e()
    # settings += f()
    settings += g()

    # for setting in settings:
    #     illustrator = Illustrator(setting)
    #     illustrator.illustrate()
    #     illustrator.save()

    base = "/home/chris/workspace/blender-hand-drawn-npr/blend_files/evaluation_images/2/"
    converted_files = [
        "cosinus_b.png",
        "cosinus_c.png",
        "cosinus_d.png",
        "cosinus_e.png",
        "cosinus_f.png",
        "cosinus_g.png"
    ]

    for converted_file in converted_files:
        image = io.imread(base + converted_file, as_gray=True)
        image = np.invert(image)
        cost = np.sum(image) / 1000000
        print(converted_file, cost)
