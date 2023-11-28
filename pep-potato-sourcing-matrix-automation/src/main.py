"""Main file of the application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
import uvicorn
"""import allocation
import plant_mtrx
import category
import dummy
import growers
import growingarea
import plants
import freightcost
import region
import ownership
import plantGrowingMapping
import erp_raw_data_us
import OwnershipGrowerGrowing
import pcusage
import erprawdata
import plant_site_growing_area_mapping
import vendor_site_code
import pagination
import potatorates
import solidrates
import offcontractinfo
import generaladministrative
import freighttaskinfo
import period_week_calc
"""
from database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:8000",
]

app.include_router(plants.router, tags=['plant'], prefix='/api/plant')
# app.include_router(growingarea.router, tags=['growing-area'], prefix='/api/growing-area')
# app.include_router(growers.router, tags=['grower'], prefix='/api/grower')
# app.include_router(region.router, tags=['region'], prefix='/api/region')
# app.include_router(allocation.router, tags=['allocation'], prefix='/api/allocation')
# app.include_router(plantGrowingMapping.router, tags=['plant-growing-mapping'], prefix='/api/plant-growing-mapping')
# app.include_router(dummy.router, tags=['dummy'], prefix='/api/dummy')
# app.include_router(category.router, tags=['category'], prefix='/api/category')
# app.include_router(OwnershipGrowerGrowing.router, tags=['OwnershipGrowerGrowingMapping'], prefix='/api/ownershipMapping')
# app.include_router(pcusage.router, tags=['pcusage'], prefix='/api/pcusage')
# app.include_router(freightcost.router, tags=['freight-cost'], prefix='/api/freight-cost')
# app.include_router(ownership.router, tags=['ownership'], prefix='/api/ownership')
# app.include_router(erp_raw_data_us.router, tags=['erp_raw_data_us'], prefix='/api/erp_raw_data_us')
# app.include_router(pcusage.router, tags=['pcusage'], prefix='/api/pcusage')
# app.include_router(freightcost.router, tags=['freight-cost'], prefix='/api/freight-cost')
# app.include_router(period_week_calc.router, tags=['period_week_calc'], prefix='/api/period_week')
# app.include_router(erprawdata.router, tags=['erp-raw-data'], prefix='/api/erp-raw-data')
# app.include_router(plant_mtrx.router, tags=['plant_mtrx'], prefix='/api/plant_mtrx')
# app.include_router(plant_site_growing_area_mapping.router, tags=['plant_site_growing_area_mapping'], prefix='/api/plant_site_growing_area_mapping')
# app.include_router(vendor_site_code.router,tags=['vendor_site_code'],prefix='/api/vendor_site_code')
# app.include_router(potatorates.router,tags=['potato-rates'], prefix='/api/potato_rates')
# app.include_router(solidrates.router,tags=['solid-rates'], prefix='/api/solid_rates')
# app.include_router(pagination.router,tags=['pagination'], prefix='/api/pagination')
# app.include_router(offcontractinfo.router, tags=['off-contract-info'], prefix='/api/off_contract_info')
# app.include_router(generaladministrative.router, tags=['general-administrative'], prefix='/api/general_administrative')
# app.include_router(freighttaskinfo.router, tags=['freight-task-info'], prefix='/api/freight_task_info')
# app.include_router(p4p_master_info.router, tags=['p4p-master-info'], prefix='/api/p4p-master-info')
# app.include_router(extensionMapping.router, tags=['extensionMapping'], prefix='/api/extensionMapping')
# app.include_router(MarketFlexMapping.router, tags=['MarketFlexMapping'], prefix='/api/MarketFlexMapping')
# app.include_router(summary_price_variance.router, tags=['summary_price_variance'], prefix='/api/summary_price_variance')
# app.include_router(solid_task_master.router, tags=['solid-task-master'], prefix='/api/solid-task-master')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/healthchecker")
def root():
    """Health checker function"""
    return {"message": "Welcome to PMP portal for health check"}


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True, access_log=True
    )
