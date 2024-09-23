#!/usr/bin/env python3
import copy
from datetime import datetime
import logging
import os
import random
import sys
import tempfile
from typing import List

import numpy as np

import pynetdicom
import pydicom
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
from pydicom.uid import generate_uid, DigitalMammographyXRayImageStorageForPresentation, ExplicitVRLittleEndian, \
    ImplicitVRLittleEndian, DeflatedExplicitVRLittleEndian, ExplicitVRBigEndian, CTImageStorage, \
    DigitalMammographyXRayImageStorageForProcessing, RTImageStorage, MRImageStorage, BasicTextSRStorage, \
    JPEGTransferSyntaxes, JPEG2000TransferSyntaxes
from pynetdicom import AE, StoragePresentationContexts

script_directory = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(script_directory)
tmp_dir = os.path.join(PROJECT_DIR, "data", "interim", "tmp")

sys.path.append(PROJECT_DIR)

from src import logging_utils
LOGGER_NAME = "dicom_client"


def _get_dcm_files(image_dir):
    input_files = os.listdir(image_dir)
    input_files = [os.path.join(image_dir, x) for x in input_files if not x.startswith(".")]
    input_files = [x for x in input_files if os.path.isfile(x) and x.endswith(".dcm")]
    return input_files


def read_dicom_images(file_paths: List[str]) -> List[pydicom.dataset.FileDataset]:
    """Read DICOM image and return the dataset"""
    return [pydicom.dcmread(file_path) for file_path in file_paths]


def get_info(dcm: pydicom.dataset):
    # dcm = pydicom.dcmread(dicom_path)
    view_str = dcm.ViewPosition
    side_str = dcm.ImageLaterality
    series_str = dcm.SOPClassUID
    view_seq = 0 if view_str == 'CC' else 1
    side_seq = 0 if side_str == 'R' else 1
    dcm_permissible = side_str in ['R', 'L'] and view_str in ['MLO', 'CC']
    return side_seq, view_seq, dcm_permissible


def send_dicom_file(filenames, dest_ae_title, dest_host, dest_port):
    """
    Send a DICOM file to an SCP/PACS server
    Args:
        filenames:
        dest_ae_title:
        dest_host:
        dest_port:

    Returns:

    """
    # Initialize the DICOM Application Entity
    logger = logging_utils.get_logger(LOGGER_NAME)
    my_ae_title = "MY_AE_TITLE"
    ae = AE(ae_title=my_ae_title)

    all_transfer_syntax = [
        ExplicitVRLittleEndian,
        ImplicitVRLittleEndian,
        ExplicitVRBigEndian,
    ] + JPEGTransferSyntaxes + JPEG2000TransferSyntaxes

    # Add the requested presentation contexts
    # Make sure that the context for the file is included
    context_ids = [DigitalMammographyXRayImageStorageForPresentation,
                   DigitalMammographyXRayImageStorageForProcessing,
                   CTImageStorage,
                   BasicTextSRStorage,]
    for cid in context_ids:
        for stx in all_transfer_syntax:
            ae.add_requested_context(cid, stx)

    # Initiate association with the PACS
    assoc = ae.associate(dest_host, dest_port, ae_title=dest_ae_title)

    if not isinstance(filenames, list):
        filenames = [filenames]

    if assoc.is_established:
        for filename in filenames:
            logger.debug(f"Sending {filename}")
            status = assoc.send_c_store(filename)
            logger.debug(f"{filename} C-STORE status: {status.Status}")

        # Release the association
        assoc.release()
    else:
        logger.error("Association with PACS failed")


# Main script
if __name__ == "__main__":
    logger = logging_utils.configure_logger(loglevel="DEBUG", logger_name=LOGGER_NAME)
    # pynetdicom.debug_logger()

    # PACS server details, replace these with your actual PACS server details
    dest_ae_title = "ARK_AE"
    dest_host = "localhost"
    dest_port = 11112

    image_dir = "/Users/silterra/Projects/Mirai_general/mirai_demo_data"
    # image_dir = "/Users/silterra/Projects/Sybil_general/sybil_demo_data"
    # image_dir = "/Users/silterra/Projects/Mirai_general/MountAuburn/OneDrive_2_9-4-2024/RADIANT_BETSY_Original-Study"
    # image_dir = "/Users/silterra/Projects/Mirai_general/MountAuburn/OneDrive_2_9-4-2024/RADIANT_JENNA"
    image_file_paths = _get_dcm_files(image_dir)

    send_dicom_file(image_file_paths, dest_ae_title, dest_host, dest_port)

