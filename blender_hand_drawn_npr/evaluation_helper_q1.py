from blender_hand_drawn_npr.illustrate import Illustrator
from blender_hand_drawn_npr.primitives import Settings, ThicknessParameters, LightingParameters, StippleParameters


def cosinus():
    name_prefix = "cosinus"

    settings = []

    settings.append(Settings(out_filename=name_prefix + "_stipples_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=0.2, shadow=0.4, ao=1.5,
                                                                    threshold=0.4),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=False,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    settings.append(Settings(out_filename=name_prefix + "_streamlines_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.8, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=1,
                                                                    threshold=0.3),
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


def catenoid():
    name_prefix = "catenoid"

    settings = []

    settings.append(Settings(out_filename=name_prefix + "_stipples_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=80,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=0.5, shadow=0.1, ao=1,
                                                                    threshold=0.55),
                             stipple_parameters=StippleParameters(head_radius=0.8, tail_radius=0, length=20,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=False,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    settings.append(Settings(out_filename=name_prefix + "_streamlines_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.6, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=0.5, shadow=0.5, ao=2,
                                                                    threshold=0.5),
                             stipple_parameters=StippleParameters(head_radius=0.8, tail_radius=0, length=20,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=True,
                             enable_internal_edges=True,
                             enable_streamlines=True,
                             enable_stipples=False,
                             in_path="/tmp/" + name_prefix))

    return settings


def hyperbolic_paraboloid_xy():
    name_prefix = "hyperbolic_paraboloid_xy"

    settings = []

    settings.append(Settings(out_filename=name_prefix + "_stipples_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=0.2,
                                                                    threshold=0.3),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.0025,
                                                                  density_fn_factor=0.001,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=False,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    settings.append(Settings(out_filename=name_prefix + "_streamlines_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.8, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=1,
                                                                    threshold=0.3),
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


def hyperbolic_paraboloid_polar():
    name_prefix = "hyperbolic_paraboloid_polar"

    settings = []

    settings.append(Settings(out_filename=name_prefix + "_stipples_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1.5, shadow=0.7, ao=0.1,
                                                                    threshold=0.3),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.0025,
                                                                  density_fn_factor=0.001,
                                                                  density_fn_exponent=3),
                             optimise_clip_paths=False,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    settings.append(Settings(out_filename=name_prefix + "_streamlines_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.8, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=1,
                                                                    threshold=0.3),
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


def undulating_plane():
    name_prefix = "undulating_plane"

    settings = []

    settings.append(Settings(out_filename=name_prefix + "_stipples_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=0,
                                                                    threshold=0.55),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.0025,
                                                                  density_fn_factor=0.0015,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=False,
                             enable_internal_edges=False,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    settings.append(Settings(out_filename=name_prefix + "_streamlines_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.8, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=1,
                                                                    threshold=0.3),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=True,
                             enable_internal_edges=False,
                             enable_streamlines=True,
                             enable_stipples=False,
                             in_path="/tmp/" + name_prefix))

    return settings


def helicoidal():
    name_prefix = "helicoidal"

    settings = []

    settings.append(Settings(out_filename=name_prefix + "_stipples_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1.5, shadow=0.1, ao=1.5,
                                                                    threshold=0.9),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.0025,
                                                                  density_fn_factor=0.001,
                                                                  density_fn_exponent=3),
                             optimise_clip_paths=False,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    settings.append(Settings(out_filename=name_prefix + "_streamlines_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.8, z=0, diffdir=0,
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
                             enable_streamlines=True,
                             enable_stipples=False,
                             in_path="/tmp/" + name_prefix))

    return settings


def hyperhelicoidal():
    name_prefix = "hyperhelicoidal"

    settings = []

    settings.append(Settings(out_filename=name_prefix + "_stipples_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1.5, shadow=0.1, ao=1.5,
                                                                    threshold=0.5),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.0025,
                                                                  density_fn_factor=0.001,
                                                                  density_fn_exponent=3),
                             optimise_clip_paths=False,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    settings.append(Settings(out_filename=name_prefix + "_streamlines_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.8, z=0, diffdir=0,
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
                             enable_streamlines=True,
                             enable_stipples=False,
                             in_path="/tmp/" + name_prefix))

    return settings


def shell():
    name_prefix = "shell"

    settings = []

    settings.append(Settings(out_filename=name_prefix + "_stipples_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1.5, shadow=0.1, ao=2,
                                                                    threshold=0.25),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.0025,
                                                                  density_fn_factor=0.001,
                                                                  density_fn_exponent=3),
                             optimise_clip_paths=False,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    settings.append(Settings(out_filename=name_prefix + "_streamlines_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=128,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.8, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=1,
                                                                    threshold=0.2),
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


def human_1():
    name_prefix = "human-1"

    settings = []

    settings.append(Settings(out_filename=name_prefix + "_stipples_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=0.1, ao=1.5,
                                                                    threshold=0.12),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=False,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    settings.append(Settings(out_filename=name_prefix + "_streamlines_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=128,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.4, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=1,
                                                                    threshold=0.3),
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


def human_2():
    name_prefix = "human-2"

    settings = []

    settings.append(Settings(out_filename=name_prefix + "_stipples_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=2, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=2, ao=3,
                                                                    threshold=0.2),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=False,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    settings.append(Settings(out_filename=name_prefix + "_streamlines_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=128,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=2, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.4, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1.2, shadow=1.5, ao=3,
                                                                    threshold=0.7),
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


def taranaki():
    name_prefix = "taranaki"

    settings = []

    settings.append(Settings(out_filename=name_prefix + "_stipples_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=2, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=2, shadow=0.5, ao=3,
                                                                    threshold=0.78),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=True,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    settings.append(Settings(out_filename=name_prefix + "_streamlines_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=128,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=2, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.4, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=1,
                                                                    threshold=0.3),
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


def teapot():
    name_prefix = "teapot"

    settings = []

    settings.append(Settings(out_filename=name_prefix + "_stipples_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=300,
                             subpix_window_size=40,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=2, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=3,
                                                                    threshold=0.15),
                             stipple_parameters=StippleParameters(head_radius=0.8, tail_radius=0, length=20,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=True,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    settings.append(Settings(out_filename=name_prefix + "_streamlines_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=300,
                             subpix_window_size=40,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=64,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=2, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.3, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=1,
                                                                    threshold=0.3),
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


def brooklynbridge():
    name_prefix = "brooklynbridge"

    settings = []

    settings.append(Settings(out_filename=name_prefix + "_stipples_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
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
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    # settings.append(Settings(out_filename=name_prefix + "_streamlines_only.svg",
    #                          cull_factor=50,
    #                          optimise_factor=5,
    #                          curve_fit_error=0.01,
    #                          harris_min_distance=40,
    #                          subpix_window_size=20,
    #                          curve_sampling_interval=20,
    #                          stroke_colour="black",
    #                          streamline_segments=32,
    #                          silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
    #                                                                              stroke_curvature=0),
    #                          internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
    #                                                                                 stroke_curvature=0),
    #                          streamline_thickness_parameters=ThicknessParameters(const=0.8, z=0, diffdir=0,
    #                                                                              stroke_curvature=0),
    #                          uv_primary_trim_size=200,
    #                          uv_secondary_trim_size=20,
    #                          lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=1,
    #                                                                 threshold=0.3),
    #                          stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
    #                                                               density_fn_min=0.005,
    #                                                               density_fn_factor=0.0025,
    #                                                               density_fn_exponent=2),
    #                          optimise_clip_paths=True,
    #                          enable_internal_edges=True,
    #                          enable_streamlines=True,
    #                          enable_stipples=False,
    #                          in_path="/tmp/" + name_prefix))

    return settings


def suzanne():
    name_prefix = "suzanne"

    settings = []

    settings.append(Settings(out_filename=name_prefix + "_stipples_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=32,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=3, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1.5, shadow=1, ao=2,
                                                                    threshold=0.2),
                             stipple_parameters=StippleParameters(head_radius=1, tail_radius=0, length=30,
                                                                  density_fn_min=0.005,
                                                                  density_fn_factor=0.0025,
                                                                  density_fn_exponent=2),
                             optimise_clip_paths=False,
                             enable_internal_edges=True,
                             enable_streamlines=False,
                             enable_stipples=True,
                             in_path="/tmp/" + name_prefix))

    settings.append(Settings(out_filename=name_prefix + "_streamlines_only.svg",
                             cull_factor=50,
                             optimise_factor=5,
                             curve_fit_error=0.01,
                             harris_min_distance=40,
                             subpix_window_size=20,
                             curve_sampling_interval=20,
                             stroke_colour="black",
                             streamline_segments=64,
                             silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                 stroke_curvature=0),
                             internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=3, diffdir=0,
                                                                                    stroke_curvature=0),
                             streamline_thickness_parameters=ThicknessParameters(const=0.4, z=0, diffdir=0,
                                                                                 stroke_curvature=0),
                             uv_primary_trim_size=200,
                             uv_secondary_trim_size=20,
                             lighting_parameters=LightingParameters(diffdir=1, shadow=1, ao=1,
                                                                    threshold=0.3),
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

if __name__ == "__main__":

    settings = []
    # settings += cosinus()
    # settings += catenoid()
    # settings += hyperbolic_paraboloid_xy()
    # settings += hyperbolic_paraboloid_polar()
    # settings += helicoidal()
    # settings += hyperhelicoidal()
    # settings += shell()
    # settings += human_1()
    # settings += human_2()
    # settings += undulating_plane()
    # settings += taranaki()
    # settings += teapot()
    # settings += brooklynbridge()
    settings += suzanne()

    for setting in settings:
        illustrator = Illustrator(setting)
        illustrator.illustrate()
        illustrator.save()
