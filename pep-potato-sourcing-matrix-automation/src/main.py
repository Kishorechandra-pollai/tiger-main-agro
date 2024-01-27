"""Main file of the application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
import allocation
import plant_mtrx
import uvicorn
import category
import growers
import growingarea
import plants
import freightcost
import region
import ownership
import plantGrowingMapping
import OwnershipGrowerGrowing
import pcusage
import plant_site_growing_area_mapping
import vendor_site_code
import potatorates
import solidrates
import offcontractinfo
import generaladministrative
import freighttaskinfo
import extensionMapping
import MarketFlexMapping
import period_week_calc
import p4p_master_info
import summary_price_variance
import inflation_deflation
import dashboard
import summary_solids
import summary_overall_cost
from database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:8000",
]

app.include_router(plants.router, tags=['plant'], prefix='/api/plant')
app.include_router(growingarea.router, tags=['growing-area'], prefix='/api/growing-area')
app.include_router(growers.router, tags=['grower'], prefix='/api/grower')
app.include_router(region.router, tags=['region'], prefix='/api/region')
app.include_router(period_week_calc.router, tags=['period_week_calc'], prefix='/api/period_week')
app.include_router(allocation.router, tags=['allocation'], prefix='/api/allocation')
app.include_router(plantGrowingMapping.router, tags=['plant-growing-mapping'], prefix='/api/plant-growing-mapping')
app.include_router(category.router, tags=['category'], prefix='/api/category')
app.include_router(pcusage.router, tags=['pcusage'], prefix='/api/pcusage')
app.include_router(ownership.router, tags=['ownership'], prefix='/api/ownership')
app.include_router(extensionMapping.router, tags=['extensionMapping'], prefix='/api/extensionMapping')
app.include_router(MarketFlexMapping.router, tags=['MarketFlexMapping'], prefix='/api/MarketFlexMapping')
app.include_router(OwnershipGrowerGrowing.router, tags=['OwnershipGrowerGrowingMapping'],
                   prefix='/api/ownershipMapping')
app.include_router(plant_mtrx.router, tags=['plant_mtrx'], prefix='/api/plant_mtrx')
app.include_router(plant_site_growing_area_mapping.router, tags=['plant_site_growing_area_mapping'],
                   prefix='/api/plant_site_growing_area_mapping')
app.include_router(vendor_site_code.router,tags=['vendor_site_code'],prefix='/api/vendor_site_code')
app.include_router(dashboard.router, tags=['dashboard'], prefix='/api/dashboard')
app.include_router(potatorates.router,tags=['potato-rates'], prefix='/api/potato_rates')

app.include_router(freightcost.router, tags=['freight-cost'], prefix='/api/freight-cost')
app.include_router(freightcost.router, tags=['freight-cost'], prefix='/api/freight-cost')
app.include_router(solidrates.router,tags=['solid-rates'], prefix='/api/solid_rates')
app.include_router(offcontractinfo.router, tags=['off-contract-info'], prefix='/api/off_contract_info')
app.include_router(generaladministrative.router, tags=['general-administrative'], prefix='/api/general_administrative')
app.include_router(freighttaskinfo.router, tags=['freight-task-info'], prefix='/api/freight_task_info')
app.include_router(p4p_master_info.router, tags=['p4p-master-info'], prefix='/api/p4p-master-info')

app.include_router(summary_price_variance.router, tags=['summary_price_variance'], prefix='/api/summary_price_variance')
app.include_router(inflation_deflation.router, tags=['inflation_deflation'], prefix='/api/inflation_deflation')
app.include_router(summary_solids.router, tags=['summary_solids'], prefix='/api/summary_solids')
app.include_router(summary_overall_cost.router, tags=['summary_overall_cost'], prefix='/api/summary_overall_cost')

app.include_router(plant_mtrx_templt.router, tags=['plant_mtrx_templt'], prefix='/api/plant_mtrx_templt')

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
