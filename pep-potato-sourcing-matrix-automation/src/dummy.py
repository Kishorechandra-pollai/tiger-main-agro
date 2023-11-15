import schemas
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response

router = APIRouter()

ownership_data = {
    "response": {
        "year": "2023",
        "ownership": "Fresh",
        "region": [
            {"id": 1, "name": "Central - US"},
            {"id": 2, "name": "East - US"},
            {"id": 3, "name": "Mid West - US"},
            {"id": 4, "name": "North East - US"},
            {"id": 5, "name": "West US"},
            {"id": 6, "name": "Canada"},
            {"id": 7, "name": "All Data"}
        ],
        "metrics": [
            {"id": 1, "name": "Central US - Contracts", "value": "8200 MCWT"},
            {"id": 2, "name": "Central US - Shrinkage", "value": "5% MCWT"},
            {"id": 3, "name": "Central US - To Ship", "value": "480"},
            {"id": 4, "name": "Central US - Market", "value": "450 MCWT"},
            {"id": 5, "name": "Central US - Total to Ship", "value": "1000 MCWT"},
            {"id": 6, "name": "Central US - Position", "value": "8200 MCWT"},
            {"id": 7, "name": "Central US - Extension", "value": "8200 MCWT"},
            {"id": 8, "name": "Central US - CY VS PY", "value": "690 MCWT"}
        ],
        "details": [
            {"growing_area": "South FL", "contract ERP": "500", "contract Value": "500", "shrikange": "7%",
             "to_ship": "467", "markets_and_flex": "32", "total_to_ship": "87", "extension": "11.1",
             "extension_qty": "467", "position": "(0)"},
            {"growing_area": "South FL", "contract ERP": "500", "contract Value": "500", "shrikange": "7%",
             "to_ship": "467", "markets_and_flex": "32", "total_to_ship": "87", "extension": "11.1",
             "extension_qty": "467", "position": "(0)"},
            {"growing_area": "South FL", "contract ERP": "500", "contract Value": "500", "shrikange": "7%",
             "to_ship": "467", "markets_and_flex": "32", "total_to_ship": "87", "extension": "11.1",
             "extension_qty": "467", "position": "(0)"},
            {"growing_area": "South FL", "contract ERP": "500", "contract Value": "500", "shrikange": "7%",
             "to_ship": "467", "markets_and_flex": "32", "total_to_ship": "87", "extension": "11.1",
             "extension_qty": "467", "position": "(0)"},
            {"growing_area": "South FL", "contract ERP": "500", "contract Value": "500", "shrikange": "7%",
             "to_ship": "467", "markets_and_flex": "32", "total_to_ship": "87", "extension": "11.1",
             "extension_qty": "467", "position": "(0)"},
            {"growing_area": "South FL", "contract ERP": "500", "contract Value": "500", "shrikange": "7%",
             "to_ship": "467", "markets_and_flex": "32", "total_to_ship": "87", "extension": "11.1",
             "extension_qty": "467", "position": "(0)"},
            {"growing_area": "South FL", "contract ERP": "500", "contract Value": "500", "shrikange": "7%",
             "to_ship": "467", "markets_and_flex": "32", "total_to_ship": "87", "extension": "11.1",
             "extension_qty": "467", "position": "(0)"},
            {"growing_area": "South FL", "contract ERP": "500", "contract Value": "500", "shrikange": "7%",
             "to_ship": "467", "markets_and_flex": "32", "total_to_ship": "87", "extension": "11.1",
             "extension_qty": "467", "position": "(0)"},
            {"growing_area": "South FL", "contract ERP": "500", "contract Value": "500", "shrikange": "7%",
             "to_ship": "467", "markets_and_flex": "32", "total_to_ship": "87", "extension": "11.1",
             "extension_qty": "467", "position": "(0)"},
            {"growing_area": "South FL", "contract ERP": "500", "contract Value": "500", "shrikange": "7%",
             "to_ship": "467", "markets_and_flex": "32", "total_to_ship": "87", "extension": "11.1",
             "extension_qty": "467", "position": "(0)"}
        ]
    }}

plant_matrix_allocation = {
    "response": {
        "year": "2023",
        "period": "P1",
        "details": [
            {
                "region_id": 1,
                "region_name": "Central - US",
                "plant_id": 1,
                "plant_name": "Beloit",
                "P1W1": [
                    {
                        "id": 1,
                        "name": "WI",
                        "value": 33
                    },
                    {
                        "id": 2,
                        "name": "RV",
                        "value": 33
                    },
                    {
                        "id": 3,
                        "name": "CS",
                        "value": 33
                    }
                ]
            },
            {
                "region_id": 1,
                "region_name": "Central - US",
                "plant_id": 2,
                "plant_name": "Denver",
                "P1W1": [
                    {
                        "id": 1,
                        "name": "WI",
                        "value": 33
                    },
                    {
                        "id": 2,
                        "name": "RV",
                        "value": 33
                    },
                    {
                        "id": 3,
                        "name": "CS",
                        "value": 33
                    }
                ]
            },
            {
                "region_id": 2,
                "region_name": "East - US",
                "plant_id": 3,
                "plant_name": "SAmple 1",
                "P1W1": [
                    {
                        "id": 1,
                        "name": "WI",
                        "value": 33
                    },
                    {
                        "id": 2,
                        "name": "RV",
                        "value": 33
                    },
                    {
                        "id": 3,
                        "name": "CS",
                        "value": 33
                    }
                ]
            },
            {
                "region_id": 2,
                "region_name": "East - US",
                "plant_id": 4,
                "plant_name": "Sample 2",
                "P1W1": [
                    {
                        "id": 1,
                        "name": "WI",
                        "value": 33
                    },
                    {
                        "id": 2,
                        "name": "RV",
                        "value": 33
                    },
                    {
                        "id": 3,
                        "name": "CS",
                        "value": 33
                    }
                ]
            },
            {
                "region_id": 3,
                "region_name": "West - US",
                "plant_id": 5,
                "plant_name": "Sample 3",
                "P1W1": [
                    {
                        "id": 1,
                        "name": "WI",
                        "value": 33
                    },
                    {
                        "id": 2,
                        "name": "RV",
                        "value": 33
                    },
                    {
                        "id": 3,
                        "name": "CS",
                        "value": 33
                    }
                ]
            },
            {
                "region_id": 3,
                "region_name": "West - US",
                "plant_id": 6,
                "plant_name": "Sample 4",
                "P1W1": [
                    {
                        "id": 1,
                        "name": "WI",
                        "value": 33
                    },
                    {
                        "id": 2,
                        "name": "RV",
                        "value": 33
                    },
                    {
                        "id": 3,
                        "name": "CS",
                        "value": 33
                    }
                ]
            },
            {
                "region_id": 4,
                "region_name": "Canada",
                "plant_id": 7,
                "plant_name": "Sample 5",
                "P1W1": [
                    {
                        "id": 1,
                        "name": "WI",
                        "value": 33
                    },
                    {
                        "id": 2,
                        "name": "RV",
                        "value": 33
                    },
                    {
                        "id": 3,
                        "name": "CS",
                        "value": 33
                    }
                ]
            },
            {
                "region_id": 4,
                "region_name": "Canada",
                "plant_id": 8,
                "plant_name": "Sample 6",
                "P1W1": [
                    {
                        "id": 1,
                        "name": "WI",
                        "value": 33
                    },
                    {
                        "id": 2,
                        "name": "RV",
                        "value": 33
                    },
                    {
                        "id": 3,
                        "name": "CS",
                        "value": 33
                    }
                ]
            }
        ]
    }
}

plant_matrix_region = {
    "response": {
        "year": "2023",
        "details": [
            {"region_id": 1, "region_name": "Central - US", "plant_id": 1, "plant_name": "Beloit", "p1w1": 33,
             "p1w2": 33, "p1w3": 33, "p1w4": 33, "p1w5": 33, "p1w6": 33, "p1w7": 33, "p1w8": 33, "p1w9": 33,
             "p1w10": 33, "p1w11": 33, "p1w12": 33, "p1w13": 33},
            {"region_id": 1, "region_name": "Central - US", "plant_id": 2, "plant_name": "Denver", "p1w1": 33,
             "p1w2": 33, "p1w3": 33, "p1w4": 33, "p1w5": 33, "p1w6": 33, "p1w7": 33, "p1w8": 33, "p1w9": 33,
             "p1w10": 33, "p1w11": 33, "p1w12": 33, "p1w13": 33},
            {"region_id": 1, "region_name": "Central - US", "plant_id": 3, "plant_name": "San Antono", "p1w1": 33,
             "p1w2": 33, "p1w3": 33, "p1w4": 33, "p1w5": 33, "p1w6": 33, "p1w7": 33, "p1w8": 33, "p1w9": 33,
             "p1w10": 33, "p1w11": 33, "p1w12": 33, "p1w13": 33},
            {"region_id": 1, "region_name": "Central - US", "plant_id": 4, "plant_name": "Rosenberg", "p1w1": 33,
             "p1w2": 33, "p1w3": 33, "p1w4": 33, "p1w5": 33, "p1w6": 33, "p1w7": 33, "p1w8": 33, "p1w9": 33,
             "p1w10": 33, "p1w11": 33, "p1w12": 33, "p1w13": 33},
            {"region_id": 1, "region_name": "Central - US", "plant_id": 5, "plant_name": "Irving", "p1w1": 33,
             "p1w2": 33, "p1w3": 33, "p1w4": 33, "p1w5": 33, "p1w6": 33, "p1w7": 33, "p1w8": 33, "p1w9": 33,
             "p1w10": 33, "p1w11": 33, "p1w12": 33, "p1w13": 33},
            {"region_id": 1, "region_name": "Central - US", "plant_id": 6, "plant_name": "Wooster", "p1w1": 33,
             "p1w2": 33, "p1w3": 33, "p1w4": 33, "p1w5": 33, "p1w6": 33, "p1w7": 33, "p1w8": 33, "p1w9": 33,
             "p1w10": 33, "p1w11": 33, "p1w12": 33, "p1w13": 33},
        ]
    }
}

plant_matrix_growing_area = {
    "response": {
        "year": "2023",
        "details": [
            {"region_id": 1, "region_name": "Central - US", "p1w1": 33, "p1w2": 33, "p1w3": 33, "p1w4": 33, "p1w5": 33,
             "p1w6": 33, "p1w7": 33, "p1w8": 33, "p1w9": 33, "p1w10": 33, "p1w11": 33, "p1w12": 33, "p1w13": 33},
            {"region_id": 2, "region_name": "East - US", "p1w1": 33, "p1w2": 33, "p1w3": 33, "p1w4": 33, "p1w5": 33,
             "p1w6": 33, "p1w7": 33, "p1w8": 33, "p1w9": 33, "p1w10": 33, "p1w11": 33, "p1w12": 33, "p1w13": 33},
            {"region_id": 3, "region_name": "West - US", "p1w1": 33, "p1w2": 33, "p1w3": 33, "p1w4": 33, "p1w5": 33,
             "p1w6": 33, "p1w7": 33, "p1w8": 33, "p1w9": 33, "p1w10": 33, "p1w11": 33, "p1w12": 33, "p1w13": 33},
            {"region_id": 4, "region_name": "Canda", "p1w1": 33, "p1w2": 33, "p1w3": 33, "p1w4": 33, "p1w5": 33,
             "p1w6": 33, "p1w7": 33, "p1w8": 33, "p1w9": 33, "p1w10": 33, "p1w11": 33, "p1w12": 33, "p1w13": 33},
            {"region_id": 5, "region_name": "Total", "p1w1": 33, "p1w2": 33, "p1w3": 33, "p1w4": 33, "p1w5": 33,
             "p1w6": 33, "p1w7": 33, "p1w8": 33, "p1w9": 33, "p1w10": 33, "p1w11": 33, "p1w12": 33, "p1w13": 33},
        ]
    }
}


@router.get('/ownership/')
def get_ownership():
    return ownership_data


@router.get('/plant-matrix/allocation/')
def get_ownership():
    return plant_matrix_allocation


@router.get('/plant-matrix/region-level/')
def get_ownership():
    return plant_matrix_region


@router.get('/plant-matrix/growing-area/')
def get_ownership():
    return plant_matrix_growing_area
