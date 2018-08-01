def uv_slicemask(image, min_intensity, max_intensity, num_slices):
    logger.debug("UV slices: %d", num_slices)

    interval = max_intensity - min_intensity
    logger.debug("UV slice interval: %f", interval)

    slice_size = interval / num_slices
    logger.debug("UV slice size: %f", slice_size)

    slicemask = np.zeros_like(image)

    boundaries = []

    for stepwise_slice in range(0, num_slices, 2):
        logger.debug("Computing slice %d...", stepwise_slice)

        start_boundary = stepwise_slice * slice_size
        boundaries.append(start_boundary)
        logger.debug("Start boundary: %f", start_boundary)

        end_boundary = start_boundary + slice_size
        boundaries.append(end_boundary)
        logger.debug("End boundary: %f", end_boundary)

        start_boundary_mask = image < start_boundary
        end_boundary_mask = image >= start_boundary + slice_size

        stepwise_slicemask = np.zeros_like(start_boundary_mask)
        stepwise_slicemask[start_boundary_mask] = True
        stepwise_slicemask[end_boundary_mask] = True

        slicemask[np.invert(stepwise_slicemask)] = True

    return slicemask, boundaries