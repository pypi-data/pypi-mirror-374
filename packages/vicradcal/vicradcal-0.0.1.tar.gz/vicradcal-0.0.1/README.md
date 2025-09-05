<div style="line-height:1; font-family: 'Times New Roman';">

# LV-VIC Radiometric Calibration Analysis Procedure

<p style="line-height:1">
<i>The goal of this document is to organize the analysis that must be performed on the calibration data taken at BAE systems for the LV-VIC instrument. Sections are meant to be organized into distinct tasks which can then be turned into individual MATLAB scripts which can finally be packaged into a distributable MATLAB toolbox for use by the greater planetary science community.</i>
</p>

### 1. Executive Summary

<table>
  <caption style="text-align:left; font-size:12px"><b>Table 2:</b> Preliminary list of MATLAB scripts to make for the radiometric calibration of the Lunar-VISE VIC. More utility scripts or subscripts may be required to make the entire framework run, but this should cover the main steps of calibration.</caption>
  <tr>
    <th>Script Name</th>
    <th>Description</th>
    <th>Input</th>
    <th>Output</th>
  </tr>
  <tr>
    <td>calculate_bias</td>
    <td>Calculates pixel-by-pixel bias component to the signal</td>
    <td>Series of zero exposures images, repeated at different temperatures</td>
    <td>Function that removes bias signal from each pixel</td>
  </tr>
  <tr>
    <td>calculate_dark_current</td>
    <td>Calculates pixel-by-pixel dark current component to the signal</td>
    <td>Series of varying exposure time images, repeated at different temperatures</td>
    <td>Function that removes offset signal for each pixel</td>
  </tr>
  <tr>
    <td>pixel_lineararity</td>
    <td>Fits a linear model to each pixel in the scene to determine linearity</td>
    <td>Series of varying exposure time images</td>
    <td>Linear fit for each pixel in the scene</td>
  </tr>
  <tr>
    <td>subarea_linearity</td>
    <td>Fits a linear model to the average response of several subscenes</td>
    <td>Series of varying exposure time images</td>
    <td>Several linear fits for several subscenes of the entire scene</td>
  </tr>
  <tr>
    <td>get_photon_transfer</td>
    <td>Creates a photon transfer curve to determine the pixel-by-pixel gain and read noise</td>
    <td>Groups of consecutive flat-field images taken at varying signal strengths (i.e. different exposure times or integrating sphere settings)</td>
    <td>Gain and read noise pixel-by-pixel maps</td>
  </tr>
  <tr>
    <td>correct_coherent_noise</td>
    <td>Corrects for known sources of coherent noise across the scene</td>
    <td>Calibrated image with sources of coherent noise</td>
    <td>Corrected image with coherent noise removed</td>
  </tr>
  <tr>
    <td>correct_flat_field</td>
    <td>Corrects for flat-field effects across the scene</td>
    <td>Series of flat field images, bias and offset corrected.</td>
    <td>Function that corrects a target image for flat-field effects</td>
  </tr>
  <tr>
    <td>get_sensitivity</td>
    <td>Obtains the sensitivity of the instrument that is needed to convert DN to radiance</td>
    <td>Series of bias and offset corrected flat-field images at varying radiances (i.e. integrating sphere settings)</td>
    <td>Sensitivity term that converts DN to radiance</td>
  </tr>
</table>

<br>

<p style="text-align:left; font-size:12px">
  <img src="./images/Calibration_Procedure_Flowchart.png" style="width:100%;">
  <br>
  <b>Figure 1:</b> Preliminary Radiometric Calibration Flowchart for Lunar-VISE. Each step corresponds to MATLAB scripts listed in Table 1. Each step also loosely corresponds with a source of error to be taken into account in the final radiance calculation.
</p>

### 2. Dark-Field Analysis

<div style="margin-left: 20px;">
  <h4>2.1 Bias Determination</h4>
  <p>Bias fundamentally depends on instrument temperature and is different for each pixel in a CMOS detector, so bias maps must be made over the full range of expected operating temperatures. It is also important to average bias frames to get a good idea of both the actual bias level and the uncertainty on bias removal. Bias frames are defined as dark-field frames (i.e. no physical exposure to light using e.g. a shutter) that are taken with the shortest possible exposure time. The MATLAB script should be able to read in a series of bias field images, find their mean and standard deviation and repeat this for many different temperatures. The temperature dependence should then be modeled for each pixel and interpolated to determine the bias for any instrument temperature. Finally, the code should be able to put this information in a form that can later be subtracted from other calibration steps.</p>

  <div style="margin-left:40px;">
  <p><strong>Inputs:</strong></p>
  <ul>
    <li>4D Array of bias field images (NxMxKxT) where N and M are spatial dimensions, K is the dimension for repeated bias images with zero exposure and T is for varying temperatures.</li>
  </ul>

  <p><strong>Outputs:</strong></p>
  <ul>
    <li>Modeled bias vs. temperature relationship at each pixel</li>
    <li>A dataframe that can be called via a function to subtract the bias value at a given temperature, interpolated from the measured temperatures.</li>
  </ul>
  </div>

  <h4>2.2 Dark Current Measurement</h4>
  <p>Dark current is also heavily dependent on temperature but will scale with exposure time. For a CMOS sensor, the dark current function will also vary across the detector (e.g. due to amp glow, hot pixels, etc…). By taking a series of exposure lengths over a dark field, the dark current can be discriminated from the bias values. It is currently unclear whether the dark current is pre-characterized for our instrument and whether a model exists to fit the measured dark current, but, assuming a roughly linear relationship to exposure time, the dark current can be obtained simply through measurement over the entire range of expected operating temperatures. The script should be able to take in a series of dark field images with varying exposure times, subtract the bias level for each, and fit a curve/line to find the dark current function. This should then be repeated across the entire temperature range. The output should be a 2-variable model where, given a temperature and an exposure time, the dark current level is given for each pixel on the image.</p>

  <div style="margin-left:40px;">
  <p><strong>Inputs:</strong></p>
  <ul>
    <li>4D array of dark-field images (NxMxJxT) where N and M are spatial dimensions, J is the series of varying exposure lengths and T is for varying temperatures.</li>
  </ul>

  <p><strong>Outputs:</strong></p>
  <ul>
    <li>A look-up table style function that gives the dark current level at every pixel for a given temperature and exposure time.</li>
  </ul>
  </div>
</div>

### 3. Linearity Analysis

<div style="text-align:left; width:50%; float:right; margin-left:20px;">
  <img src="./images/Klaasen linearity.png" style="width:100%;">
  <p style="text-align:left; font-size:12px"><b>Figure 2:</b> Preliminary Radiometric Calibration Flowchart for Lunar-VISE. Each step corresponds to MATLAB scripts listed in Table 1. Each step also loosely corresponds with a source of error to be taken into account in the final radiance calculation.</p>
</div>

<div style="margin-left: 20px;">
  <h4>3.1 Average Area Linearity</h4>
  <p>We should perform an L2 Norm minimization (i.e. least squares regression) for the average instrument response over a broad area of pixels. This is done in Klaasen et al., 2008 and the results are shown in Fig. 2. The MATLAB script should be able to take in several images (i.e. a 3D array) that correspond to different exposures times, compile an exposure time vs. average instrument response dataset for a broad area of pixels, perform an L2 Norm minimization to find the slope and intercept for this data and finally return the residuals for this linear fit. This should then be repeatable for each analyzed wavelength (4D array?). The final possible addition to this script could be the quantification of linearity by some linearity metric (TBD).</p>

  <div style="margin-left: 40px;">
    <p><strong>Inputs:</strong></p>
    <ul>
      <li>3D Array of images, where the 3rd dimension is exposure time. (Possible 4D array to account for wavelengths)</li>
      <li>Area to analyze for linearity.</li>
    </ul>

  <p><strong>Outputs:</strong></p>
  <ul>
      <li>Linearity plot (as in Fig. 1)</li>
      <li>Average signal response vs. linear fit residuals (i.e. % Error)</li>
      <li>Linearity metric (?)</li>
  </ul>
  </div>

  <h4>3.2 Pixel-by-Pixel and Band-by-Band Linearity</h4>
  <p>In addition to an average area, it would likely be good to understand how the linearity of an image changes across both the spatial and spectral dimensions. This is where a relative linearity metric (such as average residual, total residual, R2 etc…) would benefit us. A script could take in the same 3D Array mentioned in 3.1, perform an L2 norm minimization pixel-by-pixel, get the pixel-by-pixel residual and finally create an image of the pixel-by-pixel linearity metric. This could then be repeated for each band and one could assess the band-by-band linearity either averaged across the entire image or on a pixel-by-pixel basis.</p>

  <div style="margin-left: 40px;">
     <p><strong>Inputs:</strong></p>
     <ul>
       <li>3D (or 4D) array where 3rd dimension is exposure time (4th is spectral band)</li>
     </ul>

   <p><strong>Outputs:</strong></p>
   <ul>
       <li>Pixel-by-pixel map of linearity metric</li>
       <li>Band-by-Band array of linearity metric</li>
   </ul>
  </div>

### 4. Noise Analysis

<div style="text-align:left; width:50%; float:right; margin-left:20px;">
  <img src="./images/Klaasen photon transfer curve.png" style="width:100%;">
  <p style="text-align:left; font-size:12px"><b>Figure 3:</b> Photon transfer analysis from Klaasen et al., 2008. This method is used to determine the read noise and gain for each pixel in the detector.</p>
</div>

<div style="margin-left: 20px;">
  <h4>4.1 Photon Transfer Analysis</h4>
  <p>In short, photon transfer analysis uses the relationship between random noise and signal strength (i.e. noise will generally increase with increasing signal) to estimate the gain of each pixel in the detector. The result will be a pixel-by-pixel map of the instrument gain as well as a better understanding of the read noise, which is the noise that occurs when the detector converts the collected electrons to voltages. Read noise is generally independent of signal, and the overall relationship between it and the overall random noise is given by:</p>
  
  $$ \eta=\sqrt{\frac{Σ^2}{g}+ρ^2} $$

  <p>where η is the overall random noise in the signal, Σ is the shot noise due to the quantized nature of photons and counting statistics, ρ is the read noise and g is the gain (i.e. electrons/DN). Since Σ= √N where N is the number of incoming photons, Σ^2 is simply just the measured signal, which is converted to DN by dividing by the gain. The random noise can simply be determined by taking N consecutive exposures of equal length, correcting for bias and dark current and taking the standard deviation/√N for each pixel in the image. This can then be repeated for a few different signal strengths (either different radiances or different exposure times) to create the plot shown in Fig. 3. The data can then be fit using the above equation by performing an L2 Norm minimization for g and ρ. The result will be a pixel-by-pixel map of the gain and read noise. The script should be able to produce these maps by taking in a series of groups of consecutive exposures taken at different temperatures.</p>

  <div style="margin-left: 40px;">
    <p><strong>Inputs:</strong></p>
    <ul>
      <li>4D array of flat-field images (NxMxLxS) where N and M are spatial dimensions, L is a series of consecutive images at the same signal strength and S is for variations in signal strength.</li>
    </ul>

   <p><strong>Outputs:</strong></p>
   <ul>
     <li>2D map of pixel gain values</li>
     <li>2D map of pixel read noise values</li>
   </ul>
  </div>

  <h4>4.2 Coherent Noise and Other Noise Sources</h4>
  <p>This analysis will be mostly exploratory and will depend on the instrument electronics. Given that the CMOS detector is enabled with super-pixel electronics (i.e. every group of four pixels in a square is electronically connected, which typically helps detect color, but in our case is not used), there might be coherent noise across each of these groups or noise related to cross-talk between associated pixels in different groups (e.g. all the top right pixels in every super group exhibit an extra bias term). Other sources might include spatially coherent noise sources such as vertical or horizontal striping. The I/O of this script will likely depend on the results of our exploratory analysis, but will in general be able to take in a calibrated image and remove all known sources of coherent instrumental noise. This step will also include flagging bad pixels.</p>

  <div style="margin-left: 40px;">
    <p><strong>Inputs:</strong></p>
    <ul>
      <li>A radiometrically calibrated image with sources of coherent instrumental noise and bad pixels.</li>
    </ul>

   <p><strong>Outputs:</strong></p>
    <ul>
     <li>A corrected image with sources of coherent instrumental noise      and bad pixels removed.</li>
   </ul>
  </div>
</div>

### 5. Sensitivity Analysis/Radiometric Calibration

<div style="margin-left: 20px;">
  <h4>5.1 Flat-Field Correction</h4>
  <p>To correct for camera transmission variations across a scene, a flat field must be divided out. A flat field is defined as a source of constant radiance across the entire scene. To confidently use a flat field image, it must be the average of several (10-20) captured images. The script should be able to take in these images, find the mean and standard deviation, pick out any pixels that exceed a certain threshold deviation, correct the image for bias and dark current, normalize the mean image to 1 by dividing each good pixel by the mean of the whole image and, finally, divide each captured image by the flat field. The result will hopefully be an image with a much more uniform response across the scene as well as a lower amount of pixel-to-pixel variation.</p>

  <div style="margin-left: 40px;">
    <p><strong>Inputs:</strong></p>
    <ul>
      <li>A series of flat-field images (10-20)</li>
      <li>Bias and Dark Current correction images</li>
    </ul>

   <p><strong>Outputs:</strong></p>
   <ul>
     <li>Normalized flat-field image</li>
     <li>Function for the correction of future target images</li>
   </ul>
  </div>

  <h4>5.2 Filter Sensitivity Determination</h4>
  
  In general, the response of a radiometer can be converted to radiance over a bandpass, $f$, using:

  $$ N_f = \frac{DN - DN_0(t)}{tg\Omega a \int S_\lambda T_\lambda F_\lambda P_\lambda d\lambda}$$

  Where $DN$ is the digital number, $DN_0$ is the dark current and bias signal, $t$ is the exposure time, $g$ is the gain (i.e. e-/DN), $S_\lambda$ is the detector quantum efficiency (i.e. # of e- produced per photon), $T_\lambda$ is the transmission of the optics, $F_\lambda$ is the transmission of the filter and $P_\lambda = \frac{\lambda}{1.98648 \times 10^{-19}}$, which is the inverse of photon energy. The goal of sensitivity determination is to measure the $\frac{1}{\int S_\lambda T_\lambda F_\lambda d\lambda}$, which is instrument dependent and can be thought of as the instrument sensitivity. The script should be able to take in a series of flat field images of different radiances and determine what single sensitivity causes the instrument to best fit each measured radiance. From there, filter transmission, optics transmission and quantum efficiency can be derived.

  <div style="margin-left: 40px;">
    <p><strong>Inputs:</strong></p>
    <ul>
      <li>A series of flat-field images at different radiances.</li>
      <li>Bias, offset and flat field correction frames.</li>
    </ul>

   <p><strong>Outputs:</strong></p>
   <ul>
     <li>Instrument sensitivity value.</li>
     <li>Function for correcting a target image.</li>
   </ul>
  </div>
</div>

</div>


