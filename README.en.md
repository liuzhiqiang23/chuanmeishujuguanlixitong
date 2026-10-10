# Media Data Management and Recommendation System

**[English](./README.en.md) | [中文](./README.md)**

A course project that builds an end-to-end media analytics and recommendation system. It combines data cleaning, feature engineering, exploratory analysis, box-office prediction, personalized recommendations, a Java API, a web admin interface, and a Python algorithm service.

> This repository is synchronized between [GitHub](https://github.com/liuzhiqiang23/chuanmeishujuguanlixitong) and [Gitee](https://gitee.com/liu-zhiqiang20030520/liuzhiqiangdegit).

## Project goals

Film services such as TMDB and MovieLens contain extensive metadata and user behavior. This project applies data mining and machine learning to content analysis, box-office forecasting, and personalized recommendations, while demonstrating an enterprise-style development workflow.

## Architecture

The Java backend and Python algorithm engine share one cleaned dataset. The modules are organized by capability:

- **Data and preprocessing:** a shared data root, feature engineering, and reusable cleaned outputs.
- **Exploratory data analysis:** one script produces 21 charts, including charts used by the web admin.
- **Box-office prediction:** compare eight models, evaluate RMSE/MAE/R², and expose single-item and batch inference.
- **Recommendations:** combine content similarity with popular genres and cache results on disk.
- **Backend and web app:** Spring Boot serves APIs and the Vue administration interface.
- **Database:** SQL scripts create and populate the analytics and application tables.

~~~text
movie-system/
├── data/                 # The single shared dataset root
├── algorithm/
│   ├── FeatureEDA/        # Data cleaning and exploratory charts
│   ├── boxoffice_prediction/
│   └── movie_recommendation/
├── docs/                 # Analysis, design, review, and integration notes
├── sql/                  # Schema, fixes, and import scripts
├── backend/              # Spring Boot APIs and bundled web assets
├── frontend/             # Vue source
└── requirements.txt
~~~

## Deployment overview

The repository includes application code, datasets, generated charts, web assets, and a Python virtual environment. For a new machine, copy the project directory, start MySQL and Redis, initialize the database, then start the Spring Boot backend.

| Software | Version / use |
|---|---|
| JDK | 17 or later |
| Maven | 3.9 or later |
| MySQL | 8.x |
| Redis | 5 or later; use a password in production |
| Python | 3.10–3.12 when rebuilding the virtual environment |

See the Chinese [user manual](./用户手册.md) for the complete setup, database initialization, and Windows launch commands. The project also provides setup_venv.cmd, start_all.cmd, and restart_backend.cmd.

## Running the analysis

Run commands from the project root. The scripts locate data relative to their own file locations.

~~~bash
# Clean data and create shared features
.venv/Scripts/python.exe algorithm/FeatureEDA/preprocess.py

# Generate 21 EDA charts
.venv/Scripts/python.exe algorithm/FeatureEDA/eda.py

# Compare eight box-office models
.venv/Scripts/python.exe algorithm/boxoffice_prediction/train_all.py
~~~

The web interface is served at http://localhost:8000/admin after the backend is running. It includes data management, user analysis, feature exploration, recommendations, and box-office prediction.

## Configuration and security

- Configure DB_URL, DB_USERNAME, DB_PASSWORD, REDIS_PASSWORD, REMEMBER_ME_KEY, VIDEO_UPLOAD_DIR, and CORS_ALLOWED_ORIGINS through environment variables for production.
- Do not commit these values. Use a dedicated database account rather than root.
- Uploaded video files are size- and format-limited; the server chooses the storage path.
- Keep large poster files outside the application JAR and let nginx serve them from disk.

## License and contribution

This is a course project. Please fork the repository, create a feature branch, commit your changes, and open a pull request.

---

[GitHub profile](https://github.com/liuzhiqiang23) · [Gitee profile](https://gitee.com/liu-zhiqiang20030520)
