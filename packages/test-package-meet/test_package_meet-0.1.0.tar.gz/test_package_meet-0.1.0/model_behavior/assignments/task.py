from pydantic import BaseModel, Field, computed_field


class Booking(BaseModel):
    user_id: int = Field(...)
    room_id: int = Field(...)
    nights: int = Field(...)
    rate_per_night: float = Field(...)

    @computed_field
    @property
    def total_amount_per_night(self) -> float:
        return self.nights * self.rate_per_night
