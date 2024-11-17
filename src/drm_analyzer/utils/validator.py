from PyQt5.QtGui import QDoubleValidator, QIntValidator


class DoubleValidator(QDoubleValidator):
    def validate(self, input_string, pos):
        if ',' in input_string:
            return (QDoubleValidator.Invalid, input_string, pos)
        return super().validate(input_string, pos)
    
class IntValidator(QIntValidator):
    def validate(self, input_string, pos):
        if ',' in input_string or input_string.startswith('0'):
            return (QIntValidator.Invalid, input_string, pos)
        return super().validate(input_string, pos)
    
class PositiveDoubleValidator(QDoubleValidator):
    def validate(self, input_string, pos):
        if ',' in input_string or float(input_string) <= 0:
            return (QDoubleValidator.Invalid, input_string, pos)
        return super().validate(input_string, pos)