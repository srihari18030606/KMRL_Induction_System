def evaluate_trains(trains, branding_weight=2, mileage_weight=3, risk_weight=5):
    selected = []
    rejected = []

    # Calculate average mileage
    valid_mileages = [t.mileage for t in trains if t.fitness_valid and not t.open_job_card and t.cleaning_available]
    
    avg_mileage = sum(valid_mileages) / len(valid_mileages) if valid_mileages else 0

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
            # Mileage balance score (closer to average is better)
            mileage_diff = abs(train.mileage - avg_mileage)
            # mileage_score = max(0, 100 - mileage_diff)
            mileage_score = max(0, (1 - (mileage_diff / 30000)) * 100)

            # Maintenance risk (simulate)
            maintenance_risk = 1 if train.mileage > 25000 else 0

            score = (
                train.branding_priority * branding_weight
                + mileage_score * mileage_weight
                - maintenance_risk * risk_weight
            )

            selected.append({
                "train": train.name,
                "score": score,
                "details": {
                    "branding": train.branding_priority,
                    "mileage_score": mileage_score,
                    "maintenance_risk": maintenance_risk
                }
            })

    selected = sorted(selected, key=lambda x: x["score"], reverse=True)

    return selected, rejected