from PySide6.QtGui import QValidator

__version__ = "1.0.0"

class SideValidator:
    """PySide6验证器库 - 封装各种常用验证器"""
    class number:
        """数字验证器"""
        class decimal:
            """小数验证器"""
            @staticmethod
            class positive(QValidator):
                """正小数验证器"""
                def validate(self, input_text, pos):
                    if input_text == "":
                        return QValidator.Intermediate, input_text, pos
                    have_dot = False
                    for char in input_text:
                        if char not in "0123456789.":
                            return QValidator.Invalid, input_text, pos
                        if char == ".":
                            if have_dot:
                                return QValidator.Invalid, input_text, pos
                            else:
                                have_dot = True
                    return QValidator.Acceptable, input_text, pos
            
            @staticmethod
            class negative(QValidator):
                """负小数验证器"""
                def validate(self, input_text, pos):
                    if input_text == "":
                        return QValidator.Intermediate, input_text, pos
                    have_dot = False
                    have_neg = False
                    for char in input_text:
                        if char not in "0123456789.-":
                            return QValidator.Invalid, input_text, pos
                        if char == ".":
                            if have_dot:
                                return QValidator.Invalid, input_text, pos
                            else:
                                have_dot = True
                        if char == "-":
                            if have_neg:
                                return QValidator.Invalid, input_text, pos
                            else:
                                have_neg = True
                    if input_text[0] != "-":
                        return QValidator.Invalid, input_text, pos
                    return QValidator.Acceptable, input_text, pos
                
            @staticmethod
            class both(QValidator):
                """正负小数验证器"""
                def validate(self, input_text, pos):
                    if input_text == "":
                        return QValidator.Intermediate, input_text, pos
                    have_dot = False
                    have_neg = False
                    for char in input_text:
                        if char not in "0123456789.-":
                            return QValidator.Invalid, input_text, pos
                        if char == ".":
                            if have_dot:
                                return QValidator.Invalid, input_text, pos
                            else:
                                have_dot = True
                        if char == "-":
                            if have_neg:
                                return QValidator.Invalid, input_text, pos
                            else:
                                have_neg = True
                    if have_neg and input_text[0] != "-":
                        return QValidator.Invalid, input_text, pos
                    return QValidator.Acceptable, input_text, pos

        class integer:
            class positive(QValidator):
                """正整数验证器"""
                def validate(self, input_text, pos):
                    if input_text == "":
                        return QValidator.Intermediate, input_text, pos
                    if input_text.isdigit():
                        return QValidator.Acceptable, input_text, pos
                    return QValidator.Invalid, input_text, pos

            class negative(QValidator):
                """负整数验证器"""
                def validate(self, input_text, pos):
                    if input_text == "":
                        return QValidator.Intermediate, input_text, pos
                    have_neg = False
                    for char in input_text:
                        if char not in "0123456789-":
                            return QValidator.Invalid, input_text, pos
                        if char == "-":
                            if have_neg:
                                return QValidator.Invalid, input_text, pos
                            else:
                                have_neg = True
                    if input_text[0] != "-":
                        return QValidator.Invalid, input_text, pos
                    return QValidator.Acceptable, input_text, pos

            class both(QValidator):
                """正负整数验证器"""
                def validate(self, input_text, pos):
                    if input_text == "":
                        return QValidator.Intermediate, input_text, pos
                    have_neg = False
                    for char in input_text:
                        if char not in "0123456789-":
                            return QValidator.Invalid, input_text, pos
                        if char == "-":
                            if have_neg:
                                return QValidator.Invalid, input_text, pos
                            else:
                                have_neg = True
                    return QValidator.Acceptable, input_text, pos

    class string:
        """字符串验证器"""
        @staticmethod
        def length(max_len=None):
            """长度限制验证器"""
            class LengthValidator(QValidator):
                def validate(self, input_text, pos):
                    if len(input_text) == 0:
                        return QValidator.Intermediate, input_text, pos
                    if max_len > 0 and len(input_text) > max_len:
                        return QValidator.Invalid, input_text, pos
                    return QValidator.Acceptable, input_text, pos
            return LengthValidator()

        @staticmethod
        class english(QValidator):
            """英文验证器"""
            def validate(self, input_text, pos):
                if input_text == "":
                    return QValidator.Intermediate, input_text, pos
                for char in input_text:
                    if char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        return QValidator.Invalid, input_text, pos
                return QValidator.Acceptable, input_text, pos

    @staticmethod
    def custom(check_function):
        """自定义验证器"""
        class CustomValidator(QValidator):
            def validate(self, input_text, pos):
                result = check_function(input_text)
                if result == "acceptable":
                    return QValidator.Acceptable, input_text, pos
                elif result == "intermediate":
                    return QValidator.Intermediate, input_text, pos
                else:
                    return QValidator.Invalid, input_text, pos
        
        return CustomValidator()

