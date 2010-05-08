#!/usr/bin/env python

import os
import lsst.pex.policy as pexPolicy
import lsst.ip.pipeline as ipPipe
import lsst.daf.persistence as dafPersist
from lsst.obs.cfht import CfhtMapper
from lsst.pex.harness.simpleStageTester import SimpleStageTester

def isrProcess(root=None, outRoot=None, inButler=None, outButler=None, **keys):

    if inButler is None:
        bf = dafPersist.ButlerFactory(mapper=CfhtMapper(
            root=root, calibRoot="/lsst/DC3/data/obstest/CFHTLS/calib"))
        inButler = bf.create()
    if outButler is None:
        obf = dafPersist.ButlerFactory(mapper=CfhtMapper(root=outRoot))
        outButler = obf.create()

    clip = {
        'isrExposure': inButler.get("raw", **keys),
        'biasExposure': inButler.get("bias", **keys),
#         'darkExposure': inButler.get("dark", **keys),
        'flatExposure': inButler.get("flat", **keys)
    }

    pol = pexPolicy.Policy.createPolicy(pexPolicy.PolicyString(
        """#<?cfg paf policy?>
        inputKeys: {
            exposure: isrExposure
        }
        outputKeys: {
            saturationMaskedExposure: isrExposure
        }
        """))
    sat = SimpleStageTester(ipPipe.IsrSaturationStage(pol))

    pol = pexPolicy.Policy.createPolicy(pexPolicy.PolicyString(
        """#<?cfg paf policy?>
        inputKeys: {
            exposure: isrExposure
        }
        outputKeys: {
            overscanCorrectedExposure: isrExposure
        }
        """))
    over = SimpleStageTester(ipPipe.IsrOverscanStage(pol))

    pol = pexPolicy.Policy.createPolicy(pexPolicy.PolicyString(
        """#<?cfg paf policy?>
        inputKeys: {
            exposure: isrExposure
            biasexposure: biasExposure
        }
        outputKeys: {
            biasSubtractedExposure: isrExposure
        }
        """))
    bias = SimpleStageTester(ipPipe.IsrBiasStage(pol))

    # pol = pexPolicy.Policy.createPolicy(pexPolicy.PolicyString(
    #     """#<?cfg paf policy?>
    #     inputKeys: {
    #         exposure: isrExposure
    #         darkexposure: darkExposure
    #     }
    #     outputKeys: {
    #         darkSubtractedExposure: isrExposure
    #     }
    #     """))
    # dark = SimpleStageTester(ipPipe.IsrDarkStage(pol))

    pol = pexPolicy.Policy.createPolicy(pexPolicy.PolicyString(
        """#<?cfg paf policy?>
        inputKeys: {
            exposure: isrExposure
            flatexposure: flatExposure
        }
        parameters: {
            flatScalingValue: 1.0
        }
        outputKeys: {
            flatCorrectedExposure: isrExposure
        }
        """))
    flat = SimpleStageTester(ipPipe.IsrFlatStage(pol))

    clip = sat.runWorker(clip)
    clip = over.runWorker(clip)
    clip = bias.runWorker(clip)
    # clip = dark.runWorker(clip)
    clip = flat.runWorker(clip)
    exposure = clip['isrExposure']
    # exposure.writeFits("postIsr.fits")

    outButler.put(exposure, "postISR", **keys)

def run():
    root = "/lsst/DC3/data/obstest/CFHTLS"
    isrProcess(root=root, outRoot=".", field="D3", visit=788965, ccd=6, amp=0)
    isrProcess(root=root, outRoot=".", field="D3", visit=788965, ccd=6, amp=1)

if __name__ == "__main__":
    run()