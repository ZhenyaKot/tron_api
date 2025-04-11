import os

import aiohttp
from dotenv import load_dotenv, find_dotenv
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func

from database import new_session, TaskOrm
from schemas import STaskResponse, STaskRequest, STaskListResponse

load_dotenv(find_dotenv())

router = APIRouter(
    prefix='/tasks',
    tags=['Задачи']
)


# Эндпоинт для получения информации о кошельке
@router.post("/wallet-info", response_model=STaskResponse)
async def get_wallet_info(wallet_request: STaskRequest) -> STaskResponse:
    address = wallet_request.address
    url = f"https://api.trongrid.io/v1/accounts/{address}"

    headers = {
        'accept': "application/json",
        'TRON-PRO-API-KEY': os.environ.get("API_KEY")
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()

                if not data.get('data') or len(data['data']) == 0:
                    raise HTTPException(
                        status_code=404,
                        detail="Wallet not found or has no transactions"
                    )

                wallet_data = data['data'][0]

                balance_sun = wallet_data.get('balance', 0)
                balance_trx = balance_sun / 1_000_000

                bandwidth = wallet_data.get('net_window_size', 0)

                energy = 0
                if 'account_resource' in wallet_data:
                    energy = wallet_data['account_resource'].get('energy_window_size', 0)

                async with new_session() as db_session:
                    wallet_info = TaskOrm(
                        address=wallet_data['address'],
                        balance=balance_trx,
                        bandwidth=bandwidth,
                        energy=energy
                    )
                    db_session.add(wallet_info)
                    await db_session.commit()
                    await db_session.refresh(wallet_info)

                return STaskResponse(
                    id=wallet_info.id,
                    address=wallet_info.address,
                    balance=wallet_info.balance,
                    bandwidth=wallet_info.bandwidth,
                    energy=wallet_info.energy
                )
            else:
                error_data = await response.json()
                raise HTTPException(
                    status_code=response.status,
                    detail=error_data.get('error', 'Unknown error from TronGrid API')
                )


@router.get("/wallet-history", response_model=STaskListResponse)
async def get_wallet_history(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100)
) -> STaskListResponse:
    async with new_session() as session:
        total = (await session.execute(select(func.count(TaskOrm.id)))).scalar_one()

        result = await session.execute(
            select(TaskOrm)
            .order_by(TaskOrm.id.desc())
            .offset(skip)
            .limit(limit)
        )
        items = result.scalars().all()

        task_responses = [
            STaskResponse(
                id=item.id,
                address=item.address,
                balance=item.balance,
                bandwidth=item.bandwidth,
                energy=item.energy,
            )
            for item in items
        ]

        return STaskListResponse(
            items=task_responses,
            total=total,
            page=skip // limit + 1,
            size=limit
        )
