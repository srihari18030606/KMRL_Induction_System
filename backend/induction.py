def evaluate_trains(trains, traffic_level=3):

    HARD_MAINTENANCE_LIMIT = 30000

    service = []
    standby = []
    maintenance = []

    # ---------------------------
    # STEP 1: HARD SAFETY FILTER
    # ---------------------------
    eligible = []

    for train in trains:
        reasons = []

        if not train.fitness_valid:
            reasons.append("Fitness certificate invalid")

        if train.open_job_card:
            reasons.append("Open job card pending")

        if not train.cleaning_completed:
            reasons.append("Cleaning not completed")

        if train.mileage > HARD_MAINTENANCE_LIMIT:
            reasons.append("Exceeded maximum safe mileage limit")

        if train.sensor_alert:
            reasons.append("IoT sensor alert detected")

        if reasons:
            maintenance.append({
                "train": train.name,
                "category": "maintenance",
                "why": f"Sent to maintenance because: {', '.join(reasons)}"
            })
        else:
            eligible.append(train)

    if not eligible:
        return {
            "service": [],
            "standby": [],
            "maintenance": maintenance
        }

    # ---------------------------
    # STEP 2: FIXED SCORING
    # ---------------------------
    max_mileage = max(t.mileage for t in eligible)
    if max_mileage == 0:
        max_mileage = 1

    max_branding = max(t.branding_priority for t in eligible)
    if max_branding == 0:
        max_branding = 1

    scored = []

    for train in eligible:

        mileage_factor = 1 - (train.mileage / max_mileage)
        branding_factor = train.branding_priority / max_branding

        score = (mileage_factor * 0.7) + (branding_factor * 0.3)

        scored.append({
            "train": train.name,
            "score": round(score, 3),
            "mileage": train.mileage,
            "branding": train.branding_priority
        })

    scored.sort(key=lambda x: x["score"], reverse=True)

    # ---------------------------
    # STEP 3: TRAFFIC-BASED SERVICE SPLIT
    # ---------------------------
    demand_map = {
        1: 0.4,
        2: 0.55,
        3: 0.7,
        4: 0.85,
        5: 0.95
    }

    percentage = demand_map.get(traffic_level, 0.7)
    service_count = round(len(scored) * percentage)

    # Ensure at least 1 standby if more than 1 eligible
    if len(scored) > 1 and service_count >= len(scored):
        service_count = len(scored) - 1

    if service_count == 0 and len(scored) > 0:
        service_count = 1

    # ---------------------------
    # STEP 4: CATEGORIZE + PARKING
    # ---------------------------
    current_slot = 1

    for index, train in enumerate(scored):

        explanation = (
            f"Cleared all safety checks. "
            f"Mileage: {train['mileage']} km (lower mileage preferred). "
            f"Branding priority: {train['branding']}. "
            f"Composite score: {train['score']}."
        )

        if index < service_count:
            service.append({
                "train": train["train"],
                "score": train["score"],
                "parking_slot": current_slot,
                "why": explanation + " Selected for service due to highest operational suitability."
            })
        else:
            standby.append({
                "train": train["train"],
                "score": train["score"],
                "parking_slot": current_slot,
                "why": explanation + " Assigned to standby to maintain operational buffer."
            })

        current_slot += 1

    return {
        "service": service,
        "standby": standby,
        "maintenance": maintenance
    }