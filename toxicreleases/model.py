# Copyright 2012, Percy Wegmann

# This file defines the data model for triexplore.py.  Most of the logic lives here.

import sys, csv, math

# Constants
GRAMS_PER_POUND = 453.59237
ALL = "ALL"

# Create a universal key from a state and county.  Because of discrepancies in the dataset, we do some cleansing.
# This really requires more analysis to see if we're getting it right, but it's a basic first shot.
# My test showed that we still miss a handful (under 10) counties, none of which I'd heard of, so I'm okay with it for now.
def keyFromStateAndCounty(state, county):
    return (county + ', ' + state) \
        .replace(' ', '') \
        .replace('.', '') \
        .upper() \
        .replace('(CITY)', 'CITY') \
        .replace('SAINT', 'ST') \
        .replace('DISTRICTOFCOLUMBIA', 'WASHINGTON') \
        .replace('CARSONCITYCITY', 'CARSONCITY') \
        .replace('MIAMI-DADE', 'DADE')

# Prints a string without line breaking
def printWithoutBreak(string):
    sys.stdout.write(string)
    sys.stdout.flush()

# Details about a toxic release incident
# I was going to originally store details for all incidents to generate a list per county, but that got descoped.
# Consequently, most of the fields on Incident are not currently used.
class Incident(object):
    def __init__(self, _year, _facility, _street, _city, _county, _state, _fipsCode, _chemical, _poundsReleased, _parentCompany):
        self.year = _year
        self.facility = _facility
        self.street = _street
        self.city = _city
        self.county = _county
        self.stat = _state
        self.fipsCode = _fipsCode
        self.chemical = _chemical
        self.poundsReleased = _poundsReleased
        self.parentCompany = _parentCompany
        
# Toxic release metric by fipsCode and chemical
class Metric(object):
    def __init__(self, _fipsCode, _chemical, _incidents = 0, _poundsReleased = 0):
        self.fipsCode = _fipsCode
        self.chemical = _chemical    
        self.incidents = _incidents
        self.poundsReleased = _poundsReleased
        
    def addIncident(self, incident):
        self.incidents += 1
        self.poundsReleased += incident.poundsReleased
        
# A Metric representing 0 incidents and 0 pounds released        
ZERO_METRIC = Metric("UNKNOWN", "UNKNOWN", 0, 0)
        
# Holds all the data that we'll use to produce the visualization
class Model(object):
    def __init__(self):
        print 'Loading data into memory'
        print 'Feel free to grab a coffee'
        print ''
        
        # Maps state/county to fipsCode
        self.fipsCodesByStateAndCounty = self.__loadFipsCodes()
        # Tracks population by fipsCode
        self.populationByFips = self.__loadPopulationByFipsCode()
        # Stores a list of all chemicals appearing in the toxic release data
        chemicalCounts = self.__loadIncidents()
        # Turn chemicals into list
        self.chemicals = []
        for chemical, count in chemicalCounts.items():
            self.chemicals.append({'chemical': chemical, 'incidents': count})
        # Sort the list in reverse order by count and extract just the chemical
        self.chemicals = map(lambda chemical: chemical['chemical'],
                             sorted(
                                    list(self.chemicals),
                                    key=lambda chemical: chemical['incidents'],
                                    reverse=True))
        
    def incidentsByFipsCodeForChemical(self, chemical, perCapita = True):
        return self.__metricByFipsCodeForChemical('incidents',
                                                  chemical,
                                                  perCapita)
        
    def poundsReleasedByFipsCodeForChemical(self, chemical, perCapita = True):
        return self.__metricByFipsCodeForChemical('poundsReleased',
                                                  chemical,
                                                  perCapita)
        
    # Calculates aggregates for the indicated metric, accumulated using the given operation and grouped by fips code.
    #
    # Returns a dictionary with two elements:
    #   totals: a dictionary with the aggregated county info by fips code, including 'interval' and 'total'
    #   intervals: a list of the interval cutoffs.
    #
    # If perCapita is True, the values are given per 1000 residents.
    def __metricByFipsCodeForChemical(self, metric, chemical, perCapita):
        totals = {}
        maxTotal = 0
        
        # Chemicals are always upper case
        chemical = chemical.upper()
        
        # Count incidents by fips code
        for fipsCode, metricsByChemical in self.metricsByFips.items():
            total = totals.get(fipsCode, 0) + getattr(metricsByChemical.get(chemical, ZERO_METRIC), metric) 
            if perCapita:
                # Convert to per capita figure (per 1000 residents)
                total = float(total) / float(self.populationByFips[fipsCode]) * 1000
            maxTotal = max(maxTotal, total)
            totals[fipsCode] = total
        
        # Break into 5 categories on a logarithmic scale.
        # Find the base by taking the 5th root of the maximum value.  
        base = math.pow(maxTotal, .2)
        for fipsCode, total in totals.items():
            # Find the interval corresponding to the value by taking the log(base) of the value
            interval = 0 if total == 0 or base == 1 else math.log(total, base)
            interval = 0 if interval < 0 else int(math.floor(interval))
            totals[fipsCode] = {'interval': interval, 'total': total} 
        
        # Construct 4 interval cutoffs (which really represents 5 intervals)
        # TODO: add 5th cutoff corresponding to max value
        intervals = map(lambda power: round(math.pow(base, power), 2), range(1, 5))
        
        return {'totals': totals, 'intervals': intervals}

    # Loads mappings of state+count -> fips code into a dictionary
    def __loadFipsCodes(self):
        printWithoutBreak('Loading FIPS codes ')
        fipsCodesByStateAndCounty = {}
        with open('data/fips_codes.csv', 'rb') as fipsCodesFile:
            fipsCodes = csv.reader(fipsCodesFile, delimiter=',', quotechar='"')
            i = 0
            for row in fipsCodes:
                # Only process if we're not on the first row
                if i != 0:
                    key = keyFromStateAndCounty(row[0].strip(), row[1].strip())
                    fipsCodesByStateAndCounty[key] = row[2].strip().zfill(5)
                    if i % 100 == 0:
                        printWithoutBreak('.')
                i += 1
        printWithoutBreak('\n')
        return fipsCodesByStateAndCounty

    # Loads population estimates for year 2005 into a dictionary keyed to fips code
    def __loadPopulationByFipsCode(self):
        printWithoutBreak('Loading populations by county ')
        populationByFipsCode = {}
        with open('data/census_2009_population_estimates_by_county.csv', 'rb') as populationFile:
            population = csv.reader(populationFile, delimiter=',', quotechar='"')
            i = 0
            for row in population:
                # Only process if we're not on the first row
                if i != 0:
                    fipsCode = row[3].strip() + row[4].strip()
                    # Note - this was originall row[13] which was wrong
                    populationEstimate = int(row[14].strip())
                    populationByFipsCode[fipsCode] = populationEstimate
                    if i % 100 == 0:
                        printWithoutBreak('.')
                i += 1
        printWithoutBreak('\n')
        return populationByFipsCode

    # Load the actual toxic release incidents
    # As a side-effect, we will also create a dictionary of chemical names and associated frequencies, which this
    # method returns.
    def __loadIncidents(self):
        print 'Loading toxic release incidents for years 2000-2009'
        
        # Tracks the number of incidents per chemical
        chemicalCounts = {}
        # Tracks all incidents by fips code
        self.incidentsByFips = {}
        # Tracks metrics by fips
        self.metricsByFips = {}
        
        totalIncidentsLoaded = 0
        
        for y in range(10):
            year = '200' + str(y)
            printWithoutBreak('Loading year %(year)s' % {'year': year})
            # Read file
            with open('data/epa_toxic_releases_us_%(year)s.csv' % {'year': year}, 'rb') as toxicReleasesFile:
                toxicReleases = csv.reader(toxicReleasesFile, delimiter=',', quotechar='"')
    
                i = 0
                for row in toxicReleases:
                    # Only process if we're not on the first row
                    if i != 0:
                        # Read fields that we need for our incident
                        year = row[0].strip()
                        facility = row[2].strip()
                        street = row[3].strip()
                        city = row[4].strip()
                        county = row[5].strip()
                        state = row[6].strip()
                        chemical = row[23].strip()
                        unitOfMeasure = row[31].strip()
                        totalReleased = float(row[44].strip())
                        parentCompany = row[97].strip()
                        
                        # Find the fipsCode
                        countyStateKey = keyFromStateAndCounty(state, county)
                        try:
                            fipsCode = self.fipsCodesByStateAndCounty[countyStateKey]
                            # Just make sure we have a population figure - we won't use it until we calculate metrics
                            self.populationByFips[fipsCode]
                            # Keep track of the chemical
                            chemicalCounts[chemical] = chemicalCounts.get(chemical, 0) + 1
                            
                            # Normalize the total released
                            # The database contains grams or pounds
                            if unitOfMeasure == 'Grams':
                                # Convert from Grams to Pounds
                                poundsReleased = totalReleased * GRAMS_PER_POUND
                            elif unitOfMeasure == 'Pounds':
                                poundsReleased = totalReleased
                            else:
                                # This shouldn't happen
                                sys.exit("Unkown unitOfMeasure: " + unitOfMeasure)
                                
                            # Create our incident
                            incident = Incident(year, facility, street, city, county, state, fipsCode, chemical, poundsReleased, parentCompany)
                            
                            # Update metrics for this county
                            try:
                                metricsByChemical = self.metricsByFips[fipsCode]
                            except KeyError:
                                metricsByChemical = {}
                                self.metricsByFips[fipsCode] = metricsByChemical
                            
                            # This function updates the metric for the given fipsCode and chemical by adding the incident
                            def updateMetric(fipsCode, chemical):
                                try:
                                    metric = metricsByChemical[chemical]
                                except KeyError:
                                    metric = Metric(fipsCode, chemical)
                                    metricsByChemical[chemical] = metric
                                metric.addIncident(incident)
                            
                            # Update metrics for specific chemical
                            updateMetric(fipsCode, chemical)
                            # Metrics across all chemicals are tracked under the special "ALL" chemical
                            updateMetric(fipsCode, ALL)
                            
                            totalIncidentsLoaded += 1
                            
                            if i % 100 == 0:
                                printWithoutBreak('.')
                        except KeyError:
                            # Unknown FIPS or population - ignore
                            pass
                        
                    i += 1
            print ''

        printWithoutBreak('\n')
        print "Finished loading %(total)i incidents" % {'total': totalIncidentsLoaded}
        return chemicalCounts