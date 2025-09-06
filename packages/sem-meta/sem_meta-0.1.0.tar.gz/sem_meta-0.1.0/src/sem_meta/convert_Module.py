# Standard library imports
import re    # Regular expressions for text parsing


class ConvertPS(object):

    """
    A conversion utility class for handling pixel size data extracted from SEM images.
    This class provides methods to parse digit-unit strings, normalize units, and support OCR post-processing.
    """

    def __init__(self):
        # Initialize the base class (object) — placeholder for future extensibility
        super(ConvertPS, self).__init__()


    # Extract Floating-Point Number from String
    def GetFloat(self, str):

        """
        Extracts the first floating-point number from a string and converts it to a float.

        Parameters:
            str (str): A string containing one or more decimal numbers (e.g., "Pixel size = 0.428 µm").

        Returns:
            float: The first floating-point number found in the string.
        """

        # Use regex to find all decimal numbers in the string (e.g., "0.428")
        psfloat = float(re.findall("\d+\.\d+", str)[0])

        # Return the first match as a float
        return psfloat



    # Save metadata and OCR-derived pixel size values into a .dat file for logging or analysis
    def WritePixelFile(self, file, meta_pixel_size, ocr_pixel_size):

        """
        Saves pixel size values to a .dat file for record-keeping or downstream analysis.

        Parameters:
            file (str): Path to the output file where pixel size data will be appended.
            meta_pixel_size (str): Pixel size value derived from metadata or manual input.
            ocr_pixel_size (str): Pixel size value computed from OCR analysis.

        Returns:
            None
        """

        # Open the file in append mode (create if it doesn't exist)
        with open(file, 'a+') as pixelF:
            # Write both pixel size values to the file, separated by a space
            pixelF.write('{} {} \n'.format(meta_pixel_size, ocr_pixel_size))

        # No return value needed — file is updated in place
        return



    # Save pixel size error values into a .dat file for tracking discrepancies or failed computations
    def WritePixelError(self, file, pserror):

        """
        Logs pixel size error values to a .dat file for analysis or debugging.

        Parameters:
            file (str): Path to the output file where error values will be appended.
            pserror (str or float): The pixel size error value to be recorded.

        Returns:
            None
        """
        
        # Open the file in append mode (create if it doesn't exist)
        with open(file, 'a+') as pixelE:
            # Write the error value to the file, followed by a newline
            pixelE.write('{} \n'.format(pserror))

        # No return value needed — file is updated in place
        return

        

    # Convert pixel size values from various units (nm, pm, mm) into micrometers for consistent analysis
    def GetMicroPixelSize(self, pixel_size):

        """
        Converts a pixel size string to micrometers (µm) regardless of its original unit.

        Parameters:
            pixel_size (str): A string containing a pixel size value with unit (e.g., "0.428 µm", "500 nm").

        Returns:
            float or bool: The pixel size converted to micrometers, or False if the unit is unrecognized.
        """

        # Case: already in micrometers — no conversion needed
        if "µm" in pixel_size:
            ps_digit = self.GetFloat(pixel_size)
            ps_digit_micro = ps_digit

        # Case: nanometers — divide by 1,000 to convert to micrometers
        elif "nm" in pixel_size:
            ps_digit = self.GetFloat(pixel_size)
            ps_digit_micro = ps_digit / 1e3

        # Case: picometers — divide by 1,000,000 to convert to micrometers
        elif "pm" in pixel_size:
            ps_digit = self.GetFloat(pixel_size)
            ps_digit_micro = ps_digit / 1e6

        # Case: millimeters — multiply by 1,000 to convert to micrometers
        elif "mm" in pixel_size:
            ps_digit = self.GetFloat(pixel_size)
            ps_digit_micro = ps_digit * 1e3

        # Fallback: unrecognized unit — log the issue and return False
        else:
            ps_digit_micro = False
            print("Unexpected case for pixel size range:", pixel_size)

        # Return the normalized pixel size in micrometers
        return ps_digit_micro



    # Compare metadata and OCR-derived pixel sizes, log discrepancies, and flag significant errors
    def GetError(self, meta_pixel_size, comp_pixel_size, semimage, semID):

        """
        Computes the absolute error between metadata and OCR-derived pixel sizes,
        logs the values to file, and flags significant discrepancies.

        Parameters:
            meta_pixel_size (float): Pixel size value obtained from metadata or manual input.
            comp_pixel_size (float): Pixel size value computed from OCR analysis.
            semimage (str): Filename or identifier of the SEM image being processed.
            semID (str): Unique identifier or label for the SEM image, used for logging.

        Returns:
            None
        """

        # Proceed only if both pixel size values are valid
        if meta_pixel_size and comp_pixel_size:
            # Print both values for visual comparison
            print("Meta ps in µm:", meta_pixel_size, "OCR ps in µm:", comp_pixel_size)

            # Log both pixel size values to a file for validation tracking
            self.WritePixelFile("./results/pixelsize-MICRO-allsem.dat", meta_pixel_size, comp_pixel_size)

            # Compute the absolute error between metadata and OCR values
            abs_error = abs(meta_pixel_size - comp_pixel_size)

            # Log the error value to a separate file for analysis
            self.WritePixelError("./results/abs-error-MICRO-pixelsize-allsem.dat", abs_error)

            # Flag unusually large errors for manual inspection
            if abs_error > meta_pixel_size + 1:
                print("ABSOLUTE ERROR", abs_error, semimage, semID)

        # Handle missing or invalid pixel size values
        else:
            print("False value; Meta ps:", meta_pixel_size, "OCR ps:", comp_pixel_size)

        # No return value needed - results are logged
        return

