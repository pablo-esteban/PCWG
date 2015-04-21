# calculates two Gross/Ideal yields from a nominal wind speed distribution
# creates a percentage value
import numpy as np
from configuration import XmlBase
import pandas as pd
from scipy.interpolate import interp1d
import rebin

class AEPCalculator:
    def __init__(self, referenceCurve, measuredCurve, distribution = None, distributionPath = None):
        if distribution is not None and distributionPath is not None:
            raise Exception("Either a distribution instance or a path to a distribution XML must be provided - not both")
        elif distribution is not None:
            self.distribution = distribution
        elif distributionPath is not None:
            self.distribution = WindSpeedDistribution(distributionPath)
        else:
            raise Exception("A distribution instance or a path to a distribution XML must be provided")

        self.referenceCurve = referenceCurve
        self.measuredCurve = measuredCurve

        energyCols = []
        for curveType in ['Reference','Measured']:
            for col in ['Upper','Lower','Freq','Power','Energy']:
                energyCols.append("{0}_{1}".format(curveType, col))
        self.energy_distribution = pd.DataFrame(index = self.distribution.keys, columns = energyCols)


    def calculate_AEP(self):
        self.refYield = self.calculate_ideal_yield('Reference')
        self.measuredYield = self.calculate_ideal_yield('Measured')
        self.AEP = self.measuredYield/self.refYield
        return self.AEP

    def getCurve(self,curveType):
        if curveType.lower() == 'reference':
            return self.referenceCurve
        elif curveType.lower() == 'measured':
            return self.measuredCurve
        else:
            raise Exception("Unknown curve type")

    def calculate_ideal_yield(self, curveType):
        curve = self.getCurve(curveType)
        energySum = 0
        energyColumns = ["{0}_{1}".format(curveType, col) for col in ['Upper','Lower','Freq','Power','Energy']]
        for bin in self.distribution.keys:
            if not hasattr(self,"lcb") or (hasattr(self,"lcb") and bin <= self.lcb):
                upper = curve.power(bin)
                lower = 0.0 if bin-self.distribution.rebin_width < min(curve.powerCurveLevels.index) else curve.power(bin-self.distribution.rebin_width)
                power=(upper+lower)/2.0
                freq = self.distribution.cumulativeFunction(bin)-self.distribution.cumulativeFunction(bin-self.distribution.rebin_width)
                self.energy_distribution.loc[bin, energyColumns] = [float(upper),lower,freq,power,freq*power]
                energySum += freq*power
        return energySum

class AEPCalculatorLCB(AEPCalculator):
    def __init__(self,referenceCurve, measuredCurve, distribution = None, distributionPath = None):
        AEPCalculator.__init__(self, referenceCurve, measuredCurve, distribution, distributionPath)
        self.lcb = max(self.measuredCurve.powerCurveLevels[self.measuredCurve.powerCurveLevels['Data Count'] > 0].index)

class WindSpeedDistribution(XmlBase):
    rebin_width = 0.5
    def __init__(self,path):
        self.parse(path)

    def parse(self,path):
        doc = self.readDoc(path)
        self.path = path

        distNode = doc.documentElement
        distribution = {}
        self.keys = []

        for node in self.getNodes(distNode, 'Bin'):
            BinCentre = self.getNodeFloat(node, 'BinCentre')
            if BinCentre in self.keys:
                raise Exception("Bin {0} has been defined more than once!".format(BinCentre))
            self.keys.append(BinCentre)
            distribution[BinCentre] = self.getNodeFloat(node, 'BinValue')

        self.df = pd.Series(distribution)
        if len(self.df) < 1:
            raise Exception("Error reading distribution file - no 'Bin' nodes detected...")

        self.binSize = self.df.index[2]-self.df.index[1]
        self.df_rebinned = self.rebin()
        self.cumulative  = self.df_rebinned.cumsum()
        self.cumulativeFunction = interp1d(self.cumulative.index, self.cumulative,bounds_error=False, fill_value=0.0)#,kind = 'cubic')

    def rebin(self):
        rebin_values = np.arange(self.df.index.min()-(self.rebin_width/2.0), self.df.index.max()+(self.rebin_width/2.0), self.rebin_width)
        rebin_centres = np.arange(self.df.index.min(), self.df.index.max(), self.rebin_width)
        x_bin_bounds = np.append(np.array(self.df.index) - (self.binSize / 2.0),self.df.index.max()+(self.binSize/2.0))
        rebinned_values = rebin.rebin(x_bin_bounds , np.array(self.df), rebin_values)#, 'piecewise_constant')
        return pd.Series(rebinned_values, index=rebin_centres)

    def __getitem__(self, item): # define so can be used like a dict
        return self.distribution[item]