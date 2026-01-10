from datetime import datetime
from eleven_video.models.quota import QuotaInfo # Will fail import until created, which is correct for RED phase
from faker import Faker

faker = Faker()

def createQuotaInfo(overrides=None):
    if overrides is None:
        overrides = {}
        
    return QuotaInfo(
        service=overrides.get("service", faker.company()),
        used=overrides.get("used", faker.random_int(min=0, max=5000)),
        limit=overrides.get("limit", faker.random_int(min=5000, max=10000)),
        unit=overrides.get("unit", "chars"),
        reset_date=overrides.get("reset_date", datetime.now())
    )
