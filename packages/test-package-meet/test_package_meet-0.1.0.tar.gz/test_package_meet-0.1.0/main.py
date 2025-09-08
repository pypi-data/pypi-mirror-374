from examples.first_model import user, Product
from model_behavior.assignments.task import Booking
from nested_models.examples.nested_model import address, delivery, comment
from serialization.examples.serialization import meet

if __name__ == "__main__":
    print(user)

    product_data: Product = Product(id=55, name="perfume", in_stock=True, price=499)
    print(product_data.model_dump_json())

    booking: Booking = Booking(user_id=10, room_id=20, nights=3, rate_per_night=10)
    print(booking.model_dump_json())

    print(address.model_dump_json())
    print(delivery.model_dump_json())
    print(comment.model_dump_json())

    print(meet.model_dump_json())
    print(meet.model_dump())
