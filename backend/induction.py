def evaluate_trains(trains, branding_weight=2, mileage_weight=3, risk_weight=5):
    selected = []
    rejected = []

    # First filter valid trains (for mileage normalization)
    valid_trains = [
        t for t in trains
        if t.fitness_valid and not t.open_job_card and t.cleaning_available
    ]

    # If no valid trains
    if not valid_trains:
        return [], [
            {
                "train": t.name,
                "reasons": [
                    reason for reason in [
                        "Fitness expired" if not t.fitness_valid else None,
                        "Open job card" if t.open_job_card else None,
                        "Cleaning not available" if not t.cleaning_available else None
                    ] if reason is not None
                ]
            }
            for t in trains
        ]

    # Find maximum mileage among valid trains
    max_mileage = max(t.mileage for t in valid_trains)

    # Avoid division by zero
    if max_mileage == 0:
        max_mileage = 1

    for train in trains:
        reasons = []

        # Hard constraints
        if not train.fitness_valid:
            reasons.append("Fitness expired")

        if train.open_job_card:
            reasons.append("Open job card")

        if not train.cleaning_available:
            reasons.append("Cleaning not available")

        if reasons:
            rejected.append({"train": train.name, "reasons": reasons})
        else:
            # Prefer lower mileage
            mileage_score = (1 - (train.mileage / max_mileage)) * 100

            # Maintenance risk
            maintenance_risk = 1 if train.mileage > 25000 else 0

            score = (
                train.branding_priority * branding_weight
                + mileage_score * mileage_weight
                - maintenance_risk * risk_weight
            )

            selected.append({
                "train": train.name,
                "score": round(score, 2),
                "details": {
                    "branding": train.branding_priority,
                    "mileage_score": round(mileage_score, 2),
                    "maintenance_risk": maintenance_risk
                }
            })

    selected = sorted(selected, key=lambda x: x["score"], reverse=True)

    return selected, rejected