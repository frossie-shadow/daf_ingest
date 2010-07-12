#!/usr/bin/env python

# 
# LSST Data Management System
# Copyright 2008, 2009, 2010 LSST Corporation.
# 
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the LSST License Statement and 
# the GNU General Public License along with this program.  If not, 
# see <http://www.lsstcorp.org/LegalNotices/>.
#


import sys

from lsst.datarel import lsstSimMain, lsstSimSetup, runStage

import lsst.ip.pipeline as ipPipe
import lsst.meas.pipeline as measPipe

def crSplitProcess(root=None, outRoot=None, registry=None,
        inButler=None, outButler=None, **keys):
    inButler, outButler = lsstSimSetup(root, outRoot, registry, None,
            inButler, outButler)

    clip = {
        'isrCcdExposure0': inButler.get("postISRCCD", snap=0, **keys),
#        'isrCcdExposure1': inButler.get("postISRCCD", snap=1, **keys)
    }

    clip = runStage(measPipe.BackgroundEstimationStage,
        """#<?cfg paf policy?>
        inputKeys: {
            exposure: isrCcdExposure0
        }
        outputKeys: {
            backgroundSubtractedExposure: bkgSubCcdExposure0
        }
        parameters: {
            subtractBackground: true
            backgroundPolicy: {
                binsize: 512
            }
        }
        """, clip)

#     clip = runStage(measPipe.BackgroundEstimationStage,
#         """#<?cfg paf policy?>
#         inputKeys: {
#             exposure: isrCcdExposure1
#         }
#         outputKeys: {
#             backgroundSubtractedExposure: bkgSubCcdExposure1
#         }
#         parameters: {
#             subtractBackground: true
#             backgroundPolicy: {
#                 binsize: 512
#             }
#         }
#         """, clip)

    clip = runStage(ipPipe.CrRejectStage,
        """#<?cfg paf policy?>
        inputKeys: {
            exposure: bkgSubCcdExposure0
        }
        outputKeys: {
            exposure: crSubCcdExposure0
        }
        parameters: {
            defaultFwhm: 1.0
            keepCRs: false
        }
        crRejectPolicy: {
            nCrPixelMax: 100000
        }
        """, clip)
    print >>sys.stderr, "Snap 0:", clip['nCR'], "cosmic rays"

#     clip = runStage(ipPipe.CrRejectStage,
#         """#<?cfg paf policy?>
#         inputKeys: {
#             exposure: bkgSubCcdExposure1
#         }
#         outputKeys: {
#             exposure: crSubCcdExposure1
#         }
#         parameters: {
#             defaultFwhm: 1.0
#             keepCRs: false
#         }
#         crRejectPolicy: {
#             nCrPixelMax: 100000
#         }
#         """, clip)
#     print >>sys.stderr, "Snap 0:", clip['nCR'], "cosmic rays"
#     
#     clip = runStage(ipPipe.SimpleDiffImStage,
#         """#<?cfg paf policy?>
#         inputKeys: {
#             exposures: "crSubCcdExposure0" "crSubCcdExposure1"
#         }
#         outputKeys: {
#             differenceExposure: diffExposure
#         }
#         """, clip)
# 
#     clip = runStage(measPipe.SourceDetectionStage,
#         """#<?cfg paf policy?>
#         inputKeys: {
#             exposure: diffExposure
#         }
#         outputKeys: {
#             positiveDetection: positiveFootprintSet
#             negativeDetection: negativeFootprintSet
#             psf: psf
#         }
#         psfPolicy: {
#             parameter: 1.5
#         }
#         backgroundPolicy: {
#             algorithm: NONE
#         }
#         detectionPolicy: {
#             minPixels: 1
#             nGrow: 0
#             thresholdValue: 10.0
#             thresholdType: stdev
#             thresholdPolarity: both
#         }
#         """, clip)
# 
#     clip = runStage(ipPipe.CrSplitCombineStage,
#         """#<?cfg paf policy?>
#         inputKeys: {
#             exposures: "crSubCcdExposure0" "crSubCcdExposure1"
#             positiveDetection: positiveFootprintSet
#             negativeDetection: negativeFootprintSet
#         }
#         outputKeys: {
#             combinedExposure: visitExposure
#         }
#         """, clip)

    outButler.put(clip['crSubCcdExposure0'], "visitim", **keys)
#     outButler.put(clip['visitexposure'], "visitim", **keys)

def test():
    root = os.path.join(os.environ['AFWDATA_DIR'], "ImSim")
    crSplitProcess(root=root, outRoot=".",
            visit=85751839, raft="2,3", sensor="1,1")

def main():
    lsstSimMain(crSplitProcess, "visitim", "sensor")

if __name__ == "__main__":
    main()
