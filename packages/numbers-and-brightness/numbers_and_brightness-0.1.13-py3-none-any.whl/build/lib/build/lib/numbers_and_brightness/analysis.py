# Imports
import os
import warnings
from pathlib import Path
import traceback

# External imports
import tifffile
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd

# Package imports
from numbers_and_brightness._defaults import (
    DEFAULT_BACKGROUND,
    DEFAULT_SEGMENT,
    DEFAULT_DIAMETER,
    DEFAULT_FLOW_THRESHOLD,
    DEFAULT_CELLPROB_THRESHOLD,
    DEFAULT_ANALYSIS,
    DEFAULT_ERODE,
    DEFAULT_BLEACH_CORR,
    DEFAULT_USE_EXISTING_MASK,
    DEFAULT_CREATE_OVERVIEW
)

def _load_model():
    print("Loading cellpose...")
    from cellpose import models
    from torch.cuda import is_available
    if is_available():
        gpu=True
        print("Using cuda GPU")
    else:
        gpu=False
        print("Using CPU")
    print("Loading model...")
    model = models.Cellpose(gpu=gpu, model_type='cyto3')
    return model

def _savemask(mask, outputdir):
    # Save mask using cellpose naming convention - allows cellpose to match tif image with segmentation for easy segmentation editing
    mask_dict = {
        "masks" : mask.astype(np.uint16),
        "outlines" : mask.astype(np.uint16)
    }
    np.save(os.path.join(outputdir, f"segmentation_image_seg.npy"), mask_dict)

    # Save mask visualisation
    img = tifffile.imread(os.path.join(outputdir, "segmentation_image.tif"))
    from cellpose import utils
    plt.imshow(img, cmap='gray')
    outlines = utils.outlines_list(mask)
    for o in outlines:
        plt.plot(o[:,0], o[:,1], color='r')
    plt.axis('off')
    plt.colorbar()
    plt.title("cellmask")
    plt.savefig(os.path.join(outputdir, "cellmask.png"))
    plt.close()

def _segment(original_img, outputdir, model, diameter, flow_threshold, cellprob_threshold):
    if model == None:
        model=_load_model()

    seg_img = np.mean(original_img, axis=0)
    tifffile.imwrite(os.path.join(outputdir, "segmentation_image.tif"), seg_img)

    mask, flow, styles, diams = model.eval(seg_img, diameter=diameter, flow_threshold=flow_threshold, cellprob_threshold=cellprob_threshold)

    return mask

def _load_existing_mask(outputdir):
    mask = np.load(os.path.join(outputdir, "segmentation_image_seg.npy"), allow_pickle=True).item()["masks"]
    return mask

def _erode_mask(img: np.ndarray, mask: np.ndarray, pixels: int, outputdir: str) -> np.ndarray:
    from cellpose import utils
    import cv2

    plt.imshow(np.mean(img, axis=0), cmap='gray')
    outlines = utils.outlines_list(mask)
    for o in outlines:
        plt.plot(o[:,0], o[:,1], color='r')

    shrunk_masks = np.zeros(shape=(img.shape[1], img.shape[2]))

    kernel_size = pixels
    kernel = np.ones((kernel_size*2, kernel_size*2), np.uint8)

    # Shrink every cell
    for cell in np.unique(mask[mask!=0]):
        cell_mask = mask==cell
        cell_mask_uint8 = cell_mask.astype(np.uint8)
        shrunk_mask = cv2.erode(cell_mask_uint8, kernel)
        shrunk_mask = shrunk_mask.astype(bool)

        outlines = utils.outlines_list(shrunk_mask)
        for o in outlines:
            plt.plot(o[:,0], o[:,1], color='green')
        shrunk_masks[shrunk_mask]=cell

    mask = shrunk_masks

    plt.axis('off')
    plt.colorbar()
    plt.title('eroded mask')
    plt.savefig(os.path.join(outputdir, "eroded_mask.png"))
    plt.close()

    return mask

def _b_i_plot(outputdir, mask, brightness, intensity):
    """Create brightness vs intensity scatterplot"""
    if len(np.unique(mask))<2: return    # If no cells detected, cannot perform analysis

    from scipy.stats import gaussian_kde
    
    all_cells = mask>0

    brightness_cell = brightness[all_cells]
    brightness_flat = brightness_cell.flatten()
    intensity_cell = intensity[all_cells]
    intensity_flat = intensity_cell.flatten()

    # Save values
    df = pd.DataFrame({
        'Brightness' : brightness_flat,
        'Intensity' : intensity_flat
    })
    df.to_csv(os.path.join(outputdir, 'brightness_intensity_values.csv'))
    
    x = np.nan_to_num(brightness_flat, copy=True, nan=0.0, posinf=0.0, neginf=0.0)
    y = np.nan_to_num(intensity_flat, copy=True, nan=0.0, posinf=0.0, neginf=0.0)
    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)

    plt.scatter(intensity_flat, brightness_flat, c=z, s=1, cmap='hsv_r')
    plt.title("Intensity x Brightness")
    plt.xlabel('Intensity')
    plt.ylabel('Brightness')
    plt.savefig(os.path.join(outputdir, "brightness_x_intensity.png"))
    plt.close()

def _bleach_corr(img, mask, outputdir):
    """Returns img corrected for bleaching"""
    # Cannot perform bleaching correction if no cells are found
    if len(np.unique(mask))==1:
        return img
    all_cells = mask>0
    x = np.arange(img.shape[0])

    # Get average intensities of cell
    avg_intensities = np.array([])
    for t in x:
        temp_img = img[t]
        avg_intensity = temp_img[all_cells].mean()
        avg_intensities = np.append(avg_intensities, avg_intensity)

    # Perform linear regression
    slope, intercept = np.polyfit(x, avg_intensities, deg=1)
    y_pred = slope * x + intercept

    # Correct img
    baseline = y_pred[0]
    correction_factors = baseline / y_pred
    correction_factors = correction_factors[:, np.newaxis, np.newaxis]
    corrected_img = img * correction_factors

    # Get average intensities of corrected cell
    corrected_avg_intensities = np.array([])
    for t in x:
        temp_img = corrected_img[t]
        corrected_avg_intensity = temp_img[all_cells].mean()
        corrected_avg_intensities = np.append(corrected_avg_intensities, corrected_avg_intensity)

    # Perform linear regression
    corrected_slope, corrected_intercept = np.polyfit(x, corrected_avg_intensities, deg=1)
    corrected_y_pred = corrected_slope * x + corrected_intercept

    plt.plot(x, avg_intensities, label='Average intensity', color='cornflowerblue')
    plt.plot(x, y_pred, linestyle='dashed', color='royalblue', label=f"y = {slope:.4f} * x + {intercept:.4f}")
    plt.plot(x, corrected_avg_intensities, label='Corrected average intensity', color='green')
    plt.plot(x, corrected_y_pred, linestyle='dashed', color='darkgreen', label=f"Corrected fit")
    plt.title("Bleaching correction")
    plt.ylabel("Intensity")
    plt.xlabel("Frame")
    plt.legend()
    plt.savefig(os.path.join(outputdir, "Bleach correction.png"))
    plt.close()

    return corrected_img

def _calculate_numbers_and_brightness(img, background, outputdir):
    # Calculate intensity and variance
    average_intensity = np.mean(img, axis=0)
    variance = np.var(img, axis=0, ddof=0)

    # Ignore 'division by zero' or 'invalid value encountered in divide' warnings caused by x/0 or 0/0
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)

        # Calculate apparent brightness, apparent number, brightness, number
        apparent_brightness = variance / average_intensity
        apparent_number = average_intensity**2 / variance

        brightness = (variance - average_intensity) / (average_intensity - background)
        number = ((average_intensity-background)**2) / np.clip((variance - average_intensity), 1e-6, None)

    # For all imgs, save matplotlib image and tiffile
    arrays = [average_intensity, variance, apparent_brightness, apparent_number, brightness, number]
    names = ["intensity", "variance", "apparent_brightness", "apparent_number", "brightness", "number"]
    for i, arr in enumerate(arrays):
        # Save tifffile
        tifffile.imwrite(os.path.join(outputdir, f"{names[i]}.tif"), arr)
        np.save(os.path.join(outputdir, f"{names[i]}.npy"), arr)

        # Create and save matplotlib image
        plt.imshow(arr, cmap='plasma')
        plt.axis('off')
        plt.colorbar()
        plt.title(names[i])
        plt.savefig(os.path.join(outputdir, f"{names[i]}.png"))
        plt.close()

    return average_intensity, variance, apparent_brightness, apparent_number, brightness, number

def _average_values_in_roi(
        intensity: np.ndarray,
        variance: np.ndarray,
        apparent_brightness: np.ndarray,
        apparent_number: np.ndarray,
        brightness: np.ndarray,
        number: np.ndarray,
        mask: np.ndarray
    ) -> pd.DataFrame:

    all_cells = mask>0

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)

        avg_intensity = np.mean(intensity[all_cells])
        avg_variance = np.mean(variance[all_cells])
        avg_apparent_brightness = np.mean(apparent_brightness[all_cells])
        avg_apparent_number = np.mean(apparent_number[all_cells])
        avg_brightness = np.mean(brightness[all_cells])
        avg_number = np.mean(number[all_cells])

    return pd.DataFrame({
        "Intensity" : avg_intensity,
        "Variance" : avg_variance,
        "Apparent brightness" : avg_apparent_brightness,
        "Apparent number" : avg_apparent_number,
        "Brightness" : avg_brightness,
        "Number" : avg_number
    },
    index=[0]
    )

def numbers_and_brightness_analysis(
        file: str,
        model=None,
        background=DEFAULT_BACKGROUND,
        segment=DEFAULT_SEGMENT,
        diameter=DEFAULT_DIAMETER,
        flow_threshold=DEFAULT_FLOW_THRESHOLD,
        cellprob_threshold=DEFAULT_CELLPROB_THRESHOLD,
        analysis=DEFAULT_ANALYSIS,
        erode=DEFAULT_ERODE,
        bleach_corr=DEFAULT_BLEACH_CORR,
        use_existing_mask=DEFAULT_USE_EXISTING_MASK
    ):

    file=Path(file)

    if analysis: segment = True     # Segmentation is needed for analysis
    if bleach_corr: segment =  True # Segmentation is needed for bleaching correction
    if erode>0: segment = True      # Cannot erode a mask without having a mask    

    img = tifffile.imread(file)

    # Check image shape
    if len(img.shape)!=3:
        raise ValueError(f"Invalid image shape encountered. Image: \"{file}\" is of shape: {img.shape} which is not fit for numbers and brightness analysis. Image must be of dimensions (t, x, y)")

    # Create new directory
    outputdir = f"{os.path.splitext(file)[0]}_n_and_b_output"
    if not os.path.isdir(outputdir): os.mkdir(outputdir)

    results_dict = {"Filename" : file.stem}

    mask = None
    # Look for existing masks if requested
    if use_existing_mask:
        try:
            mask = _load_existing_mask(outputdir)
            results_dict["Mask"] = mask
        except Exception as error:
            traceback.print_exc
            print(f"Could not load in existing mask for: {file.stem}, using cellpose instead")
            mask = _segment(original_img=img, model=model, diameter=diameter, flow_threshold=flow_threshold, cellprob_threshold=cellprob_threshold, outputdir=outputdir)
            results_dict["Mask"] = mask
            
    # Perform segmentation using cellpose
    elif segment:
        mask = _segment(original_img=img, model=model, diameter=diameter, flow_threshold=flow_threshold, cellprob_threshold=cellprob_threshold, outputdir=outputdir)
        results_dict["Mask"] = mask
 
    # Erode mask if requested
    if erode>0:
        mask = _erode_mask(img=img, mask=mask, pixels=erode, outputdir=outputdir)
        results_dict["Mask"] = mask

    _savemask(mask=mask, outputdir=outputdir)

    # Perform bleach correction on image
    if bleach_corr:
        img = _bleach_corr(img=img, mask=mask, outputdir=outputdir)

    # Calculate numbers and brightness
    average_intensity, variance, apparent_brightness, apparent_number, brightness, number = _calculate_numbers_and_brightness(img=img, background=background, outputdir=outputdir)

    # Perform analysis
    if analysis:
        _b_i_plot(outputdir=outputdir, mask=mask, brightness=apparent_brightness, intensity=average_intensity)
        average_in_roi = _average_values_in_roi(average_intensity, variance, apparent_brightness, apparent_number, brightness, number, mask)
        average_in_roi.to_csv(os.path.join(outputdir, "average_values_in_roi.csv"))

        results_dict["Intensity"] = average_intensity
        results_dict["Variance"] = variance
        results_dict["Apparent brightness"] = apparent_brightness
        results_dict["Apparent number"] = apparent_number
        results_dict["Brightness"] = brightness
        results_dict["Number"] = number
        
    else:
        average_in_roi = None

    return average_in_roi, results_dict

def numbers_and_brightness_batch(
        folder,
        background=DEFAULT_BACKGROUND,
        segment=DEFAULT_SEGMENT,
        diameter=DEFAULT_DIAMETER,
        flow_threshold=DEFAULT_FLOW_THRESHOLD,
        cellprob_threshold=DEFAULT_CELLPROB_THRESHOLD,
        analysis=DEFAULT_ANALYSIS,
        erode=DEFAULT_ERODE,
        bleach_corr=DEFAULT_BLEACH_CORR,
        use_existing_mask=DEFAULT_USE_EXISTING_MASK,
        create_overviews=DEFAULT_CREATE_OVERVIEW
    ):

    folder = Path(folder)

    if analysis: segment = True     # Segmentation is needed for analysis
    if bleach_corr: segment = True  # Segmentation is needed for bleaching correction
    if erode>0: segment = True      # Cannot erode a mask without having a mask    

    # Collect all tiff files in folder
    extensions = ['.tif', '.tiff']
    files = [f for f in folder.iterdir() if f.suffix.lower() in extensions]

    # Initialize model - will prevent the model from having to load again for every image
    model = _load_model() if segment else None

    # If requested, create new folders that store all brightness/numbers/masking results of each file
    if create_overviews:
        apparent_brightness_dir = os.path.join(folder, "Apparent Brightness")
        if not os.path.isdir(apparent_brightness_dir): os.mkdir(apparent_brightness_dir)
        mask_dir = os.path.join(folder, "Masks")
        if not os.path.isdir(mask_dir): os.mkdir(mask_dir)

    df_list = []

    # Process all files
    for file in tqdm(files):
        avg_in_roi, results_dict = numbers_and_brightness_analysis(
            file=file,
            analysis=analysis,
            erode=erode,
            background=background,
            segment=segment,
            diameter=diameter,
            flow_threshold=flow_threshold,
            cellprob_threshold=cellprob_threshold,
            model=model,
            bleach_corr=bleach_corr,
            use_existing_mask=use_existing_mask
        )
        df_list.append(avg_in_roi)

        if create_overviews:
            if "Apparent brightness" in results_dict.keys():
                # Save apparent brightness
                plt.imshow(results_dict["Apparent brightness"], cmap='plasma')
                plt.axis('off')
                plt.colorbar()
                name = f"Apparent brightness - {results_dict['Filename']}"
                plt.title(name)
                plt.savefig(os.path.join(apparent_brightness_dir, f"{name}.png"))
                plt.close()

            
            if "Mask" in results_dict.keys():
                # Save segmentation
                from cellpose import utils
                plt.imshow(results_dict["Intensity"], cmap='gray')
                outlines = utils.outlines_list(results_dict["Mask"])
                for o in outlines:
                    plt.plot(o[:,0], o[:,1], color='r')
                plt.axis('off')
                plt.colorbar()
                name = f"Segmentation - {results_dict['Filename']}"
                plt.title(name)
                plt.savefig(os.path.join(mask_dir, f"{name}.png"))
                plt.close()

    # If analysis was turned on, the analysis function will have returned average values in roi
    # Here they are combined in a single dataframe
    if analysis:
        combined_df = pd.concat(df_list)
        combined_df.index = files
        combined_df.to_csv(os.path.join(folder, "Folder_average_values_in_roi.csv"))

        return combined_df
    else:
        return None