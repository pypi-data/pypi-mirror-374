# Standard library imports
import json, csv                    # Data serialization and structured output
from collections import Counter     # Frequency counting utility

# Scientific and visualization libraries
import numpy as np                  # Numerical computations

# Image processing and metadata
from PIL import Image, ExifTags     # Image loading and EXIF metadata extraction
#import imagehash, hashlib          # Image hashing for duplicate detection

# SQL safety
from pymysql.converters import escape_string  # Escapes special characters in strings for safe SQL insertion

# Terminal output styling
from termcolor import colored       # Colored terminal output for better readability

# SEM metadata keys
from .SEMKEYS import FullSEMKeys   # Predefined SEM metadata structure


# SEMMetaData Class Initialization
class SEMMetaData(object):
    def __init__(self, sem_path=True, image_metadata={}, FinalMetaDataDict={}):
        super(SEMMetaData, self).__init__()

        # Path to SEM image directory or pattern
        self.sem_path = sem_path

        # Accepted SEM image file extensions
        self.semext = ('tif', 'TIF')

        # Dictionary to store extracted metadata per image
        self.image_metadata = image_metadata

        # SEM-specific EXIF tag identifiers used for validation
        self.semtags = [34118, 34680, 32932, 34665, 50838, 50839]

        # Array to store image tag values (initialized empty)
        self.image_tags = np.array([], dtype='int')

        # Final structured metadata dictionary for export
        self.FinalMetaDataDict = FinalMetaDataDict


    # Logging Corrupted or Invalid SEM Images
    def WriteFile(self, file, image, cnt): 

        """
        Appends a corrupted or invalid SEM image entry to a log file.

        Parameters:
            file (str): Path to the log file where the image entry should be saved.
            image (str): Filename or path of the SEM image that encountered an issue.
            cnt (int): Unique identifier or index of the image in the processing sequence.

        Returns:
            None
        """

        # Open the log file in append mode (create if it doesn't exist)
        with open(file, 'a+') as cimg:
            # Write a formatted entry with image ID and filename
            cimg.write(f'[SEM IMAGE: {cnt}] {image}\n')
        return

        
    # Export SEM Metadata to JSON Format
    def WriteSEMJson(self, file, semdict):

        """
        Writes structured SEM metadata to a JSON file.

        Parameters:
            file (str): Path to the output JSON file.
            semdict (dict): Dictionary containing metadata for a single SEM image.

        Returns:
            None
        """

        # Open the file in write mode and serialize the metadata dictionary
        with open(file, "w") as semoutfile:
            json.dump(semdict, semoutfile)
        return


    # Write Header Row to SEM Metadata CSV
    def WriteSEMHeadercsv(self, file):

        """
        Writes the header row to a CSV file for storing SEM metadata.

        Parameters:
            file (str): Path to the output CSV file.

        Returns:
            None
        """

        try:
            # Open the CSV file in write mode and create a writer object
            with open(file, 'w') as csv_file:
                writer = csv.writer(csv_file, delimiter=',')

                # Write the predefined SEM metadata keys as the header row
                writer.writerow(FullSEMKeys)

        except Exception as e:
            # Print an error message if the file cannot be opened or written
            print(colored("Something went wrong with opening the CSV file:", "red"), str(e))
        return


    # Append SEM Metadata to CSV File with Error Handling
    def WriteSEMcsv(self, file, semdict):

        """
        Appends a single SEM image's metadata to an existing CSV file.

        Parameters:
            file (str): Path to the target CSV file.
            semdict (dict): Dictionary containing metadata for one SEM image.

        Returns:
            None
        """

        try:
            # Open the CSV file in append mode with newline handling
            with open(file, 'a', newline='') as csv_file:
                # Create a dictionary-based CSV writer using the keys from the metadata dictionary
                writer = csv.DictWriter(csv_file, fieldnames=semdict.keys(), quotechar='"', escapechar='\\')            

                # Write the metadata row to the CSV file
                writer.writerow(semdict)

        except Exception as e:
            # Handle any file I/O or write errors gracefully
            print(colored("Error writing to SEM CSV file:", "red"), str(e))
        return


    # Prepare Strings for Safe SQL Insertion
    def EscapeStrings(self, semstring):

        """
        Escapes special characters in a string for safe MySQL insertion.

        This function uses `pymysql.converters.escape_string()` to sanitize input strings
        before storing them in a SQL database. It is especially useful for handling OCR-extracted
        or user-generated metadata that may contain quotes, backslashes, or other risky characters.

        Parameters:
            semstring (str): The input string to be escaped.

        Returns:
            str: The escaped string, safe for SQL insertion.
        """

        # Escape special characters using pymysql's built-in utility
        escaped_string = escape_string(semstring)
        return escaped_string


    # Extract Raw Metadata and Tag IDs from SEM Image
    def ImageMetadata(self, img):

        """
        Extracts raw metadata and tag identifiers including 34118 
        from a SEM image.

        Parameters:
            img (PIL.Image.Image): The opened SEM image object.

        Returns:
            tuple:
                - image_metadata (dict): Dictionary of available EXIF tags and their values.
                - image_tags (np.ndarray): Array of tag identifiers (keys) present in the image.
        """

        # Retrieve the raw EXIF tag dictionary from the image
        self.image_metadata = img.tag

        # Convert tag keys to a NumPy array for efficient lookup and processing
        self.image_tags = np.array(self.image_metadata)
        return self.image_metadata, self.image_tags


    # Validate Presence of SEM-Specific Tags
    def CheckInsTag(self, instags, imgtags):

        """
        Checks if any SEM-specific EXIF tags are present in the image's tag list.

        Parameters:
            instags (list): List of SEM-specific tag identifiers to look for.
            imgtags (list or np.ndarray): List of tag identifiers extracted from the image.

        Returns:
            bool: True if at least one SEM tag is found in the image, False otherwise.
        """

        # Iterate through SEM-specific tags and check for matches in the image's tag list
        for x in instags: 
            for y in imgtags:
                if x == y: 
                    return True  # Found a matching tag
        return False  # No SEM tags found
    

    # Access Standard EXIF Tags for Metadata Mapping
    @property    
    def SEMEXIF(self):

        """
        Provides access to standard EXIF tag mappings from PIL.

        Returns:
            tuple:
                - exif_keys (list): Human-readable EXIF tag names (e.g., 'DateTime', 'Make').
                - exif_number (list): Corresponding numeric tag identifiers used in image metadata.
        """

        # Reverse the PIL EXIF tag dictionary to map names to numeric keys
        exif_dict = {k: v for v, k in ExifTags.TAGS.items()}

        # Extract all tag names (keys) from the reversed dictionary
        exif_keys = list(exif_dict.keys())

        # Extract corresponding numeric identifiers for each tag name
        exif_number = [exif_dict[k] for k in exif_keys]
        return exif_keys, exif_number


    # Extract Standard EXIF Metadata from SEM Image
    def GetExifMetadata(self, img, exif_keys, exif_number):

        """
        Extracts standard EXIF metadata from a SEM image.

        Parameters:
            img (PIL.Image.Image): The opened SEM image object.
            exif_keys (list): List of human-readable EXIF tag names.
            exif_number (list): Corresponding numeric EXIF tag identifiers.

        Returns:
            tuple:
                - found_exif_metadata (list): List of tuples (value, tag name) for tags found in the image.
                - none_exif_metadata (list): List of tuples (tag name, None) for tags not present in the image.
        """

        # Extract metadata values for tags that exist in the image
        found_exif_metadata = [
            (img.tag[idx][:], word)  # Get tag value and associate with its name
            for idx, word in zip(exif_number, exif_keys) if idx in self.image_tags]           

        # Record tags that are missing from the image
        none_exif_metadata = [
            (word, None)  # Tag name with None as placeholder
            for num, word in zip(exif_number, exif_keys) if num not in self.image_tags]             
        return found_exif_metadata, none_exif_metadata


    # Construct Unified EXIF Metadata Dictionary
    def ExifMetaDict(self, found_exif_metadata, none_exif_metadata):

        """
        Creates a unified dictionary from found and missing EXIF metadata entries.

        Parameters:
            found_exif_metadata (list): List of tuples (value, tag name) for tags found in the image.
            none_exif_metadata (list): List of tuples (tag name, None) for tags not present in the image.

        Returns:
            dict: Combined dictionary of EXIF metadata, excluding 'ColorMap' entries.
        """

        # Convert found metadata into a dictionary, excluding 'ColorMap'
        found_metadict = {
            tag_name: value[0]  # Extract the first element from the value tuple
            for value, tag_name in found_exif_metadata if tag_name != "ColorMap"}       
    
        # Convert missing metadata into a dictionary with None values, excluding 'ColorMap'
        none_metadict = {
            tag_name: None
            for tag_name, value in none_exif_metadata if tag_name != "ColorMap"}      

        # Merge both dictionaries into a single metadata dictionary
        allexif_metadict = {**found_metadict, **none_metadict}
        return allexif_metadict


    # Extract Instrument Metadata from SEM Image
    @property
    def GetInsMetadata(self):

        """
        Extracts instrument-specific metadata from SEM image EXIF tag 34118.

        Returns:
            list: A cleaned and escaped list of instrument metadata strings.
                  Returns an empty list if tag 34118 is not found.
        """

        try:
            # Extract the value associated with EXIF tag 34118
            pairs = [params for tag, params in self.image_metadata.items() if tag == 34118]

            # Unpack the first matching entry (instrument metadata)
            instrument_metadata,*_ = pairs[0]

            # Clean the metadata by skipping the first N lines (random header content)
            random_size_tag = 35
            instrument_metadata = instrument_metadata.split("\r\n")[random_size_tag:]

            # Escape each string for safe SQL/database usage if needed
            instrument_metadata = [self.EscapeStrings(ins) for ins in instrument_metadata]

        except IndexError:
            # Tag 34118 not found — likely not a SEM image
            instrument_metadata = []
        return instrument_metadata

 
    # Parse Instrument Metadata from Tag 34118
    def InsMetaDict(self, metadata_list):

        """
        Converts a flat list of instrument metadata into a structured dictionary.

        Parameters:
            metadata_list (list): A list of strings extracted from EXIF tag 34118,
                                  assumed to alternate between keys and values.

        Returns:
            dict: Dictionary of instrument metadata (key-value pairs).
                  Returns an empty dictionary if parsing fails.
        """

        try:
            # Separate keys and values based on alternating index positions
            ins_keys = [val for idx, val in enumerate(metadata_list) if idx % 2 == 0]
            ins_values = [val for idx, val in enumerate(metadata_list) if idx % 2 != 0]

            # Combine keys and values into a dictionary
            instrument_meta_dict = dict(zip(ins_keys, ins_values))

        except Exception as e:
            # Handle malformed input gracefully
            print(colored("Error parsing instrument metadata:", "red"), str(e))
            instrument_meta_dict = {}
        return instrument_meta_dict


    # Validate and Synchronize Metadata Keys
    def CheckPrams(self, list1, list2):

        """
        Validates whether all keys in list2 are present in list1.
        If not, updates list1 to include missing keys and returns the difference.

        Parameters:
            list1 (list): Reference list of expected metadata keys (e.g., FullSEMKeys).
            list2 (list): List of actual metadata keys extracted from an image.

        Returns:
            tuple:
                - CHECKKEYS (bool): True if list1 contains all keys from list2.
                - DIFF (list): List of keys in list2 that are missing from list1.
        """

        # Initial check: does list1 fully contain list2?
        CHECKKEYS = set(list1 + list2) == set(list1)

        # Identify keys in list2 that are not present in list1
        DIFF = list(set(list2) - set(list1))

        # If keys are missing, update list1 to include them and recheck
        if not CHECKKEYS:
            list1_temp = set(list1 + list2)
            list1 = list(list1_temp)  # Convert back to list for consistency
            CHECKKEYS = set(list1 + list2) == set(list1)
        return CHECKKEYS, DIFF


    # Construct Complete SEM Metadata Dictionary  
    def FullMetaData(self, SEM_FULLMD_Dict, FullSEMKeys):

        """
        Constructs a complete metadata dictionary for a SEM image.

        Parameters:
            SEM_FULLMD_Dict (dict): Dictionary of metadata extracted from the image.
            FullSEMKeys (list): List of expected metadata keys for SEM images.

        Returns:
            dict: Ordered dictionary containing all expected keys, with missing values set to None.
        """

        # Extract existing keys and their corresponding values
        existing_keys = list(SEM_FULLMD_Dict.keys())
        existing_values = [SEM_FULLMD_Dict[k] for k in existing_keys]

        # Filter metadata to include only keys present in FullSEMKeys
        found_metadata = [(key, value) for key, value in zip(existing_keys, existing_values) if key in FullSEMKeys]    

        # Identify missing keys and assign None as placeholder
        none_metadata = [(key, None) for key in FullSEMKeys if key not in existing_keys]        
    
        # Convert found and missing metadata into dictionaries
        found_metadata_dict = {key: value for key, value in found_metadata}
        none_metadata_dict = {key: value for key, value in none_metadata}

        # Merge both dictionaries into a complete metadata dictionary
        ImgMetaDataDict = {**found_metadata_dict, **none_metadata_dict}

        # Reorder the final dictionary based on FullSEMKeys
        for key in FullSEMKeys:
            self.FinalMetaDataDict[key] = ImgMetaDataDict[key]
        return self.FinalMetaDataDict


    # Classify SEM Image by Pixel Scale
    def GetImageScale(self, pixel_size):

        """
        Classifies the SEM image based on its pixel size.

        Parameters:
            pixel_size (float): The pixel size value extracted from the image metadata.

        Returns:
            str or None: One of ['Milli', 'Micro', 'Nano', 'Pico'] if matched,
                         or None if the pixel size falls outside defined ranges.
        """

        # Millimeter scale: 1,000 to 999,000 nm
        if 1000 <= pixel_size <= 999000:
            return 'Milli'

        # Micrometer scale: 1 to 999 nm
        elif 1 <= pixel_size <= 999:
            return 'Micro'

        # Nanometer scale: 0.001 to 0.999 nm
        elif 0.001 <= pixel_size <= 0.999:
            return 'Nano'

        # Picometer scale: 0.000001 to 0.0009999 nm
        elif 0.000001 <= pixel_size <= 0.0009999:
            return 'Pico'

        # Unclassified scale
        else:
            return None


    # Detect Duplicate SEM Image Entries
    def GetDuplImag(self, image_list):
        
        """
        Identifies duplicate entries in a list of SEM image identifiers.

        Parameters:
            image_list (list): List of image filenames, IDs, or hashes.

        Returns:
            list: List of items that appear more than once in the input list.
        """

        # Count occurrences of each item and filter those with count > 1
        duplicated_images = [item for item, count in Counter(image_list).items() if count > 1]       
        return duplicated_images
