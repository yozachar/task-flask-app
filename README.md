# Cajon ![progress](https://img.shields.io/badge/Progress-98%25-teal) [![submission_commit](https://img.shields.io/badge/Submission%20Commit-5fa47b4-brown)](https://github.com/yozachar/task-flask-app/tree/5fa47b4fb7622256099338f5698dcbd2a4865b0a)

> A web application that allows users to log in, upload large CSV files (up to 1GB), and interact with the uploaded data through filtering. The application will display the count of records that match the applied filters.

## Local deployment

### Requirements - setup

1. Git
2. Python
3. PDM
4. Podman/Docker (with compose)

### Process - Deploy

1. Clone the repository: `git clone https://github.com/yozachar/task-flask-app.git`
2. Change directory `cd task-flask-app`
3. Execute `./dev i` to install and set up the project.
4. Run `./dev l` to launch the app.

> On windows, you can use `dev.ps1`.

## Screenshots

| ![1][1] | ![2][2] |
| ------- | ------- |
| ![3][3] | ![4][4] |
| ![5][5] | ![6][6] |

[1]: ./screenshots/Screenshot_from_2024-07-24_12-24-07.png
[2]: ./screenshots/Screenshot_from_2024-07-24_12-24-13.png
[3]: ./screenshots/Screenshot_from_2024-07-24_12-24-19.png
[4]: ./screenshots/Screenshot_from_2024-07-24_12-24-33.png
[5]: ./screenshots/Screenshot_from_2024-07-24_12-24-41.png
[6]: ./screenshots/Screenshot_from_2024-07-24_12-24-50.png

## Requirements

### Functional

- [x] User Authentication
- [x] Data Upload and Management
- [x] Data Interaction
- [x] User Interface
- [ ] Security (WIP)

### Non-functional requirements

- [x] Performance
- [x] Scalability
- [ ] Security (WIP)

## Deliverables

- [x] Version controlled repository
- [x] Functional web app
- [x] Documentation
- [ ] Test suite (WIP)
