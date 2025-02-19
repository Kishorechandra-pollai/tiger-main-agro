from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy import func
from fastapi import Depends, HTTPException, status, APIRouter
import schemas
import models
from database import get_db

router = APIRouter()


@router.get('/')
def filtered_market(db: Session = Depends(get_db)):
    """Function to get market and flex."""
    filtered_Market = db.query(models.MarketFlexMapping).filter(
        models.MarketFlexMapping.status == "ACTIVE").all()
    if not filtered_Market:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="No market flex value is present for this year.")
    return {"status": "success", "MarketFlexMapping": filtered_Market}


@router.get('/year/{year}')
def filtered_market_year(year: int, db: Session = Depends(get_db)):
    """Function to get market and flex based on year."""
    filtered_Market = db.query(models.MarketFlexMapping) \
        .join(models.Ownership,
              models.Ownership.ownership_id == models.MarketFlexMapping.ownership_id) \
        .filter(models.MarketFlexMapping.status == "ACTIVE",
                or_(models.Ownership.year == year, models.Ownership.year == year - 1)) \
        .all()
    if not filtered_Market:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail=f"No market flex value is present for this year.")
    return {"status": "success", "MarketFlexMapping": filtered_Market}


def total_ship_calculation(ownership_id: str, db: Session = Depends(get_db)):
    """To calculate total ship in ownership table."""
    ownership_record = db.query(models.Ownership) \
        .filter(models.Ownership.ownership_id == ownership_id).first()

    ownership_record.total_ship = ownership_record.to_ship + ownership_record.market_and_flex
    db.commit()


@router.post('/market_flex')
def update_Market_flex(payload: schemas.MarketFlexPayload,
                       db: Session = Depends(get_db)):
    """update market and flex value."""
    update_market_flex = payload.Payload_MarketFlex
    update_count = 0
    try:
        for item in update_market_flex:
            record = db.query(models.MarketFlexMapping).filter(
                models.MarketFlexMapping.row_id == item.row_id,
                models.MarketFlexMapping.row_id.in_(
                    [item.row_id for item in update_market_flex])).first()

            if record is not None:
                if item.market_flex_value == 0:
                    db.query(models.MarketFlexMapping).filter(
                        models.MarketFlexMapping.row_id == item.row_id).update(
                        {models.MarketFlexMapping.market_flex_value: item.market_flex_value,
                         models.MarketFlexMapping.status: "INACTIVE"}, synchronize_session='fetch')
                else:
                    db.query(models.MarketFlexMapping).filter(
                        models.MarketFlexMapping.row_id == item.row_id).update(
                        {models.MarketFlexMapping.market_flex_value: item.market_flex_value,
                         models.MarketFlexMapping.status: "ACTIVE"}, synchronize_session='fetch')
            else:
                if item.market_flex_value == 0:  # pragma: no cover
                    payload = {
                        "row_id": item.row_id,
                        "growing_area_id": item.growing_area_id,
                        "grower_id": item.grower_id,
                        "ownership_id": item.ownership_id,
                        "status": "INACTIVE",
                        "market_flex_value": item.market_flex_value}
                    new_record = models.MarketFlexMapping(**payload)
                    db.add(new_record)
                else:  # pragma: no cover
                    payload = {
                        "row_id": item.row_id,
                        "growing_area_id": item.growing_area_id,
                        "grower_id": item.grower_id,
                        "ownership_id": item.ownership_id,
                        "status": "ACTIVE",
                        "market_flex_value": item.market_flex_value}
                    new_record = models.MarketFlexMapping(**payload)
                    db.add(new_record)
            db.commit()
            update_count += 1

            market_value = db.query(models.MarketFlexMapping.ownership_id,
                                    func.sum(models.MarketFlexMapping.market_flex_value).label('total_sum')) \
                .filter(models.MarketFlexMapping.growing_area_id == item.growing_area_id) \
                .group_by(models.MarketFlexMapping.ownership_id).all()

            # Updating the extension column in Ownership table
            for value in market_value:
                db.query(models.Ownership).filter(
                    models.Ownership.ownership_id == value.ownership_id).update(
                    {models.Ownership.market_and_flex: value.total_sum},
                    synchronize_session=False)
                # print(agg_value)
            db.commit()
            total_ship_calculation(item.ownership_id, db)

        return {"status": "success"}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))
