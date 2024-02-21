import pcbnew
import wx


class MinimumLineWidth:
    def __init__(self, control):
        self.language = control
        self.board = pcbnew.GetBoard()

    def get_pad(self, analysis_result):
        pad_result = {}
        result_list = []
        layer_list = []
        minimum = -1
        have_red = False
        have_yellow = False
        if (
            analysis_result["Pad size"] == ""
            or analysis_result["Pad size"]["check"] is None
        ):
            return ""

        footprints = self.board.GetFootprints()
        for footprint in footprints:
            pads = footprint.Pads()
            if pads is None:
                continue
            for pad in pads:
                pad_value = {}
                result = {}
                item_list = []
                pad_shape = pad.GetAttribute()  # 通孔才判断孔环
                size_shape = pad.GetShape()  # 焊盘类型
                drill_shape = pad.GetDrillShape()  # 孔类型
                if pad_shape == 3 or pad_shape == 0:
                    continue
                if size_shape == 0:
                    drill_x = round(pad.GetDrillSizeX() / 1000000, 3)
                    drill_y = round(pad.GetDrillSizeY() / 1000000, 3)
                    if drill_y < drill_x:
                        drill_minimum_width = drill_y
                    else:
                        drill_minimum_width = drill_x
                    different = abs(drill_x - drill_y)
                else:
                    drill_x = pad.GetSizeX()
                    drill_y = pad.GetSizeY()
                    if drill_y < drill_x:
                        drill_minimum_width = drill_y
                    else:
                        drill_minimum_width = drill_x
                    different = abs(drill_x - drill_y)
                if drill_shape == 0:
                    drill_x = pad.GetDrillSizeX()
                    drill_y = pad.GetDrillSizeY()
                    if drill_y > drill_x:
                        drill_minimum_width = drill_y
                    else:
                        drill_minimum_width = drill_x
                else:
                    size_x = pad.GetSizeX()
                    size_y = pad.GetSizeY()
                    if size_y > size_x:
                        size_minimum_width = size_y
                    else:
                        size_minimum_width = size_x

                if (
                    abs(size_minimum_width) - abs(drill_minimum_width) < minimum
                    or minimum == -1
                ):
                    minimum = abs(size_minimum_width) - abs(drill_minimum_width)
                pad_value["value"] = str(
                    round(abs(size_minimum_width) - abs(drill_minimum_width), 3)
                )
                pad_value["id"] = pad.m_Uuid
                layer_list.append(str(pad.GetLayerName()))
                pad_value["layer"] = layer_list
                if different > 1.2:
                    pad_value["item"] = self.language["long_pads"]
                else:
                    pad_value["item"] = self.language["short_pads"]
                    pad_value["color"] = ColorRule().get_rule(
                        analysis_result, "Pad size", pad_value["item"], different
                    )
                    if pad_value["color"] == "red":
                        have_red = True
                    elif pad_value["color"] == "orange":
                        have_yellow = True
                    else:
                        pad_value["color"] = "black"
                item_list.append(pad_value)
                result["result"] = item_list
                result_list.append(result)

        if minimum == -1:
            pad_result["display"] = "正常"
        else:
            pad_result["display"] = minimum
        pad_result["check"] = result_list
        if have_red:
            pad_result["color"] = "red"
        elif have_yellow:
            pad_result["color"] = "orange"
        else:
            pad_result["color"] = "black"
        return pad_result

    def get_annular_ring(self, analysis_result):
        annular_ring_result = {}
        result_list = []
        annular_ring_layer = []
        annular_ring_minimum = -1
        have_red = False
        have_yellow = False
        if analysis_result["RingHole"] == "":
            return ""
        if analysis_result["RingHole"]["check"] == "":
            return ""
        tracks = self.board.GetTracks()
        for item in tracks:
            if type(item) is pcbnew.PCB_VIA:
                annular_ring = {}
                result = {}
                item_list = []
                width = round(float(item.GetWidth()) / 1000000, 3)  # 外径
                drill = round(float(item.GetDrill()) / 1000000, 3)
                value = round((width - drill) / 2, 3)
                annular_ring["value"] = str(value)
                annular_ring_layer.append(item.GetLayerName())
                annular_ring["id"] = item.m_Uuid
                annular_ring["pad_diameter"] = width
                annular_ring["hole_diameter"] = drill
                annular_ring["layer"] = annular_ring_layer
                annular_ring["item"] = self.language["via_ring"]
                annular_ring["color"] = ColorRule().get_rule(
                    analysis_result, "RingHole", "Via Annular Ring", value
                )
                if annular_ring["color"] == "red":
                    have_red = True
                elif annular_ring["color"] == "orange":
                    have_yellow = True
                item_list.append(annular_ring)
                result["result"] = item_list
                result_list.append(result)
                if value < annular_ring_minimum or annular_ring_minimum == -1:
                    annular_ring_minimum = value
        footprints = self.board.GetFootprints()
        for footprint in footprints:
            pads = footprint.Pads()
            if pads is None:
                continue
            for pad in pads:
                result = {}
                item_list = []
                pad_shape = pad.GetAttribute()  # 通孔才判断孔环
                size_shape = pad.GetShape()  # 焊盘类型
                drill_shape = pad.GetDrillShape()  # 孔类型
                if pad_shape != 0:
                    continue
                if size_shape == 0 and drill_shape == 0:
                    annular_ring = {}
                    size_x = round(float(pad.GetSizeX()) / 1000000, 3)
                    drill_x = round(float(pad.GetDrillSizeX()) / 1000000, 3)
                    value = round((size_x - drill_x) / 2, 3)
                    annular_ring["value"] = str(value)
                    annular_ring_layer.append(pad.GetLayerName())
                    annular_ring["id"] = pad.m_Uuid
                    annular_ring["pad_diameter"] = size_x
                    annular_ring["hole_diameter"] = drill_x
                    annular_ring["layer"] = annular_ring_layer
                    annular_ring["item"] = self.language["pth_ring"]
                    annular_ring["color"] = ColorRule().get_rule(
                        analysis_result, "RingHole", "PTH Annular Ring", value
                    )
                    if annular_ring["color"] == "red":
                        have_red = True
                    elif annular_ring["color"] == "orange":
                        have_yellow = True
                    item_list.append(annular_ring)
                    result["result"] = item_list
                    result_list.append(result)
                    if value < annular_ring_minimum or annular_ring_minimum == -1:
                        annular_ring_minimum = value
        if annular_ring_minimum == -1:
            annular_ring_result["display"] = "正常"
        else:
            annular_ring_result["display"] = annular_ring_minimum
        annular_ring_result["check"] = result_list
        if have_red is True:
            annular_ring_result["color"] = "red"
        elif have_yellow is True:
            annular_ring_result["color"] = "orange"
        else:
            annular_ring_result["color"] = "black"

        return annular_ring_result

    # 最小线宽
    def get_line_width(self, analysis_result):
        line_width_result = {}
        result_list = []
        line_width_minimum = -1
        have_red = False
        have_yellow = False
        if (
            analysis_result["Smallest Trace Width"] == ""
            or analysis_result["Smallest Trace Width"]["check"] is None
        ):
            return ""
        for item in self.board.GetTracks():  # Can be VIA or TRACK
            if type(item) is pcbnew.PCB_TRACK:
                line_width = {}
                result = {}
                item_list = []
                line_width_layer = []
                line_width["id"] = item.m_Uuid
                width = round(float(item.GetWidth()) / 1000000, 3)  # 外径
                line_width_layer.append(item.GetLayerName())
                line_width["layer"] = line_width_layer
                line_width["value"] = str(width)
                line_width["info"] = item.m_Uuid
                line_width["item"] = self.language["line_width"]
                line_width["color"] = ColorRule().get_rule(
                    analysis_result,
                    "Smallest Trace Width",
                    "Smallest Trace Width",
                    width,
                )
                if line_width["color"] == "red":
                    have_red = True
                elif line_width["color"] == "orange":
                    have_yellow = True
                item_list.append(line_width)
                result["result"] = item_list
                result_list.append(result)
                if width < line_width_minimum or line_width_minimum == -1:
                    line_width_minimum = width
        if line_width_minimum == -1:
            line_width_result["display"] = "正常"
        else:
            line_width_result["display"] = line_width_minimum

        line_width_result["check"] = result_list
        if have_red is True:
            line_width_result["color"] = "red"
        elif have_yellow is True:
            line_width_result["color"] = "orange"
        else:
            line_width_result["color"] = "black"
        return line_width_result

    # 有无网格敷铜
    def get_zone_attribute(self, analysis_result):
        if (
            analysis_result["Hatched Copper Pour"] == ""
            or analysis_result["Hatched Copper Pour"]["check"] is None
        ):
            return ""
        minimum_value = -1
        zone_attribute_result = {}
        layer_list = []
        result_list = []
        have_red = False
        have_yellow = False
        zones = self.board.Zones()
        for zone in zones:
            result = {}
            zone_attribute = {}
            gap = round((float(zone.GetHatchGap()) / 1000000), 3)
            thickness = round((float(zone.GetHatchThickness()) / 1000000), 3)
            if zone.GetFillMode() == 1:
                zone_attribute["id"] = zone.m_Uuid
                layer_list.append(str(float(zone.GetLayerName())))
                zone_attribute["layer"] = layer_list

                if zone.GetHatchThickness() < zone.GetHatchGap():
                    zone_attribute["value"] = str(gap)
                    zone_attribute["item"] = self.language["grid_spacing"]
                    zone_attribute["color"] = ColorRule().get_rule(
                        analysis_result,
                        "Hatched Copper Pour",
                        zone_attribute["item"],
                        zone.GetHatchThickness(),
                    )
                else:
                    zone_attribute["value"] = str(thickness)
                    zone_attribute["item"] = self.language["grid_width"]
                    zone_attribute["color"] = ColorRule().get_rule(
                        analysis_result,
                        "Hatched Copper Pour",
                        zone_attribute["item"],
                        zone.GetHatchGap(),
                    )
                    if zone_attribute["color"] == "red":
                        have_red = True
                    elif zone_attribute["color"] == "orange":
                        have_yellow = True
                if minimum_value == -1 or zone.GetHatchThickness() < minimum_value:
                    minimum_value = thickness
                elif zone.GetHatchGap() < minimum_value:
                    minimum_value = gap
                result["result"] = zone_attribute
                result_list.append(result)
        if minimum_value == -1:
            zone_attribute_result["display"] = "正常"
        else:
            zone_attribute_result["display"] = minimum_value
        # zone_attribute_result["display"] = str(minimum_value)
        zone_attribute_result["check"] = result_list
        if have_red is True:
            zone_attribute_result["color"] = "red"
        elif have_yellow is True:
            zone_attribute_result["color"] = "orange"
        else:
            zone_attribute_result["color"] = "black"
        return zone_attribute_result


class ColorRule:
    def __init__(self):
        pass

    def get_rule(self, analysis_result, name, item_name, different):
        temp_rule = ""
        if analysis_result[name]["check"] is None:
            return "black"
        for item_check in analysis_result[name]["check"]:
            for result in item_check["result"]:
                item = result["item"]
                if item == item_name:
                    temp_rule = result["rule"]
        if temp_rule == "":
            return "red"
        rule_string1 = temp_rule.partition(",")
        rule_string2 = rule_string1[2].partition(",")
        if float(rule_string1[0]) < float(rule_string2[0]):
            if different < float(rule_string1[0]):
                return "red"
            elif float(rule_string2[0]) > different > float(rule_string1[0]):
                return "orange"
            else:
                return "black"
        else:
            if different > float(rule_string1[0]):
                return "red"
            elif float(rule_string2[0]) < different < float(rule_string1[0]):
                return "orange"
            else:
                return "black"