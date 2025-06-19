__all__ = [
    "SCHEMAS"
]


SCHEMAS = {
    "住所": {
        "base_type": "structured_address",
        "required_fields": ["raw"],
        "optional_fields": ["prefecture", "secondary_division", "secondary_type", "tertiary_division", "tertiary_type", "remaining", "hierarchy", "division_types"],
        "field_types": {
            "raw": str,
            "prefecture": [str, type(None)],
            "secondary_division": [str, type(None)],
            "secondary_type": [str, type(None)],
            "tertiary_division": [str, type(None)],
            "tertiary_type": [str, type(None)],
            "remaining": [str, type(None)],
            "hierarchy": [str, type(None)],
            "division_types": [str, type(None)]
        }
    },
    "交通": {
        "base_type": "access_routes",
        "required_fields": [],
        "optional_fields": ["routes", "value"],
        "field_types": {
            "routes": list,
            "value": [str, type(None)]
        }
    },
    "戸数": {
        "base_type": "single",
        "required_fields": [],
        "optional_fields": ["value", "unit", "note", "is_total", "is_current_sale"],
        "field_types": {
            "value": [int, type(None)],
            "unit": [str, type(None)],
            "note": [str, type(None)],
            "is_total": bool,
            "is_current_sale": bool
        }
    },
    "用途地域": {
        "base_type": "array",
        "required_fields": [],
        "optional_fields": ["values"],
        "field_types": {
            "values": list
        }
    },
    "築年月": {
        "base_type": "date_or_period",
        "required_fields": [],
        "optional_fields": ["value", "year", "month", "day", "is_scheduled", "note", "period_text", "estimated_date", "tentative", "completed", "immediate", "is_undefined"],
        "field_types": {
            "value": [str, type(None)],
            "year": [int, type(None)],
            "month": [int, type(None)],
            "day": [int, type(None)],
            "is_scheduled": bool,
            "note": [str, type(None)],
            "period_text": [str, type(None)],
            "estimated_date": [str, type(None)],
            "tentative": bool,
            "completed": bool,
            "immediate": bool,
            "is_undefined": bool
        }
    },
    "引渡時期": {
        "base_type": "single",
        "required_fields": [],
        "optional_fields": ["value", "type", "year", "month", "day", "is_planned", "estimated_date", "period_text", "months", "note"],
        "field_types": {
            "value": [str, type(None)],
            "type": [str, type(None)],
            "year": [int, type(None)],
            "month": [int, type(None)],
            "day": [int, type(None)],
            "is_planned": bool,
            "estimated_date": [str, type(None)],
            "period_text": [str, type(None)],
            "months": [float, type(None)],
            "note": [str, type(None)]
        }
    },
    "価格": {
        "base_type": "range_or_single",
        "required_fields": [],
        "optional_fields": ["value", "min", "max", "unit", "is_undefined", "type", "note", "tentative"],
        "field_types": {
            "value": [float, int, type(None)],
            "min": [float, int, type(None)],
            "max": [float, int, type(None)],
            "unit": [str, type(None)],
            "is_undefined": bool,
            "type": [str, type(None)],
            "note": [str, type(None)],
            "tentative": bool
        }
    },
    "価格帯": {
        "base_type": "range_or_single",
        "required_fields": [],
        "optional_fields": ["value", "min", "max", "unit", "is_undefined", "type", "note", "tentative", "values"],
        "field_types": {
            "value": [float, int, type(None)],
            "min": [float, int, type(None)],
            "max": [float, int, type(None)],
            "unit": [str, type(None)],
            "is_undefined": bool,
            "type": [str, type(None)],
            "note": [str, type(None)],
            "tentative": bool,
            "values": list
        }
    },
    "管理費": {
        "base_type": "range_or_single",
        "required_fields": [],
        "optional_fields": ["value", "min", "max", "unit", "is_undefined", "type", "note", "tentative", "management_type", "work_style", "frequency", "breakdown"],
        "field_types": {
            "value": [float, int, type(None)],
            "min": [float, int, type(None)],
            "max": [float, int, type(None)],
            "unit": [str, type(None)],
            "is_undefined": bool,
            "type": [str, type(None)],
            "note": [str, type(None)],
            "tentative": bool,
            "management_type": [str, type(None)],
            "work_style": [str, type(None)],
            "frequency": [str, type(None)],
            "breakdown": [str, type(None)]
        }
    },
    "他経費": {
        "base_type": "array",
        "required_fields": [],
        "optional_fields": ["value", "expenses"],
        "field_types": {
            "value": [str, type(None)],
            "expenses": list
        }
    },
    "間取り": {
        "base_type": "structured_layout",
        "required_fields": [],
        "optional_fields": ["types", "rooms", "main_rooms", "other_rooms", "type_summary", "value", "values"],
        "field_types": {
            "types": list,
            "rooms": [int, type(None)],
            "main_rooms": [int, type(None)],
            "other_rooms": list,
            "type_summary": [str, type(None)],
            "value": [str, type(None)],
            "values": list
        }
    },
    "専有面積": {
        "base_type": "range_or_single",
        "required_fields": [],
        "optional_fields": ["value", "min", "max", "unit", "min_tsubo", "max_tsubo"],
        "field_types": {
            "value": [float, int, type(None)],
            "min": [float, int, type(None)],
            "max": [float, int, type(None)],
            "unit": [str, type(None)],
            "min_tsubo": [float, int, type(None)],
            "max_tsubo": [float, int, type(None)]
        }
    },
    "その他面積": {
        "base_type": "array",
        "required_fields": [],
        "optional_fields": ["areas"],
        "field_types": {
            "areas": list
        }
    },
    "制限事項": {
        "base_type": "array",
        "required_fields": [],
        "optional_fields": ["restrictions"],
        "field_types": {
            "restrictions": list
        }
    },
    "取引条件有効期限": {
        "base_type": "single",
        "required_fields": [],
        "optional_fields": ["value", "date"],
        "field_types": {
            "value": [str, type(None)],
            "date": [str, type(None)]
        }
    },
    "施工会社": {
        "base_type": "structured_text",
        "required_fields": [],
        "optional_fields": ["value"],
        "field_types": {
            "value": [str, type(None)]
        }
    },
    "管理会社": {
        "base_type": "structured_text",
        "required_fields": [],
        "optional_fields": ["value"],
        "field_types": {
            "value": [str, type(None)]
        }
    },
    "所在階": {
        "base_type": "number_with_unit",
        "required_fields": [],
        "optional_fields": ["value", "unit", "note"],
        "field_types": {
            "value": [float, int, type(None)],
            "unit": [str, type(None)],
            "note": [str, type(None)]
        }
    },
    "向き": {
        "base_type": "structured_text",
        "required_fields": [],
        "optional_fields": ["value"],
        "field_types": {
            "value": [str, type(None)]
        }
    },
    "特徴": {
        "base_type": "structured_features",
        "required_fields": [],
        "optional_fields": ["feature_tags", "feature_count"],
        "field_types": {
            "feature_tags": list,
            "feature_count": int
        }
    },
    "構造階建": {
        "base_type": "single",
        "required_fields": [],
        "optional_fields": ["structure", "floors", "basement", "value", "total_floors", "basement_floors", "floor", "partial_structure", "note", "raw_value"],
        "field_types": {
            "structure": [str, type(None)],
            "floors": [int, type(None)],
            "basement": [int, type(None)],
            "value": [str, type(None)],
            "total_floors": [int, type(None)],
            "basement_floors": [int, type(None)],
            "floor": [int, type(None)],
            "partial_structure": [str, type(None)],
            "note": [str, type(None)],
            "raw_value": [str, type(None)]
        }
    },
    "リフォーム": {
        "base_type": "single",
        "required_fields": [],
        "optional_fields": ["value", "details", "cost", "has_reform", "reform_info", "completion_date", "is_scheduled", "reform_areas", "note"],
        "field_types": {
            "value": [str, type(None)],
            "details": list,
            "cost": [int, float, type(None)],
            "has_reform": bool,
            "reform_info": dict,
            "completion_date": [str, type(None)],
            "is_scheduled": bool,
            "reform_areas": dict,
            "note": [str, type(None)]
        }
    },
    "周辺施設": {
        "base_type": "structured_features",
        "required_fields": [],
        "optional_fields": ["facilities"],
        "field_types": {
            "facilities": list
        }
    },
    "駐車場": {
        "base_type": "parking_info",
        "required_fields": [],
        "optional_fields": ["availability", "available", "count", "min", "max", "unit", "notes", "value", "location", "frequency", "note"],
        "field_types": {
            "availability": bool,
            "available": bool,
            "count": [int, type(None)],
            "min": [int, float, type(None)],
            "max": [int, float, type(None)],
            "unit": [str, type(None)],
            "notes": [str, type(None)],
            "value": [str, int, float, type(None)],
            "location": [str, type(None)],
            "frequency": [str, type(None)],
            "note": [str, type(None)]
        }
    },
    "地目": {
        "base_type": "structured_text",
        "required_fields": [],
        "optional_fields": ["value", "values", "note"],
        "field_types": {
            "value": [str, type(None)],
            "values": list,
            "note": [str, type(None)]
        }
    },
    "間取り図": {
        "base_type": "structured_text",
        "required_fields": [],
        "optional_fields": ["value", "building_number", "price", "layout", "land_area", "building_area"],
        "field_types": {
            "value": [str, type(None)],
            "building_number": [str, type(None)],
            "price": dict,
            "layout": [str, type(None)],
            "land_area": dict,
            "building_area": dict
        }
    },
    "建ぺい率容積率": {
        "base_type": "structured_text",
        "required_fields": [],
        "optional_fields": ["building_coverage_ratio", "floor_area_ratio", "value", "building_coverage", "unit"],
        "field_types": {
            "building_coverage_ratio": [int, float, type(None)],
            "floor_area_ratio": [int, float, type(None)],
            "value": [str, type(None)],
            "building_coverage": [int, float, type(None)],
            "unit": [str, type(None)]
        }
    }
}
