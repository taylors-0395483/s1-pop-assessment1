class User:
    def __init__(self, user_id, first_time_user, eco_pass_holder):
        self.__user_id = user_id
        self.__first_time_user = first_time_user
        self.__eco_pass_holder = eco_pass_holder
        self.__sessions = []

    def get_user_id(self):
        return self.__user_id

    def set_user_id(self, user_id):
        if user_id.strip() != "":
            self.__user_id = user_id.strip()
        else:
            print("User ID cannot be empty.")

    def get_first_time_user(self):
        return self.__first_time_user

    def set_first_time_user(self, first_time_user):
        first_time_user = first_time_user.strip().upper()
        if first_time_user in ["YES", "NO"]:
            self.__first_time_user = first_time_user
        else:
            print("Please enter YES or NO.")

    def get_eco_pass_holder(self):
        return self.__eco_pass_holder

    def set_eco_pass_holder(self, eco_pass_holder):
        eco_pass_holder = eco_pass_holder.strip().upper()
        if eco_pass_holder in ["YES", "NO"]:
            self.__eco_pass_holder = eco_pass_holder
        else:
            print("Please enter YES or NO.")

    # Composition: the user creates and keeps its charging session records.
    def create_session(self, vehicle_number, hours, peak, idle, lost, charger):
        session = ChargingSession(
            vehicle_number, hours, peak, idle, lost, charger
        )
        self.__sessions.append(session)
        return session

    def calculate_fee(self, session):
        charger = session.get_charger()
        gross_fee = charger.calculate_gross_fee(
            session.get_hours_charged()
        )
        bill = session.calculate_surcharges()
        bill["gross_fee"] = gross_fee
        bill["first_time_waiver"] = 0
        bill["member_discount"] = 0
        bill["eco_discount"] = 0
        total = gross_fee + bill["peak_surcharge"]
        total += bill["idle_surcharge"] + bill["card_fee"]

        # First-time users pay nothing, including the additional fees.
        if self.__first_time_user == "YES":
            bill["first_time_waiver"] = total
            total = 0

        # Apply Eco-Pass only when an amount remains payable.
        if self.__eco_pass_holder == "YES" and total > 0:
            if total >= 2:
                bill["eco_discount"] = 2
            else:
                bill["eco_discount"] = total
        bill["net_payable"] = total - bill["eco_discount"]
        return bill


# Inheritance: staff and student members are also users.
class MemberUser(User):
    def __init__(self, user_id, first_time_user, eco_pass_holder, member_type):
        super().__init__(user_id, first_time_user, eco_pass_holder)
        self.__member_type = member_type

    def get_member_type(self):
        return self.__member_type

    def set_member_type(self, member_type):
        member_type = member_type.strip().upper()
        if member_type in ["STAFF", "STUDENT"]:
            self.__member_type = member_type
        else:
            print("Please enter STAFF or STUDENT.")

    # Calculate the member's bill in order: waiver, discount, then Eco-Pass.
    def calculate_fee(self, session):
        charger = session.get_charger()
        hours = session.get_hours_charged()
        gross_fee = charger.calculate_gross_fee(hours)
        bill = session.calculate_surcharges()
        bill["gross_fee"] = gross_fee
        bill["first_time_waiver"] = 0
        bill["member_discount"] = 0
        bill["eco_discount"] = 0
        total = gross_fee + bill["peak_surcharge"]
        total += bill["idle_surcharge"] + bill["card_fee"]

        if self.get_first_time_user() == "YES":
            bill["first_time_waiver"] = total
        else:
            if self.__member_type == "STAFF":
                bill["member_discount"] = gross_fee * 0.50
            elif (
                    self.__member_type == "STUDENT"
                    and charger.get_charger_type() == "AC"
            ):
                bill["member_discount"] = gross_fee * 0.25

        subtotal = total - bill["first_time_waiver"]
        subtotal -= bill["member_discount"]
        if self.get_eco_pass_holder() == "YES" and subtotal > 0:
            if subtotal >= 2:
                bill["eco_discount"] = 2
            else:
                bill["eco_discount"] = subtotal
        bill["net_payable"] = subtotal - bill["eco_discount"]
        return bill


class EVCharger:
    def __init__(self, charger_type):
        self.__charger_type = charger_type

    def get_charger_type(self):
        return self.__charger_type

    def set_charger_type(self, charger_type):
        charger_type = charger_type.strip().upper()
        if charger_type in ["AC", "DC"]:
            self.__charger_type = charger_type
        else:
            print("Please enter AC or DC.")

    def calculate_gross_fee(self, hours):
        if self.__charger_type == "AC":
            rate_1 = 4
            rate_2 = 6
            rate_3 = 8
            overtime_rate = 12
            fee_cap = 80
        else:
            rate_1 = 10
            rate_2 = 15
            rate_3 = 20
            overtime_rate = 30
            fee_cap = 150

        # Add one hour if a fractional part remains after taking the integer.
        billable_hours = int(hours)
        if hours > billable_hours:
            billable_hours += 1
        if billable_hours <= 2:
            gross_fee = billable_hours * rate_1
        elif billable_hours <= 4:
            gross_fee = 2 * rate_1 + (billable_hours - 2) * rate_2
        elif billable_hours <= 6:
            gross_fee = (
                    2 * rate_1 + 2 * rate_2 + (billable_hours - 4) * rate_3
            )
        else:
            gross_fee = (
                    2 * rate_1 + 2 * rate_2 + 2 * rate_3
                    + (billable_hours - 6) * overtime_rate
            )

        # The cap applies to the whole basic charging fee, before discounts.
        if gross_fee > fee_cap:
            gross_fee = fee_cap
        return gross_fee


class ChargingSession:
    def __init__(self, vehicle_number, hours, peak, idle, lost, charger):
        self.__vehicle_number = vehicle_number
        self.__hours_charged = hours
        self.__peak_hour_charging = peak
        self.__idle_parking = idle
        self.__lost_card = lost
        self.__charger = charger

    def get_vehicle_number(self):
        return self.__vehicle_number

    def set_vehicle_number(self, vehicle_number):
        if vehicle_number.strip() != "":
            self.__vehicle_number = vehicle_number.strip()
        else:
            print("Vehicle number cannot be empty.")

    def get_hours_charged(self):
        return self.__hours_charged

    # Update only valid values; keep the original value if validation fails.
    def set_hours_charged(self, hours):
        if hours > 0:
            self.__hours_charged = hours
        else:
            print("Charging hours must be greater than zero.")

    def set_peak_hour_charging(self, peak):
        peak = peak.strip().upper()
        if peak in ["YES", "NO"]:
            self.__peak_hour_charging = peak
        else:
            print("Please enter YES or NO.")

    def set_idle_parking(self, idle):
        idle = idle.strip().upper()
        if idle in ["YES", "NO"]:
            self.__idle_parking = idle
        else:
            print("Please enter YES or NO.")

    def set_lost_card(self, lost):
        lost = lost.strip().upper()
        if lost in ["YES", "NO"]:
            self.__lost_card = lost
        else:
            print("Please enter YES or NO.")

    def get_charger(self):
        return self.__charger

    # Association: a session refers to an independently created charger.
    def set_charger(self, charger):
        if isinstance(charger, EVCharger):
            self.__charger = charger
        else:
            print("The charger must be an EVCharger object.")

    def calculate_surcharges(self):
        bill = {"peak_surcharge": 0, "idle_surcharge": 0, "card_fee": 0}

        # Add RM 5 once when the session overlaps 12 PM to 4 PM.
        if self.__peak_hour_charging == "YES":
            bill["peak_surcharge"] = 5
        if self.__idle_parking == "YES":
            bill["idle_surcharge"] = 15
        if self.__lost_card == "YES":
            bill["card_fee"] = 30
        return bill


# Use a loop to repeat the question when the choice is invalid.
def read_choice(prompt, choices):
    value = input(prompt).strip().upper()
    while value not in choices:
        print("Invalid choice. Please try again.")
        value = input(prompt).strip().upper()
    return value


def read_text(prompt):
    value = input(prompt).strip()
    while not value:
        print("This value cannot be empty.")
        value = input(prompt).strip()
    return value


def main():
    process_another = "YES"
    while process_another == "YES":
        user_id = read_text("User ID: ")
        vehicle_number = read_text("Vehicle number: ")
        member_type = read_choice(
            "Member type (STAFF/STUDENT/OTHER): ",
            ["STAFF", "STUDENT", "OTHER"]
        )
        charger_type = read_choice("Charger type (AC/DC): ", ["AC", "DC"])

        # Enter a number; repeat if the charging time is zero or negative.
        hours = float(input("Hours charged: "))
        while hours <= 0:
            print("Charging hours must be greater than zero.")
            hours = float(input("Hours charged: "))

        first_time = read_choice("First-time user? (YES/NO): ", ["YES", "NO"])
        eco_pass = read_choice("Eco-Pass holder? (YES/NO): ", ["YES", "NO"])
        peak = read_choice("Does charging overlap 12 PM to 4 PM? (YES/NO): ", ["YES", "NO"])
        idle = read_choice("Occupying bay after full charge? (YES/NO): ", ["YES", "NO"])
        lost = read_choice("Replace a lost RFID card? (YES/NO): ", ["YES", "NO"])

        # Create the appropriate user object and its charging session.
        if member_type == "OTHER":
            user = User(user_id, first_time, eco_pass)
        else:
            user = MemberUser(user_id, first_time, eco_pass, member_type)
        charger = EVCharger(charger_type)
        session = user.create_session(
            vehicle_number, hours, peak, idle, lost, charger
        )

        # Polymorphism: the same call runs the actual user type's method.
        bill = user.calculate_fee(session)

        billable_hours = int(hours)
        if hours > billable_hours:
            billable_hours += 1

        print("\n" + "=" * 42)
        print("EV CHARGING BILL")
        print("=" * 42)
        print(f"User ID: {user.get_user_id()}")
        print(f"Vehicle Number: {session.get_vehicle_number()}")
        print(f"Member Type: {member_type}")
        print(f"Charger Type: {charger.get_charger_type()}")
        print(f"Actual Hours: {session.get_hours_charged():g}")
        print(f"Billable Hours: {billable_hours}")
        print(f"Gross Charging Fee: RM {bill['gross_fee']:.2f}")
        print(f"First-Time Waiver: RM {bill['first_time_waiver']:.2f}")
        print(f"Member Discount: RM {bill['member_discount']:.2f}")
        print(f"Eco-Pass Discount: RM {bill['eco_discount']:.2f}")
        print(f"Peak Surcharge: RM {bill['peak_surcharge']:.2f}")
        print(f"Idle Parking Surcharge: RM {bill['idle_surcharge']:.2f}")
        print(f"Card Replacement Fee: RM {bill['card_fee']:.2f}")
        print(f"Net Payable: RM {bill['net_payable']:.2f}")
        print("=" * 42)

        process_another = read_choice("Process another vehicle? (YES/NO): ", ["YES", "NO"])
    print("Program ended.")


if __name__ == "__main__":
    main()
