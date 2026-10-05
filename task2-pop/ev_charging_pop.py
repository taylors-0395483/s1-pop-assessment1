def main():
    process_another = "YES"
    while process_another == "YES":
        # Collect user, vehicle and charging information.
        user_id = input("User ID: ").strip()
        vehicle_number = input("Vehicle number: ").strip()

        member_type = input("Member type (STAFF/STUDENT/OTHER): ")
        member_type = member_type.strip().upper()
        while member_type not in ["STAFF", "STUDENT", "OTHER"]:
            print("Please enter STAFF, STUDENT or OTHER.")
            member_type = input("Member type: ").strip().upper()

        charger_type = input("Charger type (AC/DC): ").strip().upper()
        while charger_type not in ["AC", "DC"]:
            print("Please enter AC or DC.")
            charger_type = input("Charger type: ").strip().upper()

        # Enter a number; repeat if the charging time is zero or negative.
        hours_charged = float(input("Hours charged: "))
        while hours_charged <= 0:
            print("Charging hours must be greater than zero.")
            hours_charged = float(input("Hours charged: "))

        # Collect special conditions affecting the bill.
        first_time_user = input("First-time user? (YES/NO): ").strip().upper()
        while first_time_user not in ["YES", "NO"]:
            print("Please enter YES or NO.")
            first_time_user = input("First-time user? (YES/NO): ")
            first_time_user = first_time_user.strip().upper()

        eco_pass_holder = input("Eco-Pass holder? (YES/NO): ").strip().upper()
        while eco_pass_holder not in ["YES", "NO"]:
            print("Please enter YES or NO.")
            eco_pass_holder = input("Eco-Pass holder? (YES/NO): ")
            eco_pass_holder = eco_pass_holder.strip().upper()

        peak_hour_charging = input(
            "Does charging overlap 12 PM to 4 PM? (YES/NO): "
        ).strip().upper()
        while peak_hour_charging not in ["YES", "NO"]:
            print("Please enter YES or NO.")
            peak_hour_charging = input(
                "Does charging overlap 12 PM to 4 PM? (YES/NO): "
            ).strip().upper()

        idle_parking = input("Occupying bay after full charge? (YES/NO): ")
        idle_parking = idle_parking.strip().upper()
        while idle_parking not in ["YES", "NO"]:
            print("Please enter YES or NO.")
            idle_parking = input("Occupying bay after full charge? (YES/NO): ")
            idle_parking = idle_parking.strip().upper()

        lost_card = (
            input("Replace a lost RFID card? (YES/NO): ").strip().upper()
        )
        while lost_card not in ["YES", "NO"]:
            print("Please enter YES or NO.")
            lost_card = input("Replace a lost RFID card? (YES/NO): ")
            lost_card = lost_card.strip().upper()

        # Set the hourly rates and charging fee cap.
        if charger_type == "AC":
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

        # Take the integer part and add one if a fractional part remains.
        billable_hours = int(hours_charged)
        if hours_charged > billable_hours:
            billable_hours += 1

        # Apply each rate only to the hours within its tier.
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
                    2 * rate_1
                    + 2 * rate_2
                    + 2 * rate_3
                    + (billable_hours - 6) * overtime_rate
            )

        # Cap the total basic charging fee before applying discounts.
        if gross_fee > fee_cap:
            gross_fee = fee_cap

        # Reset and calculate the additional charges for this vehicle.
        peak_surcharge = 0
        idle_surcharge = 0
        card_fee = 0

        # Add RM 5 once per session if charging overlaps 12 PM to 4 PM.
        if peak_hour_charging == "YES":
            peak_surcharge = 5

        # Add the flat fee for occupying the bay after charging is complete.
        if idle_parking == "YES":
            idle_surcharge = 15

        # Add the replacement fee for a lost RFID access card.
        if lost_card == "YES":
            card_fee = 30

        total_surcharges = peak_surcharge + idle_surcharge + card_fee

        # Reset and evaluate waivers and discounts.
        first_time_waiver = 0
        member_discount = 0
        eco_discount = 0

        # Give the first-time waiver priority over the member discount.
        if first_time_user == "YES":
            first_time_waiver = gross_fee + total_surcharges
        else:
            # Staff receive a 50% discount on the gross charging fee.
            if member_type == "STAFF":
                member_discount = gross_fee * 0.50
            # The student discount applies to AC charging only.
            elif member_type == "STUDENT" and charger_type == "AC":
                member_discount = gross_fee * 0.25

        subtotal = (gross_fee + total_surcharges - first_time_waiver - member_discount)

        # Apply the Eco-Pass discount only when a payment remains.
        if eco_pass_holder == "YES" and subtotal > 0:
            # Limit the discount to the remaining amount payable.
            if subtotal >= 2:
                eco_discount = 2
            else:
                eco_discount = subtotal

        net_payable = subtotal - eco_discount

        # Display an itemized bill with amounts to two decimal places.
        print("\n" + "=" * 42)
        print("EV CHARGING BILL")
        print("=" * 42)
        print(f"User ID: {user_id}")
        print(f"Vehicle Number: {vehicle_number}")
        print(f"Member Type: {member_type}")
        print(f"Charger Type: {charger_type}")
        print(f"Actual Hours: {hours_charged:g}")
        print(f"Billable Hours: {billable_hours}")
        print(f"Gross Charging Fee: RM {gross_fee:.2f}")
        print(f"First-Time Waiver: RM {first_time_waiver:.2f}")
        print(f"Member Discount: RM {member_discount:.2f}")
        print(f"Eco-Pass Discount: RM {eco_discount:.2f}")
        print(f"Peak Surcharge: RM {peak_surcharge:.2f}")
        print(f"Idle Parking Surcharge: RM {idle_surcharge:.2f}")
        print(f"Card Replacement Fee: RM {card_fee:.2f}")
        print(f"Net Payable: RM {net_payable:.2f}")
        print("=" * 42)
        # Process another vehicle without restarting the program.
        process_another = input("Process another vehicle? (YES/NO): ")
        process_another = process_another.strip().upper()
        while process_another not in ["YES", "NO"]:
            print("Please enter YES or NO.")
            process_another = input("Process another vehicle? (YES/NO): ")
            process_another = process_another.strip().upper()
    print("Program ended.")


if __name__ == "__main__":
    main()
