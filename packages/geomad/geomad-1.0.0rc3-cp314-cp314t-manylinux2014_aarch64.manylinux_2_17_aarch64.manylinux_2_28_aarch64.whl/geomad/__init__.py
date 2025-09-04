# Copyright (c) 2018-2025 Geoscience Australia
# SPDX-License-Identifier: Apache-2.0

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "Unknown/Not Installed"

from .pcm import (
    gm as nangeomedian_pcm,
    wgm as nanwgeomedian_pcm,
    emad as emad_pcm,
    smad as smad_pcm,
    bcmad as bcmad_pcm,
)

__all__ = [
    "nangeomedian_pcm",
    "nanwgeomedian_pcm",
    "emad_pcm",
    "smad_pcm",
    "bcmad_pcm"
]