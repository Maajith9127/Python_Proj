# Project Write-up: FitPulse and FitMetrics

**Project type:** Partner fitness analytics and REST API system  
**FitPulse developer:** Abdul Maajith — 23MIC0052  
**FitMetrics developer:** Yasash S — 23MIC0060  
**Status:** Two independently deployable applications with service-to-service integration

> Before submission, confirm the student names/IDs, deployed URLs, and references with the project team. This report describes the implementation in the local repositories; it does not claim that either service is a medical device or that every estimate is clinically validated.

## 1. Title

**FitPulse and FitMetrics: A Partnered Fitness Analytics and Workout Tracking System**

FitPulse provides fitness calculations and a consolidated 24-method athlete report. FitMetrics analyzes individual workout sessions, training load, heart-rate intensity, recovery, and energy balance. The two services exchange data through authenticated HTTP APIs.

## 2. Motivation

Fitness information is often split between workout logs, calorie calculators, heart-rate tools, and strength trackers. This project brings several commonly used estimates into accessible web interfaces and REST APIs. An athlete can enter measurements and session details once, see the resulting estimates, and download a summary. The partner design also demonstrates how one service can request a calculation from another instead of duplicating it.

The outputs are estimates based on the supplied inputs and the selected models. They are intended for educational and general fitness-information use, not diagnosis, treatment, or replacement of professional advice.

## 3. Existing gap / event motivating the project and its USP

### Gap

A single workout-analysis tool may report calories or heart rate but not connect those results to longer-term training balance, recovery, body-composition estimates, or daily energy needs. Conversely, a collection of unrelated calculators can use inconsistent inputs and provide no API for other applications.

### Project response / USP

- **FitPulse:** combines 24 calculations/methods across metabolic, cardio, strength, training-load/recovery, and body-composition domains into a master analysis endpoint (`POST /api/v1/fitness/full-analysis`). Its website shows results with explanations, variable definitions, and worked examples, and can generate a PDF report.
- **FitMetrics:** focuses on workout-level analytics and training records, including MET-based calories, heart-rate zones, TRIMP, hydration, readiness, and training-balance metrics.
- **Partner integration:** FitMetrics obtains maintenance calories from FitPulse rather than implementing a separate BMR/TDEE calculation. FitPulse can request workout-analysis data from FitMetrics. Each application can also run locally with a partner stub for development/testing.

The USP is the integration of two focused services through explicit API contracts, rather than a claim that the underlying formulas are novel.

## 4. Architecture

### High-level design

```text
Athlete / Browser
      │
      ├── FitPulse frontend ── FitPulse FastAPI ── calculation engines
      │                              │
      │                              └── calls FitMetrics workout endpoint
      │
      └── FitMetrics frontend ─ FitMetrics FastAPI ── workout/training engines
                                     │
                                     └── calls FitPulse calories endpoint
```

Each repository is a separate FastAPI application with a static HTML/CSS frontend. The backend validates request bodies using Pydantic schemas, routes requests to domain calculation modules, and returns JSON responses. The API documentation is exposed through FastAPI/Swagger at `/docs` when the service is running.

### FitPulse

- FastAPI app: `backend/app/main.py`
- API routers: `backend/app/routers/fitness.py` and `system.py`
- Calculation modules: `backend/app/engine/metabolic.py`, `cardio.py`, `strength.py`, `training.py`, and `body.py`
- PDF reporting: `backend/app/report.py`
- Partner HTTP client: `backend/app/clients/fitmetrics.py`
- Frontend: `frontend/index.html` and `frontend/style.css`
- Local launcher: `run.py` (starts the site/API and local partner stand-in when configured)

### FitMetrics

- FastAPI app: `backend/app/main.py`
- API routers: `backend/app/routers/metrics.py` and `system.py`
- Calculation modules: `backend/app/engine/workout.py`, `cardio.py`, `training.py`, `strength.py`, and `body.py`
- Partner HTTP client: `backend/app/clients/fitpulse.py`
- Frontend: `frontend/index.html`
- Local launcher: `run.py` (starts the site/API and local FitPulse stand-in when configured)

### Service integration and data flow

1. FitMetrics sends athlete demographics/activity-level fields to FitPulse `POST /api/v1/fitness/calories` and uses the returned `dailyCalories` maintenance estimate in its energy-balance calculation.
2. FitPulse sends workout details to FitMetrics `POST /api/v1/metrics/workout-analysis` in the partner-sync flow and can display the returned calorie burn, zone, and training-load information.
3. Partner base URLs, timeouts, and optional keys are configured through environment variables. Local launchers can use a stub so the applications can be demonstrated without the partner deployment being available.

## 5. Complete tech stack

| Area | FitPulse | FitMetrics |
|---|---|---|
| Language | Python 3.8+ (project launcher checks version) | Python 3.8+ (project launcher checks version) |
| Backend framework | FastAPI | FastAPI |
| ASGI server | Uvicorn | Uvicorn |
| Request validation | Pydantic v2 schemas | Pydantic schemas |
| HTTP integration | HTTPX async client | HTTPX async client |
| Frontend | HTML, CSS, browser JavaScript | HTML, CSS, browser JavaScript |
| API documentation | FastAPI OpenAPI / Swagger UI | FastAPI OpenAPI / Swagger UI |
| PDF output | ReportLab | ReportLab (where report endpoints are enabled) |
| Key storage / rate limiting | SQLite plus in-process sliding-window limiter | SQLite plus in-process sliding-window limiter |
| Tests | pytest and FastAPI TestClient | pytest and FastAPI TestClient |
| Deployment configuration | `render.yaml`; Vercel files may exist in the current FitPulse checkout | `render.yaml` |

The exact installed versions should be taken from the repositories' requirements files and deployment build logs at submission time. Current requirements specify minimum versions rather than fully pinned versions.

## 6. Datasets used

**No external/downloaded athlete dataset is used by the implementation described here.** The applications calculate outputs from values entered by the user or sent in an API request.

Data sources at runtime are:

- Athlete-provided values such as age, sex/gender selection, height, weight, circumference measurements, heart rates, activity, duration, distance, and lift/repetition values.
- A built-in MET/activity lookup table used to estimate exercise energy expenditure. It is a set of model constants/reference values in code, not a collected user dataset.
- A built-in sample 28-day daily training-load series used for the FitPulse demo/master analysis when a daily load series is not supplied.
- Standard equation constants and thresholds embedded in the calculation engines.
- Optional partner API responses from the other application.

The project should not be described as training a machine-learning model on a dataset; the calculation engines implement deterministic formula-based estimates. Avoid including real personal or health data in a public demo or report without permission.

## 7. Prompts used for website construction (if applicable)

The code repositories do not contain a complete AI prompt-history file, so the following is a **summary of prompts visible in the development conversation**, not a verified exhaustive log. If the course requires the exact prompts used, replace or supplement this section with the team's own saved prompt history.

- “Explain what each of the 24 formulas does, with an example, and add explanations in the code/page so it is easy to present.”
- “Format the formula matrix so it is easy to read, in a good container with a small description under each item.”
- “Under each formula, add a small example so it is easy to explain during a presentation.”
- “Explain all variables under each formula, including what each variable represents.”
- “Prepare a project write-up for both FitPulse and FitMetrics covering the required report sections.”

These prompts supported explanation and presentation improvements. They do not replace implementation, testing, checking calculations, or validating API behavior. Credit any AI/tool assistance according to the institution's policy.

## 8. API integration

### FitPulse API (base path `/api/v1`)

Notable endpoints include:

- `POST /fitness/full-analysis` — master 24-method synthesis.
- `POST /fitness/calories` — BMR/TDEE and goal-related energy profile; also used by FitMetrics.
- `POST /fitness/workout-analysis` — workout calories, training load, recovery/hydration-related output.
- `POST /fitness/heart-rate-zones`, `/fitness/vo2max`, `/fitness/pace` — cardio calculations.
- `POST /fitness/strength-analysis`, `/fitness/session-volume` — lift estimates and session volume.
- `POST /fitness/training-balance`, `/fitness/readiness`, `/fitness/hydration` — training-load and recovery outputs.
- `POST /fitness/bmi`, `/fitness/body-fat`, `/fitness/ideal-weight` — body-composition estimates.
- `POST /fitness/partner-sync` — calls FitMetrics for workout analysis and combines workout output with FitPulse energy information.
- `POST /reports/fitness-sheet` — downloadable PDF report.

### FitMetrics API (base path `/api/v1`)

Notable endpoints include:

- `POST /metrics/workout-analysis` — workout summary including activity calories, HR intensity/zone, TRIMP, recovery, and hydration.
- `POST /metrics/calories-burned`, `/metrics/workout-intensity`, `/metrics/heart-rate-zones`, `/metrics/hydration` — individual workout metrics.
- `POST /metrics/training-balance`, `/metrics/readiness` — training history and recovery analysis.
- `POST /metrics/pace`, `/metrics/vo2max`, `/metrics/strength-analysis`, `/metrics/session-volume` — cardio and strength calculations.
- `POST /metrics/energy-balance` — requests maintenance calories from FitPulse, totals exercise calories for supplied workouts, and returns a net balance/projection.

### Authentication and responses

Fitness/metrics endpoints are generally protected with an `X-API-Key` header. Public/demo and partner keys are configured in each service; free API keys can be issued through the key endpoint. Do not publish production secrets in this report or repository. Responses generally use a JSON envelope such as `{"success": true, "data": {...}}`; validation and service errors use appropriate HTTP error responses. Rate limiting is configured through environment variables and is currently process-local.

## 9. Users, inputs, formats, and outputs

### Intended users

- Athletes and fitness enthusiasts seeking educational estimates and workout summaries.
- Coaches or instructors reviewing session metrics and training-load trends.
- Developers demonstrating or integrating fitness analytics through REST APIs.
- Project evaluators reviewing a two-service API integration.

These are intended user groups, not evidence of clinical suitability.

### FitPulse inputs

| Input group | Example fields | Format |
|---|---|---|
| Athlete profile | athlete name, age, gender, height (cm), weight (kg) | JSON numbers/strings or web form fields |
| Metabolic/body measurements | activity level, goal, neck/waist/optional hip, body-fat estimate | enums and numeric values |
| Workout/cardio | activity, duration (minutes), average/resting/max HR (bpm), 5K time, Cooper distance, distance | JSON values / form fields |
| Strength | exercise, lifted weight (kg), repetitions, bodyweight, sets | JSON object/list |
| Training/recovery | daily load series, hours since session, sleep hours, soreness, climate | JSON list/numbers/enums |

### FitMetrics inputs

| Input group | Example fields | Format |
|---|---|---|
| Athlete/workout profile | age, gender, weight (kg), activity, duration (minutes) | JSON values / form fields |
| Heart-rate data | resting HR and average HR (bpm) | JSON numbers |
| Hydration context | intensity, climate, optional pre/post workout weight | JSON values / form fields |
| Training history | daily loads, sleep, soreness, recovery time | JSON lists/numbers |
| Energy balance | calories eaten, activity level, list of workouts | JSON numbers/list of objects |

Pydantic request schemas validate required fields and basic types/ranges. Exact optional fields and constraints are defined in each repository's `backend/app/schemas.py`; refer to `/docs` for the deployed OpenAPI contract.

### Outputs

- **FitPulse:** 24-item summary with domains, calculated values, and supporting detail; metabolic profile; cardio zones/VO₂max/pace; strength estimates; training balance/readiness; BMI/body-fat/ideal-weight estimates; downloadable PDF.
- **FitMetrics:** per-workout calories, HR reserve percentage and zone, training-load score, recovery/hydration guidance, and energy-balance summary using FitPulse's maintenance estimate.
- **Both:** JSON API responses and interactive web pages; Swagger/OpenAPI documentation for developers.

## 10. References

Use the following foundational sources as a bibliography starting point, and verify the exact editions/URLs required by your course before submission:

1. Mifflin, M. D., et al. (1990). “A new predictive equation for resting energy expenditure in healthy individuals.” *The American Journal of Clinical Nutrition*, 51(2), 241–247. DOI: 10.1093/ajcn/51.2.241.
2. Roza, A. M., & Shizgal, H. M. (1984). “The Harris Benedict equation reevaluated: resting energy requirements and the body cell mass.” *The American Journal of Clinical Nutrition*, 40(1), 168–182. DOI: 10.1093/ajcn/40.1.168.
3. Katch, F. I., & McArdle, W. D. Lean-body-mass-based resting energy expenditure equation (370 + 21.6 × lean mass); cite the exact textbook/edition used by the course or implementation.
4. Tanaka, H., Monahan, K. D., & Seals, D. R. (2001). “Age-predicted maximal heart rate revisited.” *Journal of the American College of Cardiology*, 37(1), 153–156. DOI: 10.1016/S0735-1097(00)01054-8.
5. Cooper, K. H. (1968). “A means of assessing maximal oxygen intake: correlation between field and treadmill testing.” *JAMA*, 203(3), 201–204.
6. Uth, N., Sørensen, H., Overgaard, K., & Pedersen, P. K. (2004). “Estimation of VO₂max from the ratio between HRmax and HRrest—the Heart Rate Ratio Method.” *European Journal of Applied Physiology*, 91, 111–115.
7. Riegel, P. S. (1981). “Athletic records and human endurance.” *American Scientist*, 69(3), 285–290.
8. Brzycki, M. (1993). “Strength testing—Predicting a one-rep max from reps-to-fatigue.” *Journal of Physical Education, Recreation & Dance*, 64(1), 88–90.
9. Banister, E. W. (1991). “Modeling elite athletic performance.” In *Physiological Testing of the High-Performance Athlete*, 2nd ed., Human Kinetics.
10. Foster, C. (1998). “Monitoring training in athletes with reference to overtraining syndrome.” *Medicine & Science in Sports & Exercise*, 30(7), 1164–1168.
11. American College of Sports Medicine (ACSM). *ACSM's Guidelines for Exercise Testing and Prescription*; cite the edition used for hydration/exercise guidance.
12. Epley, Hamwi, Devine, Robinson, and Miller equations, MET/activity values, and the U.S. Navy circumference method: add the exact source or textbook edition consulted by the project team before submission.
13. FastAPI documentation: https://fastapi.tiangolo.com/
14. Pydantic documentation: https://docs.pydantic.dev/
15. Vercel Python Functions documentation: https://vercel.com/docs/functions/runtimes/python (relevant to FitPulse deployment configuration).

> **Bibliography check before submission:** Add the exact sources/editions consulted for Epley, MET/activity values, hydration, ACWR interpretations, the U.S. Navy body-fat method, and ideal-weight equations. Do not present these estimates as validated clinical advice.

## Conclusion

FitPulse and FitMetrics demonstrate a modular approach to fitness analytics: FitPulse specializes in broad multi-domain calculations, while FitMetrics specializes in workout analysis and energy balance. Their APIs integrate maintenance-energy and workout results, while their web interfaces make the services accessible to non-developer users. The numerical results should be interpreted as formula-based estimates whose accuracy depends on the quality of user inputs and the assumptions of each model.
