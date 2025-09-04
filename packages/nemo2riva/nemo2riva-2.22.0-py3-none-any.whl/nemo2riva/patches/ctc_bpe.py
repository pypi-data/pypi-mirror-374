# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

import logging

from nemo2riva.schema import check_nemo_version


def bpe_check_inputs_and_version(model, artifacts, **kwargs):
    if model.__class__.__name__ == 'EncDecCTCModelBPE':
        enc_class = model.encoder.__class__.__name__
        if enc_class == "ConformerEncoder":
            logging.info("Checking Nemo version for ConformerEncoder ...")
            check_nemo_version(">=1.7.0rc0")
