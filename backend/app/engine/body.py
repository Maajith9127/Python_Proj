"""Domain 5: Body Composition, Ideal Weight & Comprehensive 24-Metric Synthesis (Formulas 21–24)."""
from __future__ import annotations
import math
from . import cardio, metabolic, strength, training
from .metabolic import MetricError


def bmi_analysis(weight: float, height: float) -> dict:
    """Formula 21: Body Mass Index (BMI), BMI Prime & Rohrer's Ponderal Index."""
    h_m = height / 100
    bmi = round(weight / (h_m ** 2), 1)
    bmi_prime = round(bmi / 25.0, 2)
    ponderal = round(weight / (h_m ** 3), 2)
    if bmi < 18.5:
        cat = "Underweight"
    elif bmi < 25.0:
        cat = "Normal"
    elif bmi < 30.0:
        cat = "Overweight"
    else:
        cat = "Obese"
    return {
        "bmi": bmi,
        "category": cat,
        "bmiPrime": bmi_prime,
        "ponderalIndex": ponderal,
        "healthyWeightMinKg": round(18.5 * (h_m ** 2), 1),
        "healthyWeightMaxKg": round(24.9 * (h_m ** 2), 1),
    }


def body_fat_navy(
    gender: str,
    height: float,
    neck: float,
    waist: float,
    hip: float | None = None,
    weight: float | None = None,
) -> dict:
    """Formula 22: Body Fat Percentage (U.S. Navy Circumference Method) + Fat & Lean Mass."""
    if gender == "male":
        if waist <= neck:
            raise MetricError("waist must be larger than neck")
        bf = 495 / (1.0324 - 0.19077 * math.log10(waist - neck) + 0.15456 * math.log10(height)) - 450
        bands = [(6, "Essential"), (14, "Athletic"), (18, "Fitness"), (25, "Average")]
    else:
        if hip is None:
            raise MetricError("hip is required for female body-fat calculation")
        if waist + hip <= neck:
            raise MetricError("waist + hip must be larger than neck")
        bf = 495 / (1.29579 - 0.35004 * math.log10(waist + hip - neck) + 0.22100 * math.log10(height)) - 450
        bands = [(14, "Essential"), (21, "Athletic"), (25, "Fitness"), (32, "Average")]
    bf = round(max(2.0, bf), 1)
    out = {
        "bodyFat": bf,
        "category": next((n for lim, n in bands if bf < lim), "Above Average"),
        "method": "US Navy Circumference Method",
    }
    if weight:
        out["fatMass"] = round(weight * bf / 100, 1)
        out["leanMass"] = round(weight - out["fatMass"], 1)
    return out


def ideal_body_weight(height: float, gender: str) -> dict:
    """Formula 23: Ideal Body Weight Range (Hamwi, Devine, Robinson & Miller Equations)."""
    inches_over_5ft = max(0.0, (height / 2.54) - 60.0)
    if gender == "male":
        hamwi = 48.0 + 2.7 * inches_over_5ft
        devine = 50.0 + 2.3 * inches_over_5ft
        robinson = 52.0 + 1.9 * inches_over_5ft
        miller = 56.2 + 1.41 * inches_over_5ft
    else:
        hamwi = 45.5 + 2.2 * inches_over_5ft
        devine = 45.5 + 2.3 * inches_over_5ft
        robinson = 49.0 + 1.7 * inches_over_5ft
        miller = 53.1 + 1.36 * inches_over_5ft

    avg_ibw = round((hamwi + devine + robinson + miller) / 4, 1)
    return {
        "idealWeightKg": avg_ibw,
        "hamwiKg": round(hamwi, 1),
        "devineKg": round(devine, 1),
        "robinsonKg": round(robinson, 1),
        "millerKg": round(miller, 1),
        "rangeKg": {"min": round(avg_ibw * 0.9, 1), "max": round(avg_ibw * 1.1, 1)},
    }


def comprehensive_24_analysis(d: dict) -> dict:
    """Master 24-Formula Synthesis Engine — runs all 5 fitness domains in one call."""
    age = d["age"]
    gender = d["gender"]
    height = d["height"]
    weight = d["weight"]
    activity_level = d.get("activityLevel", "moderate")
    goal = d.get("goal", "maintain")
    neck = d.get("neck", 38.0)
    waist = d.get("waist", 84.0)
    hip = d.get("hip", 96.0 if gender == "female" else None)

    bf = body_fat_navy(gender, height, neck, waist, hip, weight)
    bmi = bmi_analysis(weight, height)
    ibw = ideal_body_weight(height, gender)
    energy = metabolic.energy_profile(age, gender, height, weight, activity_level, goal, bf["bodyFat"])
    workout = training.analyse_workout(
        d.get("activity", "running"),
        d.get("duration", 45),
        weight,
        age,
        d.get("restingHr", 62),
        d.get("avgHr", 172),
        gender,
        d.get("climate", "normal"),
    )
    zones = cardio.hr_zones(age, d.get("restingHr", 62))
    vo2 = cardio.vo2max_analysis(
        age, gender, d.get("restingHr", 62), d.get("maxHr"), d.get("cooperDistance")
    )
    pace_res = cardio.pace_and_predictions(
        d.get("paceActivity", "running"), d.get("distanceKm", 5.0), d.get("paceDurationMin", 25.0)
    )
    lift_res = strength.analyse_lift(
        d.get("exercise", "bench_press"), d.get("liftWeight", 80.0), d.get("liftReps", 6), weight
    )
    vol_res = strength.session_volume(
        d.get("sets") or [{"exercise": "bench_press", "weight": 80, "reps": 6}, {"exercise": "squat", "weight": 100, "reps": 5}],
        weight,
    )
    loads = d.get("dailyLoads") or [55, 0, 70, 0, 60, 85, 0, 60, 0, 75, 0, 65, 90, 0, 65, 0, 80, 0, 70, 95, 0, 121, 0, 68, 0, 47, 95, 0]
    acwr_res = training.training_balance(loads)
    ready_res = training.readiness(
        d.get("lastLoad", workout["trainingLoad"]),
        d.get("hoursSince", 36),
        d.get("restingHr", 62),
        d.get("baselineRestingHr", 62),
        d.get("sleepHours", 7.5),
        d.get("soreness", 2),
    )

    # -------------------------------------------------------------------------
    # 24-Formula Analytical Matrix (Equation + Variables + Meaning + Example)
    # -------------------------------------------------------------------------
    formulas_summary = [
        # DOMAIN 1: METABOLIC & ENERGY (Formulas 1–4)
        {
            "id": 1,
            "domain": "Metabolic",
            "name": "BMR (Mifflin-St Jeor)",
            "value": f"{energy['bmrMifflinStJeor']} kcal/day",
            "formula": "BMR = 10×W + 6.25×H − 5×A + S",
            "variables": f"W = Weight ({weight} kg) · H = Height ({height} cm) · A = Age ({age} yrs) · S = Sex constant (+5 male, −161 female)",
            "meaning": "Resting calories your body burns in 24h just to stay alive (breathing, organs, circulation).",
            "example": f"10×{weight} + 6.25×{height} − 5×{age} {'+ 5' if gender == 'male' else '− 161'} = {energy['bmrMifflinStJeor']} kcal/day burned at complete rest.",
        },
        {
            "id": 2,
            "domain": "Metabolic",
            "name": "BMR (Harris-Benedict)",
            "value": f"{energy['bmrHarrisBenedict']} kcal/day",
            "formula": "BMR = 88.362 + 13.397×W + 4.799×H − 5.677×A",
            "variables": f"W = Weight ({weight} kg) · H = Height ({height} cm) · A = Age ({age} yrs) · 88.362 = Male intercept (447.593 female)",
            "meaning": "Classic clinical BMR cross-check; slightly higher than Mifflin-St Jeor for active builds.",
            "example": f"88.362 + 13.397×{weight} + 4.799×{height} − 5.677×{age} = {energy['bmrHarrisBenedict']} kcal/day clinical baseline.",
        },
        {
            "id": 3,
            "domain": "Metabolic",
            "name": "TDEE & Katch-McArdle BMR",
            "value": f"{energy['tdee']} kcal/day (Katch: {energy['bmrKatchMcArdle']} kcal)",
            "formula": "TDEE = BMR × AF · Katch_BMR = 370 + 21.6 × LBM",
            "variables": f"BMR = Resting calories ({energy['bmrMifflinStJeor']}) · AF = Activity Factor ({energy['activityMultiplier']} for {activity_level}) · LBM = Lean Body Mass ({bf['leanMass']} kg)",
            "meaning": "Total Daily Energy Expenditure to maintain current weight; Katch-McArdle computes BMR purely from lean muscle mass.",
            "example": f"{energy['bmrMifflinStJeor']} × {energy['activityMultiplier']} = {energy['tdee']} kcal/day TDEE; Katch = 370 + 21.6×{bf['leanMass']} = {energy['bmrKatchMcArdle']} kcal.",
        },
        {
            "id": 4,
            "domain": "Metabolic",
            "name": "Activity Calorie Burn (MET)",
            "value": f"{workout['caloriesBurned']} kcal ({workout['activity']})",
            "formula": "Calories = (MET × 3.5 × W ÷ 200) × T",
            "variables": f"MET = Metabolic Equivalent of Task for {workout['activity']} · W = Weight ({weight} kg) · T = Workout Duration ({d.get('duration', 45)} min) · 3.5 = Resting O2 constant (ml/kg/min)",
            "meaning": "Active calories burned during this specific sport session using Compendium of Physical Activities METs.",
            "example": f"{d.get('duration', 45)} min of {workout['activity']} at {weight} kg bodyweight burns {workout['caloriesBurned']} kcal.",
        },
        # DOMAIN 2: CARDIOVASCULAR & ENDURANCE (Formulas 5–10)
        {
            "id": 5,
            "domain": "Cardio",
            "name": "Max Heart Rate (Tanaka / Fox)",
            "value": f"{zones['tanaka']} bpm / {zones['fox']} bpm",
            "formula": "Tanaka_MHR = 208 − 0.7×A · Fox_MHR = 220 − A",
            "variables": f"A = Age ({age} yrs) · 208 & 0.7 = Tanaka regression constants · 220 = Classic Fox ceiling constant · MHR = Max Heart Rate (bpm)",
            "meaning": "Your ceiling heart rate during all-out effort; used to anchor safe training intensity zones.",
            "example": f"At age {age}, Tanaka = 208 − 0.7×{age} = {zones['tanaka']} bpm, and Fox = 220 − {age} = {zones['fox']} bpm.",
        },
        {
            "id": 6,
            "domain": "Cardio",
            "name": "Karvonen HR Reserve & Zones",
            "value": f"{zones['heartRateReserve']} bpm HRR · {workout['zone']}",
            "formula": "HRR = MHR − RHR · %HRR = (AvgHR − RHR) ÷ HRR",
            "variables": f"MHR = Max HR ({zones['maxHr']} bpm) · RHR = Resting HR ({d.get('restingHr', 62)} bpm) · AvgHR = Session Avg HR ({d.get('avgHr', 172)} bpm) · HRR = Heart Rate Reserve ({zones['heartRateReserve']} bpm)",
            "meaning": "Working heart-rate range (HRR) and which of the 5 training zones your session Avg HR falls into.",
            "example": f"HRR = {zones['maxHr']} − {d.get('restingHr', 62)} = {zones['heartRateReserve']} bpm. Avg HR {d.get('avgHr', 172)} bpm puts the athlete in {workout['zone']}.",
        },
        {
            "id": 7,
            "domain": "Cardio",
            "name": "VO2max (Cooper 12-min Model)",
            "value": f"{vo2['vo2maxCooper'] or 'N/A (optional)'} ml/kg/min",
            "formula": "VO2max = (D_12min − 504.9) ÷ 44.73",
            "variables": f"D_12min = Distance covered in a 12-minute run ({d.get('cooperDistance', 2800)} meters) · 504.9 & 44.73 = Cooper linear O2 regression constants",
            "meaning": "Field-test aerobic capacity (max milliliters of oxygen used per kg of bodyweight per minute) from a 12-minute run.",
            "example": f"({d.get('cooperDistance', 2800)} m − 504.9) ÷ 44.73 = {vo2['vo2maxCooper']} ml/kg/min of maximum oxygen uptake.",
        },
        {
            "id": 8,
            "domain": "Cardio",
            "name": "VO2max (Uth HR-Ratio Model)",
            "value": f"{vo2['vo2maxUth']} ml/kg/min ({vo2['rating']})",
            "formula": "VO2max = 15.3 × (MHR ÷ RHR)",
            "variables": f"MHR = Max Heart Rate ({zones['maxHr']} bpm) · RHR = Resting Heart Rate ({d.get('restingHr', 62)} bpm) · 15.3 = Uth proportionality factor (ml/kg/min)",
            "meaning": "Non-exercise VO2max estimate from heart-rate efficiency, plus your ACSM aerobic fitness tier.",
            "example": f"15.3 × ({zones['maxHr']} ÷ {d.get('restingHr', 62)}) = {vo2['vo2maxUth']} ml/kg/min, rated '{vo2['rating']}' for age {age}.",
        },
        {
            "id": 9,
            "domain": "Cardio",
            "name": "Pace & Speed Analysis",
            "value": f"{pace_res['paceMinPerKm']} /km ({pace_res['speedKmh']} km/h)",
            "formula": "Pace = T ÷ D · Speed = D ÷ (T ÷ 60)",
            "variables": f"T = Run Time ({d.get('paceDurationMin', 25)} min) · D = Distance ({d.get('distanceKm', 5.0)} km) · 60 = Minutes per hour conversion",
            "meaning": "Minutes taken per kilometer and average velocity in km/h for your timed run.",
            "example": f"Completing 5 km in {d.get('paceDurationMin', 25)} min = {pace_res['paceMinPerKm']} min/km pace at {pace_res['speedKmh']} km/h speed.",
        },
        {
            "id": 10,
            "domain": "Cardio",
            "name": "Riegel Race Prediction (10K)",
            "value": pace_res.get("predictions", {}).get("10K", {}).get("time", "—"),
            "formula": "T2 = T1 × (D2 ÷ D1)^1.06",
            "variables": f"T1 = Known 5K Time ({d.get('paceDurationMin', 25)} min) · D1 = Known Distance (5 km) · D2 = Target Race Distance (10 km) · 1.06 = Riegel endurance fatigue exponent",
            "meaning": "Predicts your 10K finish time from your 5K time accounting for a 6% endurance fatigue decay as distance doubles.",
            "example": f"{d.get('paceDurationMin', 25)} min × (10 km ÷ 5 km)^1.06 = {pace_res.get('predictions', {}).get('10K', {}).get('time', '—')} predicted 10K finish.",
        },
        # DOMAIN 3: STRENGTH & MUSCULAR POWER (Formulas 11–15)
        {
            "id": 11,
            "domain": "Strength",
            "name": "One-Rep Max (Epley Formula)",
            "value": f"{lift_res['epley']} kg",
            "formula": "1RM = L × (1 + R ÷ 30)",
            "variables": f"L = Lifted Weight ({d.get('liftWeight', 80)} kg) · R = Repetitions completed ({d.get('liftReps', 6)} reps) · 30 = Epley fatigue divisor (+3.33% per rep)",
            "meaning": "Estimated maximum weight you can lift for 1 single rep based on a submaximal set.",
            "example": f"{d.get('liftWeight', 80)} kg × (1 + {d.get('liftReps', 6)} ÷ 30) = {lift_res['epley']} kg estimated max single lift.",
        },
        {
            "id": 12,
            "domain": "Strength",
            "name": "One-Rep Max (Brzycki Formula)",
            "value": f"{lift_res['brzycki']} kg",
            "formula": "1RM = L × 36 ÷ (37 − R)",
            "variables": f"L = Lifted Weight ({d.get('liftWeight', 80)} kg) · R = Repetitions completed ({d.get('liftReps', 6)} reps) · 36 & 37 = Brzycki linear rep-decay constants",
            "meaning": "Conservative 1RM estimate that is highly accurate for lower rep ranges (1–10 reps).",
            "example": f"{d.get('liftWeight', 80)} kg × 36 ÷ (37 − {d.get('liftReps', 6)}) = {lift_res['brzycki']} kg conservative 1RM.",
        },
        {
            "id": 13,
            "domain": "Strength",
            "name": "Relative Strength Index",
            "value": f"{lift_res.get('relativeStrength', '—')} × BW",
            "formula": "RSI = 1RM_consensus ÷ BW",
            "variables": f"1RM_consensus = Mean of Epley, Brzycki & Lombardi 1RM ({lift_res['oneRepMax']} kg) · BW = Athlete Bodyweight ({weight} kg)",
            "meaning": "Pound-for-pound strength ratio comparing your 1-Rep Max directly against your bodyweight.",
            "example": f"{lift_res['oneRepMax']} kg consensus 1RM ÷ {weight} kg bodyweight = {lift_res.get('relativeStrength', '—')}× BW.",
        },
        {
            "id": 14,
            "domain": "Strength",
            "name": "Strength Level Classification",
            "value": lift_res.get("strengthLevel", "—"),
            "formula": "Tier = Lookup(RSI vs Lift Thresholds)",
            "variables": f"RSI = Relative Strength ({lift_res.get('relativeStrength', '—')}× BW) · Bench Thresholds: Beginner <0.75× · Novice ≥0.75× · Intermediate ≥1.25× · Advanced ≥1.5× · Elite ≥2.0×",
            "meaning": "Ranks your lift against strength standards for that movement.",
            "example": f"At {lift_res.get('relativeStrength', '—')}× BW on bench press, the athlete classifies as '{lift_res.get('strengthLevel', '—')}'.",
        },
        {
            "id": 15,
            "domain": "Strength",
            "name": "Total Session Volume",
            "value": f"{vol_res['totalVolumeKg']} kg ({vol_res['trainingFocus']})",
            "formula": "Volume = Σ (L_i × R_i) for i = 1..n sets",
            "variables": "L_i = Weight lifted in set i (kg) · R_i = Reps performed in set i · n = Total sets in workout",
            "meaning": "Total mechanical tonnage lifted in the gym session and the primary training stimulus.",
            "example": f"Bench (80×6 = 480 kg) + Squat (100×5 = 500 kg) = {vol_res['totalVolumeKg']} kg total session tonnage ({vol_res['trainingFocus']}).",
        },
        # DOMAIN 4: TRAINING LOAD & RECOVERY (Formulas 16–20)
        {
            "id": 16,
            "domain": "Training Load",
            "name": "TRIMP Load (Banister & Edwards)",
            "value": f"{workout['trainingLoad']} TRIMP / {workout['edwardsTrimp']} Edwards",
            "formula": "Banister = T × ΔHR × 0.64 × e^(k·ΔHR) · Edwards = T × Z",
            "variables": f"T = Duration ({d.get('duration', 45)} min) · ΔHR = Fractional HR Reserve ((AvgHR−RHR)÷(MHR−RHR)) · k = Sex weighting (1.92 male, 1.67 female) · Z = HR Zone number (1–5)",
            "meaning": "Internal physiological stress score combining workout duration and heart-rate intensity.",
            "example": f"{d.get('duration', 45)} min at {d.get('avgHr', 172)} bpm generates {workout['trainingLoad']} Banister TRIMP and {workout['edwardsTrimp']} Edwards points.",
        },
        {
            "id": 17,
            "domain": "Training Load",
            "name": "ACWR (Acute:Chronic Ratio)",
            "value": f"{acwr_res['acwr']} ({acwr_res['zone']})",
            "formula": "ACWR = Load_7d ÷ Load_28d",
            "variables": f"Load_7d = 7-day Acute daily TRIMP average ({acwr_res['acuteLoad']}) · Load_28d = 28-day Chronic daily TRIMP average ({acwr_res['chronicLoad']})",
            "meaning": "Injury-risk gauge (Gabbett model): 0.8–1.3 is the 'Sweet Spot'; >1.5 signals high overtraining/injury risk.",
            "example": f"Acute ({acwr_res['acuteLoad']}) ÷ Chronic ({acwr_res['chronicLoad']}) = {acwr_res['acwr']} ({acwr_res['zone']}).",
        },
        {
            "id": 18,
            "domain": "Training Load",
            "name": "Training Monotony & Strain",
            "value": f"{acwr_res['monotony']} · Strain {acwr_res['strain']}",
            "formula": "Monotony = μ_7d ÷ σ_7d · Strain = W_load × Monotony",
            "variables": f"μ_7d = 7-day mean daily load · σ_7d = 7-day standard deviation of daily load · W_load = 7-day total weekly load",
            "meaning": "Foster's index of load variation (<1.5 is healthy hard/easy variety; >2.0 means repetitive daily grind).",
            "example": f"Monotony of {acwr_res['monotony']} (<1.5) shows healthy day-to-day load variation, yielding weekly strain of {acwr_res['strain']}.",
        },
        {
            "id": 19,
            "domain": "Training Load",
            "name": "Readiness & Recovery Score",
            "value": f"{ready_res['readinessScore']}/100 ({ready_res['status']})",
            "formula": "Readiness = 100 − (P_fatigue + P_hr + P_sleep + P_sore)",
            "variables": "P_fatigue = Residual load penalty (decays over 48h) · P_hr = Elevated morning RHR penalty · P_sleep = Sleep deficit penalty (<8h) · P_sore = Muscle soreness penalty (1–5)",
            "meaning": "Daily CNS/muscular recovery score (0–100) indicating if you are ready for high-intensity training.",
            "example": f"With 7.5h sleep, 36h rest, and normal resting HR ({d.get('restingHr', 62)} bpm), readiness is {ready_res['readinessScore']}/100 ({ready_res['status']}).",
        },
        {
            "id": 20,
            "domain": "Training Load",
            "name": "Recovery & Hydration Plan",
            "value": f"~{workout['recoveryHours']}h rest · {workout['hydration']['drinkLitres']} L fluid",
            "formula": "Fluid_L = SweatLoss_L × 1.25",
            "variables": f"SweatLoss_L = Estimated sweat lost from duration, intensity & climate ({workout['hydration']['estimatedSweatLossLitres']} L) · 1.25 = ACSM 125% post-exercise fluid replacement factor",
            "meaning": "Recommended post-workout recovery window and fluid/electrolyte rehydration target.",
            "example": f"After this session, rest ~{workout['recoveryHours']}h before hard training and drink {workout['hydration']['drinkLitres']} L fluid.",
        },
        # DOMAIN 5: BODY COMPOSITION & ANTHROPOMETRY (Formulas 21–24)
        {
            "id": 21,
            "domain": "Body Comp",
            "name": "BMI & Ponderal Index",
            "value": f"{bmi['bmi']} kg/m² ({bmi['category']}) · PI {bmi['ponderalIndex']}",
            "formula": "BMI = W ÷ H_m² · PI = W ÷ H_m³",
            "variables": f"W = Weight ({weight} kg) · H_m = Height in meters ({round(height/100, 2)} m) · PI = Rohrer's Ponderal Index (kg/m³)",
            "meaning": "Weight-to-height screening category plus 3D Ponderal Index (more accurate for tall/short athletes).",
            "example": f"{weight} ÷ ({round(height/100, 2)})² = {bmi['bmi']} kg/m² ({bmi['category']}); PI = {weight} ÷ ({round(height/100, 2)})³ = {bmi['ponderalIndex']}.",
        },
        {
            "id": 22,
            "domain": "Body Comp",
            "name": "Body Fat % (U.S. Navy Method)",
            "value": f"{bf['bodyFat']}% ({bf['category']}) · Lean {bf['leanMass']} kg",
            "formula": "BF% = 495 ÷ (1.0324 − 0.19077×log10(Waist−Neck) + 0.15456×log10(H)) − 450",
            "variables": f"Waist = {waist} cm · Neck = {neck} cm · H = Height ({height} cm) · 495 & 450 = Siri body-density conversion constants · LeanMass = W × (1 − BF%/100)",
            "meaning": "Estimates body fat % and lean muscle mass (kg) from tape-measure waist, neck, and height.",
            "example": f"Waist {waist} cm & Neck {neck} cm at {height} cm → {bf['bodyFat']}% body fat ({bf['category']}), Lean Mass = {bf['leanMass']} kg.",
        },
        {
            "id": 23,
            "domain": "Body Comp",
            "name": "Ideal Body Weight (Hamwi/Devine)",
            "value": f"{ibw['idealWeightKg']} kg ({ibw['rangeKg']['min']}–{ibw['rangeKg']['max']} kg)",
            "formula": "IBW = Mean(Hamwi, Devine, Robinson, Miller) · Devine = 50 + 2.3 × InchesOver5ft",
            "variables": f"InchesOver5ft = (Height_cm ÷ 2.54) − 60 ({round(max(0.0, height/2.54 - 60.0), 1)} in) · 50 kg = Base male weight at 5 ft (45.5 kg female) · 2.3 kg = Weight added per inch over 5 ft",
            "meaning": "Consensus healthy reference weight and ±10% athletic frame range for your height.",
            "example": f"For {height} cm height, average ideal weight is {ibw['idealWeightKg']} kg (range: {ibw['rangeKg']['min']}–{ibw['rangeKg']['max']} kg).",
        },
        {
            "id": 24,
            "domain": "Body Comp",
            "name": "Physiological Fitness Age",
            "value": f"{vo2['fitnessAge']} years (Chronological: {age})",
            "formula": "FitnessAge = 20 + (NormVO2_20 − VO2max) ÷ 0.35",
            "variables": f"VO2max = Athlete's aerobic capacity ({vo2['vo2max']} ml/kg/min) · NormVO2_20 = Healthy 20yo baseline (48 male / 40 female) · 0.35 = Average VO2max decline per year of aging",
            "meaning": "How old your cardiovascular system acts compared to your actual age based on VO2max.",
            "example": f"With VO2max = {vo2['vo2max']} ml/kg/min, cardiovascular fitness age is {vo2['fitnessAge']} yrs (chronological age: {age}).",
        },
    ]

    return {
        "athlete": d.get("athlete", "Athlete"),
        "formulasCount": 24,
        "formulasSummary": formulas_summary,
        "metabolic": energy,
        "workout": workout,
        "cardio": {"zones": zones, "vo2max": vo2, "pace": pace_res},
        "strength": {"lift": lift_res, "volume": vol_res},
        "trainingLoad": {"balance": acwr_res, "readiness": ready_res},
        "bodyComposition": {"bmi": bmi, "bodyFat": bf, "idealWeight": ibw, "fitnessAge": vo2["fitnessAge"]},
    }
