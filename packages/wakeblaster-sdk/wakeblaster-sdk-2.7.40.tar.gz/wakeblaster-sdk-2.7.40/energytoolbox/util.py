
class SignalNames:
    wind_speed = 'WindSpeed_avg'
    wind_direction = 'WindDirection'
    wind_speed_standard_deviation = 'WindSpeed_std'
    temperature = 'AirTemperature'
    pressure = 'AirPressure'
    nacelle_direction = 'NacDirection'
    operating_state = 'OperatingState'
    operating_mode = 'OperatingMode'
    monin_obukhov_length = 'MoninObukhovLength'
    air_density = 'AirDensity'

    @classmethod
    def is_signal(cls, signal_name):
        """Determine whether signal_name is in the list of signal names"""
        return signal_name in cls.__dict__.values()
