from abc import ABC, abstractmethod
from typing import List, Dict, Type, Tuple, Union

class TimeSeries(ABC):
    """
    Base abstract class for all time series with simple sequential tagging
    """
    _time_series = {}  # Class-level dictionary to track all time series

    def __init__(self, series_type: str):
        """
        Initialize a new time series with a sequential tag
        
        Args:
            series_type (str): The type of time series (e.g., 'Constant', 'Linear')
        """
        self.tag = len(TimeSeries._time_series) + 1
        self.series_type = series_type
        
        # Register this time series in the class-level tracking dictionary
        self._time_series[self.tag] = self

    @classmethod
    def get_time_series(cls, tag: int) -> 'TimeSeries':
        """
        Retrieve a specific time series by its tag.
        
        Args:
            tag (int): The tag of the time series
        
        Returns:
            TimeSeries: The time series with the specified tag
        
        Raises:
            KeyError: If no time series with the given tag exists
        """
        if tag not in cls._time_series:
            raise KeyError(f"No time series found with tag {tag}")
        return cls._time_series[tag]

    @classmethod
    def remove_time_series(cls, tag: int) -> None:
        """
        Delete a time series by its tag and re-tag all remaining series sequentially.
        
        Args:
            tag (int): The tag of the time series to delete
        """
        if tag in cls._time_series:
            del cls._time_series[tag]
            # Re-tag all remaining time series sequentially
            cls._reassign_tags()

    @classmethod
    def _reassign_tags(cls) -> None:
        """
        Reassign tags to all time series sequentially starting from 1.
        """
        new_time_series = {}
        for idx, series in enumerate(sorted(cls._time_series.values(), key=lambda ts: ts.tag), start=1):
            series.tag = idx
            new_time_series[idx] = series
        cls._time_series = new_time_series

    @classmethod
    def get_all_time_series(cls) -> Dict[int, 'TimeSeries']:
        """
        Retrieve all created time series.
        
        Returns:
            Dict[int, TimeSeries]: A dictionary of all time series, keyed by their tags
        """
        return cls._time_series.copy()


    @abstractmethod
    def to_tcl(self) -> str:
        """
        Convert the time series to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        pass

    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """
        Get the parameters defining this time series
        
        Returns:
            Dict[str, float]: Dictionary of parameter names and explanations
        """
        pass

    @abstractmethod
    def get_values(self) -> Dict[str, Union[str, int, float, list]]:
        """
        Get the parameters defining this time series
        """
        pass

    @abstractmethod
    def update_values(self, **kwargs) -> None:
        """
        Update the values of the time series
        
        Args:
            **kwargs: Parameters for time series initialization
        """
        pass

    @staticmethod
    @abstractmethod
    def validate(**kwargs) -> Dict[str, Union[str, list, float, int]]:
        """
        Validate the input parameters for creating a TimeSeries
        """
        pass



class ConstantTimeSeries(TimeSeries):
    """
    TimeSeries object with constant load factor
    """
    def __init__(self, **kwargs):
        """
        Initialize a Constant TimeSeries
        
        Args:
            factor (float): The constant load factor value
            tag (int, optional): Specific tag to use. If None, auto-assigned.
        """
        kwargs = self.validate(**kwargs)
        super().__init__('Constant')
        self.factor = kwargs["factor"]


    def to_tcl(self) -> str:
        """
        Convert the time series to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"timeSeries Constant {self.tag} -factor {self.factor}"

    
    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """
        Get the parameters defining this time series
        
        Returns:
            List[Tuple[str, str]]: List of parameter names and explanations
        """
        return [("factor", "The constant load factor value (optional , default: 1.0)")]
    
    @staticmethod
    def validate(**kwargs)-> Dict[str, Union[str, list, float, int]]:
        """
        Validate the input parameters for creating a Constant TimeSeries
        
        Args:
            **kwargs: Parameters for time series initialization
        
        Returns:
            Dict[str, Union[str, list, float, int]]: Dictionary of parameter names and values
        """
        factor = kwargs.get("factor", 1.0)
        factor = float(factor)
        # check if factor is a number
        if not isinstance(factor, (int, float)):
            raise ValueError("factor must be a number")
        return {"factor": factor}
    
    def get_values(self) -> Dict[str, Union[str, int, float, list]]:
        """
        Get the parameters defining this time series
        """
        return {"factor": self.factor}
    
    def update_values(self, **kwargs) -> None:
        """
        Update the values of the time series
        
        Args:
            **kwargs: Parameters for time series initialization
        """
        kwargs = self.validate(**kwargs)
        self.factor = kwargs["factor"]


class LinearTimeSeries(TimeSeries):
    """
    TimeSeries object with linear load factor
    """
    def __init__(self, **kwargs):
        """
        Initialize a Linear TimeSeries
        
        Args:
            factor (float): The linear load factor scale
            tag (int, optional): Specific tag to use. If None, auto-assigned.
        """
        kwargs = self.validate(**kwargs)
        super().__init__('Linear')
        self.factor = kwargs["factor"]

    def to_tcl(self) -> str:
        """
        Convert the time series to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"timeSeries Linear {self.tag} -factor {self.factor}"

    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """
        Get the parameters defining this time series
        
        Returns:
            List[Tuple[str, str]]: List of parameter names and explanations
        """
        return [("factor", "The linear load factor scale (optional, default: 1.0)")]
    
    @staticmethod
    def validate(**kwargs) -> Dict[str, Union[str, list, float, int]]:
        """
        Validate the input parameters for creating a Linear TimeSeries
        
        Args:
            **kwargs: Parameters for time series initialization
        
        Returns:
            Dict[str, Union[str, list, float, int]]: Dictionary of parameter names and values
        """
        factor = kwargs.get("factor", 1.0)
        factor = float(factor)
        if not isinstance(factor, (int, float)):
            raise ValueError("factor must be a number")
        return {"factor": factor}
    
    def get_values(self) -> Dict[str, Union[str, int, float, list]]:
        """
        Get the parameters defining this time series
        """
        return {"factor": self.factor}
    
    def update_values(self, **kwargs) -> None:
        """
        Update the values of the time series
        
        Args:
            **kwargs: Parameters for time series initialization
        """
        kwargs = self.validate(**kwargs)
        self.factor = kwargs["factor"]


class TrigTimeSeries(TimeSeries):
    """
    TimeSeries object with sinusoidal load factor
    """
    def __init__(self, **kwargs):
        """
        Initialize a Trig TimeSeries
        
        Args:
            tStart (float): Start time of time series
            tEnd (float): End time of time series
            period (float): Period of sine wave
            factor (float): Load factor amplitude
            shift (float): Phase shift in radians
        """
        kwargs = self.validate(**kwargs)
        super().__init__('Trig')
        self.tStart = kwargs["tStart"]
        self.tEnd = kwargs["tEnd"]
        self.period = kwargs["period"]
        self.factor = kwargs["factor"]
        self.shift = kwargs["shift"]

    def to_tcl(self) -> str:
        """
        Convert the time series to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return (f"timeSeries Trig {self.tag} "
                f"{self.tStart} {self.tEnd} {self.period} "
                f"-factor {self.factor} -shift {self.shift}")

    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """
        Get the parameters defining this time series
        
        Returns:
            List[Tuple[str, str]]: List of parameter names and explanations
        """
        return [
            ("tStart", "Start time of time series (optional, default: 0.0)"),
            ("tEnd", "End time of time series (optional, default: 1.0)"),
            ("period", "Period of sine wave (optional, default: 1.0)"),
            ("factor", "Load factor amplitude (optional, default: 1.0)"),
            ("shift", "Phase shift in radians (optional, default: 0.0)"),
        ]
    
    @staticmethod
    def validate(**kwargs) -> Dict[str, Union[str, list, float, int]]:
        """
        Validate the input parameters for creating a Trig TimeSeries
        
        Args:
            **kwargs: Parameters for time series initialization
        
        Returns:
            Dict[str, Union[str, list, float, int]]: Dictionary of parameter names and values
        """
        tStart = kwargs.get("tStart", 0.0)
        tEnd = kwargs.get("tEnd", 1.0)
        period = kwargs.get("period", 1.0)
        factor = kwargs.get("factor", 1.0)
        shift = kwargs.get("shift", 0.0)

        try:
            tStart = float(tStart)
        except ValueError:
            raise ValueError("tStart must be a number")
        
        try:
            tEnd = float(tEnd)
        except ValueError:
            raise ValueError("tEnd must be a number")
        
        try:
            period = float(period)
        except ValueError:
            raise ValueError("period must be a number")
        
        try:
            factor = float(factor)
        except ValueError:
            raise ValueError("factor must be a number")
        
        try:
            shift = float(shift)
        except ValueError:
            raise ValueError("shift must be a number")
        
        if tStart >= tEnd:
            raise ValueError("tStart must be less than tEnd")
        
        if period <= 0:
            raise ValueError("period must be greater than 0")
        
        return {
            "tStart": tStart,
            "tEnd": tEnd,
            "period": period,
            "factor": factor,
            "shift": shift,
        }
    
    def get_values(self) -> Dict[str, Union[str, int, float, list]]:
        """
        Get the parameters defining this time series
        """
        return {
            "tStart": self.tStart,
            "tEnd": self.tEnd,
            "period": self.period,
            "factor": self.factor,
            "shift": self.shift,
        }
    
    def update_values(self, **kwargs) -> None:
        """
        Update the values of the time series
        
        Args:
            **kwargs: Parameters for time series initialization
        """
        kwargs = self.validate(**kwargs)
        self.tStart = kwargs["tStart"]
        self.tEnd = kwargs["tEnd"]
        self.period = kwargs["period"]
        self.factor = kwargs["factor"]
        self.shift = kwargs["shift"]

class RampTimeSeries(TimeSeries):
    """
    TimeSeries object with ramped load factor from tStart to tEnd
    """
    def __init__(self, **kwargs):
        """
        Initialize a Ramp TimeSeries
        
        Args:
            tStart (float): Start time of ramp
            tRamp (float): Length of time to perform the ramp
            smoothness (float): Smoothness parameter (optional, default: 0.0)
            offset (float): Vertical offset amount (optional, default: 0.0)
            cFactor (float): Load factor scale factor (optional, default: 1.0)
        """
        kwargs = self.validate(**kwargs)
        super().__init__('Ramp')
        self.tStart = kwargs["tStart"]
        self.tRamp = kwargs["tRamp"]
        self.smoothness = kwargs["smoothness"]
        self.offset = kwargs["offset"]
        self.cFactor = kwargs["cFactor"]

    def to_tcl(self) -> str:
        """
        Convert the time series to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        cmd = f"timeSeries Ramp {self.tag} {self.tStart} {self.tRamp}"
        cmd += f" -smooth {self.smoothness}"
        cmd += f" -offset {self.offset}"
        cmd += f" -factor {self.cFactor}"
        return cmd

    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """
        Get the parameters defining this time series
        
        Returns:
            List[Tuple[str, str]]: List of parameter names and explanations
        """
        return [
            ("tStart", "Start time of ramp (optional, default: 0.0)"),
            ("tRamp", "Length of time to perform the ramp (optional, default: 1.0)"),
            ("smoothness", "Smoothness parameter (optional, default: 0.0)"),
            ("offset", "Vertical offset amount (optional, default: 0.0)"),
            ("cFactor", "Load factor scale factor (optional, default: 1.0)")
        ]
    
    @staticmethod
    def validate(**kwargs) -> Dict[str, Union[str, list, float, int]]:
        """
        Validate the input parameters for creating a Ramp TimeSeries
        
        Args:
            **kwargs: Parameters for time series initialization
        
        Returns:
            Dict[str, Union[str, list, float, int]]: Dictionary of parameter names and values
        """
        tStart = kwargs.get("tStart", 0.0)
        tRamp = kwargs.get("tRamp", 1.0)
        smoothness = kwargs.get("smoothness", 0.0)
        offset = kwargs.get("offset", 0.0)
        cFactor = kwargs.get("cFactor", 1.0)

        try :
            tStart = float(tStart)
        except ValueError:
            raise ValueError("tStart must be a number")
        
        try:
            tRamp = float(tRamp)
        except ValueError:
            raise ValueError("tRamp must be a number")
        
        try:
            smoothness = float(smoothness)
        except ValueError:
            raise ValueError("smoothness must be a number")
        
        try:
            offset = float(offset)
        except ValueError:
            raise ValueError("offset must be a number")
        
        try:
            cFactor = float(cFactor)
        except ValueError:
            raise ValueError("cFactor must be a number")
        
        
        if not (0 <= smoothness <= 1):
            raise ValueError("smoothness must be between 0 and 1")
        
        return {
            "tStart": tStart,
            "tRamp": tRamp,
            "smoothness": smoothness,
            "offset": offset,
            "cFactor": cFactor
        }
    
    def get_values(self) -> Dict[str, Union[str, int, float, list]]:
        """
        Get the parameters defining this time series
        """
        return {
            "tStart": self.tStart,
            "tRamp": self.tRamp,
            "smoothness": self.smoothness,
            "offset": self.offset,
            "cFactor": self.cFactor
        }
    
    def update_values(self, **kwargs) -> None:
        """
        Update the values of the time series
        
        Args:
            **kwargs: Parameters for time series initialization
        """
        kwargs = self.validate(**kwargs)
        self.tStart = kwargs["tStart"]
        self.tRamp = kwargs["tRamp"]
        self.smoothness = kwargs["smoothness"]
        self.offset = kwargs["offset"]
        self.cFactor = kwargs["cFactor"]



class TriangularTimeSeries(TimeSeries):
    """
    TimeSeries object with triangular load pattern
    """
    def __init__(self, **kwargs):
        """
        Initialize a Triangular TimeSeries
        
        Args:
            tStart (float): Start time of series
            tEnd (float): End time of series
            period (float): Period of triangular wave
            factor (float): Load factor amplitude
            shift (float): Phase shift
        """
        kwargs = self.validate(**kwargs)
        super().__init__('Triangular')
        self.tStart = kwargs["tStart"]
        self.tEnd = kwargs["tEnd"]
        self.period = kwargs["period"]
        self.factor = kwargs["factor"]
        self.shift = kwargs["shift"]

    def to_tcl(self) -> str:
        """
        Convert the time series to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return (f"timeSeries Triangular {self.tag} "
                f"{self.tStart} {self.tEnd} {self.period} "
                f"-factor {self.factor} -shift {self.shift}")

    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """
        Get the parameters defining this time series
        
        Returns:
            List[Tuple[str, str]]: List of parameter names and explanations
        """
        return [
            ("tStart", "Start time of series (optional, default: 0.0)"),
            ("tEnd", "End time of series (optional, default: 1.0)"),
            ("period", "Period of triangular wave (optional, default: 1.0)"),
            ("factor", "Load factor amplitude (optional, default: 1.0)"),
            ("shift", "Phase shift (optional, default: 0.0)")
        ]
    
    @staticmethod
    def validate(**kwargs) -> Dict[str, Union[str, list, float, int]]:
        """
        Validate the input parameters for creating a Triangular TimeSeries
        
        Args:
            **kwargs: Parameters for time series initialization
        
        Returns:
            Dict[str, Union[str, list, float, int]]: Dictionary of parameter names and values
        """
        tStart = kwargs.get("tStart", 0.0)
        tEnd = kwargs.get("tEnd", 1.0)
        period = kwargs.get("period", 1.0)
        factor = kwargs.get("factor", 1.0)
        shift = kwargs.get("shift", 0.0)

        count = 0
        try:
            tStart = float(tStart); count += 1
            tEnd = float(tEnd); count += 1
            period = float(period); count += 1
            factor = float(factor); count += 1
            shift = float(shift); count += 1
        except ValueError:
            if count == 0:
                raise ValueError("tStart must be a number")
            elif count == 1:
                raise ValueError("tEnd must be a number")
            elif count == 2:
                raise ValueError("period must be a number")
            elif count == 3:
                raise ValueError("factor must be a number")
            elif count == 4:
                raise ValueError("shift must be a number")
            
        
        if tStart >= tEnd:
            raise ValueError("tStart must be less than tEnd")
        
        if period <= 0:
            raise ValueError("period must be greater than 0")
        
        return {
            "tStart": tStart,
            "tEnd": tEnd,
            "period": period,
            "factor": factor,
            "shift": shift
        }
    
    def get_values(self) -> Dict[str, Union[str, int, float, list]]:
        """
        Get the parameters defining this time series
        """
        return {
            "tStart": self.tStart,
            "tEnd": self.tEnd,
            "period": self.period,
            "factor": self.factor,
            "shift": self.shift
        }
    
    def update_values(self, **kwargs) -> None:
        """
        Update the values of the time series
        
        Args:
            **kwargs: Parameters for time series initialization
        """
        kwargs = self.validate(**kwargs)
        self.tStart = kwargs["tStart"]
        self.tEnd = kwargs["tEnd"]
        self.period = kwargs["period"]
        self.factor = kwargs["factor"]
        self.shift = kwargs["shift"]


class RectangularTimeSeries(TimeSeries):
    """
    TimeSeries object with rectangular (step) load pattern
    """
    def __init__(self, **kwargs):
        """
        Initialize a Rectangular TimeSeries
        
        Args:
            tStart (float): Start time of series
            tEnd (float): End time of series
            factor (float): Load factor amplitude
        """
        kwargs = self.validate(**kwargs)
        super().__init__('Rectangular')
        self.tStart = kwargs["tStart"]
        self.tEnd = kwargs["tEnd"]
        self.factor = kwargs["factor"]
        self.period = kwargs["period"]
        self.shift = kwargs["shift"]

    def to_tcl(self) -> str:
        """
        Convert the time series to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return (f"timeSeries Rectangular {self.tag} "
                f"{self.tStart} {self.tEnd}  {self.period} -shift {self.shift} -factor {self.factor}")

    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """
        Get the parameters defining this time series
        
        Returns:
            List[Tuple[str, str]]: List of parameter names and explanations
        """
        return [
            ("tStart", "Start time of series (optional, default: 0.0)"),
            ("tEnd", "End time of series (optional, default: 1.0)"),
            ("factor", "Load factor amplitude (optional, default: 1.0)"),
            ("period", "Period of rectangular wave (optional, default: 0.0)"),
            ("shift", "Phase shift (optional, default: 0.0)")
        ]
    
    @staticmethod
    def validate(**kwargs) -> Dict[str, Union[str, list, float, int]]:
        """
        Validate the input parameters for creating a Rectangular TimeSeries
        
        Args:
            **kwargs: Parameters for time series initialization
        
        Returns:
            Dict[str, Union[str, list, float, int]]: Dictionary of parameter names and values
        """
        tStart = kwargs.get("tStart", 0.0)
        tEnd = kwargs.get("tEnd", 1.0)
        factor = kwargs.get("factor", 1.0)
        period = kwargs.get("period", 0.0)
        shift = kwargs.get("shift", 0.0)

        try:
            tStart = float(tStart)
        except ValueError:
            raise ValueError("tStart must be a number")
        
        try:
            tEnd = float(tEnd)
        except ValueError:
            raise ValueError("tEnd must be a number")
        
        try:
            factor = float(factor)
        except ValueError:
            raise ValueError("factor must be a number")
        

        try:
            period = float(period)
        except ValueError:
            raise ValueError("period must be a number")
        
        try:
            shift = float(shift)
        except ValueError:
            raise ValueError("shift must be a number")

        
        if tStart >= tEnd:
            raise ValueError("tStart must be less than tEnd")
        
        if period <= 0:
            raise ValueError("period must be greater than 0")
        

        
        return {
            "tStart": tStart,
            "tEnd": tEnd,
            "factor": factor
        }
    
    def get_values(self) -> Dict[str, Union[str, int, float, list]]:
        """
        Get the parameters defining this time series
        """
        return {
            "tStart": self.tStart,
            "tEnd": self.tEnd,
            "factor": self.factor,
            "period": self.period,
            "shift": self.shift
        }
    
    def update_values(self, **kwargs) -> None:
        """
        Update the values of the time series
        
        Args:
            **kwargs: Parameters for time series initialization
        """
        kwargs = self.validate(**kwargs)
        self.tStart = kwargs["tStart"]
        self.tEnd = kwargs["tEnd"]
        self.factor = kwargs["factor"]
        self.period = kwargs["period"]
        self.shift = kwargs["shift"]



class PulseTimeSeries(TimeSeries):
    """
    TimeSeries object with pulse load pattern
    """
    def __init__(self, **kwargs):
        """
        Initialize a Pulse TimeSeries
        
        Args:
            tStart (float): Start time of pulse
            tEnd (float): End time of pulse
            period (float): Period of pulse
            width (float): Width of pulse as a fraction of period
            factor (float): Load factor amplitude
            shift (float): Phase shift
        """
        kwargs = self.validate(**kwargs)
        super().__init__('Pulse')
        self.tStart = kwargs["tStart"]
        self.tEnd = kwargs["tEnd"]
        self.period = kwargs["period"]
        self.width = kwargs["width"]
        self.factor = kwargs["factor"]
        self.shift = kwargs["shift"]

    def to_tcl(self) -> str:
        """
        Convert the time series to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return (f"timeSeries Pulse {self.tag} "
                f"{self.tStart} {self.tEnd} {self.period} -width {self.width} "
                f"-factor {self.factor} -shift {self.shift}")

    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """
        Get the parameters defining this time series
        
        Returns:
            List[Tuple[str, str]]: List of parameter names and explanations
        """
        return [
            ("tStart", "Start time of pulse (optional, default: 0.0)"),
            ("tEnd", "End time of pulse (optional, default: 1.0)"),
            ("period", "Period of pulse (optional, default: 1.0)"),
            ("width", "Width of pulse as a fraction of period (optional, default: 0.5)"),
            ("factor", "Load factor amplitude (optional, default: 1.0)"),
            ("shift", "Phase shift (optional, default: 0.0)"),
        ]
    
    @staticmethod
    def validate(**kwargs) -> Dict[str, Union[str, list, float, int]]:
        """
        Validate the input parameters for creating a Pulse TimeSeries
        
        Args:
            **kwargs: Parameters for time series initialization
        
        Returns:
            Dict[str, Union[str, list, float, int]]: Dictionary of parameter names and values
        """
        tStart = kwargs.get("tStart", 0.0)
        tEnd = kwargs.get("tEnd", 1.0)
        period = kwargs.get("period", 1.0)
        width = kwargs.get("width", 0.5)
        factor = kwargs.get("factor", 1.0)
        shift = kwargs.get("shift", 0.0)


        count = 0
        try:
            tStart = float(tStart); count += 1
            tEnd = float(tEnd); count += 1
            period = float(period); count += 1
            width = float(width); count += 1
            factor = float(factor); count += 1
            shift = float(shift); count += 1
        except ValueError:
            if count == 0:
                raise ValueError("tStart must be a number")
            elif count == 1:
                raise ValueError("tEnd must be a number")
            elif count == 2:
                raise ValueError("period must be a number")
            elif count == 3:
                raise ValueError("width must be a number")
            elif count == 4:
                raise ValueError("factor must be a number")
            elif count == 5:
                raise ValueError("shift must be a number")
        
        if tStart >= tEnd:
            raise ValueError("tStart must be less than tEnd")
        
        if period <= 0:
            raise ValueError("period must be greater than 0")
        
        if width <= 0 or width >= 1:
            raise ValueError("width must be between 0 and 1")
        
        return {
            "tStart": tStart,
            "tEnd": tEnd,
            "period": period,
            "width": width,
            "factor": factor,
            "shift": shift,
        }
    
    def get_values(self) -> Dict[str, Union[str, int, float, list]]:
        """
        Get the parameters defining this time series
        """
        return {
            "tStart": self.tStart,
            "tEnd": self.tEnd,
            "period": self.period,
            "width": self.width,
            "factor": self.factor,
            "shift": self.shift,
        }
    
    def update_values(self, **kwargs) -> None:
        """
        Update the values of the time series
        
        Args:
            **kwargs: Parameters for time series initialization
        """
        kwargs = self.validate(**kwargs)
        self.tStart = kwargs["tStart"]
        self.tEnd = kwargs["tEnd"]
        self.period = kwargs["period"]
        self.width = kwargs["width"]
        self.factor = kwargs["factor"]
        self.shift = kwargs["shift"]


class PathTimeSeries(TimeSeries):
    """
    TimeSeries object that interpolates between defined time and load factor points
    """
    def __init__(self, **kwargs):
        """
        Initialize a Path TimeSeries
        
        Args:
            dt (float): Time increment for path
            values (list): List of force values
            filePath (str): Path to file containing force values
            factor (float): Scale factor for force values
            useLast (bool): Use last force value beyond the last time point if true
            prependZero (bool): Prepend a zero value at the start
            startTime (float): Start time of the time series
            time (list): List of time points
            fileTime (str): Path to file containing time points
        """
        kwargs = self.validate(**kwargs)
        super().__init__('Path')
        self.dt = kwargs.get("dt")
        self.values = kwargs.get("values")
        self.filePath = kwargs.get("filePath")
        self.factor = kwargs["factor"]
        self.useLast = kwargs["useLast"]
        self.prependZero = kwargs["prependZero"]
        self.startTime = kwargs["startTime"]
        self.time = kwargs.get("time")
        self.fileTime = kwargs.get("fileTime")

    def to_tcl(self) -> str:
        """
        Convert the time series to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        cmd = f"timeSeries Path {self.tag}"
        if self.dt is not None:
            cmd += f" -dt {self.dt}"
        if self.filePath:
            cmd += f" -filePath {self.filePath}"
        elif self.values:
            values_str = " ".join(map(str, self.values))
            cmd += f" -values {{{values_str}}}"
        if self.time:
            time_str = " ".join(map(str, self.time))
            cmd += f" -time {{{time_str}}}"
        if self.fileTime:
            cmd += f" -fileTime {self.fileTime}"
        if self.factor != 1.0:
            cmd += f" -factor {self.factor}"
        if self.useLast:
            cmd += " -useLast"
        if self.prependZero:
            cmd += " -prependZero"
        if self.startTime != 0.0:
            cmd += f" -startTime {self.startTime}"
        return cmd

    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """
        Get the parameters defining this time series
        
        Returns:
            List[Tuple[str, str]]: List of parameter names and explanations
        """
        return [
            ("dt", "Time increment for path"),
            ("time", "List of time points (optional)"),
            ("fileTime", "Path to file containing time points (optional)"),
            ("values", "List of comma separated force values (optional if using filePath)"),
            ("filePath", "Path to file containing force values (optional)"),
            ("factor", "Scale factor for force values (optional, default: 1.0)"),
            ("useLast", "Use last force value beyond the last time point if true (optional, default: False)"),
            ("prependZero", "Prepend a zero value at the start (optional, default: False)"),
            ("startTime", "Start time of the time series (optional, default: 0.0)"),
        ]
    
    @staticmethod
    def validate(**kwargs) -> Dict[str, Union[str, list, float, int, bool]]:
        """
        Validate the input parameters for creating a Path TimeSeries
        
        Args:
            **kwargs: Parameters for time series initialization
        
        Returns:
            Dict[str, Union[str, list, float, int, bool]]: Dictionary of parameter names and values
        """
        dt = kwargs.get("dt")
        factor = kwargs.get("factor", 1.0)
        useLast = kwargs.get("useLast", False)
        prependZero = kwargs.get("prependZero", False)
        startTime = kwargs.get("startTime", 0.0)
        time = kwargs.get("time")
        fileTime = kwargs.get("fileTime")
        values = kwargs.get("values")
        filePath = kwargs.get("filePath")

        if kwargs.get("values") is not None and kwargs.get("filePath") is None:
            values = kwargs.get("values")
            values = [float(v) for v in values.split(",")]
        elif kwargs.get("filePath") is not None and kwargs.get("values") is None:
            filePath = str(kwargs.get("filePath"))
        elif kwargs.get("values") is None and kwargs.get("filePath") is None:
            raise ValueError("Either values or filePath must be provided")
        else:
            raise ValueError("Only one of values or filePath should be provided")
        

        if time is not None and fileTime is not None and dt is not None:
            raise ValueError("Only one of time, fileTime or dt should be provided")
        elif time is None and fileTime is None and dt is None:
            raise ValueError("One of time, fileTime or dt should be provided")
        elif time is  None and fileTime is None and dt is not None:
            try:
                dt = float(dt)
            except ValueError:
                raise ValueError("dt must be a number")
        elif time is not None and fileTime is None and dt is None:
            try :
                time = [float(t) for t in time.split(",")]
            except ValueError:
                raise ValueError("time must be a list of comma separated numbers")
        elif time is None and fileTime is not None and dt is None:
            fileTime = str(fileTime)
        
        elif time is not None :
            if fileTime is not None or dt is not None:
                raise ValueError("Only one of time, fileTime or dt should be provided")
        elif time is None:
            if fileTime is not None and dt is not None:
                raise ValueError("Only one of time, fileTime or dt should be provided")


        if values and not isinstance(values, list):
            raise ValueError("values must be a list")
        

        try :
            factor = float(factor)
        except ValueError:
            raise ValueError("factor must be a number")
        
        
        if not isinstance(useLast, bool):
            raise ValueError("useLast must be a boolean")
        
        if not isinstance(prependZero, bool):
            raise ValueError("prependZero must be a boolean")
        
        try:
            startTime = float(startTime)
        except ValueError:
            raise ValueError("startTime must be a number")
        
        if time and not isinstance(time, list):
            raise ValueError("time must be a list")
        
        return {
            "dt": dt,
            "values": values,
            "filePath": filePath,
            "factor": factor,
            "useLast": useLast,
            "prependZero": prependZero,
            "startTime": startTime,
            "time": time,
            "fileTime": fileTime
        }
    
    def get_values(self) -> Dict[str, Union[str, int, float, list, bool]]:
        """
        Get the parameters defining this time series
        """
        return {
            "dt": self.dt,
            "values": ",".join(map(str, self.values)) if self.values else None,
            "filePath": self.filePath,
            "factor": self.factor,
            "useLast": self.useLast,
            "prependZero": self.prependZero,
            "startTime": self.startTime,
            "time": ",".join(map(str, self.time)) if self.time else None,
            "fileTime": self.fileTime
        }
    
    def update_values(self, **kwargs) -> None:
        """
        Update the values of the time series
        
        Args:
            **kwargs: Parameters for time series initialization
        """
        kwargs = self.validate(**kwargs)
        self.dt = kwargs["dt"]
        self.values = kwargs["values"]
        self.filePath = kwargs["filePath"]
        self.factor = kwargs["factor"]
        self.useLast = kwargs["useLast"]
        self.prependZero = kwargs["prependZero"]
        self.startTime = kwargs["startTime"]
        self.time = kwargs["time"]
        self.fileTime = kwargs["fileTime"]




class TimeSeriesRegistry:
    """
    A registry to manage time series types and their creation.
    """
    _time_series_types = {
        'constant': ConstantTimeSeries,
        'linear': LinearTimeSeries,
        'trig': TrigTimeSeries,
        'ramp': RampTimeSeries,
        'triangular': TriangularTimeSeries,
        'rectangular': RectangularTimeSeries,
        'pulse': PulseTimeSeries,
        'path': PathTimeSeries,
    }

    @classmethod
    def register_time_series_type(cls, name: str, series_class: Type[TimeSeries]):
        """
        Register a new time series type for easy creation.
        
        Args:
            name (str): The name of the time series type
            series_class (Type[TimeSeries]): The class of the time series
        """
        cls._time_series_types[name.lower()] = series_class

    @classmethod
    def get_time_series_types(cls):
        """
        Get available time series types.
        
        Returns:
            List[str]: Available time series types
        """
        return list(cls._time_series_types.keys())

    @classmethod
    def create_time_series(cls, series_type: str, **kwargs) -> TimeSeries:
        """
        Create a new time series of a specific type.
        
        Args:
            series_type (str): Type of time series to create
            **kwargs: Parameters for time series initialization
        
        Returns:
            TimeSeries: A new time series instance
        
        Raises:
            KeyError: If the time series type is not registered
        """
        if series_type.lower() not in cls._time_series_types:
            raise KeyError(f"Time series type {series_type} not registered")
        
        return cls._time_series_types[series_type.lower()](**kwargs)




class TimeSeriesManager:
    """
    Singleton class for managing time series
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TimeSeriesManager, cls).__new__(cls)
        return cls._instance

    def create_time_series(self, series_type: str, **kwargs) -> TimeSeries:
        """Create a new time series"""
        return TimeSeriesRegistry.create_time_series(series_type, **kwargs)

    def get_time_series(self, tag: int) -> TimeSeries:
        """Get time series by tag"""
        return TimeSeries.get_time_series(tag)

    def remove_time_series(self, tag: int) -> None:
        """Remove time series by tag"""
        TimeSeries.remove_time_series(tag)

    def get_all_time_series(self) -> Dict[int, TimeSeries]:
        """Get all time series"""
        return TimeSeries.get_all_time_series()

    def get_available_types(self) -> List[str]:
        """Get list of available time series types"""
        return TimeSeriesRegistry.get_time_series_types()
    
    def clear_all(self):
        """Clear all time series"""  
        TimeSeries._time_series.clear()

