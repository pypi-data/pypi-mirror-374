# -*- coding: utf-8 -*-
r"""Module implementing spatial feature recognition (localization) in Consenrich-estimated genomic signals."""

import logging
import os
from pybedtools import BedTool
from typing import List, Optional

import pandas as pd
import pywt as pw
import numpy as np
import numpy.typing as npt

from scipy import signal, stats

from . import cconsenrich

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(module)s.%(funcName)s -  %(levelname)s - %(message)s",
)
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(module)s.%(funcName)s -  %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def matchWavelet(
    chromosome: str,
    intervals: npt.NDArray[int],
    values: npt.NDArray[np.float64],
    templateNames: List[str],
    cascadeLevels: List[int],
    iters: int,
    alpha: float,
    minMatchLengthBP: Optional[int],
    maxNumMatches: Optional[int] = 100_000,
    minSignalAtMaxima: Optional[float] = None,
    randSeed: int = 42,
    recenterAtPointSource: bool = True,
) -> pd.DataFrame:
    r"""Match discrete wavelet-based templates in the sequence of Consenrich estimates

    See :ref:`matching`.

    :param values: 'Consensus' signal estimates derived from multiple samples, e.g., from Consenrich.
    :type values: npt.NDArray[np.float64]
    :param templateNames: List of discrete wavelet template names to use for matching, e.g.
        `[haar, db2, db4, coif1]`.
    :type templateNames: List[str]
    :param cascadeLevels: List of cascade levels used to discretely sample
        the given wavelet function.
    :type cascadeLevels: List[int]
    :param iters: Number of random blocks to sample in the response sequence while building
        an empirical null to test significance. See :func:`cconsenrich.csampleBlockStats`.
    :type iters: int
    :param alpha: Significance threshold on detected matches. Specifically, the
        :math:`1 - \alpha` quantile of the empirical null distribution.
    :type alpha: float
    :param minMatchLengthBP: Within a window of `minMatchLengthBP` length (bp), relative maxima in
        the signal-template convolution must be greater in value than others to qualify as matches
        (...in addition to the other criteria.)
    :type minMatchLengthBP: int
    :param minSignalAtMaxima: Minimum *signal* value (not response value) at the maxima to qualify matches.
        If None, the mean of the signal is used. Set to zero to disable this criterion.
    :type minSignalAtMaxima: float

    :seealso: :class:`consenrich.core.matchingParams`, :func:`cconsenrich.csampleBlockStats`
    """

    if len(intervals) < 5:
        raise ValueError("`intervals` must be at least length 5")
    if len(values) != len(intervals):
        raise ValueError("`values` must have the same length as `intervals`")
    intervalLengthBP = intervals[1] - intervals[0]
    if not np.all(np.abs(np.diff(intervals)) == intervalLengthBP):
        raise ValueError("`intervals` must be evenly spaced.")

    randSeed_: int = int(randSeed)
    cols = [
        "chromosome",
        "start",
        "end",
        "name",
        "score",
        "strand",
        "signal",
        "pValue",
        "qValue",
        "pointSource",
    ]
    matchDF = pd.DataFrame(columns=cols)
    minMatchLengthBPCopy: Optional[int] = minMatchLengthBP
    cascadeLevels = sorted(list(set(cascadeLevels)))

    for l_, cascadeLevel in enumerate(cascadeLevels):
        for t_, templateName in enumerate(templateNames):
            try:
                templateName = str(templateName)
                cascadeLevel = int(cascadeLevel)
            except ValueError:
                logger.warning(
                    f"Skipping invalid templateName or cascadeLevel: {templateName}, {cascadeLevel}"
                )
                continue
            if templateName not in pw.wavelist(kind="discrete"):
                logger.warning(
                    f"\nSkipping unknown wavelet template: {templateName}\nAvailable templates: {pw.wavelist(kind='discrete')}"
                )
                continue

            wav = pw.Wavelet(templateName)
            scalingFunc, waveletFunc, x = wav.wavefun(level=cascadeLevel)
            template = np.array(waveletFunc, dtype=np.float64) / np.linalg.norm(
                waveletFunc
            )
            logger.info(
                f"Matching: wavelet template: {templateName}, cascade level: {cascadeLevel}, template length: {len(template)}"
            )

            responseSequence: npt.NDArray[np.float64] = signal.fftconvolve(
                values, template[::-1], mode="same"
            )

            minMatchLengthBP = minMatchLengthBPCopy
            if minMatchLengthBP is None:
                minMatchLengthBP = len(template) * intervalLengthBP
            # Ensure minMatchLengthBP is a multiple of intervalLengthBP
            if minMatchLengthBP % intervalLengthBP != 0:
                minMatchLengthBP += intervalLengthBP - (
                    minMatchLengthBP % intervalLengthBP
                )

            # reduce overlaps
            relativeMaximaWindow = int(
                ((minMatchLengthBP / intervalLengthBP) / 2) + 1
            )
            relativeMaximaWindow = max(relativeMaximaWindow, 1)

            logger.info(
                f"\nSampling {iters} block maxima for template {templateName} at cascade level {cascadeLevel} with (expected) relative maxima window size {relativeMaximaWindow}."
            )
            blockMaxima = cconsenrich.csampleBlockStats(
                responseSequence, relativeMaximaWindow, iters, randSeed_
            )
            logger.info("Done.")

            responseThreshold = np.quantile(blockMaxima, 1 - alpha)
            ecdfBlockMaximaSF = stats.ecdf(blockMaxima).sf

            signalThreshold: float = 0.0
            if minSignalAtMaxima is None:
                signalThreshold = max(0, np.mean(values))
            elif minSignalAtMaxima == 0:
                signalThreshold = -np.inf

            relativeMaximaIndices = signal.argrelmax(
                responseSequence, order=relativeMaximaWindow
            )[0]

            relativeMaximaIndices = relativeMaximaIndices[
                (responseSequence[relativeMaximaIndices] > responseThreshold)
                & (values[relativeMaximaIndices] > signalThreshold)
            ]

            if maxNumMatches is not None:
                if len(relativeMaximaIndices) > maxNumMatches:
                    # take the greatest maxNumMatches (by 'signal')
                    relativeMaximaIndices = relativeMaximaIndices[
                        np.argsort(values[relativeMaximaIndices])[
                            -maxNumMatches:
                        ]
                    ]

            if len(relativeMaximaIndices) == 0:
                logger.warning(
                    f"no matches were detected using for template {templateName} at cascade level {cascadeLevel}."
                )
                continue

            # Get the start, end, and point-source indices of matches
            startsIdx = np.maximum(
                relativeMaximaIndices - relativeMaximaWindow, 0
            )
            endsIdx = np.minimum(
                len(values) - 1, relativeMaximaIndices + relativeMaximaWindow
            )
            pointSourcesIdx = []
            for start_, end_ in zip(startsIdx, endsIdx):
                pointSourcesIdx.append(
                    np.argmax(values[start_ : end_ + 1]) + start_
                )
            pointSourcesIdx = np.array(pointSourcesIdx)
            starts = intervals[startsIdx]
            ends = intervals[endsIdx]
            pointSources = (intervals[pointSourcesIdx]) + max(
                1, intervalLengthBP // 2
            )
            if recenterAtPointSource:  # recenter at point source (signal maximum) rather than maximum in response
                starts = pointSources - (
                    relativeMaximaWindow * intervalLengthBP
                )
                ends = pointSources + (relativeMaximaWindow * intervalLengthBP)
            pointSources = (intervals[pointSourcesIdx] - starts) + max(
                1, intervalLengthBP // 2
            )

            # Calculate ucsc browser scores
            sqScores = (1 + responseSequence[relativeMaximaIndices]) ** 2
            minResponse = np.min(sqScores)
            maxResponse = np.max(sqScores)
            rangeResponse = max(maxResponse - minResponse, 1.0)
            scores = (
                250 + 750 * (sqScores - minResponse) / rangeResponse
            ).astype(int)

            names = [
                f"{templateName}_{cascadeLevel}_{i}"
                for i in relativeMaximaIndices
            ]
            strands = ["." for _ in range(len(scores))]
            # Note, p-values are in -log10 per convention (narrowPeak)
            pValues = -np.log10(
                np.clip(
                    ecdfBlockMaximaSF.evaluate(
                        responseSequence[relativeMaximaIndices]
                    ),
                    1e-10,
                    1.0,
                )
            )

            qValues = np.array(np.ones_like(pValues) * -1.0)  # leave out (-1)

            tempDF = pd.DataFrame(
                {
                    "chromosome": [chromosome] * len(relativeMaximaIndices),
                    "start": starts.astype(int),
                    "end": ends.astype(int),
                    "name": names,
                    "score": scores,
                    "strand": strands,
                    "signal": responseSequence[relativeMaximaIndices],
                    "pValue": pValues,
                    "qValue": qValues,
                    "pointSource": pointSources.astype(int),
                }
            )

            if matchDF.empty:
                matchDF = tempDF
            else:
                matchDF = pd.concat([matchDF, tempDF], ignore_index=True)
            randSeed_ += 1

    if matchDF.empty:
        logger.warning("No matches detected, returning empty DataFrame.")
        return matchDF
    matchDF.sort_values(by=["chromosome", "start", "end"], inplace=True)
    matchDF.reset_index(drop=True, inplace=True)
    return matchDF


def mergeMatches(filePath: str, mergeGapBP: int = 25):
    r"""Merge overlapping or nearby structured peaks (matches) in a narrowPeak file.

    Where an overlap occurs within `mergeGapBP` base pairs, the feature with the greatest signal defines the new summit/pointSource

    :param filePath: narrowPeak file containing matches detected with :func:`consenrich.matching.matchWavelet`
    :type filePath: str
    :param mergeGapBP: Maximum gap size (in base pairs) to consider for merging
    :type mergeGapBP: int

    :seealso: :class:`consenrich.core.matchingParams`
    """
    if not os.path.isfile(filePath):
        logger.warning(f"Couldn't access {filePath}...skipping merge")
        return None
    bed = None
    try:
        bed = BedTool(filePath)
    except Exception as ex:
        logger.warning(f"Couldn't create BedTool for {filePath}:\n{ex}\n\nskipping merge...")
        return None
    if bed is None:
        logger.warning(
            f"Couldn't create BedTool for {filePath}...skipping merge"
        )
        return None

    bed = bed.sort()
    clustered = bed.cluster(d=mergeGapBP)
    groups = {}
    for f in clustered:
        fields = f.fields
        chrom = fields[0]
        start = int(fields[1])
        end = int(fields[2])
        score = float(fields[4])
        signal = float(fields[6])
        pval = float(fields[7])
        qval = float(fields[8])
        peak = int(fields[9])
        clId = fields[-1]
        if clId not in groups:
            groups[clId] = {
                "chrom": chrom,
                "sMin": start,
                "eMax": end,
                "scSum": 0.0,
                "sigSum": 0.0,
                "pSum": 0.0,
                "qSum": 0.0,
                "n": 0,
                "maxS": float("-inf"),
                "peakAbs": -1,
            }
        g = groups[clId]
        if start < g["sMin"]:
            g["sMin"] = start
        if end > g["eMax"]:
            g["eMax"] = end
        g["scSum"] += score
        g["sigSum"] += signal
        g["pSum"] += pval
        g["qSum"] += qval
        g["n"] += 1
        # scan for largest signal, FFR: consider using the p-val in the future
        if signal > g["maxS"]:
            g["maxS"] = signal
            g["peakAbs"] = start + peak if peak >= 0 else -1
    items = []
    for clId, g in groups.items():
        items.append((g["chrom"], g["sMin"], g["eMax"], g))
    items.sort(key=lambda x: (str(x[0]), x[1], x[2]))
    outPath = f"{filePath.replace('.narrowPeak', '')}.mergedMatches.narrowPeak"
    lines = []
    i = 0
    for chrom, sMin, eMax, g in items:
        i += 1
        avgScore = g["scSum"] / g["n"]
        if avgScore < 0:
            avgScore = 0
        if avgScore > 1000:
            avgScore = 1000
        scoreInt = int(round(avgScore))
        sigAvg = g["sigSum"] / g["n"]
        pAvg = g["pSum"] / g["n"]
        qAvg = g["qSum"] / g["n"]
        pointSource = g["peakAbs"] - sMin if g["peakAbs"] >= 0 else -1
        name = f"mergedPeak{i}"
        lines.append(
            f"{chrom}\t{int(sMin)}\t{int(eMax)}\t{name}\t{scoreInt}\t.\t{sigAvg:.3f}\t{pAvg:.3f}\t{qAvg:.3f}\t{int(pointSource)}"
        )
    with open(outPath, "w") as outF:
        outF.write("\n".join(lines) + ("\n" if lines else ""))
    logger.info(f"Merged matches written to {outPath}")
    return outPath
