import os
import sys
import time
from sqlalchemy import select
from .persistence import database, Outbox, MockReceipt

def tick(factory, mode: str = "mock") -> int:
    """외부 호출 없이 DB receipt와 처리 상태를 함께 커밋한다."""
    if mode != "mock":
        raise RuntimeError("real adapters are not implemented")
    count = 0
    with factory.begin() as session:
        rows = session.scalars(select(Outbox).where(Outbox.status == "pending").with_for_update()).all()
        for item in rows:
            if not session.get(MockReceipt, item.id):
                session.add(MockReceipt(outbox_id=item.id))
            item.status = "succeeded"
            count += 1
    return count

if __name__ == "__main__":
    engine, factory = database()
    while True:
        tick(factory, os.getenv("ADAPTER_MODE", "mock"))
        if "--loop" not in sys.argv:
            break
        time.sleep(2)
