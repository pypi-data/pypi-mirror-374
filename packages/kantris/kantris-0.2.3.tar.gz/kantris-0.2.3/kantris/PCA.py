import traceback
import requests
import numpy as np


from .DataManipulation import Array, DataManipulation
from .plotter import Plotter
from .Basics import Geometry
from sklearn.decomposition import PCA as skPCA


class PCA:
    VERSION = 'Kantris.PCA: 0.2.0'
    def PCA(Data: np.ndarray, PCAConfig: dict=None, PlotConfig: dict=None,):
        try:
            if PCAConfig is None:
                PCAConfig = {}
            if PlotConfig is None:
                PlotConfig = {}

            #Default Variables
            axis_default = (None, None)


            stddev = PCAConfig.get("stddev", None)
            if stddev:
                Data = Array.RemoveOutliers(Data, stddev)
            
            if PCAConfig.get("standardise", False):
                Data = Array.Normalise(Data, mode="standard", col=[i for i in range(0, Data.shape[1])])
                axis_default = (None, "x")  


            n_features = Data.shape[1]
            pca = skPCA(n_components=n_features)
            pca.fit(Data)


            result = {
                "principal_components": pca.components_,
                "explained_variance": pca.explained_variance_,
                "explained_variance_ratio": pca.explained_variance_ratio_,
                "singular_values": pca.singular_values_,
                "mean_vector": pca.mean_,
            }

            PLOTTER_CONFIG = {
                "plot": {
                    "plotsize": PlotConfig.get("plotsize", (8,8)),
                    "filename": PlotConfig.get("filename", None),
                    "title": PlotConfig.get("title", "PCA Plot"),
                },
                "x-axis": {
                    "label": PlotConfig.get("x-label", "x-axis"),
                    "limits": PlotConfig.get("x-limits", axis_default[0])
                },
                "y-axis": {
                    "label": PlotConfig.get("y-label", "y-axis"),
                    "limits": PlotConfig.get("y-limits", axis_default[1])
                }
            }
            GRAPHS = [
                {
                    "data": Plotter.Scatter().Points(Data),
                    "marker": Plotter.Marker().Size(20).Color("dodgerblue").Alpha(0.3)
                }
            ]
            OBJECTS = [
                Plotter.Objects.Vector(result['principal_components'][0][0:2]).Origin(result['mean_vector'][0], result['mean_vector'][1]).Length(np.sqrt(result['explained_variance'][0])).Width(10).HeadLength(5).HeadWidth(4).Color("crimson").Alpha(1).Mirror(),
                Plotter.Objects.Vector(result['principal_components'][1][0:2]).Origin(result['mean_vector'][0], result['mean_vector'][1]).Length(np.sqrt(result['explained_variance'][1])).Width(10).HeadLength(5).HeadWidth(4).Color("crimson").Alpha(1).Mirror(),
            ]

            result["plot"] = Plotter.Plot(PLOTTER_CONFIG, GRAPHS, OBJECTS)


            ### HAUPTKOMPONENTEN ANSICHT
            Data = Geometry.project_to_plane(Data, result['principal_components'][0:2].T)
            PLOTTER_CONFIG = {
                "plot": {
                    "plotsize": PlotConfig.get("plotsize", (8,8)),
                    "filename": PlotConfig.get("filename", None),
                    "title": PlotConfig.get("title", "PCA Plot (1. und 2. Hauptkomponente)"),
                },
                "x-axis": {
                    "label": Plotter.Label("1. Hauptkomponente").Unit(f"{result['explained_variance_ratio'][0]*100:.2f}" + r'\%,\ ' + f"L={np.sqrt(result['explained_variance'][0]):.2f}"),
                    "limits": axis_default[0],
                },
                "y-axis": {
                    "label": Plotter.Label("2. Hauptkomponente").Unit(f"{result['explained_variance_ratio'][1]*100:.2f}" + r'\%,\ ' + f"L={np.sqrt(result['explained_variance'][1]):.2f}"),
                    "limits": axis_default[1],
                }
            }
            GRAPHS = [
                {
                    "data": Plotter.Scatter().Points(Data),
                    "marker": Plotter.Marker().Size(20).Color("dodgerblue").Alpha(0.3)
                }
            ]

            mean_x, mean_y = np.mean(Data[:, 0]), np.mean(Data[:, 1])
            OBJECTS = [
                Plotter.Objects.Vector(np.array([1,0])).Origin(mean_x, mean_y).Length(np.sqrt(result['explained_variance'][0])).Width(10).HeadLength(5).HeadWidth(4).Color("crimson").Alpha(1).Mirror(),
                Plotter.Objects.Vector(np.array([0,1])).Origin(mean_x, mean_y).Length(np.sqrt(result['explained_variance'][1])).Width(10).HeadLength(5).HeadWidth(4).Color("crimson").Alpha(1).Mirror(),
            ]
            result["plot-primary-components"] = Plotter.Plot(PLOTTER_CONFIG, GRAPHS, OBJECTS)

            return result
        except Exception as err:
            # Gibt den kompletten Traceback auf stderr aus, inkl. Dateiname und Zeilennummer
            traceback.print_exc()
            return {}


class PCA_Signalum:
    VERSION = 'Kantris.PCA_Signalum: 0.0.1'
    def PCA(Dataqueues: list[int, str], PCAConfig: dict=None, PlotConfig: dict=None, host=None):
        if PCAConfig is None:
            PCAConfig = {}
        if PlotConfig is None:
            PlotConfig = {}
                   

        dataqueue_data = {}
        for dataqueue_id in Dataqueues:
            ctx = DataqueueQuery(host, dataqueue_id)
            data = ctx.get("data")
            data = np.array(data)
            fields = ctx.get("information").get("fields")
            if fields[0] == "timestamp":
                timestamp_index = 0
                value_index = 1
            else :
                timestamp_index = 1
                value_index = 0
            dataqueue_data[dataqueue_id] = {
                "data": data,
                "t_i": timestamp_index,
                "v_i": value_index,
                "name": ctx.get("information").get("dataqueue")
            }



        timestamps = Array.Col(dataqueue_data.get(Dataqueues[0])["data"], dataqueue_data.get(Dataqueues[0])["t_i"])

        for key in Dataqueues:
            if key == Dataqueues[0]:
                data_for_PCA = Array.Merge(Array.Col(dataqueue_data.get(key)["data"], dataqueue_data.get(key)["v_i"]))
            else :
                interpolated_data = DataManipulation.LinearInterpol(timestamps, Array.Col(dataqueue_data.get(key)["data"], dataqueue_data.get(key)["t_i"]), Array.Col(dataqueue_data.get(key)["data"], dataqueue_data.get(key)["v_i"]))
                data_for_PCA = Array.Merge(data_for_PCA, interpolated_data)

        PlotConfig["x-label"] = Plotter.Label(dataqueue_data.get(Dataqueues[0])["name"])
        PlotConfig["y-label"] = Plotter.Label(dataqueue_data.get(Dataqueues[1])["name"])


        pca_result = PCA.PCA(data_for_PCA, PCAConfig, PlotConfig)
        return pca_result
    


def DataqueueQuery(host, dataqueue_id: int|str) -> dict:
    """
    Does a Default Query for a Dataqueue
    """
    if host is None:
        host = "http://localhost:8080"
    dataqueue_data = DataqueueObjectQuery(host, dataqueue_id).get("object")
    if isinstance(dataqueue_id, int):
        mode = "dataqueue_id"
    elif isinstance(dataqueue_id, str):
        mode = "dataqueue_uuid"
    RequestBody = {
        "context": {
            mode: dataqueue_id,
            "fields": list(dataqueue_data.get("fields").keys()),
            "order": {
                "asc": "timestamp"
            },
        }
    }

    response = requests.post(host + "/signalum/dataqueue/query", json=RequestBody)
    response.raise_for_status()
    return response.json()




def DataqueueObjectQuery(host, dataqueue_id: int|str) -> dict:
    if host is None:
        host = f"http://localhost:8080"
    response = requests.get(host + f"/signalum/objects/query/dataqueues/{dataqueue_id}")
    response.raise_for_status()
    return response.json()