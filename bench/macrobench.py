
from os import system
from sys import exit
import pickle
import json


## START OF EXPERIMENTAL PARAMETERS

RUNTIMES = [1000, 5000, 10000, 20000, 40000]

ALGORITHMS = ["PORKCHOP", "ADMM", "MiniBatchADMM", "AsyncADMM", "HOGWILD"]#, "HOGWILD", "GD", "PORKCHOP"]

PICKLED_OUTPUT = "experiment.pkl"

## END OF EXPERIMENTAL PARAMETERS


## START OF CONSTANTS

GLOBAL_ADMMepsilon = 0.0
GLOBAL_ADMMlocalEpsilon = 1.0e-5
GLOBAL_ADMMrho = 1000

GLOBAL_ADMMlagrangianRho = 1000

GLOBAL_ADMM_maxLocalIterations = 100000
GLOBAL_ADMM_localEpsilon = 1.0e-5
GLOBAL_ADMM_localTimeout = 100000000

GLOBAL_MiniBatchADMM_maxLocalIterations = 100000000
GLOBAL_MiniBatchADMM_localEpsilon = 1.0e-3
GLOBAL_MiniBatchADMM_localTimeout = 500

GLOBAL_HOGWILD_maxLocalIterations = 10
GLOBAL_HOGWILD_broadcastDelay = 10

GLOBAL_AsyncADMM_maxLocalIterations = 100000
GLOBAL_AsyncADMM_broadcastDelay = 100

GLOBAL_PORKCHOP_maxLocalIterations = 1400000
GLOBAL_PORKCHOP_localEpsilon = 1.0e-3
GLOBAL_PORKCHOP_broadcastDelay = 100

GLOBAL_inputTokenHashKernelDimension = 1000

## END OF CONSTANTS


## START OF DATASET FORMATTING

def describe_point_cloud(pointsPerPartition = 500000,
                         partitionSkew = 0.00,
                         labelNoise = 0.05,
                         dimension = 100):
    return   "--pointCloudPointsPerPartition " + str(pointsPerPartition) + " " + \
             "--pointCloudPartitionSkew " + str(partitionSkew) + " " + \
             "--pointCloudLabelNoise " + str(labelNoise) + " " + \
             "--pointCloudDimension " + str(dimension) + " " 

def describe_forest():
    return " --input /user/root/bismarck_data/forest* "

def describe_flights(year):
    return " --input /user/root/flights/"+str(year)+".csv"

def describe_dblp():
    return " --input /user/root/dblp/binarized-year-to-title.txt"

def describe_wikipedia():
    return " --input /user/root/wiki/en-wiki-8-7-2014-tokenized.txt"

## END OF DATASET FORMATTING


## START OF TEST RUNNING CODE

def runTest(runtimeMS,
            algorithm,
            datasetName,
            ADMMepsilon = GLOBAL_ADMMepsilon,
            ADMMlocalEpsilon = GLOBAL_ADMMlocalEpsilon,
            ADMMmaxLocalIterations = 1000,
            ADMMrho = GLOBAL_ADMMrho,
            ADMMlagrangianRho = GLOBAL_ADMMlagrangianRho,
            regType="L2",
            regParam=0.1,
            numPartitions = (8*16),
            broadcastDelay = 100,
            cloudDim=-1,
            localTimeout = 10000000,
            cloudPartitionSkew=-1,
            flightsYear = "2008",
            wikipediaTargetWordToken = 4690,
            dblpSplitYear = 2007,
            inputTokenHashKernelDimension = GLOBAL_inputTokenHashKernelDimension,
            miscStr = ""):
    if datasetName == "bismarck":
        datasetConfigStr = describe_forest()
    elif datasetName == "cloud":
        datasetConfigStr = describe_point_cloud(partitionSkew = cloudPartitionSkew, dimension = cloudDim)
    elif datasetName == "flights":
        datasetConfigStr = describe_flights(flightsYear)
    elif datasetName == "dblp":
        datasetConfigStr = describe_dblp()
    elif datasetName == "wikipedia":
        datasetConfigStr = describe_wikipedia()
    else:
        print "Unknown dataset!"
        raise

    cmd = "cd /mnt/spark; sbin/stop-all.sh; sleep 5; sbin/start-all.sh; sleep 3;" \
          "./bin/spark-submit " \
          "--driver-memory 52g " \
          "--class org.apache.spark.examples.mllib.research.SynchronousADMMTests " \
          "examples/target/scala-*/spark-examples-*.jar " \
          "--algorithm " + str(algorithm) + " " + \
          "--regType " + str(regType) + " " + \
          "--regParam " + str(regParam) + " " + \
          "--format " + str(datasetName) + " " + \
          "--numPartitions " + str(numPartitions) + " " + \
          "--runtimeMS " + str(runtimeMS) + " " + \
          "--ADMMmaxLocalIterations " + str(ADMMmaxLocalIterations) + " " + \
          "--ADMMepsilon " + str(ADMMepsilon) + " " + \
          "--ADMMLocalepsilon " + str(ADMMlocalEpsilon) + " " + \
          "--ADMMrho " + str(ADMMrho) + " " + \
          "--ADMMLagrangianrho " + str(ADMMlagrangianRho) + " " + \
          "--broadcastDelayMs " + str(broadcastDelay) + " " +  \
          "--dblpSplitYear " + str(dblpSplitYear) + " " + \
          "--wikipediaTargetWordToken " + str(wikipediaTargetWordToken) + " " +  \
          "--inputTokenHashKernelDimension " + str(inputTokenHashKernelDimension) + " " + \
          "--localTimeout " + str(localTimeout) + " " + \
          datasetConfigStr + " " + miscStr + " "

           # (algorithm,
           # regType,
           # regParam,
           # datasetName,
           # numPartitions,
           # runtimeMS,
           # ADMMmaxLocalIterations,
           # ADMMepsilon,
           # ADMMlocalEpsilon,
           # ADMMrho,
           # ADMMlagrangianRho,
           # broadcastDelay,
           # dblpSplitYear,
           # wikipediaTargetWordToken,
           # inputTokenHashKernelDimension,
           # datasetConfigStr,
           # miscStr)

    print cmd

    system("eval '%s' > /tmp/run.out 2>&1" % (cmd))

    results = []
    # s"RESULT: ${params.algorithm} \t ${i} \t ${totalTimeMs} \t ${metrics.areaUnderPR()} \t ${metrics.areaUnderROC()} " +
    # s"\t ${trainingLoss} \t  ${regularizationPenalty} \t ${trainingLoss + regularizationPenalty} \t ${model.weights}"
    for line in open("/tmp/run.out"):
        if line.find("RESULT") != -1:
            record = json.loads(line[7:])
            pyConfig = {
                "algorithm": algorithm,
                "dataset": datasetName,
                "datasetConfigStr": datasetConfigStr,
                "line": line,
                "ADMMepsilon": ADMMepsilon,
                "ADMMlocalEpsilon": ADMMlocalEpsilon,
                "ADMMmaxLocalIterations": ADMMmaxLocalIterations,
                "ADMMrho": ADMMrho,
                "ADMMlagrangianRho": ADMMlagrangianRho,
                "broadcastDelay": broadcastDelay,
                "command": cmd,
                "regParam": regParam,
                "numPartitions": numPartitions,
                "regType": regType,
                "pointCloudDim": cloudDim,
                "pointCloudSkew": cloudPartitionSkew,
                "inputTokenHashKernelDimension": inputTokenHashKernelDimension,
                "dblpSplitYear": dblpSplitYear,
                "localTimeout": localTimeout,
                "wikipediaTargetWordToken": wikipediaTargetWordToken
            }
            record['pyConfig'] = pyConfig
            results.append(record)

    return results

results = []

## END OF TEST RUNNING CODE


## START OF EXPERIMENT RUNS

for dataset in ["wikipedia", "bismarck", "dblp"]: #, "flights"]:
    for runtime in RUNTIMES:
        for algorithm in ALGORITHMS:
            broadcastDelay = -1
            localEpsilon = GLOBAL_ADMMlocalEpsilon
            miscStr = "" # " --useLineSearch true --miniBatchSize 10000000"
            if algorithm == "ADMM":
                maxLocalIterations = GLOBAL_ADMM_maxLocalIterations
                localEpsilon = GLOBAL_ADMM_localEpsilon
                localTimeout = GLOBAL_ADMM_localTimeout
            elif algorithm == "MiniBatchADMM":
                maxLocalIterations = GLOBAL_MiniBatchADMM_maxLocalIterations
                localEpsilon = GLOBAL_MiniBatchADMM_localEpsilon
                localTimeout = GLOBAL_MiniBatchADMM_localTimeout
            elif algorithm == "HOGWILD":
                maxLocalIterations = GLOBAL_HOGWILD_maxLocalIterations
                broadcastDelay = GLOBAL_HOGWILD_broadcastDelay
            elif algorithm == "PORKCHOP":
                maxLocalIterations = GLOBAL_PORKCHOP_maxLocalIterations
                broadcastDelay = GLOBAL_PORKCHOP_broadcastDelay
                localEpsilon = GLOBAL_PORKCHOP_localEpsilon
                localTimeout = -1
            elif algorithm == "AsyncADMM":
                maxLocalIterations = GLOBAL_AsyncADMM_maxLocalIterations
                broadcastDelay = GLOBAL_AsyncADMM_broadcastDelay

            results += runTest(runtime,
                            algorithm,
                            dataset,
                            flightsYear = 2008,
                            regParam = 1000,
                            ADMMmaxLocalIterations = maxLocalIterations,
                            ADMMlocalEpsilon = localEpsilon,
                            broadcastDelay = broadcastDelay,
                               miscStr = miscStr,
                               localTimeout = localTimeout)

            output = open(PICKLED_OUTPUT, 'wb')
            pickle.dump(results, output)
            output.close()


for runtime in RUNTIMES:
    for dim in [2, 10, 100]:
        for skew in [0.0]:
            for algorithm in ALGORITHMS:
                broadcastDelay = -1
                localEpsilon = GLOBAL_ADMMlocalEpsilon
                miscStr = "" # " --useLineSearch true --miniBatchSize 10000000"
                if algorithm == "ADMM":
                    maxLocalIterations = GLOBAL_ADMM_maxLocalIterations
                    localEpsilon = GLOBAL_ADMM_localEpsilon
                    localTimeout = GLOBAL_ADMM_localTimeout
                elif algorithm == "MiniBatchADMM":
                    maxLocalIterations = GLOBAL_MiniBatchADMM_maxLocalIterations
                    localEpsilon = GLOBAL_MiniBatchADMM_localEpsilon
                    localTimeout = GLOBAL_MiniBatchADMM_localTimeout
                elif algorithm == "HOGWILD":
                    maxLocalIterations = GLOBAL_HOGWILD_maxLocalIterations
                    broadcastDelay = GLOBAL_HOGWILD_broadcastDelay
                elif algorithm == "PORKCHOP":
                    maxLocalIterations = GLOBAL_PORKCHOP_maxLocalIterations
                    broadcastDelay = GLOBAL_PORKCHOP_broadcastDelay
                    localEpsilon = GLOBAL_PORKCHOP_localEpsilon
                    localTimeout = -1
                elif algorithm == "AsyncADMM":
                    maxLocalIterations = GLOBAL_AsyncADMM_maxLocalIterations
                    broadcastDelay = GLOBAL_AsyncADMM_broadcastDelay
                

                results += runTest(runtime,
                                   algorithm,
                                   "cloud",
                                   cloudPartitionSkew = skew,
                                   cloudDim = dim,
                                   regParam = 1000,
                                   ADMMmaxLocalIterations = maxLocalIterations,
                                   ADMMlocalEpsilon = localEpsilon,
                                   broadcastDelay = broadcastDelay,
                                   miscStr = miscStr,
                                   localTimeout= localTimeout
                )

                output = open(PICKLED_OUTPUT, 'wb')
                pickle.dump(results, output)
                output.close()

for runtime in RUNTIMES:
    for dim in [10]:
        for skew in [0.1, 0.2, 0.5]:
            for algorithm in ALGORITHMS:
                broadcastDelay = -1
                localEpsilon = GLOBAL_ADMMlocalEpsilon
                miscStr = "" # " --useLineSearch true --miniBatchSize 10000000"
                if algorithm == "ADMM":
                    maxLocalIterations = GLOBAL_ADMM_maxLocalIterations
                    localEpsilon = GLOBAL_ADMM_localEpsilon
                    localTimeout = GLOBAL_ADMM_localTimeout
                elif algorithm == "MiniBatchADMM":
                    maxLocalIterations = GLOBAL_MiniBatchADMM_maxLocalIterations
                    localEpsilon = GLOBAL_MiniBatchADMM_localEpsilon
                    localTimeout = GLOBAL_MiniBatchADMM_localTimeout
                elif algorithm == "HOGWILD":
                    maxLocalIterations = GLOBAL_HOGWILD_maxLocalIterations
                    broadcastDelay = GLOBAL_HOGWILD_broadcastDelay
                elif algorithm == "PORKCHOP":
                    maxLocalIterations = GLOBAL_PORKCHOP_maxLocalIterations
                    broadcastDelay = GLOBAL_PORKCHOP_broadcastDelay
                    localEpsilon = GLOBAL_PORKCHOP_localEpsilon
                    localTimeout = -1
                elif algorithm == "AsyncADMM":
                    maxLocalIterations = GLOBAL_AsyncADMM_maxLocalIterations
                    broadcastDelay = GLOBAL_AsyncADMM_broadcastDelay
                

                results += runTest(runtime,
                                   algorithm,
                                   "cloud",
                                   cloudPartitionSkew = skew,
                                   cloudDim = dim,
                                   regParam = 1000,
                                   ADMMmaxLocalIterations = maxLocalIterations,
                                   ADMMlocalEpsilon = localEpsilon,
                                   broadcastDelay = broadcastDelay,
                                   miscStr = miscStr,
                                   localTimeout = localTimeout)

                output = open(PICKLED_OUTPUT, 'wb')
                pickle.dump(results, output)
                output.close()


# for runtime in RUNTIMES:
#     for dim in [10]:
#         for skew in [0.0, 0.1]:
#             for algorithm in ALGORITHMS:
#                 broadcastDelay = -1
#                 localEpsilon = GLOBAL_ADMMlocalEpsilon
#                 if algorithm == "ADMM":
#                     maxLocalIterations = GLOBAL_ADMM_maxLocalIterations
#                     localEpsilon = GLOBAL_ADMM_localEpsilon
#                 elif algorithm == "MiniBatchADMM":
#                     maxLocalIterations = GLOBAL_MiniBatchADMM_maxLocalIterations
#                     localEpsilon = GLOBAL_MiniBatchADMM_localEpsilon
#                 elif algorithm == "HOGWILD":
#                     maxLocalIterations = GLOBAL_HOGWILD_maxLocalIterations
#                     broadcastDelay = GLOBAL_HOGWILD_broadcastDelay                    
#                 elif algorithm == "PORKCHOP":
#                     maxLocalIterations = GLOBAL_PORKCHOP_maxLocalIterations
#                     broadcastDelay = GLOBAL_PORKCHOP_broadcastDelay
#                 elif algorithm == "AsyncADMM":
#                     maxLocalIterations = GLOBAL_AsyncADMM_maxLocalIterations
#                     broadcastDelay = GLOBAL_AsyncADMM_broadcastDelay

#                 results += runTest(runtime,
#                                    algorithm,
#                                    "cloud",
#                                    cloudPartitionSkew = skew,
#                                    cloudDim = dim,
#                                    ADMMmaxLocalIterations = maxLocalIterations,
#                                    ADMMlocalEpsilon = localEpsilon,
#                                    broadcastDelay = broadcastDelay)

#                 output = open(PICKLED_OUTPUT, 'wb')
#                 pickle.dump(results, output)
#                 output.close()


## END OF EXPERIMENT RUNS

# display the results
print results[0].keys()
for r in results:
    print [r[k] for k in r if k is not "line"]
    
