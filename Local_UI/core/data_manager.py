import pandas as pd
import os
import matplotlib.pyplot as plt
from tqdm import tqdm
import datetime
from PyQt5.QtCore import QObject, pyqtSignal


def load_parquet_or_csv (path_ : str, verbose : bool = False) -> pd.DataFrame :
    """
    Load the parquet or csv file and return the dataframe.

    Args:
        path (str): the path to the parquet or csv file
    Returns:
        pd.DataFrame: the dataframe loaded
    """
    try :
        os.path.exists(path_)
    except FileNotFoundError :
        raise ValueError (f"The file {path_} doesn't exist")
    
    if path_.endswith(".parquet"):
        df = pd.read_parquet(path_, engine='pyarrow')
    elif path_.endswith(".csv"):
        df = pd.read_csv(path_)
    else :
        raise ValueError (f"The file {path_} is not a parquet or csv file")

    if verbose :
        print(f"    The file {path_.split(os.sep)[-1]} has been loaded successfully")
    return df          


def cut_accelero_data (accelero_data_ : pd.DataFrame, lower_date:pd.DatetimeIndex = 0, upper_date : pd.DatetimeIndex = 0) -> pd.DataFrame:
    """
    Cut the accelerometer data for a specific time range

    Args:
        accelero_data_ (pd.DataFrame): the accelerometer data
        lower_date (pd.DatetimeIndex): the lower limit date to cut the accelerometer to
        upper_date (pd.DatetimeIndex): the upper limit date to cut the accelerometer to
        
    Returns:
        pd.DataFrame: the cut accelerometer data
    """
    accelero_data = accelero_data_.copy()
    short_accelero_data = accelero_data[accelero_data["relative_DateTime"] < upper_date]
    if short_accelero_data.empty :
        short_accelero_data_2 = accelero_data[accelero_data["relative_DateTime"] > lower_date]
        short_accelero_data_2 = short_accelero_data_2[short_accelero_data_2["relative_DateTime"] < upper_date]
        return short_accelero_data_2
    
    else :
        short_accelero_data = short_accelero_data[short_accelero_data["relative_DateTime"] > lower_date]
        return short_accelero_data
    


def get_accelero_id_from_parquet_or_csv_files (path_parquet_or_csv: str, only_id : str = False) -> str :
    """
    Retrieve the id of the accelerometer from the path.

    Args:
        path_parquet_or_csv (str): the path to the accelerometer data
        only_id (bool, optional): if True, only the id is returned. Defaults to False.
    Returns:
        str: the id of the accelerometer
    """
    
    if path_parquet_or_csv.endswith(".parquet") or path_parquet_or_csv.endswith(".csv") :
        nom_parquet = path_parquet_or_csv.split(os.sep)[-1]
        id_accelero_long = nom_parquet.split("_")[1]
        if only_id :
            id_accelero = id_accelero_long[-4:]
            return id_accelero
        else :
            return id_accelero_long
    else :
        raise ValueError(f"The file {path_parquet_or_csv} is not a parquet nor a csv")


def plot_multiple_rssi (all_rssi_data : dict, accel_to_plot_ids : list[str], 
                                lower_date:pd.DatetimeIndex = 0, upper_date : pd.DatetimeIndex = 0) :
    """
    Plot multiple accelerometers data
    Args:
        all_rssi_data (dict): the datastructure containing all the accelerometer data with the accelerometer id as key
        accel_to_plot_ids (list[str]): the list of the accelerometers ids to plot
        lower_date (pd.DatetimeIndex, optional): the lower limit date to plot. Defaults to 0.
        upper_date (pd.DatetimeIndex, optional): the upper limit date to plot. Defaults to 0.
    
    Returns:
        plot
    """
    plt.close("all")
    fig = plt.figure(figsize=(14, 8))
    plt.margins(x=0)

    for sensor_id, rssi_data_ in tqdm(all_rssi_data.items(), desc="Plotting RSSI"):
        if sensor_id not in accel_to_plot_ids :
            continue
        rssi_data_1 = rssi_data_.copy()
        if lower_date == 0 or upper_date == 0 :
            short_rssi_data = rssi_data_1.copy()
        else :
            short_rssi_data = cut_accelero_data(rssi_data_1, lower_date, upper_date)
            
        plt.scatter(short_rssi_data["relative_DateTime"], short_rssi_data["RSSI"], alpha=0.4, label=sensor_id)
        
    plt.legend(loc="upper right")
    plt.grid()
    if lower_date == 0 or upper_date == 0 :
        plt.title("RSSI data for the whole time range for the accelerometers " + str(accel_to_plot_ids))
    else : 
        plt.title("RSSI data from " + str(lower_date) + " to " + str(lower_date) + " for the accelerometers " + str(accel_to_plot_ids))
    plt.xlabel("relative_DateTime")
    plt.ylabel("RSSI (dbm)")
    plt.plot()
    return plt.show()


def plot_single_sensor_separate_rssi (single_rssi_data : pd.DataFrame, accelero_id_to_plot : str, 
                                    accel_to_plot_ids : list[str],
                                    lower_date:pd.DatetimeIndex = 0, upper_date : pd.DatetimeIndex = 0) :
    """
    Plot multiple accelerometers data
    Args:
        single_rssi_data (pd.DataFrame): the RSSI data for a single sensor
        accel_to_plot_ids (list[str]): the list of the accelerometers ids to plot
        lower_date (pd.DatetimeIndex, optional): the lower limit date to plot. Defaults to 0.
        upper_date (pd.DatetimeIndex, optional): the upper limit date to plot. Defaults to 0.
    
    Returns:
        plot
    """
    plt.close("all")
    fig = plt.figure(figsize=(14, 8))
    plt.margins(x=0)
    
    rssi_data_1 = single_rssi_data.copy()
    if lower_date == 0 or upper_date == 0 :
        short_rssi_data = rssi_data_1.copy()
    else :
        short_rssi_data = cut_accelero_data(rssi_data_1, lower_date, upper_date)

    all_sensor_detected = short_rssi_data["accelero_id"].unique()
    all_sensor_detected = [sensor_id for sensor_id in all_sensor_detected if sensor_id in accel_to_plot_ids] # selecting the sensors to plot

    all_separated_rssi_data = {}
    for sensor_id in all_sensor_detected :
        all_separated_rssi_data[sensor_id] = short_rssi_data[short_rssi_data["accelero_id"] == sensor_id].copy()
    
    for sensor_id, rssi_data_ in tqdm(all_separated_rssi_data.items(), desc="Plotting RSSI"):
        plt.scatter(rssi_data_["relative_DateTime"], rssi_data_["RSSI"], alpha=0.4, label=sensor_id)
        
    plt.legend(loc="upper right")
    plt.grid()
    if lower_date == 0 or upper_date == 0 :
        plt.title(f"RSSI data for the whole time range for the accelerometer {accelero_id_to_plot}")
    else : 
        plt.title(f"RSSI data from {str(lower_date)} to {str(upper_date)} for the accelerometer {str(accelero_id_to_plot)}")
    plt.xlabel("relative_DateTime")
    plt.ylabel("RSSI (dbm)")
    plt.plot()
    return plt.show()


class DataManager(QObject):
    """
    Minimal placeholder for DataManager.
    """
    
    data_loaded_signal = pyqtSignal(object)
    data_updated_signal = pyqtSignal(object, float)
    
    def __init__(self):
        super().__init__()
        self.rssi_data = None
        self.start_datetime = None
        self.accelero_ids = []
    
    def load_data(self, file_path):
        """Stub method for API compatibility"""
        print(f"DataManager.load_data called but functionality removed")
        return False
    
    def synchronize_data(self, video_position_ms):
        """Stub method for API compatibility"""
        return None
    
    def update_data_for_position(self, video_position_ms):
        """Stub method for API compatibility"""
        return None
    
    def get_available_sensor_ids(self):
        """Stub method for API compatibility"""
        return []